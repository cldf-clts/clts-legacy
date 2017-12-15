# coding: utf-8
"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

import unicodedata

from clldutils.path import Path

def test_data(*comps):
    return Path(__file__).parent.joinpath('data', *comps)

