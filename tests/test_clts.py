# coding: utf-8
from __future__ import unicode_literals, print_function, division
from util import test_data
import pytest
from clldutils.dsv import UnicodeReader


def test_translate(bipa, asjp):
    from pyclts import translate

    assert translate('ts a', bipa, asjp) == 'c E'
    assert translate('c a', asjp, bipa) == 'ts ɐ'


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
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'
    assert sound.uname == 'LATIN SMALL LETTER D / MODIFIER LETTER SMALL W / MODIFIER LETTER SMALL H WITH HOOK'


def test_parse(bipa):
    sounds = ['ʰdʱ', "ˈa", 'á']
    for s in sounds:
        res = bipa[s]
        assert res.generated
    for s in ['a', 't']:
        assert str(bipa[s]) == s
    
    # diphthongs
    dips = ['ao', 'ea', 'ai', 'ua']
    for s in dips:
        res = bipa[s]
        assert res.type == 'diphthong'
        assert res.name.endswith('diphthong')
        assert s == str(s)

    # clusters
    clus = ['tk', 'pk', 'dg', 'bdʰ']
    for s in clus:
        res = bipa[s]
        assert res.type == 'cluster'
        assert 'cluster' in res.name
        assert s == str(s)
        bipa._add(res)
        assert res in bipa


def test_sound_from_name(bipa):
    from pyclts.models import UnknownSound

    assert bipa['from unrounded open front to unrounded close-mid front diphthong'].grapheme == 'ae'
    assert isinstance(bipa['a bad diphthong'], UnknownSound)
    assert bipa['from voiceless alveolar stop to voiceless velar stop cluster'].grapheme == 'tk'
    with pytest.raises(ValueError):
        bipa['very bad feature voiced labial stop consonant']
        


def test_ts(bipa):
    from pyclts.transcriptionsystem import TranscriptionSystem
    from pyclts.models import Cluster,Diphthong
    with pytest.raises(ValueError):
        TranscriptionSystem('')
        TranscriptionSystem('_f1')
        TranscriptionSystem('_f2')
        bads = TranscriptionSystem('what')

    # test clicks data
    with UnicodeReader(test_data('clicks.tsv'), delimiter='\t') as f:
        for row in [r for r in f][1:]:
            grapheme = row[0]
            gtype = row[4]
            if gtype == 'stop-cluster':
                assert isinstance(bipa[grapheme], Cluster)


def test_models(bipa, asjp):
    from pyclts.models import Symbol
    sym = Symbol(ts=bipa, grapheme='s', source='s', generated=False, note='')
    assert str(sym) == sym.source == sym.grapheme
    assert sym == sym
    assert not sym.name
    assert sym.uname == "LATIN SMALL LETTER S"
    # complex sounds are always generated
    assert bipa['ae'].generated
    assert bipa['tk'].generated

    # equality tests in model for sound
    s1 = bipa['t']
    s2 = 't'
    assert s1 != s2

    # repr test for sound
    assert s1.name in repr(s1)

    # test the table function
    assert s1.table[1] == 'voiceless'
    assert '|' in bipa["ts'"].table[0]

    # test table for generated entities
    assert bipa['tk'].table[1] == bipa['t'].name

    # test the unicode name
    assert Symbol(ts='', grapheme=[['1', '2'], '2'], source='').uname == '-'

    # test complex sound
    assert str(bipa['ae']) == 'ae'

    # test equality of symbols
    assert Symbol(ts=bipa, grapheme='1', source='1') != Symbol(
            ts=asjp, grapheme='1', source='1')


def test_transcriptiondata(sca, dolgo, asjpd, phoible, pbase, bipa):

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
        dolgo['A']
        sca['B']

    # test data from sound name
    assert sca.resolve_sound(bipa['ʰb']) == 'P'
    assert sca.resolve_sound(bipa['ae']) == 'A'
    assert sca.resolve_sound(bipa['tk']) == 'T'


def test_transcription_system_consistency(bipa, asjp, gld):

    # bipa should always be able to be translated to
    for sound in asjp:
        print(sound, asjp[sound].name)
        if sound not in bipa:
            assert '<?>' not in str(bipa[asjp[sound].name])
    for sound in gld:
        print(sound, gld[sound].name)
        if sound not in bipa:
            assert '<?>' not in str(bipa[gld[sound].name])

