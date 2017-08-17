# coding: utf-8
"""
CLTS module for consistent IPA handling.
========================================

"""
from __future__ import unicode_literals
import re
import unicodedata

from clldutils.path import Path
from clldutils.csvw.metadata import TableGroup
from clldutils.misc import UnicodeMixin, nfilter
import attr
from six import string_types, text_type

EMPTY = "◌"
UNKNOWN = "�"


def data_path(*comps):
    """Function creates local path to data."""
    return Path(__file__).parent.parent.joinpath('data', *comps)


def _norm(string):
    return string.replace(EMPTY, "")


def _nfd(string):
    return unicodedata.normalize("NFD", string)


def codepoint(s):
    "Return unicode codepoint(s) for a character set."
    return ' '.join(['U+'+('000'+hex(ord(x))[2:])[-4:] for x in s])


def itertable(table):
    for item in table:
        res = {
            k.lower(): _nfd(v) if isinstance(v, text_type) else v
            for k, v in item.items()}
        for extra in res.pop('extra', []):
            k, _, v = extra.strip().partition(':')
            res[k] = v
        yield res


def translate(s, source_system, target_system):
    res = []
    for snd in source_system(s):
        res.append(target_system.get(snd))
    return ' '.join(['{0}'.format(target_system.get(snd)) for snd in source_system(s)])


class CLTS(object):
    """
    A transcription system
    """
    def __init__(self, system='bipa'):
        """
        :param system: The name of a transcription system or a directory containing one.
        """
        if isinstance(system, string_types):
            for d in data_path().iterdir():
                if d.is_dir() and d.name == system:
                    system = d
                    break
            else:
                raise ValueError('unknown system: {0}'.format(system))

        if system.joinpath('metadata.json').exists():
            self.system = TableGroup.from_file(system.joinpath('metadata.json'))
        else:
            self.system = TableGroup.from_file(
                data_path('transcription-system-metadata.json'))
            self.system._fname = system.joinpath('metadata.json')

        self._features = {'consonant': {}, 'vowel': {}}  # Sounds by name
        self.diacritics = dict(consonant={}, vowel={}, click={}, dipthong={})
        for dia in itertable(self.system.tabledict['diacritics.tsv']):
            if not dia['alias']:
                self._features[dia['type']][dia['value']] = dia['grapheme']

            self.diacritics[dia['type']][dia['grapheme']] = {dia['feature']: dia['value']}

        self.sound_classes = {}
        self._sounds = {}  # Sounds by grapheme
        for cls in [Consonant, Vowel, Tone, Marker, Click]:
            type_ = cls.__name__.lower()
            self.sound_classes[type_] = cls
            for l, item in enumerate(itertable(
                    self.system.tabledict['{0}s.tsv'.format(type_)])):
                if item['grapheme'] in self._sounds:
                    raise ValueError('duplicate grapheme in {0}:{1}: {2}'.format(
                        type_ + 's.tsv', l + 2, item['grapheme']))
                sound = cls(clts=self, **item)
                self._sounds[item['grapheme']] = sound
                if not sound.alias:
                    if sound.name in self._features:
                        raise ValueError('duplicate features in {0}:{1}: {2}'.format(
                            type_ + 's.tsv', l + 2, sound.name))
                    self._features[sound.name] = sound

        # basic regular expression, used to match the basic sounds in the system.
        self._regex = None
        self._update_regex()

        # normalization data
        self._normalize = {
            _norm(r['source']): _norm(r['target'])
            for r in itertable(self.system.tabledict['normalize.tsv'])}

    def _update_regex(self):
        self._regex = re.compile('|'.join(
            sorted(map(re.escape, self._sounds), key=lambda x: len(x), reverse=True)))

    def _add(self, sound):
        assert sound.generated
        self._sounds[sound.grapheme] = sound
        if not sound.alias:
            self._features[sound.name] = sound
        self._update_regex()

    @property
    def id(self):
        return self.system._fname.parent.name

    def _norm(self, string):
        """Extended normalization: normalize by list of norm-characers, split
        by character "/"."""
        nstring = _norm(string)
        if "/" in string:
            s, t = string.split('/')
            if t:
                nstring = t
            else:
                nstring = s
        return self.normalize(nstring)

    def normalize(self, string):
        """Normalize the string according to normalization list"""
        return ''.join([self._normalize.get(x, x) for x in _nfd(string)])

    def _parse(self, string):
        """Parse a string and return its features.

        :param string: A one-symbol string in NFD

        Note
        ----
        Strategy is rather simple: we determine the base part of a string and
        then search left and right of this part for the additional features as
        expressed by the diacritics. Fails if a segment has more than one basic
        part.
        """
        nstring = self._norm(string)

        m = list(self._regex.finditer(nstring))
        if len(m) != 1:
            # Either no match or more than one; both is considered an error.
            return UnknownSound(grapheme=nstring, source=string, clts=self)

        pre, mid, post = nstring.partition(nstring[m[0].start():m[0].end()])

        #
        # FIXME: Shouldn't we re-order the diacritics here, and then lookup the
        # re-assembled symbol?
        #

        base_sound = self._sounds[mid]

        if string == base_sound.grapheme:
            # A known sound
            return base_sound

        # A base sound with diacritics or a custom symbol.
        features = attr.asdict(base_sound)
        features.update(
            source=string,
            grapheme=base_sound.grapheme,
            generated=True,
            alias=not bool(pre or post))

        for dia in [p + EMPTY for p in pre] + [EMPTY + p for p in post]:
            feature = self.diacritics[base_sound.type].get(dia, {})
            if not feature:
                return UnknownSound(grapheme=nstring, source=string, clts=self)
            features.update(feature)

        sound = self.sound_classes[base_sound.type](**features)
        if sound.generated and sound.grapheme not in self._sounds:
            self._add(sound)
        return sound

    def __getitem__(self, string):
        if isinstance(string, Sound):
            return self._features[string.name]

        string = _nfd(string)
        try:
            return self._parse(string)
        # here, we should take over to handle also dipthongs
        except ValueError:
            raise KeyError()

    def __contains__(self, item):
        if isinstance(item, Sound):
            return item.name in self._features

        try:
            _ = self[item]
            return True
        except KeyError:
            return False

    def get(self, string):
        try:
            return self[string]
        except KeyError:
            return UnknownSound(grapheme=string, clts=self)

    def __call__(self, string, text=False):
        res = [
            self.get(s)
            for s in (string.split(' ') if isinstance(string, text_type) else string)]
        if not text:
            return res
        return ' '.join('{0}'.format(s) for s in res)


