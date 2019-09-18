from itertools import groupby
from pathlib import Path

import pytest
from csvw.dsv import iterrows as reader

from pyclts import TranscriptionSystem, TranscriptionData, SoundClasses


def pytest_generate_tests(metafunc):
    if 'test_sounds' == metafunc.function.__name__:
        fixturenames = None
        tests = []
        for i, test in enumerate(reader(
            Path(__file__).parent / 'data' / 'test_data.tsv',
            delimiter='\t',
            dicts=True
        )):
            if i == 0:
                fixturenames = list(test.keys())
                fixturenames.pop(fixturenames.index('bipa'))
            del test['bipa']
            if None in test:
                del test[None]
            if len(fixturenames) != len(test.keys()):
                raise ValueError(set(test.keys()) - set(fixturenames))
            tests.append(test)

        attrs = ['nfd-normalized', 'clts-normalized', 'aliased', 'generated', 'stressed']
        tests = sorted(tests, key=lambda t: tuple([t[a] for a in attrs]))
        batches = []
        for _, ts in groupby(tests, lambda t: tuple([t[a] for a in attrs])):
            for test in ts:
                batches.append(tuple(test.values()))
                break

        metafunc.parametrize(','.join(n.replace('-', '_') for n in fixturenames), batches)
    elif 'test_clicks' == metafunc.function.__name__:
        tests = []
        for test in reader(
            Path(__file__).parent / 'data' / 'clicks.tsv', delimiter='\t', dicts=True
        ):
            tests.append((test['GRAPHEME'], test['MANNER']))
        metafunc.parametrize('grapheme,gtype', tests)


@pytest.fixture
def bipa():
    return TranscriptionSystem('bipa')


@pytest.fixture
def asjp():
    return TranscriptionSystem('asjpcode')


@pytest.fixture
def gld():
    return TranscriptionSystem('gld')


@pytest.fixture
def sca():
    return SoundClasses('sca')


@pytest.fixture
def asjpd():
    return SoundClasses('asjp')


@pytest.fixture
def dolgo():
    return SoundClasses('dolgo')


@pytest.fixture
def dolgo():
    return SoundClasses('dolgo')


@pytest.fixture
def phoible():
    return TranscriptionData('phoible')


@pytest.fixture
def pbase():
    return TranscriptionData('pbase')
