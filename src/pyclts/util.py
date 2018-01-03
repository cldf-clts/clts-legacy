# coding: utf-8
"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

import unicodedata

from clldutils.path import Path

__all__ = ['EMPTY', 'UNKNOWN', 'pkg_path', 'norm', 'nfd']

EMPTY = "◌"
UNKNOWN = "�"


def pkg_path(*comps):
    return Path(__file__).parent.joinpath(*comps)


def app_path(*comps):
    return Path(__file__).parent.parent.parent.joinpath('app', *comps)


def norm(string):
    return string.replace(EMPTY, "")


def nfd(string):
    return unicodedata.normalize("NFD", string)