@attr.s(cmp=False)
class Symbol(UnicodeMixin):
    clts = attr.ib(validator=attr.validators.instance_of(CLTS))
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
        return self.clts.id == other.clts.id and self.grapheme == other.grapheme

    @property
    def name(self):
        return None


@attr.s(cmp=False)
class UnknownSound(Symbol):
    pass


@attr.s(cmp=False)
class Sound(Symbol):
    """
    Sound object stores basic features of the individual sound objects.
    """
    base = attr.ib(default=None)
    alias = attr.ib(default=None)
    unknown = attr.ib(default=None)

    _name_order = []
    _write_order = dict(pre=[], post=[])

    def __eq__(self, other):
        return self.name == other.name

    @property
    def codepoints(self):
        return codepoint(str(self))

    def __unicode__(self):
        # search for best base-string
        elements = nfilter([getattr(self, p, None) for p in self._name_order])
        base_str = '<?>'
        while elements:
            name = ' '.join(elements + [self.type])
            base = self.clts._features.get(name)
            if base:
                base_str = base.grapheme
                break
            elements.pop(0)

        #base =

        base_vals = elements[:-1]
        out = ''
        for p in [x for x in self._write_order['pre'] if x not in base_vals]:
            out += _norm(self.clts._features[self.type].get(
                getattr(self, p, ''), ''))
        out += base_str
        for p in [x for x in self._write_order['post'] if x not in base_vals]:
            out += _norm(self.clts._features[self.type].get(
                getattr(self, p, ''), ''))
        return out

    @property
    def name(self):
        return ' '.join(
            nfilter([getattr(self, p, '') for p in self._name_order] + [self.type]))

    def get(self, desc):
        return self.clts.features.get(desc, '')


@attr.s(cmp=False)
class Click(Sound):
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    phonation = attr.ib(default=None)
    secondary = attr.ib(default=None)
    preceding = attr.ib(default=None)

    _write_order = dict(pre=['preceding'], post=['phonation'])
    _name_order = ['preceding', 'phonation', 'place', 'manner', 'secondary']


@attr.s(cmp=False)
class Marker(Symbol):
    alias = attr.ib(default=None)
    feature = attr.ib(default=None)
    value = attr.ib(default=None)
    unknown = attr.ib(default=None)

    @property
    def name(self):
        return self.grapheme

    def __unicode__(self):
        return self.base


@attr.s(cmp=False)
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

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=['preceding'],
        post=[
            'phonation',
            'syllabicity',
            'nasalization',
            'palatalization',
            'aspiration',
            'labialization',
            'glottalization',
            'velarization',
            'pharyngealization',
            'duration',
            'release'])
    _name_order = [
        'preceding', 'syllabicity', 'nasalization', 'palatalization',
        'labialization', 'glottalization', 'aspiration', 'velarization',
        'pharyngealization',
        'duration', 'release', 'phonation', 'place', 'manner']


@attr.s(cmp=False)
class Vowel(Sound):
    roundedness = attr.ib(default=None)
    height = attr.ib(default=None)
    backness = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    frication = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    rhotacization = attr.ib(default=None)
    centrality = attr.ib(default=None)

    _write_order = dict(
        pre=[],
        post=[
            'phonation',
            'rhotacization',
            'syllabicity',
            'nasalization',
            'duration',
            'frication'])
    _name_order = [
        'phonation', 'rhotacization', 'syllabicity', 'duration', 'nasalization',
        'roundedness', 'height', 'backness', 'frication', 'centrality']


@attr.s(cmp=False)
class Tone(Sound):
    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    _name_order = ['contour', 'start', 'middle', 'end']


if __name__ == "__main__":
    from lingpy import *
    from pyclpa import base
    from pylexibank.util import data_path as dpath
    clpa = base.get_clpa()
    clts = CLTS()
    wl = Wordlist(dpath('baidial', 'raw', 'Bai-Dialect-Survey.tsv').as_posix())
    wl = get_wordlist(
            dpath('galuciotupi', 'cldf', 'galuciotupi.csv'),
            col="Language_name", row="Parameter_name")
    sounds = []
    for k, ipa in iter_rows(wl, 'segments'):
        sounds += ipa.split()
    sounds = sorted(set(sounds))
    errors = []
    errors2 = []
    modified = []
    generated = []
    for sound in sounds:
        testx = clts.get_sound(sound)
        test2 = clpa(sound)[0]
        if testx.generated:
            generated += [sound]
        if not hasattr(test2, 'clpa'):
            errors2 += [sound]
        if testx.type == 'unknown':
            errors += [sound]
        elif testx.unknown:
            errors += [sound]
        else:
            if testx.source != str(testx):
                modified += [[sound, str(testx)]]
            print(str(testx), testx.name, '◌'.join(testx.source),
                    len(testx.source))
