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
    'Click',
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
        # search for best base-string
        elements = self._features()
        base_str = self.base or '<?>'
        while elements:
            base = self.ts._features.get(' '.join(elements + [self.type]))
            if base:
                base_str = base.grapheme
                break
            elements.pop(0)

        base_vals = {self.ts._feature_values[elm] for elm in elements}
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

    def get(self, desc):
        return self.ts.features.get(desc, '')

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


@attr.s(cmp=False, repr=False)
class Click(Sound):
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    phonation = attr.ib(default=None)
    secondary = attr.ib(default=None)
    preceding = attr.ib(default=None)
    voicing = attr.ib(default=None)

    _write_order = dict(pre=['preceding'], post=['phonation'])
    _name_order = ['preceding', 'phonation', 'place', 'manner', 'voicing', 'secondary']


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

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=['preceding'],
        post=[
            'phonation',
            'ejection',
            'syllabicity',
            'voicing',
            'nasalization',
            'palatalization',
            'labialization',
            'aspiration',
            'glottalization',
            'velarization',
            'pharyngealization',
            'duration',
            'release'])
    _name_order = [
        'preceding', 'syllabicity', 'nasalization', 'palatalization',
        'labialization', 'glottalization', 'aspiration', 'velarization',
        'pharyngealization',
        'duration', 'release', 'voicing',
        'phonation', 'place', 'ejection', 'manner']


@attr.s(cmp=False, repr=False)
class ComplexSound(Sound):
    from_sound = attr.ib(default=None)
    to_sound = attr.ib(default=None)

    def __unicode__(self):
        return self.from_sound.__unicode__() + self.to_sound.__unicode()

    @classmethod
    def from_sounds(cls, source, sound1, sound2, ts):
        items = {
            'from_'+f: 'from_'+getattr(sound1, f)
            for f in sound1._name_order if getattr(sound1, f)}
        items.update(
            {'to_'+f: 'to_'+getattr(sound2, f)
             for f in sound2._name_order if getattr(sound2, f)})
        return cls(
            ts=ts,
            source=source,
            from_sound=sound1,
            to_sound=sound2,
            grapheme=str(sound1)+str(sound2),
            generated=True,
            base=str(sound1)+str(sound2),
            normalized=sound1.normalized or sound2.normalized,
            **items)


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
    from_manner = attr.ib(default=None)
    from_place = attr.ib(default=None)
    from_aspiration = attr.ib(default=None)
    from_labialization = attr.ib(default=None)
    from_palatalization = attr.ib(default=None)
    from_preceding = attr.ib(default=None)
    from_velarization = attr.ib(default=None)
    from_duration = attr.ib(default=None)
    from_phonation = attr.ib(default=None)
    from_release = attr.ib(default=None)
    from_syllabicity = attr.ib(default=None)
    from_nasalization = attr.ib(default=None)
    from_glottalization = attr.ib(default=None)
    from_pharyngealization = attr.ib(default=None)
    from_ejection = attr.ib(default=None)
    from_voicing = attr.ib(default=None)

    to_manner = attr.ib(default=None)
    to_place = attr.ib(default=None)
    to_aspiration = attr.ib(default=None)
    to_labialization = attr.ib(default=None)
    to_palatalization = attr.ib(default=None)
    to_preceding = attr.ib(default=None)
    to_velarization = attr.ib(default=None)
    to_duration = attr.ib(default=None)
    to_phonation = attr.ib(default=None)
    to_release = attr.ib(default=None)
    to_syllabicity = attr.ib(default=None)
    to_nasalization = attr.ib(default=None)
    to_glottalization = attr.ib(default=None)
    to_pharyngealization = attr.ib(default=None)
    to_ejection = attr.ib(default=None)
    to_voicing = attr.ib(default=None)

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=[],
        post=[]
    )
    _name_order = [
        'from_preceding',
        'from_syllabicity',
        'from_nasalization',
        'from_palatalization',
        'from_labialization',
        'from_glottalization',
        'from_aspiration',
        'from_velarization',
        'from_pharyngealization',
        'from_duration',
        'from_release',
        'from_voicing',
        'from_phonation',
        'from_place',
        'from_ejection',
        'from_manner',
        'to_preceding',
        'to_syllabicity',
        'to_nasalization',
        'to_palatalization',
        'to_labialization',
        'to_glottalization',
        'to_aspiration',
        'to_velarization',
        'to_pharyngealization',
        'to_duration',
        'to_release',
        'to_voicing',
        'to_phonation',
        'to_place',
        'to_ejection',
        'to_manner'
    ]


@attr.s(cmp=False, repr=False)
class Vowel(Sound):
    roundedness = attr.ib(default=None)
    height = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    frication = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    rhotacization = attr.ib(default=None)
    centrality = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    velarization = attr.ib(default=None)
    tone = attr.ib(default=None)
    voicing = attr.ib(default=None)

    _write_order = dict(
        pre=[],
        post=[
            'voicing',
            'phonation',
            'rhotacization',
            'syllabicity',
            'nasalization',
            'tone',
            'pharyngealization',
            'glottalization',
            'velarization',
            'duration',
            'frication'])
    _name_order = [
        'duration', 'rhotacization', 'pharyngealization', 'glottalization',
        'velarization', 'syllabicity', 'nasalization', 'voicing', 'phonation',
        'roundedness', 'height',
        'frication', 'centrality', 'tone']


@attr.s(cmp=False, repr=False)
class Diphthong(ComplexSound):
    from_roundedness = attr.ib(default=None)
    from_height = attr.ib(default=None)
    from_centrality = attr.ib(default=None)
    to_roundedness = attr.ib(default=None)
    to_height = attr.ib(default=None)
    to_centrality = attr.ib(default=None)
    from_nasalization = attr.ib(default=None)
    from_frication = attr.ib(default=None)
    from_duration = attr.ib(default=None)
    from_phonation = attr.ib(default=None)
    from_release = attr.ib(default=None)
    from_syllabicity = attr.ib(default=None)
    from_pharyngealization = attr.ib(default=None)
    from_glottalization = attr.ib(default=None)
    from_rhotacization = attr.ib(default=None)
    from_velarization = attr.ib(default=None)

    to_nasalization = attr.ib(default=None)
    to_frication = attr.ib(default=None)
    to_duration = attr.ib(default=None)
    to_phonation = attr.ib(default=None)
    to_release = attr.ib(default=None)
    to_syllabicity = attr.ib(default=None)
    to_pharyngealization = attr.ib(default=None)
    to_glottalization = attr.ib(default=None)
    to_rhotacization = attr.ib(default=None)
    to_velarization = attr.ib(default=None)

    # dipthongs are simply handled by adding the three base types for vowel and
    # consonant, plus the additional features, which are, however, only
    # supposed to occur on the first vowel

    _write_order = dict(
        pre=[],
        post=['to_syllabicity', 'to_nasalization', 'to_duration'])

    _name_order = [
        'from_phonation',
        'from_rhotacization',
        'from_pharyngealization',
        'from_glottalization',
        'from_velarization',
        'from_syllabicity',
        'from_duration',
        'from_nasalization',
        'from_roundedness',
        'from_height',
        'from_centrality',
        'from_frication',
        'to_phonation',
        'to_rhotacization',
        'to_pharyngealization',
        'to_glottalization',
        'to_velarization',
        'to_syllabicity',
        'to_duration',
        'to_nasalization',
        'to_roundedness',
        'to_height',
        'to_centrality',
        'to_frication'
    ]


@attr.s(cmp=False, repr=False)
class Tone(Sound):
    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    _name_order = ['contour', 'start', 'middle', 'end']
