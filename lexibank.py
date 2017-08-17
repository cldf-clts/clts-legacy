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

    clts = CLTS()
    ds = TableGroup.from_file(
        LEXIBANK.joinpath(sys.argv[1], 'cldf', 'cldf-metadata.json'))

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

    for k, v in unknown.most_common():
        print('{3}: {0} [{1}] {2}'.format(k, codepoint(k) if k else '-', uname(k), v))

    print('---------------------------------')
    print('recognized segments: {0}'.format(len(sounds)))
    print('errors: {0}'.format(len(unknown)))
    print('average inventory size: {0}'.format(
        sum([len(v) for v in inventories.values()])/float(len(inventories))))
    print('average number of errors per inventory: {0}'.format(
        sum([len(v) for v in inventories_errors.values()])/float(len(inventories))))
