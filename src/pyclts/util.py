# coding: utf-8
"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

import unicodedata

from clldutils.path import Path

__all__ = ['EMPTY', 'UNKNOWN', 'pkg_path', 'norm', 'nfd']

EMPTY = "◌"
UNKNOWN = "�"


def is_valid_sound(sound, ts):
    """Check the consistency of a given transcription system conversino"""
    if sound.type in ['unknownsound', 'marker']:
        return False
    s1 = ts[sound.name]
    s2 = ts[sound.s]
    if s1.name == s2.name and s1.s == s2.s:
        return True
    return False



def pkg_path(*comps):
    return Path(__file__).parent.joinpath(*comps)


def app_path(*comps):
    return Path(__file__).parent.parent.parent.joinpath('app', *comps)


def data_path(*comps):
    return Path(__file__).parent.parent.parent.joinpath('data', *comps)


def norm(string):
    return string.replace(EMPTY, "")


def nfd(string):
    return unicodedata.normalize("NFD", string)
