# coding: utf-8
"""
Main command line interface to the pyclts package.
"""
from __future__ import unicode_literals, print_function, division
import sys
from collections import defaultdict, Counter
import json

from six import text_type
import tabulate
from uritemplate import URITemplate
import attr

from clldutils.clilib import ArgumentParserWithLogging, command
from clldutils.dsv import reader, UnicodeWriter
from clldutils.markup import Table
from clldutils.path import Path

from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.soundclasses import SOUNDCLASS_SYSTEMS
from pyclts.models import is_valid_sound
from pyclts.util import pkg_path
from pyclts.api import CLTS


@command()
def sounds(args):
    tts = TranscriptionSystem(args.system)
    data = []
    for sound in args.args:
        sound = tts.get(sound if isinstance(sound, text_type) else sound.decode('utf8'))
        if sound.type != 'unknownsound':
            data += [[text_type(sound),
                      sound.source or ' ',
                      '1' if sound.generated else ' ',
                      sound.grapheme if sound.alias else ' ',
                      sound.name]]
        else:
            data += [['?', sound.source, '?', '?', '?']]
    tbl = Table(args.system.upper(), 'SOURCE', 'GENERATED', 'ALIAS', 'NAME', rows=data)
    print(tbl.render(tablefmt=args.format, condensed=False))


@command()
def _make_package(args):  # pragma: no cover
    """Prepare transcriptiondata from the transcription sources."""
    from lingpy.sequence.sound_classes import token2class
    from lingpy.data import Model

    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = TranscriptionSystem('bipa')
    for src, rows in args.repos.iter_sources(type='td'):
        args.log.info('TranscriptionData {0} ...'.format(src['NAME']))
        uritemplate = URITemplate(src['URITEMPLATE']) if src['URITEMPLATE'] else None
        out = [['BIPA_GRAPHEME', 'CLTS_NAME', 'GENERATED', 'EXPLICIT',
                'GRAPHEME', 'URL'] + columns]
        graphemes = set()
        for row in rows:
            if row['GRAPHEME'] in graphemes:
                args.log.warn('skipping duplicate grapheme: {0}'.format(row['GRAPHEME']))
                continue
            graphemes.add(row['GRAPHEME'])
            if not row['BIPA']:
                bipa_sound = bipa[row['GRAPHEME']]
                explicit = ''
            else:
                bipa_sound = bipa[row['BIPA']]
                explicit = '+'
            generated = '+' if bipa_sound.generated else ''
            if is_valid_sound(bipa_sound, bipa):
                bipa_grapheme = bipa_sound.s
                bipa_name = bipa_sound.name
            else:
                bipa_grapheme, bipa_name = '<NA>', '<NA>'
            url = uritemplate.expand(**row) if uritemplate else row.get('URL', '')
            out.append(
                [bipa_grapheme, bipa_name, generated, explicit, row['GRAPHEME'],
                 url] + [
                    row.get(c, '') for c in columns])
        found = len([o for o in out if o[0] != '<NA>'])
        args.log.info('... {0} of {1} graphemes found ({2:.0f}%)'.format(
            found, len(out), found / len(out) * 100))
        with UnicodeWriter(
            pkg_path('transcriptiondata', '{0}.tsv'.format(src['NAME'])), delimiter='\t'
        ) as writer:
            writer.writerows(out)

    count = 0
    with UnicodeWriter(pkg_path('soundclasses', 'lingpy.tsv'), delimiter='\t') as writer:
        writer.writerow(['CLTS_NAME', 'BIPA_GRAPHEME'] + SOUNDCLASS_SYSTEMS)
        for grapheme, sound in sorted(bipa.sounds.items()):
            if not sound.alias:
                writer.writerow(
                    [sound.name, grapheme] +
                    [token2class(grapheme, Model(cls)) for cls in SOUNDCLASS_SYSTEMS])
                count += 1
    args.log.info('SoundClasses: {0} written to file.'.format(count))


