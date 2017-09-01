# coding: utf-8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

from pyclts.clts import CLTS, UnknownSound, translate


class Tests1(TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            _ = CLTS(system='unknown')

    def test_translate(self):
        self.assertEqual(translate('a c', CLTS(system='asjp'), CLTS()), '\u0250 ts')


class Tests2(TestCase):
    def setUp(self):
        self.clts = CLTS()

    def test_unknown(self):
        self.assertIsInstance(self.clts.get('ab'), UnknownSound)
        self.assertIsInstance(self.clts.get('E'), UnknownSound)
        self.assertIsInstance(self.clts.get('Ea'), UnknownSound)

    def test_generated(self):
        sound = self.clts.get('kˡ')
        self.assertTrue(sound.generated)
        self.assertEqual(sound.type, 'consonant')

    def test_custom(self):
        sound = self.clts.get('q/a')
        self.assertTrue(sound.alias)
        self.assertEqual(self.clts[sound].grapheme, 'a')
        self.assertEqual(sound.source, 'q/a')

    def test_stacked_diacritics(self):
        s1 = self.clts.get("tʰː")
        s2 = self.clts.get("tːʰ")
        self.assertEqual(s1, s2)
        self.assertEqual('{0}'.format(s1), '{0}'.format(s2))

        # aspiration comes before duration:
        self.assertEqual('{0}'.format(s1), "tʰː")

        # FIXME: Do we want this to be two Sounds? And if so, shouldn't one be an alias?
        self.assertNotEqual(s1.grapheme, s2.grapheme)

    def test_normalize(self):
        self.assertEqual(self.clts.normalize('a \u01dd'), 'a \u0259')

    def _sound_classes(self, tokens):
        return [type(t) for t in tokens]

    def test_call(self):
        #self.assertEqual(self.clts('q/a th', text=True), 'a tʰ')
        self.assertNotIn(
            UnknownSound, self._sound_classes(self.clts(['t', 'e', 's', 't'])))
        self.assertNotIn(
            UnknownSound, self._sound_classes(self.clts('t e s t')))

        sound = self.clts('t e th s t')[2]
        self.assertTrue(sound.alias)
        self.assertEqual(self.clts[sound].grapheme, 'tʰ')
        self.assertEqual(sound.name, self.clts['tʰ'].name)

        self.assertIsInstance(self.clts('t X s t')[1], UnknownSound)

        #assert self.clts('ˈt e s t')[0].origin[1] == 't'

        #self.assertEqual(self.clts('p h² t e r', text=True), 'p \ufffd t e r')

        #tokens = self.clpa('p h₂/ t e r')
        #self.assertIn(Custom, self._token_classes(tokens))
        #self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p h₂ t e r')

        #sounds = {}
        #tokens = self.clts('p h₂/x t e r u̯')
        #self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p x t e r w')
        #self.assertEqual(
        #    len([t for t in tokens if isinstance(t, Sound) and t.converted]), 2)
        #assert 'h₂/x' in sounds

        #tokens = self.clpa('p / t e r')
        #self.assertEqual(' '.join(['%s' % t for t in tokens]), 'p \ufffd t e r')
