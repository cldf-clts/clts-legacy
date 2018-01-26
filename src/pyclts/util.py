# coding: utf-8
"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

import unicodedata

from six import text_type

from clldutils.path import Path
from csvw.dsv import reader

__all__ = ['EMPTY', 'UNKNOWN', 'pkg_path', 'norm', 'nfd']

EMPTY = "◌"
UNKNOWN = "�"


def similarity(soundA, soundB, dtype='difference'):
    f1, f2 = set(soundA.featureset), set(soundB.featureset)
    f12 = f1.union(f2)
    f1_2 = f1.intersection(f2)
    f_12 = f1.difference(f2)
    if dtype == 'difference':
        return f_12
    elif dtype == 'intersection':
        return f1_2

    return 1 - f1_2 / f12 


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


def itertable(table):
    """Auxiliary function for iterating over a data table."""
    for item in table:
        res = {
            k.lower(): nfd(v) if isinstance(v, text_type) else v for k, v in item.items()}
        for extra in res.pop('extra', []):
            k, _, v = extra.partition(':')
            res[k.strip()] = v.strip()
        yield res


def iterdata(folder, fname, grapheme_col, *cols):
    seen = set()
    for row in reader(pkg_path(folder, fname), delimiter='\t', dicts=True):
        grapheme = {"grapheme": row[grapheme_col]}
        if folder != 'soundclasses' and grapheme['grapheme'] in seen:
            print(folder, fname)
            print(grapheme['grapheme'])
            raise ValueError
        seen.add(grapheme['grapheme'])
        for col in cols:
            grapheme[col.lower()] = row[col]
        yield row['CLTS_NAME'], row['BIPA_GRAPHEME'], grapheme