@command()
def _make_app_data(args, test=False):
    tts = TranscriptionSystem('bipa')

    def sound_to_dict(snd):
        res = {'name': snd.name, 'bipa': snd.s, 'type': snd.type}
        for f in snd._name_order:
            res[f] = getattr(snd, f)
        return res

    # retrieve all sounds in the datasets
    all_sounds = {}
    for td in args.repos.iter_transcriptiondata():
        for sound in td.data:
            if ' ' in sound:
                snd = tts[sound]
                glyph = snd.s
                assert '<?>' not in snd.s
                if snd.s not in all_sounds:
                    all_sounds[glyph] = sound_to_dict(snd)
                for item in td.data[sound]:
                    if item['grapheme'] not in all_sounds:
                        all_sounds[item['grapheme']] = all_sounds[glyph]

                all_sounds[glyph][td.id] = td.data[sound]
        if test:
            break

    # add sounds from transcription system
    for sound in tts:
        if sound not in all_sounds:
            snd = tts[sound]
            if snd.type != 'marker':
                if snd.s in all_sounds:
                    all_sounds[sound] = all_sounds[snd.s]
                else:
                    all_sounds[sound] = sound_to_dict(snd)

    args.log.info('{0} unique graphemes loaded'.format(len(all_sounds)))

    for i, sc in enumerate(args.repos.iter_soundclass()):
        for sound in all_sounds:
            try:
                all_sounds[sound][sc.id] = [dict(grapheme=sc[sound])]
            except KeyError:  # pragma: no cover
                pass
            if i == 0:
                if hasattr(sound, 's'):
                    all_sounds[sound]['bipa'] = tts[sound].s
        if test:
            break

    datafile = args.repos.app_path('data.js')
    with datafile.open('w', encoding='utf8') as handler:
        handler.write('var BIPA = ' + json.dumps(all_sounds, indent=2) + ';\n')
        handler.write('var normalize = ' + json.dumps(tts._normalize) + ';\n')
    args.log.info('{0} written'.format(datafile))


@attr.s
class Grapheme(object):
    GRAPHEME = attr.ib()
    NAME = attr.ib()
    EXPLICIT = attr.ib()
    ALIAS = attr.ib()
    DATASET = attr.ib()
    FREQUENCY = attr.ib(default=0)
    URL = attr.ib(default='')
    FEATURES = attr.ib(default='')
    IMAGE = attr.ib(default='')
    SOUND = attr.ib(default='')
    NOTE = attr.ib(default='')


@command()
def dump(args, test=False):
    sounds = defaultdict(dict)
    data = []
    bipa = TranscriptionSystem('bipa')
    # start from assembling bipa-sounds
    for grapheme, sound in sorted(
            bipa.sounds.items(), key=lambda p: p[1].alias if p[1].alias else False):
        if sound.type not in ['marker']:
            if sound.alias:
                assert sound.name in sounds
                sounds[sound.name]['aliases'].add(grapheme)
            else:
                assert sound.name not in sounds
                sounds[sound.name] = {
                    'grapheme': grapheme,
                    'unicode': sound.uname or '',
                    'generated': '',
                    'note': sound.note or '',
                    'type': sound.type,
                    'aliases': set(),
                    'normalized': '+' if sound.normalized else ''
                }
            data.append(Grapheme(
                grapheme,
                sound.name,
                '+',
                '',
                'bipa',
                '0',
                '',
                '',
                '',
                '',
                sound.note or ''))

    # add sounds systematically by their alias
    for td in args.repos.iter_transcriptiondata():
        for name in td.names:
            bipa_sound = bipa[name]
            # check for consistency of mapping here
            if not is_valid_sound(bipa_sound, bipa):
                continue

            sound = sounds.get(name)
            if not sound:
                sound = sounds[name] = {
                    'grapheme': bipa_sound.s,
                    'aliases': {bipa_sound.s},
                    'generated': '+',
                    'unicode': bipa_sound.uname or '',
                    'note': '',
                    'type': bipa_sound.type,
                    'alias': '+' if bipa_sound.alias else '',
                    'normalized': '+' if bipa_sound.normalized else ''
                }

            for item in td.data[name]:
                sound['aliases'].add(item['grapheme'])
                # add the values here
                data.append(Grapheme(
                    item['grapheme'],
                    name,
                    item['explicit'],
                    '',  # sounds[name]['alias'],
                    td.id,
                    item.get('frequency', ''),
                    item.get('url', ''),
                    item.get('features', ''),
                    item.get('image', ''),
                    item.get('sound', ''),
                ))
        if test:
            break

    # sound classes have a generative component, so we need to treat them
    # separately
    for sc in args.repos.iter_soundclass():
        for name in sounds:
            try:
                grapheme = sc[name]
                data.append(Grapheme(
                    grapheme,
                    name,
                    '+' if name in sc.data else '',
                    '',
                    sc.id,
                ))
            except KeyError:  # pragma: no cover
                args.log.debug(name, sounds[name]['grapheme'])
        if test:
            break

    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    for ts in args.repos.iter_transcriptionsystem(exclude=['bipa']):
        for name in sounds:
            try:
                ts_sound = ts[name]
                if is_valid_sound(ts_sound, ts):
                    sounds[name]['aliases'].add(ts_sound.s)
                    data.append(Grapheme(
                        ts_sound.s,
                        name,
                        '' if sounds[name]['generated'] else '+',
                        '',  # sounds[name]['alias'],
                        ts.id,
                    ))
            except ValueError:
                pass
            except TypeError:
                args.log.debug('{0}: {1}'.format(ts.id, name))
        if test:
            break

    with UnicodeWriter(args.repos.data_path('sounds.tsv'), delimiter='\t') as writer:
        writer.writerow([
            'NAME', 'TYPE', 'GRAPHEME', 'UNICODE', 'GENERATED', 'NOTE'])
        for k, v in sorted(sounds.items(), reverse=True):
            writer.writerow([
                k, v['type'], v['grapheme'], v['unicode'], v['generated'], v['note']])

    with UnicodeWriter(args.repos.data_path('graphemes.tsv'), delimiter='\t') as writer:
        writer.writerow([f.name for f in attr.fields(Grapheme)])
        for row in data:
            writer.writerow(attr.astuple(row))


