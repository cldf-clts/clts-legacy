# coding: utf-8
from __future__ import unicode_literals

from pyclts.util import read_data, TranscriptionBase
from pyclts.transcriptionsystem import Sound, TranscriptionSystem


class TranscriptionData(TranscriptionBase):
    """
    Class for handling transcription data.
    """
    def __init__(self, id_):
        if not hasattr(self, 'data'):
            # Only initialize, if this is really a new instance!
            self.data, self.sounds, self.names = read_data(
                'transcriptiondata',
                id_ + '.tsv',
                'GRAPHEME',
                'URL',
                'BIPA_GRAPHEME',
                'GENERATED',
                'URL',
                'LATEX',
                'FEATURES',
                'SOUND',
                'IMAGE',
                'COUNT',
                'NOTE',
                'EXPLICIT'
            )
            self.system = TranscriptionSystem('bipa')

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
