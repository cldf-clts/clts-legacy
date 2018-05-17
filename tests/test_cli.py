# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path

from pyclts.__main__ import sounds, dump, stats, table


def test_sounds_cmd(capsys, mocker):
    sounds(mocker.Mock(system='bipa', args=['a', 'kh']))
    out, err = capsys.readouterr()
    assert 'kʰ' in out


def test_table(capsys, mocker):
    table(mocker.Mock(system='bipa', args=['a', 'kh']))
    out, err = capsys.readouterr()
    assert '# vowel' in out
    assert '# consonant' in out


def test_dump(capsys, mocker, tmpdir):
    tmpdir.join('data').mkdir()
    dump(mocker.Mock(repos=Path(str(tmpdir))), test=True)
    out, err = capsys.readouterr()
    assert Path(str(tmpdir)).joinpath('data', 'graphemes.tsv').exists()
    stats(mocker.Mock(repos=Path(str(tmpdir))))
    out, err = capsys.readouterr()
    assert 'Unique graphemes' in out
