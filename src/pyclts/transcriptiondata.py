# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict

from pyclts.util import iterdata
from pyclts.transcriptionsystem import Sound, TranscriptionSystem
from pyclts.models import TranscriptionBase


class TranscriptionData(TranscriptionBase):
    """
    Class for handling transcription data.
    """
    def __init__(self, data='phoible', system=None):
        self.data, self.sounds, self.names = defaultdict(list), [], []
        for name, bipa, grapheme in iterdata(
            'transcriptiondata',
            data + '.tsv',
            'GRAPHEME', 'URL',
            'BIPA_GRAPHEME', 'GENERATED', 'URL', 'LATEX', 'FEATURES', 'SOUND',
            'IMAGE', 'COUNT', 'NOTE', 'EXPLICIT'
        ):
            self.data[name].append(grapheme)
            self.data[bipa].append(grapheme)
            self.sounds += [bipa]
            self.names += [name]
        self.id = data
        self.system = system or TranscriptionSystem()
        # we want to know whether data type is lingpy, as in this case, we want
        # to resolve the mappings

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        sound = sound if isinstance(sound, Sound) else self.system[sound]
        if sound.name in self.data:
            return '//'.join([x['grapheme'] for x in self.data[sound.name]])
        raise KeyError(":td:resolve_sound: No sound could be found.")
