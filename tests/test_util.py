
def test_TranscriptionBase_translate(bipa, asjp, asjpd):
    assert bipa.translate('ts a', asjp) == 'c E'
    assert asjp.translate('c a', bipa) == 'ts ɐ'
    assert bipa.translate('t o h t a', asjpd)[0] == 't'
