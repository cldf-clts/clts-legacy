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

def uname(s):
    "Return unicode name(s) for a character set."
    try:
        return ' / '.join(unicodedata.name(ss) for ss in s)
    except:
        return '-'

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

        self._features = {'consonant': {}, 'vowel': {}, 'diphthong': {}, 
                'cluster': {}, 'click': {}}  # Sounds by name
        # dictionary for feature values, checks when writing elements from
        # write_order to make sure no output is doubled
        self._feature_values = {}

        self.diacritics = dict(consonant={}, vowel={}, click={}, diphthong={},
                tone={}, cluster={})
        for dia in itertable(self.system.tabledict['diacritics.tsv']):
            if not dia['alias']:
                self._features[dia['type']][dia['value']] = dia['grapheme']
            # assign feature values to the dictionary
            self._feature_values[dia['value']] = dia['feature']

            self.diacritics[dia['type']][dia['grapheme']] = {dia['feature']: dia['value']}

        self.sound_classes = {}
        self._columns = {} # the basic column structure, to allow for rendering
        self._sounds = {}  # Sounds by grapheme
        for cls in [Consonant, Vowel, Tone, Marker, Click, Diphthong,
                Cluster]:
            type_ = cls.__name__.lower()
            self.sound_classes[type_] = cls
            # store information on column structure to allow for rendering of a
            # sound in this form, which will make it easier to insert it when
            # finding generated sounds
            self._columns[type_] = [c['name'].lower() for c in \
                    self.system.tabledict['{0}s.tsv'.format(type_)].asdict(
                        )['tableSchema']['columns']]
            for l, item in enumerate(itertable(
                    self.system.tabledict['{0}s.tsv'.format(type_)])):
                if item['grapheme'] in self._sounds:
                    raise ValueError('duplicate grapheme in {0}:{1}: {2}'.format(
                        type_ + 's.tsv', l + 2, item['grapheme']))
                sound = cls(clts=self, **item)
                # make sure this does not take too long
                for key, value in item.items():
                    if value and value not in {'grapheme', 'note', 'alias'}:
                        self._feature_values[value] = key
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
            map(re.escape, sorted(self._sounds, key=lambda x: len(x),
                reverse=True))))

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
    
    def from_name(self, string):
        """Parse a sound from its name"""
        if string in self._features:
            return self._features[string]
        components = string.split(' ')
        rest, sound_class = components[:-1], components[-1]
        if sound_class not in self.sound_classes:
            raise ValueError('no sound class specified')
        
        args = {self._feature_values.get(comp, '?'): comp for comp in rest}
        if '?' in args:
            raise ValueError('string contains unknown features')
        args['grapheme'] = ''
        args['clts'] = self
        sound = self.sound_classes[sound_class](**args)
        glyph = str(sound)
        if not glyph in self._sounds:
            sound.generated = True
            return sound
        return self[glyph]
    
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

        # check whether sound is in self.sounds
        if nstring in self._sounds:
            return self._sounds[nstring]

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
        if nstring == base_sound.grapheme:
            # A known sound, but we check whether we normalized it or not
            if nstring == string:
                return base_sound
            # if the sound was normalized, we assign it a different source, and
            # return the sound for the normalized sound
            else:
                base_sound.source = string
                return base_sound

        # A base sound with diacritics or a custom symbol.
        features = attr.asdict(base_sound)
        features.update(
            source=string,
            grapheme=base_sound.grapheme,
            generated=True,
            alias=base_sound.alias)

        for dia in [p + EMPTY for p in pre] + [EMPTY + p for p in post]:
            feature = self.diacritics[base_sound.type].get(dia, {})
            if not feature:
                return UnknownSound(grapheme=nstring, source=string, clts=self)
            if self.diacritics[base_sound.type][dia] != dia:
                features['alias'] = True
            features.update(feature)

        sound = self.sound_classes[base_sound.type](**features)
        if sound.generated and sound.grapheme not in self._sounds:
            self._add(sound)
        return sound

    def __getitem__(self, string):
        if isinstance(string, Sound):
            return self._features[string.name]
        if [s for s in self.sound_classes if s in string]:
            return self.from_name(string)
        string = _nfd(string)
        try:
            return self._parse(string)
        # here, we should take over to handle also dipthongs
        except ValueError:
            raise KeyError('your string is not attested')

    def __contains__(self, item):
        if isinstance(item, Sound):
            return item.name in self._features
        
        return item in self._sounds

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

    @property
    def uname(self):
        return uname(self.grapheme)


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

    @property
    def uname(self):
        return uname(str(self))

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

        base_vals = [self.clts._feature_values[elm] for elm in elements]
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

    @property
    def table(self):
        """Returns the tabular representation of the sound as given in our data
        """
        tbl = []
        features = [f for f in self._name_order if f not in
                self.clts._columns[self.type]]
        # make sure to mark generated sounds
        if self.generated and str(self) != self.source:
            tbl += [str(self)+' | '+self.source]
        else:
            tbl += [str(self)]
        for name in self.clts._columns[self.type][1:]:
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
        return self.grapheme


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
        'duration', 'release', 'phonation', 'place', 'manner']

@attr.s(cmp=False)
class Cluster(Sound):
    
    # features follow basic information about IPA from various sources, they
    # are potentially not yet exhaustive and should be updated at some point
    from_manner = attr.ib(default=None)
    from_place = attr.ib(default=None)
    to_manner = attr.ib(default=None)
    to_place = attr.ib(default=None)

    aspiration = attr.ib(default=None)
    labialization = attr.ib(default=None)
    palatalization = attr.ib(default=None)
    preceding = attr.ib(default=None)
    velarization = attr.ib(default=None)
    duration = attr.ib(default=None)
    from_phonation = attr.ib(default=None)
    to_phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=[],
        post=[]
        )
    _name_order = [
        'preceding', 'syllabicity', 'nasalization', 'palatalization',
        'labialization', 'glottalization', 'aspiration', 
        'velarization',
        'pharyngealization',
        'duration', 
        'release', 
        'from_phonation', 
        'from_place', 'from_manner',
        'to_phonation', 'to_place', 'to_manner']



@attr.s(cmp=False)
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

    _write_order = dict(
        pre=[],
        post=[
            'phonation',
            'rhotacization',
            'syllabicity',
            'nasalization',
            'pharyngealization',
            'glottalization',
            'velarization',
            'duration',
            'frication'])
    _name_order = [
        'phonation', 'rhotacization', 'pharyngealization', 'glottalization',
        'velarization', 'syllabicity', 'duration', 'nasalization',
        'roundedness', 'height', #'backness', 
        'frication', 'centrality']

@attr.s(cmp=False)
class Diphthong(Sound):
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

@attr.s(cmp=False)
class Tone(Sound):
    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    _name_order = ['contour', 'start', 'middle', 'end']
