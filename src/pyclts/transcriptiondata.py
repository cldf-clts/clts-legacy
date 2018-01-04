# coding: utf-8
from __future__ import unicode_literals
from functools import partial

from clldutils.dsv import UnicodeDictReader
from collections import defaultdict

from pyclts.util import pkg_path
from pyclts.transcriptionsystem import Sound, TranscriptionSystem


def iterdata(what, grapheme_col, *cols):
    with UnicodeDictReader(
            pkg_path('transcriptiondata', what), delimiter='\t') as reader:
        for row in reader:
            grapheme = {"grapheme": row[grapheme_col]}
            plus = []
            if cols:
                for col in cols:
                    grapheme[col.lower()] = row[col]
            yield row['CLTS_NAME'], row['BIPA_GRAPHEME'], grapheme


def read(what, grapheme_col, *cols):
    out = defaultdict(list)
    graphemes, names = [], []
    for name, bipa, grapheme in iterdata(what, grapheme_col, *cols):
        out[name].append(grapheme)
        out[bipa].append(grapheme)
        graphemes += [bipa]
        names += [name]
    return out, graphemes, names


phoible = partial(read, 'phoible.tsv', 'GRAPHEME', 'ID')
pbase = partial(read, 'pbase.tsv', 'GRAPHEME', 'URL')
ruhlen = partial(read, 'creanza.tsv', 'GRAPHEME', 'FREQUENCY')
eurasian = partial(read, 'eurasian.tsv', 'GRAPHEME', 'URL')
lapsyd = partial(read, 'lapsyd.tsv', 'GRAPHEME', 'ID', 'FEATURES')
nidaba = partial(read, 'nidaba.tsv', 'GRAPHEME', 'FEATURES', 'LATEX')


def lingpy(sound_class):
    out = {}
    graphemes, names = [], []
    for name, bipa, grapheme in iterdata('lingpy.tsv', sound_class):
        out[bipa] = out[name] = grapheme
        graphemes += [bipa]
        names += [names]
    return out, graphemes, names


class TranscriptionData(object):
    """
    Class for handling transcription data.
    """
    def __init__(self, data='phoible', system=None):
        self.data, self.sounds, self.names = {
            "phoible": phoible,
            "pbase": pbase,
            "sca": lambda: lingpy('SCA_CLASS'),
            "dolgo": lambda: lingpy('DOLGOPOLSKY_CLASS'),
            "cv": lambda: lingpy('CV_CLASS'),
            "prosody": lambda: lingpy('PROSODY_CLASS'),
            "asjp": lambda: lingpy('ASJP_CLASS'),
            "color": lambda: lingpy('COLOR_CLASS'),
            'lapsyd': lapsyd,
            'eurasian': eurasian,
            'ruhlen': ruhlen,
            'nidaba': nidaba
        }[data]()
        self.name = data
        self.id = data
        self.system = system or TranscriptionSystem()
        # we want to know whether data type is lingpy, as in this case, we want
        # to resolve the mappings
        self._sc = data in ['sca', 'dolgo', 'cv', 'prosody', 'asjp', 'color']

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        if sound.name in self.data:
            dpoints = self.data[sound.name]
            if isinstance(dpoints, dict):
                return dpoints['grapheme']
            return '//'.join([x['grapheme'] for x in dpoints])
        if self._sc:
            if not sound.type == 'unknownsound':                    
                name = [s for s in sound.name.split(' ') if s not in ['apical',
                    'laminal', 'ejective']]
                if sound.type in ['diphthong', 'cluster']:
                    return self.resolve_sound(sound.from_sound)
                while len(name) >= 4:
                    sound = self.system.get(' '.join(name))
                    if sound and sound.name in self.data:
                        return self.resolve_sound(sound)
                    name.pop(0)

        raise KeyError(":resolve_sound_classes: No sound could be found.")

    def __getitem__(self, sound):
        if isinstance(sound, Sound):
            return self.resolve_sound(sound)
        return self.resolve_sound(self.system[sound])
    
    def get(self, sound, default=None):
        try:
            return self[sound]
        except KeyError:
            return default

    def items(self, sound, default=None):
        return self._data.items()

    def __call__(self, sounds, default="0"):
        return [self.get(x, default) for x in sounds.split()]
