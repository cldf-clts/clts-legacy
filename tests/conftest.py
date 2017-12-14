# coding: utf-8
from __future__ import unicode_literals, print_function, division

import pytest

from pyclts import TranscriptionSystem, TranscriptionData


@pytest.fixture
def bipa():
    return TranscriptionSystem()


@pytest.fixture
def asjp():
    return TranscriptionSystem()


@pytest.fixture
def gld():
    return TranscriptionSystem()


@pytest.fixture
def sca():
    return TranscriptionData('sca')


@pytest.fixture
def asjpd():
    return TranscriptionData('asjp')


@pytest.fixture
def dolgo():
    return TranscriptionData('dolgo')


@pytest.fixture
def dolgo():
    return TranscriptionData('dolgo')


@pytest.fixture
def phoible():
    return TranscriptionData('phoible')


@pytest.fixture
def pbase():
    return TranscriptionData('pbase')

