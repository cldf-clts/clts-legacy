# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import defaultdict
import argparse
import json

from clldutils.clilib import ArgumentParser, command
from clldutils.dsv import UnicodeReader, reader
from clldutils.markup import Table
from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.transcriptiondata import TranscriptionData
from pyclts.util import pkg_path, data_path


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
def dump(args):
    def check(sound, ts):
        """Check the consistency of a given transcription system conversino"""
        if sound.type in ['unknownsound', 'marker']:
            return False
        s1 = ts[sound.name]
        s2 = ts[sound.s]
        if s1.name == s2.name and s1.s == s2.s:
            return True
        return False

    sounds = defaultdict(dict)
    data = [] 
    classes = []
    bipa = TranscriptionSystem('bipa')
    # start from assembling bipa-sounds
    for grapheme, sound in bipa.items():
        if not sound.type in ['marker']:
            if not sound.alias and not sound.name in sounds:
                sounds[sound.name] = {
                        'grapheme': grapheme,
                        'aliases': set([grapheme]),
                        'representation': 1,
                        'td': set(),
                        'ts': set(['bipa']),
                        'sc': set()
                        }
            else:
                if sound.name in sounds:
                    sounds[sound.name]['aliases'].add(grapheme)
                else:
                    sounds[sound.name] = {
                            'grapheme': sound.s,
                            'aliases': set([grapheme, sound.s]),
                            'representation': 1,
                            'td': set(),
                            'ts': set(['bipa']),
                            'sc': set()
                            }
    
    # add sounds systematically by their alias
    for line in reader(pkg_path('transcriptiondata', 'transcriptiondata.tsv'),
            delimiter='\t', namedtuples=True):
        td = TranscriptionData(line.ID)
        if td.id not in ['asjp', 'sca', 'prosody', 'dolgo', 'color']:
            for name in td.names:
                nodiscard = True
                if name not in sounds:
                    bipa_sound = bipa[name]
                    # check for consistency of mapping here
                    if check(bipa_sound, bipa):
                        sounds[name] = {
                                'grapheme': bipa_sound.s,
                                'aliases': set([bipa_sound.s]),
                                'representation': 1,
                                'td': set(),
                                'ts': set(['bipa']),
                                'sc': set()}
                    else:
                        nodiscard = False
                if nodiscard:
                    sounds[name]['representation'] += 1
                    for item in td.data[name]:
                        sounds[name]['aliases'].add(item['grapheme'])
                        sounds[name]['td'].add(td.id)
                        # add the values here
                        data += [(
                            item['grapheme'],
                            name,
                            td.id,
                            item.get('frequency', ''),
                            item.get('url', ''),
                            item.get('id', ''),
                            item.get('features', ''),
                            item.get('image', ''),
                            item.get('sound', ''))]

    # sound classes have a generative component, so we need to treat them
    # separately
    for td_ in ['sca', 'color', 'asjp', 'dolgo', 'prosody']:
        td = TranscriptionData(td_)
        for name in sounds:
            try:
                grapheme = td[name]
                sounds[name]['sc'].add((td.id, grapheme))
                classes += [(
                    sounds[name]['grapheme'],
                    grapheme,
                    name,
                    td.id)] 

            except KeyError:
                print(name, sounds[name]['grapheme'])

            
    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    for line in reader(pkg_path('transcriptionsystems',
        'transcriptionsystems.tsv'), delimiter="\t", namedtuples=True):
        if line.ID != 'bipa':
            ts = TranscriptionSystem(line.ID)
            for name in sounds:
                try:
                    ts_sound = ts[name]
                    # check for consistency of mapping
                    if check(ts_sound, ts):
                        sounds[name]['ts'].add(ts.id)
                        sounds[name]['representation'] += 1
                        sounds[name]['aliases'].add(ts_sound.s)
                except ValueError:
                    pass
                except TypeError:
                    print(ts.id, name)

    with open(data_path('sounds.tsv'), 'w') as f:
        f.write('ID\tGRAPHEME\tALIASES\tREPRESENTATION\tTRANSCRIPTION_SYSTEMS\tTRANSCRIPTION_DATA\tSOUND_CLASSES\n')
        for k, v in sorted(sounds.items(), key=lambda x: x[1]['representation'],
                reverse=True):
            f.write('\t'.join([k, v['grapheme'], ', '.join(sorted(v['aliases'])),
                str(v['representation']), ', '.join(sorted(v['ts'])), 
                ', '.join(sorted(v['td'])),
                ', '.join(['{0}:{1}'.format(k, v) for k, v in sorted(v['sc'])])
                    ])+'\n')

    with open(data_path('classes.tsv'), 'w') as f:
        f.write('GRAPHEME\tSOUND_CLASS\tNAME\tSOUND_CLASS_MODEL\n')
        for line in classes:
            f.write('\t'.join(line)+'\n')

    with open(data_path('graphemes.tsv'), 'w') as f:
        f.write('\t'.join([
            'GRAPHEME', 'NAME', 'TRANSCRIPTION_DATA', 'FREQUENCY', 'URL', 'ID',
            'FEATURES', 'IMAGE', 'SOUND'])+'\n')
        for line in data:
            f.write('\t'.join(line)+'\n')

            

    #for line in reader(pkg_path('transcriptionsystems',
    #    'transcriptionsystems.tsv'), delimiter='\t', namedtuples=True):
    #    ts = TranscriptionSystem(line.ID)
         


@command()
def table(args):
    tts = TranscriptionSystem(args.system)
    tts_sounds = [tts.get(sound) for sound in args.args]
    if args.filter == 'generated':
        tts_sounds = [s for s in tts_sounds if s.generated]
    elif args.filter == 'unknown':
        tts_sounds = [s for s in tts_sounds if s.type == 'unknownsound']
    elif args.filter == 'known':
        tts_sounds = [s for s in tts_sounds if not s.generated and not s.type == 'unknownsound']

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
            tbl = Table(*[c.upper() for c in tts._columns[cls]], rows=data[cls])
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
