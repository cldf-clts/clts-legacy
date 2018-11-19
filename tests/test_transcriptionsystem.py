# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest

from pyclts.transcriptionsystem import TranscriptionSystem


def test_ts():
    with pytest.raises(AssertionError):
        TranscriptionSystem('')
    with pytest.raises(ValueError):
        TranscriptionSystem('_f1')
    with pytest.raises(ValueError):
        TranscriptionSystem('_f2')
    with pytest.raises(ValueError):
        TranscriptionSystem('_f3')
    with pytest.raises(ValueError):
        _ = TranscriptionSystem('what')
