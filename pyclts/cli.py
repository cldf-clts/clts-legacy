# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import OrderedDict, defaultdict
import argparse
import unicodedata

from six import text_type
from clldutils.clilib import ArgumentParser, ParserError, command
from clldutils.path import Path
from clldutils.dsv import UnicodeWriter
from clldutils.markup import Table
from pyclts import clts
from pyclts.util import data_path, metadata_path
from pyclts.metadata import phoible

import json

@command()
def sounds(args):
    bipa = clts.CLTS('bipa')
    sounds = [bipa.get(sound) for sound in args.args]
    data = []
    for sound in sounds:
        if sound.type != 'unknownsound':
            data += [[str(sound), 
                sound.source or ' ', 
                '1' if sound.generated else ' ',
                sound.grapheme if sound.alias else ' ',
                sound.name]]
        else:
            data += [['?', sound.source, '?', '?', '?']]
    tbl = Table('BIPA', 'SOURCE', 'GENERATED', 'ALIAS', 'NAME', rows=data)
    print(tbl.render(tablefmt=args.format, condensed=False))

@command()
def table(args):
    bipa = clts.CLTS('bipa')
    sounds = [bipa.get(sound) for sound in args.args]
    if args.filter == 'generated':
        sounds = [s for s in sounds if s.generated]
    elif args.filter == 'unknown':
        sounds = [s for s in sounds if s.type == 'unknownsound']
    elif args.filter == 'known':
        sounds = [s for s in sounds if not s.generated and not s.type == 'unknownsound']

        
    data = defaultdict(list)
    ucount = 0
    for sound in sounds:
        if sound.type != 'unknownsound':
            data[sound.type] += [sound.table]
        else:
            ucount += 1
            data['unknownsound'] += [[str(ucount), sound.source or '', sound.grapheme]]
    for cls in bipa.sound_classes:
        if cls in data:
            print('# {0}\n'.format(cls))
            tbl = Table(*[c.upper() for c in bipa._columns[cls]], rows=data[cls])
            print(tbl.render(tablefmt=args.format, condensed=False))
            print('')
    if data['unknownsound']:
        print('# Unknown sounds\n')
        tbl = Table('NUMBER', 'SOURCE', 'GRAPHEME', rows=data['unknownsound'])
        print(tbl.render(tablefmt=args.format, condensed=False))

@command()
def dump(args):

    bipa = clts.CLTS('bipa')
    phoible_ = phoible()
    dump, digling = {}, {}
    for glyph, sound in bipa._sounds.items():
        if sound.type == 'marker':
            digling[glyph] = ['marker', '', '', '']
            dump[glyph] = {'type': 'marker'}
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
                        ' '.join([x for x in [sound.middle or '', sound.end or
                            '']]),
                        sound.contour]
            dump[glyph] = {k: getattr(sound, k) for k in sound._name_order}
            dump[glyph]['name'] = sound.name
            dump[glyph]['alias'] = sound.alias
            dump[glyph]['bipa'] = str(sound)
            dump[glyph]['type'] = sound.type
            if sound.name in phoible_:
                dump[glyph]['phoible_grapheme'] = phoible_[sound.name]['grapheme']
                dump[glyph]['phoible_id'] = phoible_[sound.name]['id']
            
    with open(data_path('bipa-dump.json'), 'w') as f:
        f.write(json.dumps(dump, indent=1))
    with open(data_path('digling-dump.json'), 'w') as f:
        f.write(json.dumps(digling, indent=1))
    with open(data_path('../app/script.js'), 'w') as f:
        f.write('var BIPA = '+json.dumps(dump)+';\n')
        f.write('var normalize = '+json.dumps(bipa._normalize)+';\n')
    print('files written to clts/data')
                    

def main(args=None):
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

    res = parser.main(args=args)
    if args is None:  # pragma: no cover
        sys.exit(res)
