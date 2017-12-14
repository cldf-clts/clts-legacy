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


@command()
def loadmeta(args):
    bipa = TranscriptionSystem('bipa')

    def write_transcriptiondata(data, filename):
        with open(pkg_path('transcriptiondata', filename).as_posix(), 'w') as handler:
            for line in data:
                handler.write('\t'.join(line)+'\n')
        print('file <{0}> has been successfully written ({1} lines)'.format(filename,
            len(out)))

    if args.data == 'phoible':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'PHOIBLE_ID', 'PHOIBLE_GRAPHEME']]
        with UnicodeReader(pkg_path('sources', 'Parameters.csv')) as uni:
            for line in uni:
                glyph = line[-4]
                url = line[4]
                sound = bipa[glyph]
                if sound.type != 'unknownsound' and not (sound.generated and str(sound) != glyph):
                    out += [[sound.name, str(sound), url, glyph]]
        write_transcriptiondata(out, 'phoible.tsv')

    if args.data == 'pbase':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'PBASE_URL', 'PBASE_GRAPHEME']]
        url = "http://pbase.phon.chass.ncsu.edu/visualize?lang=True&input={0}&inany=false&coreinv=on"
        with UnicodeReader(pkg_path('sources', 'IPA1999.tsv'), delimiter="\t") as uni:
            for line in uni:
                glyph = line[2]
                url_ = url.format(glyph)
                try:
                    sound = bipa[glyph]
                    if sound.type != 'unknownsound' and not (sound.generated and str(sound) != glyph):
                        out += [[sound.name, str(sound), url_, glyph]]
                except KeyError:
                    pass
        write_transcriptiondata(out, 'pbase.tsv')

    if args.data == 'lingpy':
        from lingpy.sequence.sound_classes import token2class
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'CV_CLASS', 'PROSODY_CLASS', 'SCA_CLASS',
                'DOLGOPOLSKY_CLASS', 'ASJP_CLASS', 'COLOR_CLASS']]
        for glyph, sound in bipa._sounds.items():
            if not sound.alias:
                out += [[sound.name, str(sound)] + [token2class(glyph, m) for m
                         in ['cv', 'art', 'sca', 'dolgo', 'asjp', '_color']]]
        write_transcriptiondata(out, 'lingpy.tsv')

    if args.data == 'wikipedia':
        import urllib.request, urllib.error, urllib.parse
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'WIKIPEDIA_URL']]
        wiki = 'https://en.wikipedia.org/wiki/'
        for glyph, sound in bipa._sounds.items():
            if not sound.alias and not sound.type in ['marker', 'diphthong']:
                if not sound.type == 'click':
                    url1 = wiki + '_'.join(sound.name.split(' ')[:-1])
                    url2 = wiki + '_'.join([s for s in sound.name.split(' ') if
                        s not in ['consonant', 'vowel', 'diphthong', 'cluster',
                        'voiced', 'unvoiced']])
                else:
                    url1 = wiki + '_'.join(sound.name.split(' '))
                    url2 = wiki+urllib.parse.quote(str(sound))
                try:
                    with urllib.request.urlopen(url1) as response:
                        pass
                    out += [[sound.name, str(sound), url1]]
                    print("found url for {0}".format(sound))
                except urllib.error.HTTPError:
                    print("no url found for {0}".format(sound))
                    try:
                        with urllib.request.urlopen(url2) as response:
                            pass
                        out += [[sound.name, str(sound), url2]]
                    except urllib.error.HTTPError:
                        print("really no url found for {0}".format(sound))

        write_transcriptiondata(out, 'wikipedia.tsv')


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
