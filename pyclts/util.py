# coding: utf-8

"""Auxiliary functions for pyclts."""

from __future__ import unicode_literals, print_function, division

from clldutils.path import Path


def local_path(*comps):
    return Path(__file__).parent.parent.joinpath(*comps).as_posix()


def metadata_path(*comps):
    return local_path('metadata', *comps)


def data_path(*comps):
    """Helper function to create a local path to the current directory of CLPA"""
    return local_path('data', *comps)


def sources_path(*comps):
    """Helper function to create a local path to the sources of CLPA data."""
    return local_path('sources', *comps)
