# coding: utf-8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path, readlines
from clldutils.dsv import reader


def local_path(*comps):
    """Helper function to create a local path to the current directory of CLPA"""
    return Path(__file__).parent.joinpath('data', *comps)


def load_whitelist():
    """
    Basic function to load the CLPA whitelist.
    """
    return {s.CLPA: s for s in
            reader(local_path('clpa.tsv'), delimiter='\t', namedtuples=True)}


def load_alias(_path):
    """
    Alias are one-character sequences which we can convert on a step-by step
    basis by applying them successively to all subsegments of a segment.
    """
    path = Path(_path)
    if not path.is_file():
        path = local_path(_path)

    alias = {}
    for line in readlines(path, comment='#'):
        source, target = line.split('\t')
        alias[eval('"' + source + '"')] = eval('r"' + target + '"')
    return alias


def split(string):
    return string.split(' ')


def join(tokens):
    return ' '.join('%s' % t for t in tokens)
