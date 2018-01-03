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
from pyclts.transcriptiondata import TranscriptionData
from pyclts.util import pkg_path, app_path

def dump():
    """Command writes data to different files for re-use across web-applications.
    """
    tts = TranscriptionSystem('bipa')
    phoible, color, sca, dolgo, asjp, ruhlen, pbase, eurasian, lapsyd = [
            TranscriptionData(x) for x in ['phoible', 'color', 'sca', 'dolgo',
                'asjp', 'ruhlen',
            'pbase', 'eurasian', 'lapsyd']]

    # retrieve all sounds in the datasets
    to_dump, digling = {}, {}
    all_sounds = {}
    bads = 0
    for td in [phoible, ruhlen, pbase, eurasian, lapsyd]:
        for sound in td.data:
            if ' ' in sound:
                snd = tts[sound]
                glyph = snd.s
                if not '<?>' in snd.s:
                    if snd.s not in all_sounds:
                        all_sounds[glyph] = {}
                        for f in snd._name_order:
                            all_sounds[glyph][f] = getattr(snd, f)
                        all_sounds[glyph]['name'] = snd.name
                        all_sounds[glyph]['bipa'] = glyph
                    for item in td.data[sound]:
                        if item['grapheme'] not in all_sounds:
                            all_sounds[item['grapheme']] = all_sounds[glyph]
                        
                    all_sounds[glyph][td.name] = td.data[sound]
                else:
                    print(snd.name, snd.s)
                    bads += 1
    # add sounds from transcription system
    for sound in tts:
        if sound not in all_sounds:
            snd = tts[sound]
            if snd.type != 'marker':
                if snd.s in all_sounds:
                    all_sounds[sound] = all_sounds[snd.s]
                else:
                    all_sounds[sound] = {}
                    for f in snd._name_order:
                        all_sounds[sound][f] = getattr(snd, f)
                    all_sounds[sound]['name'] = snd.name
                    all_sounds[sound]['bipa'] = snd.s

    print(bads, len(all_sounds))
    for sound in all_sounds:
        all_sounds[sound]['asjp'] = [dict(grapheme = asjp[sound])]
        all_sounds[sound]['sca'] =   [dict(grapheme= sca[sound])]
        all_sounds[sound]['color'] = [dict(grapheme= color[sound])]
        all_sounds[sound]['dolgo'] = [dict(grapheme= dolgo[sound])]
        all_sounds[sound]['type'] = tts[sound].type
        all_sounds[sound]['bipa'] = tts[sound].s

    for glyph in all_sounds:
        sound = tts[glyph]
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
                    sound.from_sound.height + ' ' +sound.to_sound.height,
                    sound.from_sound.centrality + ' ' + sound.to_sound.centrality,
                    sound.from_sound.roundedness + ' ' + sound.to_sound.roundedness,
                    ]
            if sound.type == 'tone':
                digling[glyph] = [ 
                    sound.type,
                    sound.start,
                    ' '.join([x for x in [sound.middle or '', sound.end or '']]),
                    sound.contour]

    #with open(data_path('digling-dump.json'), 'w') as handler:
    #    handler.write(json.dumps(digling, indent=1))
    with open(app_path('data.js').as_posix(), 'w') as handler:
        handler.write('var BIPA = '+json.dumps(all_sounds,
            indent=2)+';\n')
        handler.write('var normalize = '+json.dumps(tts._normalize)+';\n')
    print('files written ')

if __name__ == "__main__":
    dump()
