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

    if data == 'nidaba':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'GRAPHEME', 'LATEX', 'FEATURES']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'nidaba.co.uk'), delimiter='\t') as uni:
            for line in uni:
                glyph = line[0].strip()
                place = line[1].strip()
                stype = line[2].strip()
                manner = line[3].strip()
                features = '{0}::{1}::{2}'.format(stype, place, manner)
                latex = line[4].strip()
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):                    
                        out += [[sound.name, sound.s, glyph, latex, features]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound)
                    else:
                        if not sound.type in ['cluster', 'diphthong']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'nidaba.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))
    
    if data == 'diachronica':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'GRAPHEME', 'URL']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'diachronica.tsv'), delimiter='\t') as uni:
            for line in uni:
                glyph = line[0]
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):                    
                        out += [[sound.name, sound.s, glyph, line[1]]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound)
                    else:
                        if not sound.type in ['cluster', 'diphthong', 'marker']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'diachronica.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))


    if data == 'phoible':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'ID', 'GRAPHEME']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'Parameters.csv')) as uni:
            for line in uni:
                glyph = line[-4]
                url = line[4]
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):
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
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'FREQUENCY', 'GRAPHEME']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'creanza.tsv'), delimiter="\t") as uni:
            for i, line in enumerate(uni):
                glyph = line[0]
                if '+' in glyph:
                    continue
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):
                    out += [[sound.name, sound.s, line[1], glyph]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound)
                    else:
                        if not sound.type in ['cluster', 'diphthong', 'marker']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'creanza.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))

    if data == 'lapsyd':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'ID', 'GRAPHEME',
            'FEATURES']]
        all_lines = 0
        with UnicodeReader(pkg_path('sources', 'lapsyd.tsv'), delimiter="\t") as uni:
            for i, line in enumerate(uni):
                glyph = line[1]
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):
                    out += [[sound.name, sound.s, line[0], glyph, line[2]]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound, line[2])
                    else:
                        if not sound.type in ['cluster', 'diphthong', 'marker']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'lapsyd.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))

    if data == 'multimedia':
        out = [["CLTS_NAME", "BIPA_GRAPHEME", 'GRAPHEME', "IMAGE", "SOUND", "FEATURES"]]
        all_lines = 0
        url1 = 'http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/images/'
        url2 = 'http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/'
        with UnicodeReader(pkg_path('sources', 'sounds.tsv'), delimiter="\t") as uni:
            for i, line in enumerate(uni):
                glyph = line[0]
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                            sound.generated and
                            frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and (
                                    len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):
                    out += [[sound.name, sound.s, line[0], url1+line[3], url2+line[1],
                        line[2]]]
                else:
                    if sound.type == 'unknownsound':
                        print(sound, line[2])
                    else:
                        if not sound.type in ['cluster', 'diphthong', 'marker']:
                            tbl = sound.table
                            print('\t'.join(tbl))
                all_lines += 1
        write_transcriptiondata(out, 'multimedia.tsv')
        print('{0:.2f} covered'.format(len(out) / all_lines))


    if data == 'eurasian':
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'URL', 'GRAPHEME']]
        data = json.load(codecs.open(pkg_path('sources',
            'phono_dbase.json').as_posix(), 'r', 'utf-8'))
        url = 'http://eurasianphonology.info/search_exact?dialects=True&query='
        visited = set()
        for language, vals in data.items():
            for glyph in vals['inv']:
                if glyph not in visited:
                    visited.add(glyph)
                    sound = bipa[glyph]
                    if sound.type not in ['unknownsound', 'marker'] and not \
                        (sound.generated and frozenset(bipa._norm(glyph)) !=
                            frozenset(bipa._norm(sound.s))) and \
                        (len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):
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
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'URL', 'GRAPHEME']]
        url = "http://pbase.phon.chass.ncsu.edu/visualize?lang=True&input={0}&inany=false&coreinv=on"
        with UnicodeReader(pkg_path('sources', 'pbase.tsv'), delimiter="\t") as uni:
            all_lines = 0
            for line in uni:
                glyph = line[0]
                url_ = url.format(glyph)
                sound = bipa[glyph]
                if sound.type not in ['unknownsound', 'marker'] and not (
                        sound.generated and
                        frozenset(bipa._norm(glyph)) !=
                        frozenset(bipa._norm(sound.s))) and (
                                len(bipa._norm(glyph)) == len(bipa._norm(sound.s))):                         
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
        out = [['CLTS_NAME', 'BIPA_GRAPHEME', 'URL']]
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

    if 'all' in argv:
        for itm in ['pbase', 'lingpy', 'phoible', 'eurasian', 'ruhlen',
                'phoible', 'nidaba', 'multimedia', 'diachronica']:
            loadmeta(itm)
