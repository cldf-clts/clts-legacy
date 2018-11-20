# coding: utf-8
"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division
import unicodedata
from collections import defaultdict

from six import text_type

from clldutils.path import Path
from csvw.dsv import reader

__all__ = ['EMPTY', 'UNKNOWN', 'pkg_path', 'norm', 'nfd']

EMPTY = "◌"
UNKNOWN = "�"


class TranscriptionBase(object):
    #
    # This base class makes sure only one instance per (sub-class, id_) is created.
    # We do this to avoid re-reading the instance data from disk repeatedly. To make this
    # work, derived classes must do the heavy-lifting in __init__ conditionally, i.e.
    # check, whether the instance has been initialized before.
    #
    __instances = {}

    def __new__(cls, id_, **kw):
        key = (cls.__name__, id_)
        if key not in cls.__instances:
            # Only create a new instance if the combination (cls, id_) hasn't been seen
            # before.
            cls.__instances[key] = object.__new__(cls)
        cls.__instances[key].id = id_
        return cls.__instances[key]

    def resolve_sound(self, sound):
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, sound):
        """Return a Sound instance matching the specification."""
        return self.resolve_sound(sound)

    def get(self, sound, default=None):
        try:
            res = self[sound]
            if getattr(res, 'type', None) == 'unknownsound' and default:
                return default
            return res
        except KeyError:
            return default

    def __call__(self, sounds, default="0"):
        return [self.get(x, default=default) for x in sounds.split()]

    def translate(self, string, target_system):
        return ' '.join('{0}'.format(
            target_system.get(self[s].name or '?', '?')) for s in string.split())


def pkg_path(*comps):
    return Path(__file__).parent.joinpath(*comps)


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


def read_data(folder, fname, grapheme_col, *cols):
    data, sounds, names = defaultdict(list), [], []

    for row in reader(pkg_path(folder, fname), delimiter='\t', dicts=True):
        grapheme = {"grapheme": row[grapheme_col]}
        for col in cols:
            grapheme[col.lower()] = row[col]
        data[row['BIPA_GRAPHEME']].append(grapheme)
        data[row['CLTS_NAME']].append(grapheme)
        sounds.append(row['BIPA_GRAPHEME'])
        names.append(row['CLTS_NAME'])

    return data, sounds, names
