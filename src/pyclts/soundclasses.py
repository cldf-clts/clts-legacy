# coding: utf-8
from __future__ import unicode_literals

from pyclts.transcriptionsystem import Sound, TranscriptionSystem
from pyclts.util import iterdata
from pyclts.models import TranscriptionBase

SOUNDCLASS_SYSTEMS = ['sca', 'cv', 'art', 'dolgo', 'asjp', 'color']


class SoundClasses(TranscriptionBase):
    """
    Class for handling sound class models.
    """
    def __init__(self, data='sca', system=None):
        assert data in SOUNDCLASS_SYSTEMS
        self.data, self.sounds, self.names = {}, [], []

        for sound_name, sound_bipa, grapheme in iterdata(
                'soundclasses', 'lingpy.tsv', data):
            self.data[sound_bipa] = self.data[sound_name] = grapheme
            self.sounds.append(sound_bipa)
            self.names.append(sound_name)

        self.id = data
        self.system = system or TranscriptionSystem()

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
            return self.data[sound.name]['grapheme']
        if not sound.type == 'unknownsound':
            if sound.type in ['diphthong', 'cluster']:
                return self.resolve_sound(sound.from_sound)
            name = [s for s in sound.name.split(' ') if 
                self.system._feature_values.get(s, '') not in [
                    'laminality', 'ejection', 'tone'
                ]]
            while len(name) >= 4:
                sound = self.system.get(' '.join(name))
                if sound and sound.name in self.data:
                    return self.resolve_sound(sound)
                name.pop(0)
        raise KeyError(":sc:resolve_sound: No sound could be found.")
