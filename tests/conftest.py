# coding: utf-8
from __future__ import unicode_literals, print_function, division

import pytest

from pyclts import TranscriptionSystem


@pytest.fixture
def bipa():
    return TranscriptionSystem()


@pytest.fixture
def asjp():
    return TranscriptionSystem()


@pytest.fixture
def gld():
    return TranscriptionSystem()
