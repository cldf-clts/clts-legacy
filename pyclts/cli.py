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
    elif args.filter == 'unkown':
        sounds = [s for s in sounds if s.type == 'unknownsound']
        
    data = defaultdict(list)
    for sound in sounds:
        if sound.type != 'unknownsound':
            data[sound.type] += [sound.table]
        else:
            data['unkownsound'] = [sound]
    for cls in bipa.sound_classes:
        if cls in data:
            print('# {0}\n'.format(cls))
            tbl = Table(*[c.upper() for c in bipa._columns[cls]], rows=data[cls])
            print(tbl.render(tablefmt=args.format, condensed=False))
            print('')
    if data['unknownsound']:
        print('# Unknown sounds\n')
        print('\n'.join(data['unknownsound']))

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
