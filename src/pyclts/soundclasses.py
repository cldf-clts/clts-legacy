from pyclts.transcriptionsystem import Symbol, TranscriptionSystem
from pyclts.util import read_data, TranscriptionBase

SOUNDCLASS_SYSTEMS = ['sca', 'cv', 'art', 'dolgo', 'asjp', 'color']


class SoundClasses(TranscriptionBase):
    """
    Class for handling sound class models.
    """
    def __init__(self, id_):
        if not hasattr(self, 'data'):
            # Only initialize, if this is really a new instance!
            assert id_ in SOUNDCLASS_SYSTEMS
            data, self.sounds, self.names = read_data(
                'soundclasses', 'lingpy.tsv', id_)
            self.data = {}
            self.classes = set()
            for k, v in data.items():
                self.data[k] = v[0]
                self.classes.add(v[0]['grapheme'])
            self.system = TranscriptionSystem('bipa')

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        sound = sound if isinstance(sound, Symbol) else self.system[sound]
        if sound.name in self.data:
            return self.data[sound.name]['grapheme']
        if not sound.type == 'unknownsound':
            if sound.type in ['diphthong', 'cluster']:
                return self.resolve_sound(sound.from_sound)
            name = [
                s for s in sound.name.split(' ') if
                self.system._feature_values.get(s, '') not in
                ['laminality', 'ejection', 'tone']]
            while len(name) >= 4:
                sound = self.system.get(' '.join(name))
                if sound and sound.name in self.data:
                    return self.resolve_sound(sound)
                name.pop(0)
        raise KeyError(":sc:resolve_sound: No sound could be found.")
