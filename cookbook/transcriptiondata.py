# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import defaultdict
import codecs
import json

from clldutils.dsv import UnicodeReader
from clldutils.markup import Table
from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.util import pkg_path

def loadmeta(data):
    bipa = TranscriptionSystem('bipa')

    def write_transcriptiondata(data, filename):
        with open(pkg_path('transcriptiondata', filename).as_posix(), 'w') as handler:
            for line in data:
                handler.write('\t'.join(line)+'\n')
        print('file <{0}> has been successfully written ({1} lines)'.format(filename,
            len(out)))

    if data == 'phoible':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'PHOIBLE_ID', 'PHOIBLE_GRAPHEME']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'Parameters.csv')) as uni:
            for line in uni:
                glyph = line[-4]
                url = line[4]
                sound = bipa[glyph]
                if sound.type != 'unknownsound' and not (sound.generated and
                        frozenset(bipa._norm(glyph)) != frozenset(bipa._norm(sound.s))):
                    out += [[sound.name, sound.s, url, glyph]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound)
                    else:
                        if not sound.type in ['cluster', 'diphthong']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'phoible.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))
    
    if data == 'ruhlen':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'RUHLEN_ID', 'RUHLEN_GRAPHEME']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'Ruhlen_Features_Fonetikode.csv'), delimiter="\t") as uni:
            for i, line in enumerate(uni):
                glyph = line[0]
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (sound.generated and
                        frozenset(bipa._norm(glyph)) != frozenset(bipa._norm(sound.s))):
                    out += [[sound.name, sound.s, str(i), glyph]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound)
                    else:
                        if not sound.type in ['cluster', 'diphthong', 'marker']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'ruhlen.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))

    if data == 'eurasian':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'EURASIAN_URL', 'EURASIAN_GRAPHEME']]
        data = json.load(codecs.open(pkg_path('sources',
            'phono_dbase.json').as_posix(), 'r', 'utf-8'))
        url = 'http://eurasianphonology.info/search_exact?dialects=True&query='
        visited = set()
        for language, vals in data.items():
            for glyph in vals['inv']:
                if glyph not in visited:
                    visited.add(glyph)
                    sound = bipa[glyph]
                    if sound.type not in ['unknownsound', 'marker'] and not (sound.generated and
                            frozenset(bipa._norm(glyph)) != frozenset(bipa._norm(sound.s))):
                        out += [[sound.name, sound.s, url + str(glyph), glyph]]
                    else:
                        if sound.type == 'unknownsound':
                            print(sound)
                        else:
                            if not sound.type in ['cluster', 'diphthong', 'marker']:
                                tbl = sound.table
                                print('\t'.join(tbl))
        write_transcriptiondata(out, 'eurasian.tsv')
        print('{0:.2f} covered'.format(len(out) / len(visited)))




    if data == 'pbase':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'PBASE_URL', 'PBASE_GRAPHEME']]
        url = "http://pbase.phon.chass.ncsu.edu/visualize?lang=True&input={0}&inany=false&coreinv=on"
        with UnicodeReader(pkg_path('sources', 'IPA1999.tsv'), delimiter="\t") as uni:
            all_lines = 0
            for line in uni:
                glyph = line[2]
                url_ = url.format(glyph)
                sound = bipa[glyph]

                if sound.type != 'unknownsound' and not (sound.generated and
                        frozenset(bipa._norm(glyph)) != frozenset(bipa._norm(sound.s))):
                    out += [[sound.name, str(sound), url_, glyph]]
                else:
                    print(sound)
                all_lines += 1
        write_transcriptiondata(out, 'pbase.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))

    if data == 'lingpy':
        from lingpy.sequence.sound_classes import token2class
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'CV_CLASS', 'PROSODY_CLASS', 'SCA_CLASS',
                'DOLGOPOLSKY_CLASS', 'ASJP_CLASS', 'COLOR_CLASS']]
        for glyph, sound in bipa._sounds.items():
            if not sound.alias:
                out += [[sound.name, str(sound)] + [token2class(glyph, m) for m
                         in ['cv', 'art', 'sca', 'dolgo', 'asjp', '_color']]]
        write_transcriptiondata(out, 'lingpy.tsv')


    if data == 'wikipedia':
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


if __name__ == '__main__':
    from sys import argv

    if 'data' in argv: 
        dset = argv[argv.index('data')+1]
        loadmeta(dset)
