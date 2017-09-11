# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import Counter, defaultdict
import unicodedata

from clldutils.path import Path
from clldutils.csvw.metadata import TableGroup

from pyclts.clts import CLTS, codepoint

LEXIBANK = Path('../../lexibank/lexibank-data/datasets')


def uname(s):
    try:
        return ' / '.join(unicodedata.name(ss) for ss in s)
    except:
        return '-'


if __name__ == "__main__":
    import sys

    sounds = Counter()
    unknown = Counter()
    inventories = defaultdict(set)
    inventories_errors = defaultdict(set)

    if '--lexibank' in sys.argv:
        LEXIBANK = Path(sys.argv[sys.argv.index('--lexibank')+1])
        dset = sys.argv[sys.argv.index('--lexibank')+2]
    else:
        dset = sys.argv[1]

    clts = CLTS()
    ds = TableGroup.from_file(
        LEXIBANK.joinpath(dset, 'cldf', 'cldf-metadata.json'))

    for row in ds.tabledict['forms.csv']:
        if row['Segments']:
            for segment in row['Segments']:
                sound = clts.get(segment)
                name = sound.name
                if name:
                    inventories[row['Language_ID']].add(sound.grapheme)
                    sounds.update(['{0} [{1}]'.format(sound.grapheme, name)])
                else:
                    inventories_errors[row['Language_ID']].add(sound.source)
                    inventories[row['Language_ID']].add(sound.source)
                    unknown.update([sound.source])

    for i, (k, v) in enumerate(unknown.most_common()):
        if i == 0:
            print('\nUnknown sound segments:\n')
        print('{3}: {0} [{1}] {2}'.format(k, codepoint(k) if k else '-', uname(k), v))

    print('\nSummary:\n')
    print('recognized segments: {0}'.format(len(sounds)))
    print('unknown segments: {0}'.format(len(unknown)))
    print('average inventory size: {0}'.format(
        sum([len(v) for v in inventories.values()])/float(len(inventories))))
    print('average number of unknown segments per inventory: {0}'.format(
        sum([len(v) for v in inventories_errors.values()])/float(len(inventories))))
