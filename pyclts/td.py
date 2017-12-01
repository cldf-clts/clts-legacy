# coding: utf-8
from __future__ import unicode_literals

from clldutils.dsv import NamedTupleReader
from collections import defaultdict

from pyclts.util import td_path
from pyclts.ts import Sound, TranscriptionSystem


def phoible():
    out = defaultdict(list)
    with NamedTupleReader(td_path('phoible.tsv'), delimiter='\t') as uni:
        for row in uni:
            if row.PHOIBLE_ID not in [x.get('id', '') for x in
                    out[row.CLTS_NAME]]:
                out[row.CLTS_NAME] += [{
                        "id": row.PHOIBLE_ID, 
                        "grapheme": row.PHOIBLE_GRAPHEME}]
                out[row.BIPA_GRAPHEME] += [out[row.CLTS_NAME]]
    return out


def pbase():
    out = defaultdict(list)
    with NamedTupleReader(td_path('pbase.tsv'), delimiter='\t') as uni:
        for row in uni:
            if row.PBASE_URL not in [x.get('id', '') for x in
                    out[row.CLTS_NAME]]:
                out[row.CLTS_NAME] += [{
                        "id": row.PBASE_URL, 
                        "grapheme": row.PBASE_GRAPHEME}]
                out[row.BIPA_GRAPHEME] += [out[row.CLTS_NAME]]
    return out


def lingpy(sound_class):
    out = {}
    with NamedTupleReader(td_path('lingpy.tsv'), delimiter='\t') as uni:
        for row in uni:
            out[row.CLTS_NAME] = {
                    "grapheme": getattr(row, sound_class), 
                    }
            out[row.BIPA_GRAPHEME] = out[row.CLTS_NAME]
    return out


class TranscriptionData(object):
    """
    Class for handling transcription data.
    """
    def __init__(self, data='phoible', system=None):

        self.data = {
                "phoible": phoible,
                "pbase": pbase,
                "sca": lambda: lingpy('SCA_CLASS'),
                "dolgo": lambda: lingpy('DOLGOPOLSKY_CLASS'),
                "cv": lambda: lingpy('CV_CLASS'),
                "prosody": lambda: lingpy('PROSODY_CLASS'),
                "asjp": lambda: lingpy('ASJP_CLASS'),
                "color": lambda: lingpy('COLOR_CLASS')
                }[data]()
        self.name = data
        self.system = system or TranscriptionSystem()
        # we want to know whether data type is lingpy, as in this case, we want
        # to resolve the mappings
        if data in ['sca', 'dolgo', 'cv', 'prosody', 'asjp', 'color']:
            self._dtype = 'sc'
        else:
            self._dtype = ''

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        if sound.name in self.data:
            return self.data[sound.name]['grapheme']
        elif self._dtype == 'sc':
            if not sound.type == 'unknownsound':                    
                name = sound.name.split(' ')
                if sound.type == 'diphthong':
                    vowel = ' '.join([n[3:] for n in name if n.startswith('to_')]+['vowel'])
                    return self.resolve_sound(self.system[vowel])
                elif sound.type == 'cluster':
                    vowel = ' '.join([n for n in name if
                        n.startswith('to_')]+['cluster'])
                    return self.resolve_sound(self.system[cluster])
                while len(name) >= 4:
                    sound = self.system.get(' '.join(name))
                    if sound:
                        return sound
                    name.pop(0)

        raise KeyError(":resolve_sound_classes: No sound could be found.")

    def __getitem__(self, sound):
        if isinstance(sound, Sound):
            return self.resolve_sound(sound)
        else:
            return self.resolve_sound(self.system[sound])
    
    def get(self, sound, default=None):
        try:
            return self[sound]
        except KeyError:
            return default

    def __call__(self, sounds, default="0"):
        sounds = [self.get(x, default) for x in sounds.split()]
        return sounds

