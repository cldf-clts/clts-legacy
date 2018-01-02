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
from clldutils.dsv import UnicodeReader
from clldutils.markup import Table
from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.util import pkg_path


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


@command()
def dump(args):
    """Command writes data to different files for re-use across web-applications.
    """
    tts = clts.CLTS(args.system)
    phoible_, pbase_, lingpy_ = phoible(), pbase(), lingpy()
    to_dump, digling = {}, {}
    for glyph, sound in tts._sounds.items():
        if sound.type == 'marker':
            digling[glyph] = ['marker', '', '', '']
            to_dump[glyph] = {'type': 'marker'}
        else:
            if sound.type == 'consonant':
                digling[glyph] = [
                    sound.type,
                    sound.manner,
                    sound.place,
                    sound.phonation + ' ' + sound.table[-2]]
            if sound.type == 'vowel':
                digling[glyph] = [
                    sound.type,
                    sound.height,
                    sound.centrality,
                    sound.roundedness + ' ' + sound.table[-2]]
            if sound.type == 'diphthong':
                digling[glyph] = [
                    sound.type,
                    sound.from_height + ' ' +sound.to_height,
                    sound.from_centrality + ' ' + sound.to_centrality,
                    sound.from_roundedness + ' ' + sound.to_roundedness,
                    ]
            if sound.type == 'tone':
                digling[glyph] = [
                    sound.type,
                    sound.start,
                    ' '.join([x for x in [sound.middle or '', sound.end or '']]),
                    sound.contour]
            to_dump[glyph] = {k: getattr(sound, k) for k in sound._name_order}
            to_dump[glyph]['name'] = sound.name
            to_dump[glyph]['alias'] = sound.alias
            to_dump[glyph][args.system] = str(sound)
            to_dump[glyph]['type'] = sound.type
            if sound.name in phoible_:
                to_dump[glyph]['phoible'] = phoible_[sound.name]
            if sound.name in pbase_:
                to_dump[glyph]['pbase'] = pbase_[sound.name]
            if sound.name in lingpy_:
                to_dump[glyph]['color'] = lingpy_[sound.name]['color']

    with open(data_path(args.system+'-dump.json'), 'w') as handler:
        handler.write(json.dumps(to_dump, indent=1))
    with open(data_path('digling-dump.json'), 'w') as handler:
        handler.write(json.dumps(digling, indent=1))
    with open(data_path('../app/data.js'), 'w') as handler:
        handler.write('var '+args.system.upper()+' = '+json.dumps(to_dump)+';\n')
        handler.write('var normalize = '+json.dumps(tts._normalize)+';\n')
    print('files written to clts/data')


def main(args=None):  # pragma: no cover
    parser = ArgumentParser('pyclts', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--format",
        default="markdown",
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
