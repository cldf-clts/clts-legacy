# coding: utf8
from __future__ import unicode_literals, print_function, division

import unicodedata

import attr
from clldutils.misc import UnicodeMixin, nfilter

from pyclts.util import norm

__all__ = [
    'Sound',
    'Consonant',
    'Vowel',
    'Tone',
    'Marker',
    'Diphthong',
    'Cluster',
    'UnknownSound']


@attr.s(cmp=False)
class Symbol(UnicodeMixin):
    ts = attr.ib()
    grapheme = attr.ib()
    source = attr.ib(default=None)
    generated = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    note = attr.ib(default=None)

    @property
    def type(self):
        return self.__class__.__name__.lower()

    def __unicode__(self):
        return self.grapheme

    def __eq__(self, other):
        """
        In the absence of features, we consider symbols equal, if they belong to the same
        system and are represented by the same grapheme.
        """
        return self.ts.id == other.ts.id and self.grapheme == other.grapheme

    @property
    def name(self):
        return None

    @property
    def uname(self):
        "Return unicode name(s) for a character set."
        try:
            return ' / '.join(unicodedata.name(ss) for ss in self.__unicode__())
        except TypeError:
            return '-'

    @property
    def codepoints(self):
        "Return unicode codepoint(s) for a grapheme."
        return ' '.join('U+' + ('000' + hex(ord(x))[2:])[-4:] for x in self.__unicode__())


@attr.s(cmp=False)
class UnknownSound(Symbol):
    pass


@attr.s(cmp=False, repr=False)
class Sound(Symbol):
    """
    Sound object stores basic features of the individual sound objects.
    """
    base = attr.ib(default=None)
    alias = attr.ib(default=None)
    normalized = attr.ib(default=None)
    unknown = attr.ib(default=None)
    stress = attr.ib(default=None)

    _name_order = []
    _write_order = dict(pre=[], post=[])

    def __eq__(self, other):
        if isinstance(other, Sound):
            return self.name == other.name
        return False

    def __repr__(self):
        return '<{0}.{1}: {2}>'.format(
            self.__module__, self.__class__.__name__, self.name)

    def _features(self):
        return nfilter(getattr(self, p, None) for p in self._name_order)

    def __unicode__(self):
        """
        Return the reference representation of the sound.

        Note
        ----
        We first try to return the non-alias value in our data. If this fails,
        we create the sound based on it's feature representation.
        """
        # generated sounds need to be re-produced for double-checking
        if not self.generated:
            if not self.alias and self.grapheme in self.ts._sounds:
                return self.grapheme
            elif self.alias and self.name in self.ts._features:
                return str(self.ts[self.name])
        
        # search for best base-string
        elements = self._features()
        base_str = self.base or '<?>'
        base_graphemes = []
        while elements:
            base = self.ts._features.get(' '.join(elements + [self.type]))
            if base:
                base_str = base.grapheme
                base_graphemes += [base_str]
            elements.pop(0)
        base_str = base_graphemes[-1] if base_graphemes else base_str or '<?>'
        base_vals = {self.ts._feature_values[elm] for elm in 
                self.ts._sounds[base_str].name.split(' ')[:-1]} if \
                        base_str != '<?>' else {}
        out = []
        for p in self._write_order['pre']:
            if p not in base_vals:
                out.append(
                    norm(self.ts._features[self.type].get(getattr(self, p, ''), '')))
        out.append(base_str)
        for p in self._write_order['post']:
            if p not in base_vals:
                out.append(
                    norm(self.ts._features[self.type].get(getattr(self, p, ''), '')))
        return ''.join(out)

    @property
    def name(self):
        return ' '.join([f or '' for f in self._features()] + [self.type])

    @property
    def table(self):
        """Returns the tabular representation of the sound as given in our data
        """
        tbl = []
        features = [
            f for f in self._name_order if f not in self.ts._columns[self.type]]
        # make sure to mark generated sounds
        if self.generated and self.__unicode__() != self.source:
            tbl += [self.__unicode__() + ' | ' + self.source]
        else:
            tbl += [self.__unicode__()]
        for name in self.ts._columns[self.type][1:]:
            if name != 'extra' and name != 'alias':
                tbl += [getattr(self, name) or '']
            elif name == 'alias':
                tbl += ['+' if getattr(self, name) else '']
            else:
                bundle = []
                for f in features:
                    val = getattr(self, f)
                    if val:
                        bundle += ['{0}:{1}'.format(f, val)]
                tbl += [','.join(bundle)]
        return tbl


