# coding: utf-8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path, readlines
from clldutils.dsv import reader


def metadata_path(*comps):
    return Path(__file__).parent.parent.joinpath('metadata', *comps)


def data_path(*comps):
    """Helper function to create a local path to the current directory of CLPA"""
    return Path(__file__).parent.parent.joinpath('data', *comps)