@command()
def features(args):
    bipa = TranscriptionSystem(args.system)
    features = set()
    for sound in bipa.sounds.values():
        if sound.type not in ['marker', 'unknownsound']:
            for k, v in sound.featuredict.items():
                features.add((sound.type, k, v or ''))
    table = Table('TYPE', 'FEATURE', 'VALUE')
    table.extend(sorted(features))
    print(table.render(tablefmt='simple'))


@command()
def stats(args):
    sounds = {}
    for row in reader(args.repos.data_path('sounds.tsv'), delimiter='\t', dicts=True):
        sounds[row['NAME']] = row
    graphs = {}
    for row in reader(args.repos.data_path('graphemes.tsv'), delimiter='\t', dicts=True):
        graphs['{GRAPHEME}-{NAME}-{DATASET}'.format(**row)] = row

    graphdict = defaultdict(list)
    for id_, row in graphs.items():
        graphdict[row['GRAPHEME']] += [row['DATASET']]

    text = [['DATA', 'STATS', 'PERC']]
    text.append(
        ['Unique graphemes', len(set(row['GRAPHEME'] for row in graphs.values())), ''])
    text.append(['different sounds', len(sounds), ''])
    text.append(
        ['singletons', len([g for g in graphdict if len(set(graphdict[g])) == 1]), ''])
    text.append(
        ['multiples', len([g for g in graphdict if len(set(graphdict[g])) > 1]), ''])
    total = len(sounds)
    for type_, count in Counter([s['TYPE'] for s in sounds.values()]).most_common():
        text.append([type_ + 's', count, '{0:.2f}'.format(count / total)])

    print(tabulate.tabulate(text, headers='firstrow'))


@command()
def table(args):
    tts = TranscriptionSystem(args.system)
    tts_sounds = [tts.get(sound if isinstance(sound, text_type) else sound.decode('utf8'))
                  for sound in args.args]
    if args.filter == 'generated':
        tts_sounds = [s for s in tts_sounds if s.generated]
    elif args.filter == 'unknown':
        tts_sounds = [s for s in tts_sounds if s.type == 'unknownsound']
    elif args.filter == 'known':
        tts_sounds = [s for s in tts_sounds if
                      not s.generated and not s.type == 'unknownsound']

    data = defaultdict(list)
    ucount = 0
    for sound in tts_sounds:
        if sound.type != 'unknownsound':
            data[sound.type] += [sound.table]
        else:
            ucount += 1
            data['unknownsound'].append(
                [text_type(ucount), sound.source or '', sound.grapheme])
    for cls in tts.sound_classes:
        if cls in data:
            print('# {0}\n'.format(cls))
            tbl = Table(*[c.upper() for c in tts.columns[cls]], rows=data[cls])
            print(tbl.render(tablefmt=args.format, condensed=False))
            print('')
    if data['unknownsound']:
        print('# Unknown sounds\n')
        tbl = Table('NUMBER', 'SOURCE', 'GRAPHEME', rows=data['unknownsound'])
        print(tbl.render(tablefmt=args.format, condensed=False))


def main(args=None):  # pragma: no cover
    parser = ArgumentParserWithLogging('pyclts')
    parser.add_argument(
        "--repos",
        default=CLTS(repos=Path(__file__).parent.parent.parent),
        type=CLTS,
        help="Path to clts repos.")
    parser.add_argument(
        "--format",
        default="pipe",
        help="Format of tabular output.")
    parser.add_argument(
        '--nonames', help="do not report the sound names in the output",
        action='store_true')
    parser.add_argument(
        '--filter', help="only list generated sounds",
        default='')
    parser.add_argument(
        '--data', help="specify the transcription data you want to load",
        default="phoible")
    parser.add_argument(
        '--system', help="specify the transcription system you want to load",
        default="bipa")

    res = parser.main(args=args)
    if args is None:  # pragma: no cover
        sys.exit(res)
