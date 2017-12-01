# coding: utf-8

"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

from clldutils.path import Path


def local_path(*comps):
    return Path(__file__).parent.parent.joinpath(*comps)


def td_path(*comps):
    return local_path('transcriptiondata', *comps)


def ts_path(*comps):
    return local_path('transcriptionsystems', *comps)


def sources_path(*comps):
    """Helper function to create a local path to the sources of CLPA data."""
    return local_path('sources', *comps)
