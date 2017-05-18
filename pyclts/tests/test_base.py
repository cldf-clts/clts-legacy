# coding: utf-8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

from pyclpa.base import get_clpa, Unknown, Custom, Sound


class Tests(TestCase):
    def setUp(self):
        self.clpa = get_clpa()

    def test_normalize(self):
        self.assertEqual(self.clpa.normalize('a \u01dd'), 'a \u0259')

    def _token_classes(self, tokens):
        return [type(t) for t in tokens]

    def test_call(self):
        self.assertNotIn(Unknown, self._token_classes(self.clpa(['t', 'e', 's', 't'])))
        self.assertNotIn(Unknown, self._token_classes(self.clpa('t e s t')))

        assert self.clpa('t e th s t')[2].clpa.CLPA == 'tʰ'

        self.assertIsInstance(self.clpa('t X s t')[1], Unknown)

        assert self.clpa('ˈt e s t')[0].origin[1] == 't'

        self.assertEqual(self.clpa('p h₂ t e r', text=True), 'p \ufffd t e r')

        tokens = self.clpa('p h₂/ t e r')
        self.assertIn(Custom, self._token_classes(tokens))
        self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p h₂ t e r')

        sounds = {}
        tokens = self.clpa('p h₂/x t e r u̯', sounds=sounds)
        self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p x t e r w')
        self.assertEqual(
            len([t for t in tokens if isinstance(t, Sound) and t.converted]), 2)
        assert 'h₂/x' in sounds

        tokens = self.clpa('p / t e r')
        self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p \ufffd t e r')
