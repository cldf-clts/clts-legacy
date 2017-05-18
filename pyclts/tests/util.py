# coding: utf-8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import WithTempDir
from clldutils.path import Path


class TestCase(WithTempDir):
    def setUp(self):
        super(TestCase, self).setUp()

    def data_path(self, *comps):
        return Path(__file__).parent.joinpath('data', *comps)
