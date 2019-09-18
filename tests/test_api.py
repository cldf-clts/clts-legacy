import pytest

from pyclts.api import CLTS


@pytest.fixture
def sources(tmpdir):
    tmpdir.join('sources').mkdir()
    tmpdir.join('sources', 'index.tsv').write_text(
        'NAME\tDESCRIPTION\tREFS\tTYPE\tURITEMPLATE\ntest\t\t\ttd\t', 'utf8')
    tmpdir.join('sources', 'test').mkdir()
    tmpdir.join('sources', 'test', 'graphemes.tsv').write_text('GRAPHEME\tBIPA', 'utf8')


def test_iter_sources(sources, tmpdir):
    api = CLTS(repos=str(tmpdir))
    srcs = list(api.iter_sources(type='td'))
    assert len(srcs[0][1]) == 0
    assert srcs[0][0]['NAME'] == 'test'
