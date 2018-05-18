# coding: utf-8
from __future__ import unicode_literals, print_function, division
from six import text_type

import pytest

from pyclts.models import Marker, UnknownSound, is_valid_sound, Symbol, Sound


def test_is_valid_sound(bipa):
    assert not is_valid_sound(bipa['_'], bipa)
    assert not is_valid_sound(bipa['ä'], bipa)


def test_getitem(bipa):
    s = bipa['a']
    assert bipa[s] == s
    assert bipa[s.name] == s


def test_ts_contains(bipa, asjp):
    assert bipa['ts'] in asjp


def test_ts_equality(bipa, asjp):
    asjp_ts = asjp[bipa['ts']]
    assert bipa['ts'] == asjp_ts


def test_examples(bipa):
    sound = bipa['dʷʱ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert not sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'
    assert sound.uname == 'LATIN SMALL LETTER D / MODIFIER LETTER SMALL W / MODIFIER LETTER SMALL H WITH HOOK'
    sound = bipa['dʱʷ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'


def test_parse(bipa):
    assert all(bipa[s].generated for s in ['ʰdʱ', "ˈa", 'á'])
    assert all(text_type(bipa[s]) == s for s in ['a', 't'])

    a = bipa['a']
    comps = a.name.split()
    assert bipa[' '.join(list(reversed(comps[:-2])) + [comps[-1]])]

    # diphthongs
    for s in ['ao', 'ea', 'ai', 'ua']:
        res = bipa[s]
        assert res.type == 'diphthong'
        assert res.name.endswith('diphthong')
        assert s == text_type(s)

    # clusters
    for s in ['tk', 'pk', 'dg', 'bdʰ']:
        res = bipa[s]
        assert res.type == 'cluster'
        assert 'cluster' in res.name
        assert s == text_type(s)

    # go for bad diacritics in front and end of a string
    assert bipa['*a'].type == 'unknownsound'
    assert bipa['a*'].type == 'unknownsound'

    # marker
    assert isinstance(bipa['_'], Marker)

    # decorated marker
    assert isinstance(bipa['_\u0329'], UnknownSound)


def test_call(bipa):
    assert bipa('th o x t a')[0].alias


def test_get(bipa):
    "test for the case that we have a new default"
    assert bipa.get('A', '?') == '?'


@pytest.mark.parametrize(
    "name,check",
    [
        (
            'from unrounded open front to unrounded close-mid front diphthong',
            lambda s: s.grapheme == 'ae'),
        (
            'from voiceless alveolar stop to voiceless velar stop cluster',
            lambda s: s.grapheme == 'tk'),
        ('pre-aspirated voiced bilabial nasal consonant', lambda s: s.generated),
        ('voiced nasal bilabial consonant', lambda s: not s.generated),
        # complex sounds are always generated
        ('ae', lambda s: s.generated),
        ('tk', lambda s: s.generated),
    ]
)
def test_sound_from_name(name, check, bipa):
    assert check(bipa[name])


def test_sound_from_name_error(bipa):
    with pytest.raises(ValueError):
        _ = bipa['very bad feature voiced labial stop consonant']

    with pytest.raises(ValueError):
        _ = bipa._from_name('very bad feature with bad consonantixs')

    with pytest.raises(ValueError):
        _ = bipa._from_name('from something to something diphthong')

    with pytest.raises(ValueError):
        _ = bipa._from_name('something diphthong')


def test_models(bipa, asjp):
    sym = Symbol(ts=bipa, grapheme='s', source='s', generated=False, note='')
    assert text_type(sym) == sym.source == sym.grapheme
    assert sym == sym
    assert not sym.name
    assert sym.uname == "LATIN SMALL LETTER S"

    # equality tests in model for sound
    s1 = bipa['t']
    s2 = 't'
    assert s1 != s2
    assert not Sound(ts=None, grapheme='a') == 5

    # repr test for sound
    assert s1.name in repr(s1)

    # test the table function
    assert s1.table[1] == 'voiceless'
    assert '|' in bipa["ts'"].table[0]

    # test table for generated entities
    assert bipa['tk'].table[1] == bipa['t'].name

    # test the unicode name
    assert Symbol(ts='', grapheme=[['1', '2'], '2'], source='').uname == '-'
    s = Symbol(ts=None, grapheme='\x84')  # U+0084 <control>
    assert s.uname == '?'

    # test complex sound
    assert text_type(bipa['ae']) == 'ae'

    # test equality of symbols
    assert Symbol(ts=bipa, grapheme='1', source='1') != Symbol(
        ts=asjp, grapheme='1', source='1')

    assert pytest.approx(1.0) == bipa['t'].similarity(asjp['t'])


def test_transcriptiondata(sca, dolgo, asjpd, phoible, bipa):
    seq = 'tʰ ɔ x ˈth ə r A ˈI ʲ'
    seq2 = 'th o ?/x a'
    seq3 = 'th o ?/ a'
    seq4 = 'ǃŋ i b ǃ'

    assert dolgo(seq) == list('TVKTVR000')
    assert sca(seq2)[2] == 'G'
    assert asjpd(seq2)[2] == 'x'
    assert sca(seq3)[2] == '0'

    # these tests need to be adjusted once lingpy accepts click sounds
    assert sca(seq4)[0] == '0'
    assert asjpd(seq4)[0] == '0'
    assert sca(seq4)[3] == '!'
    assert asjpd(seq4)[3] == '!'

    with pytest.raises(KeyError):
        _ = dolgo['A']

    with pytest.raises(KeyError):
        _ = sca['B']

    # test data from sound name
    assert sca.resolve_sound(bipa['ʰb']) == 'P'
    assert sca.resolve_sound(bipa['ae']) == 'A'
    assert sca.resolve_sound(bipa['tk']) == 'T'

    assert phoible.resolve_sound('m') == 'm'
    with pytest.raises(KeyError):
        phoible.resolve_sound(bipa['tk'])


def test_transcription_system_consistency(bipa, asjp, gld):
    # bipa should always be able to be translated to
    for sound in asjp:
        if sound not in bipa:
            assert '<?>' not in text_type(bipa[asjp[sound].name])
    for sound in gld:
        if sound not in bipa:
            assert '<?>' not in text_type(bipa[gld[sound].name])
    for sound in bipa:
        if bipa[sound].type != 'unknownsound' and not bipa[sound].alias:
            if sound != text_type(bipa[sound]):
                raise ValueError
        elif bipa[sound].type == 'unknownsound':
            raise ValueError
    for sound in gld:
        if gld[sound].type != 'unknownsound' and not gld[sound].alias:
            if sound != text_type(gld[sound]):
                raise ValueError
        elif gld[sound].type == 'unknownsound':
            raise ValueError
    for sound in asjp:
        if asjp[sound].type != 'unknownsound' and not asjp[sound].alias:
            if sound != text_type(asjp[sound]):
                raise ValueError
        elif asjp[sound].type == 'unknownsound':
            raise ValueError

    # important test for alias
    assert text_type(bipa['d̤ʷ']) == text_type(bipa['dʷʱ']) == text_type(bipa['dʱʷ'])


def test_clicks(bipa, grapheme, gtype):
    if gtype == 'stop-cluster':
        assert bipa[grapheme].type == 'cluster'


def test_sounds(
        bipa,
        source,
        type,
        grapheme,
        nfd_normalized,
        clts_normalized,
        aliased,
        generated,
        stressed,
        name,
        codepoints
        ):
    """Test on a large pre-assembled dataset whether everything is consistent"""

    sound = bipa[source]
    if sound.type not in ['unknownsound', 'marker']:
        if nfd_normalized == '+':
            assert bipa[source] != sound.source
        if clts_normalized == "+":
            assert sound.normalized
        if aliased == '+':
            assert sound.alias
        if generated:
            assert sound.generated
        if stressed:
            assert sound.stress
        assert sound.name == name
        assert sound.codepoints == codepoints
