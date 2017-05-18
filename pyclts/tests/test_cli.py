# coding: utf8
from __future__ import unicode_literals, print_function, division

from six import text_type
from clldutils.testing import capture
from clldutils.dsv import reader

from pyclpa.tests.util import TestCase
from pyclpa.cli import main


class Tests(TestCase):
    def _read_tsv(self, path):
        return set(tuple(row[1:]) for row in reader(path, delimiter='\t'))

    def _main(self, cmd, arg=None, text=None, **opts):
        args = ['--{0}={1}'.format(k, v) for k, v in opts.items()] + [cmd]
        if arg:
            args.append(arg)
        with capture(main, args=args) as out:
            if text:
                if not isinstance(out, text_type):
                    out = out.decode('utf8')
                self.assertIn(text, out)

    def test_main(self):
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
