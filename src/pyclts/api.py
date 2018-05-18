# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.apilib import API
from csvw.dsv import reader

from pyclts.util import pkg_path
from pyclts import TranscriptionData, TranscriptionSystem, SoundClasses
from pyclts.soundclasses import SOUNDCLASS_SYSTEMS


class CLTS(API):
    def data_path(self, *comps):
        return self.repos.joinpath('data', *comps)

    def app_path(self, *comps):
        return self.repos.joinpath('app', *comps)

    def iter_sources(self, type=None):
        for src in reader(
                self.repos / 'sources' / 'index.tsv', dicts=True, delimiter='\t'):
            if (type is None) or (type == src['TYPE']):
                graphemesp = self.repos / 'sources' / src['NAME'] / 'graphemes.tsv'
                if graphemesp.exists():
                    yield src, list(reader(graphemesp, dicts=True, delimiter='\t'))

    def iter_transcriptiondata(self):
        for td in pkg_path('transcriptiondata').iterdir():
            yield TranscriptionData(td.stem)

    def iter_soundclass(self):
        for sc in SOUNDCLASS_SYSTEMS:
            yield SoundClasses(sc)

    def iter_transcriptionsystem(self, include_private=False, exclude=None):
        exclude = exclude or []
        for ts in pkg_path('transcriptionsystems').iterdir():
            if ts.is_dir():
                if (not ts.name.startswith('_')) or include_private:
                    if ts.name not in exclude:
                        yield TranscriptionSystem(ts.name)
