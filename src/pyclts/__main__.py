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
from pyclts.soundclasses import SoundClasses
from pyclts.util import pkg_path, data_path, is_valid_sound


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
    visited = set()
    # start from assembling bipa-sounds
    for grapheme, sound in bipa.items():
        if not sound.type in ['marker']:
            
            if not sound.alias and not sound.name in sounds:
                sounds[sound.name] = {
                        'grapheme': grapheme,
                        'unicode': sound.uname or '',
                        'aliases': set([grapheme]),
                        'reflexes': set(['bipa:'+grapheme]),
                        'generated': '0',
                        'note': sound.note or ''
                        }
            else:
                if sound.name in sounds:
                    sounds[sound.name]['aliases'].add(grapheme)
                else:
                    sounds[sound.name] = {
                            'grapheme': sound.s,
                            'aliases': set([grapheme, sound.s]),
                            'unicode': sound.uname or '',
                            'reflexes': set(['bipa:'+sound.s]),
                            'generated': '0',
                            'note': sound.note or ''
                            }
            data += [( grapheme, sound.name, sound.s, 'bipa', 'ts', '0', '',
                '', '', '', sound.note or '')]
            
            visited.add(('bipa', grapheme))
    sound_classes, transcriptions = [], []
    # add sounds systematically by their alias
    for line in reader(data_path('datasets.tsv'),
            delimiter='\t', namedtuples=True):
        if line.TYPE == 'sc':
            sound_classes += [line.NAME]
        elif line.TYPE == 'ts':
            transcriptions += [line.NAME]
        elif line.TYPE == 'td':
            td = TranscriptionData(line.NAME)
            for name in td.names:
                nodiscard = True
                if name not in sounds:
                    bipa_sound = bipa[name]
                    # check for consistency of mapping here
                    if is_valid_sound(bipa_sound, bipa):
                        sounds[name] = {
                                'grapheme': bipa_sound.s,
                                'aliases': set([bipa_sound.s]),
                                'reflexes': set(['bipa:'+bipa_sound.s]),
                                'generated': '1',
                                'unicode': bipa_sound.uname or '',
                                'note': ''
                                }
                    else:
                        nodiscard = False
                if nodiscard:
                    for item in td.data[name]:
                        if (td.id, item['grapheme']) not in visited:
                            sounds[name]['aliases'].add(item['grapheme'])
                            sounds[name]['reflexes'].add(td.id+':'+item['grapheme'])
                            # add the values here
                            data += [( item['grapheme'], name,
                                sounds[name]['grapheme'], td.id, 'td',
                                item.get('frequency', ''), item.get('url', ''),
                                item.get('features', ''), item.get('image',
                                    ''), item.get('sound', '')), '']
                            visited.add((grapheme, td.id))

    # sound classes have a generative component, so we need to treat them
    # separately
    for sc_ in sound_classes:
        sc = SoundClasses(sc_)
        for name in sounds:
            try:
                grapheme = sc[name]
                sounds[name]['reflexes'].add(sc.id+':'+grapheme)
                data += [( grapheme, name, sounds[name]['grapheme'], sc.id,
                    'sc', '0', '', '', '', '', '')] 

            except KeyError:
                print(name, sounds[name]['grapheme'])
            
    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    for tr in transcriptions:
        if tr != 'bipa':
            ts = TranscriptionSystem(tr)
            for name in sounds:
                try:
                    ts_sound = ts[name]
                    if is_valid_sound(ts_sound, ts):
                        sounds[name]['reflexes'].add(ts.id+':'+ts_sound.s)
                        sounds[name]['aliases'].add(ts_sound.s)
                        data += [( ts_sound.s, name, sounds[name]['grapheme'],
                            ts.id, 'ts', '0', '', '', '', '', '')]
                except ValueError:
                    pass
                except TypeError:
                    print(ts.id, name)

    with open(data_path('sounds.tsv').as_posix(), 'w') as f:
        f.write('\t'.join(['NAME', 'GRAPHEME', 'UNICODE', 'ALIASES', 'GENERATED',
            'REFLEXES', 'NOTE'])+'\n')
        for k, v in sorted(sounds.items(), key=lambda x: len(x[1]['reflexes']),
                reverse=True):
            f.write('\t'.join([k, v['grapheme'], v['unicode'],
                ','.join(sorted(v['aliases'])), v['generated'],
                ','.join(sorted(v['reflexes'])), v['note']])+'\n')

    with open(data_path('graphemes.tsv').as_posix(), 'w') as f:
        f.write('\t'.join([
            'GRAPHEME', 'NAME', 'BIPA', 'DATASET', 'DATATYPE', 'FREQUENCY', 'URL',
            'FEATURES', 'IMAGE', 'SOUND', 'NOTE'])+'\n')
        for line in data:
            f.write('\t'.join(line)+'\n')


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
