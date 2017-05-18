# coding: utf-8
from __future__ import unicode_literals, print_function, division

from pyclpa.tests.util import TestCase


class Tests(TestCase):
    def test_local_path(self):
        from pyclpa.util import local_path

        assert local_path('bla').name == 'bla'

    def test_load_alias(self):
        from pyclpa.util import local_path, load_alias

        assert load_alias(local_path('alias.tsv'))['ɡ'] == 'g'
