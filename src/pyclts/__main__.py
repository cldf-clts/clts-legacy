# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import defaultdict
import argparse

import tabulate
import attr

from clldutils.clilib import ArgumentParser, command
from clldutils.dsv import reader, UnicodeWriter
from clldutils.markup import Table
from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.transcriptiondata import TranscriptionData
from pyclts.soundclasses import SoundClasses
from pyclts.util import pkg_path, data_path
from pyclts.models import is_valid_sound


@command()
def sounds(args):
    tts = TranscriptionSystem(args.system)
    tts_sounds = [tts.get(sound) for sound in args.args]
    data = []
    for sound in tts_sounds:
        if sound.type != 'unknownsound':
            data += [[str(sound),
                      sound.source or ' ',
                      '1' if sound.generated else ' ',
                      sound.grapheme if sound.alias else ' ',
                      sound.name]]
        else:
            data += [['?', sound.source, '?', '?', '?']]
    tbl = Table(args.system.upper(), 'SOURCE', 'GENERATED', 'ALIAS', 'NAME', rows=data)
    print(tbl.render(tablefmt=args.format, condensed=False))


@command()
def td(args):
    """Prepare transcriptiondata from the transcription sources."""
    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = TranscriptionSystem('bipa')
    urls = {
        'phoible.tsv': 'http://phoible.org/parameters/{ID}',
        'eurasian.tsv': 'http://eurasianphonology.info/search_exact?dialects=True&query={GRAPHEME}',
        'pbase.tsv': 'http://pbase.phon.chass.ncsu.edu/visualize?lang=True&input={GRAPHEME}&inany=false&coreinv=on',

    }
    for f in pkg_path('sources').iterdir():
        if not f.parts[-1][0] in '._' and f.parts[-1][-3:] == 'tsv':
            print(f.parts[-1], end="\t")
            out = [['BIPA_GRAPHEME', 'CLTS_NAME', 'GENERATED', 'EXPLICIT',
                    'GRAPHEME', 'URL'] + columns]
            graphemes = set()
            for row in reader(f, dicts=True, delimiter='\t'):
                if row['GRAPHEME'] in graphemes:
                    continue
                graphemes.add(row['GRAPHEME'])
                if not row['BIPA']:
                    bipa_sound = bipa[row['GRAPHEME']]
                    generated = '+' if bipa_sound.generated else ''
                    explicit = ''
                else:
                    bipa_sound = bipa[row['BIPA']]
                    generated = '+' if bipa_sound.generated else ''
                    explicit = '+'
                if is_valid_sound(bipa_sound, bipa) and bipa_sound.type != 'marker':
                    bipa_grapheme = bipa_sound.s
                    bipa_name = bipa_sound.name
                else:
                    bipa_grapheme, bipa_name = '<NA>', '<NA>'
                if f.parts[-1] in urls:
                    url = urls[f.parts[-1]].format(**row)
                else:
                    url = row.get('URL', '')
                out.append(
                    [bipa_grapheme, bipa_name, generated, explicit, row['GRAPHEME'],
                     url] + [
                        row.get(c, '') for c in columns])
            found = len([o for o in out if o[0] != '<NA>'])
            total = len(out)
            gens = len([o for o in out if o[2] == '+'])
            print('{0:.2f}% ({1} out of {2})'.format(found / total, found,
                                                     total))
            with UnicodeWriter(pkg_path('transcriptiondata', f.parts[-1]),
                               delimiter='\t') as writer:
                writer.writerows(out)


@command()
def sc(args):
    from lingpy.sequence.sound_classes import token2class
    from lingpy.data import Model
    bipa = TranscriptionSystem('bipa')
    classes = ['sca', 'cv', 'art', 'dolgo', 'asjp', 'color']
    conv = {x: x.upper() + '_CLASS' for x in classes}
    conv['art'] = 'PROSODY_CLASS'
    conv['dolgo'] = 'DOLGOPOLSKY_CLASS'
    count = 0
    with open(pkg_path('soundclasses', 'lingpy.tsv').as_posix(), 'w') as f:
        f.write('CLTS_NAME\tBIPA_GRAPHEME\t' + '\t'.join([
            conv[x] for x in classes]) + '\n')
        for grapheme, sound in bipa.items():
            if not sound.alias:
                f.write(sound.name + '\t' + grapheme)
                for cls in classes:
                    f.write('\t' + token2class(grapheme, Model(cls)))
                f.write('\n')
                count += 1
    print('Wrote {0} sound classes to file.'.format(count))


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
def dump(args):
    sounds = defaultdict(dict)
    data = []
    bipa = TranscriptionSystem('bipa')
    # start from assembling bipa-sounds
    for grapheme, sound in sorted(bipa.sounds.items(), key=lambda p: p[1].alias
            if p[1].alias else False):
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

    mapping = {'td': TranscriptionData, 'ts': TranscriptionSystem, 'sc': SoundClasses}
    datasets = defaultdict(list)
    for line in reader(data_path('datasets.tsv'), delimiter='\t', namedtuples=True):
        datasets[line.TYPE].append(mapping[line.TYPE](line.NAME))

    # add sounds systematically by their alias
    for td in datasets['td']:
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

    # sound classes have a generative component, so we need to treat them
    # separately
    for sc in datasets['sc']:
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
            except KeyError:
                print(name, sounds[name]['grapheme'])

    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    for ts in datasets['ts']:
        if ts.id != 'bipa':
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
                    print(ts.id, name)

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
    sounds = {}
    for row in reader(data_path('sounds.tsv'), delimiter='\t', dicts=True):
        sounds[row['NAME']] = row
    graphs = {}
    for row in reader(data_path('graphemes.tsv'), delimiter='\t', dicts=True):
        graphs['{GRAPHEME}-{NAME}-{DATASET}'.format(**row)] = row

    graphdict = defaultdict(list)
    for id_, row in graphs.items():
        if row['DATATYPE'] == 'td':
            graphdict[row['GRAPHEME']] += [row['DATASET']]

    text = [['DATA', 'STATS', 'PERC']]
    text += [['Unique graphemes',
              len(set([row['GRAPHEME'] for row in graphs.values()]))]]
    text += [['different sounds', len(sounds), '']]
    text += [['singletons', len([g for g in graphdict if len(set(graphdict[g]))
                                 == 1]), '']]
    text += [['multiples', len([g for g in graphdict if len(set(graphdict[g]))
                                > 1]), '']]
    for sc in ['consonant', 'vowel', 'tone', 'diphthong', 'cluster']:
        consonants = len([s for s in sounds.values() if s['TYPE'] == sc])
        total = len(sounds)
        text += [[sc + 's', consonants, '{0:.2f}'.format(consonants / total)]]

    print(tabulate.tabulate(text, headers='firstrow'))


@command()
def table(args):
    tts = TranscriptionSystem(args.system)
    tts_sounds = [tts.get(sound) for sound in args.args]
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
    parser = ArgumentParser('pyclts', formatter_class=argparse.RawTextHelpFormatter)
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
