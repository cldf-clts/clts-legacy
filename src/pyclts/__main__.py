# coding: utf-8
"""
Main command line interface to the pyclts package.
"""
from __future__ import unicode_literals, print_function, division
import sys
from collections import defaultdict, Counter

from six import text_type
import tabulate
from uritemplate import URITemplate
import attr

from clldutils.clilib import ArgumentParserWithLogging, command
from clldutils.dsv import reader, UnicodeWriter
from clldutils.markup import Table
from clldutils.path import Path

from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.transcriptiondata import TranscriptionData
from pyclts.soundclasses import SoundClasses, SOUNDCLASS_SYSTEMS
from pyclts.models import is_valid_sound
from pyclts.util import pkg_path


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
    for src in reader(args.repos / 'sources' / 'index.tsv', dicts=True, delimiter='\t'):
        if src['TYPE'] != 'td':
            continue
        graphemesp = args.repos / 'sources' / src['NAME'] / 'graphemes.tsv'
        if not graphemesp.exists():
            continue
        args.log.info('TranscriptionData {0} ...'.format(src['NAME']))
        uritemplate = URITemplate(src['URITEMPLATE']) if src['URITEMPLATE'] else None
        out = [['BIPA_GRAPHEME', 'CLTS_NAME', 'GENERATED', 'EXPLICIT',
                'GRAPHEME', 'URL'] + columns]
        graphemes = set()
        for row in reader(graphemesp, dicts=True, delimiter='\t'):
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
    def data_path(*comps):
        return args.repos.joinpath('data', *comps)

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
    for td in pkg_path('transcriptiondata').iterdir():
        td = TranscriptionData(td.stem)
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
    for sc in SOUNDCLASS_SYSTEMS:
        sc = SoundClasses(sc)
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
    for ts in pkg_path('transcriptionsystems').iterdir():
        if (not ts.is_dir()) or ts.name.startswith('_') or ts.name == 'bipa':
            continue  # pragma: no cover
        ts = TranscriptionSystem(ts.name)
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

    with UnicodeWriter(data_path('sounds.tsv'), delimiter='\t') as writer:
        writer.writerow([
            'NAME', 'TYPE', 'GRAPHEME', 'UNICODE', 'GENERATED', 'NOTE'])
        for k, v in sorted(sounds.items(), reverse=True):
            writer.writerow([
                k, v['type'], v['grapheme'], v['unicode'], v['generated'], v['note']])

    with UnicodeWriter(data_path('graphemes.tsv'), delimiter='\t') as writer:
        writer.writerow([f.name for f in attr.fields(Grapheme)])
        for row in data:
            writer.writerow(attr.astuple(row))


@command()
def stats(args):
    def data_path(*comps):
        return args.repos.joinpath('data', *comps)
    sounds = {}
    for row in reader(data_path('sounds.tsv'), delimiter='\t', dicts=True):
        sounds[row['NAME']] = row
    graphs = {}
    for row in reader(data_path('graphemes.tsv'), delimiter='\t', dicts=True):
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
            data['unknownsound'] += [[str(ucount), sound.source or '', sound.grapheme]]
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
        default=Path(__file__).parent.parent.parent,
        type=Path,
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
        default="bipa"
    )

    res = parser.main(args=args)
    if args is None:  # pragma: no cover
        sys.exit(res)
