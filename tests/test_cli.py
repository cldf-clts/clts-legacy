# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path

from pyclts.__main__ import sounds, dump, stats, table, _make_app_data, features
from pyclts.api import CLTS


def test_features(capsys, mocker):
    features(mocker.Mock(system='bipa'))
    out, err = capsys.readouterr()
    assert 'labialized' in out


def test_sounds_cmd(capsys, mocker):
    sounds(mocker.Mock(system='bipa', args=['a', 'kh', 'zz']))
    out, err = capsys.readouterr()
    assert 'kʰ' in out


def test_table(capsys, mocker):
    table(mocker.Mock(system='bipa', args=['a', 'kh', 'zz']))
    out, err = capsys.readouterr()
    assert '# vowel' in out
    assert '# consonant' in out
    assert '# Unknown sounds' in out
    table(mocker.Mock(system='bipa', args=['a', 'kh', 'zz'], filter='unknown'))
    table(mocker.Mock(system='bipa', args=['a', 'kh', 'zz'], filter='known'))
    table(mocker.Mock(system='bipa', args=['a', 'kh', 'zz'], filter='generated'))


def test_make_app_data(capsys, mocker, tmpdir):
    tmpdir.join('app').mkdir()
    _make_app_data(mocker.Mock(repos=CLTS(str(tmpdir))), test=True)
    assert Path(str(tmpdir)).joinpath('app', 'data.js').exists()


def test_dump(capsys, mocker, tmpdir):
    tmpdir.join('data').mkdir()
    dump(mocker.Mock(repos=CLTS(str(tmpdir))), test=True)
    out, err = capsys.readouterr()
    assert Path(str(tmpdir)).joinpath('data', 'graphemes.tsv').exists()
    stats(mocker.Mock(repos=CLTS(str(tmpdir))))
    out, err = capsys.readouterr()
    assert 'Unique graphemes' in out
