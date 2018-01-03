# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.dsv import reader

from pyclts.__main__ import sounds, table


def _read_tsv(self, path):
    return set(tuple(row[1:]) for row in reader(path, delimiter='\t'))


def _test_main(self):
    self._main('report', text='no input')
    self._main('report', arg='xyz', text='invalid input')
    self._main('report', arg=self.data_path('KSL.tsv').as_posix(), text='sounds')

    infile = self.data_path('KSL.tsv').as_posix()
    out = self.tmp_path('test.csv')
    self._main('report', arg=infile, format='csv', text='existing')
    self._main('report', arg=infile, output=out.as_posix(), format='csv')
    self.assertEqual(
        self._read_tsv(out), self._read_tsv(self.data_path('KSL_report.csv')))

    self._main('annotate', arg=infile, text='CLPA_TOKENS')

    out = self.tmp_path('test.md')
    self._main('report', arg=infile, output=out.as_posix())
    self.assertTrue(out.exists())

    self._main('check', text='only one')
    self._main('check', arg='abcd', text='\ufffd')