@attr.s(cmp=False)
class Marker(Symbol):
    alias = attr.ib(default=None)
    feature = attr.ib(default=None)
    value = attr.ib(default=None)
    unknown = attr.ib(default=None)

    @property
    def name(self):
        return self.grapheme


@attr.s(cmp=False, repr=False)
class Consonant(Sound):

    # features follow basic information about IPA from various sources, they
    # are potentially not yet exhaustive and should be updated at some point
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    aspiration = attr.ib(default=None)
    labialization = attr.ib(default=None)
    palatalization = attr.ib(default=None)
    preceding = attr.ib(default=None)
    velarization = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    ejection = attr.ib(default=None)
    voicing = attr.ib(default=None)
    breathiness = attr.ib(default=None)
    creakiness = attr.ib(default=None)

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=['preceding'],
        post=['creakiness', 'phonation', 'ejection', 'syllabicity', 'voicing',
            'nasalization', 'duration', 'palatalization', 'labialization',
            'breathiness', 'aspiration', 'glottalization', 'velarization',
            'pharyngealization', 'release'])
    _name_order = ['preceding', 'syllabicity', 'nasalization', 'palatalization',
        'labialization', 'glottalization', 'aspiration', 'velarization',
        'pharyngealization', 'duration', 'release', 'voicing', 'creakiness',
        'breathiness', 'phonation', 'place', 'ejection', 'manner']


@attr.s(cmp=False, repr=False)
class ComplexSound(Sound):
    from_sound = attr.ib(default=None)
    to_sound = attr.ib(default=None)

    def __unicode__(self):
        return self.from_sound.__unicode__() + self.to_sound.__unicode__()

    @property
    def name(self):
        n1 = ' '.join(self.from_sound.name.split(' ')[:-1])
        n2 = ' '.join(self.to_sound.name.split(' ')[:-1])
        return 'from '+n1+' to '+n2+' '+self.type

    @classmethod
    def from_sounds(cls, source, sound1, sound2, ts):
        return cls(
                source=source, 
                grapheme=sound1.grapheme+sound2.grapheme, 
                from_sound=sound1, 
                to_sound=sound2, 
                ts=ts,
                generated=True,
                stress = sound1.stress or sound2.stress
                )

    @property
    def table(self):
        """Overwrite the table attribute for complex sounds"""
        return [self.grapheme, self.from_sound.name, self.to_sound.name]
        

@attr.s(cmp=False, repr=False)
class Cluster(ComplexSound):
    """
    A cluster of two consonants whose manner is either plosive or implosive.

    Notes
    -----
    To keep the search space low and to avoid that users start defining too
    invalid sound clusters, we restrict the ```manner``` attribute of the two
    sounds to ```plosive``` and ```implosive```.
    """


@attr.s(cmp=False, repr=False)
class Vowel(Sound):
    roundedness = attr.ib(default=None)
    height = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    frication = attr.ib(default=None)
    duration = attr.ib(default=None)
    voicing = attr.ib(default=None)
    breathiness = attr.ib(default=None)
    creakiness = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    rhotacization = attr.ib(default=None)
    centrality = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    velarization = attr.ib(default=None)
    tone = attr.ib(default=None)
    retraction = attr.ib(default=None)

    _write_order = dict(
        pre=[],
        post=['voicing', 'breathiness', 'creakiness', 'retraction',
            'rhotacization', 'syllabicity', 'nasalization', 'tone',
            'pharyngealization', 'glottalization', 'velarization', 'duration',
            'frication'])
    _name_order = ['duration', 'rhotacization', 'pharyngealization',
            'glottalization', 'velarization', 'syllabicity', 'retraction',
            'nasalization', 'voicing', 'creakiness', 'breathiness',
            'roundedness', 'height', 'frication', 'centrality', 'tone']


@attr.s(cmp=False, repr=False)
class Diphthong(ComplexSound):
    """
    A dipthong consists of two vowels.
    """


@attr.s(cmp=False, repr=False)
class Tone(Sound):
    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    _name_order = ['contour', 'start', 'middle', 'end']
