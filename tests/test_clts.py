# coding: utf-8
from __future__ import unicode_literals, print_function, division


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
    assert sound.name == 'labialized breathy-voiced alveolar plosive consonant'
    assert sound.generated
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+0324 U+02b7'
    assert sound.uname == 'LATIN SMALL LETTER D / COMBINING DIAERESIS BELOW ' \
                          '/ MODIFIER LETTER SMALL W'


def test_parse(bipa):
    res = bipa["'a"]
    assert res.generated
