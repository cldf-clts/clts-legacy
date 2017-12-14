# coding: utf-8
from __future__ import unicode_literals, print_function, division
from util import test_data
import pytest


def test_translate(bipa, asjp):
    from pyclts import translate

    translate('ts a', bipa, asjp)


def test_getitem(bipa):
    s = bipa['a']
    assert bipa[s] == s
    assert bipa[s.name] == s
    #bipa["'#"]  # raises KeyError but at the wrong place


def test_ts_contains(bipa, asjp):
    assert bipa['ts'] in asjp


def test_ts_equality(bipa, asjp):
    asjp_ts = asjp[bipa['ts']]
    assert bipa['ts'] == asjp_ts


def test_examples(bipa):
    sound = bipa['dʷʱ']
    assert sound.name == 'labialized breathy-voiced alveolar stop consonant'
    assert sound.generated
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+0324 U+02b7'
    assert sound.uname == 'LATIN SMALL LETTER D / COMBINING DIAERESIS BELOW ' \
                          '/ MODIFIER LETTER SMALL W'


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



def test_models(bipa):
    from pyclts.models import Symbol
    sym = Symbol(ts=bipa, grapheme='s', source='s', generated=False, note='')
    assert str(sym) == sym.source == sym.grapheme
    assert sym == sym
    assert not sym.name
    assert sym.uname == "LATIN SMALL LETTER S"
    # complex sounds are always generated
    assert bipa['ae'].generated
    assert bipa['tk'].generated


def test_sound_from_name(bipa):
    from pyclts.models import UnknownSound

    assert bipa['from unrounded open front to unrounded close-mid front diphthong'].grapheme == 'ae'
    assert isinstance(bipa['a bad diphthong'], UnknownSound)
    assert bipa['from voiceless alveolar stop to voiceless velar stop cluster'].grapheme == 'tk'

def test_ts():
    from pyclts.transcriptionsystem import TranscriptionSystem
    with pytest.raises(ValueError):
        TranscriptionSystem('')
        asjp = TranscriptionSystem(test_data('asjp'))
        bads = TranscriptionSystem('what')

def test_transcriptiondata(sca, dolgo, asjpd, phoible, pbase):

    seq = 'tʰ ɔ x ˈth ə r A ˈI ʲ'
    seq2 = 'th o ?/x a'
    seq3 = 'th o ?/ a'

    assert dolgo(seq) == list('TVKTVR000')
    assert sca(seq2)[2] == 'G'
    assert asjpd(seq2)[2] == 'x'
    assert sca(seq3)[2] == '0'
    
    with pytest.raises(KeyError):
        dolgo['A']
        sca['B']

