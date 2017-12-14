"""Test how well clts works on the data used in NorthEuralex"""

from pylexibank.util import data_path
from pyclts import TranscriptionSystem as TS
from clldutils.csvw.metadata import TableGroup
from collections import defaultdict
from tabulate import tabulate
clts = TS()

visited = set()
errors = defaultdict(list)

for ds in ['powoco-Bahnaric-200-24.csv',
        'powoco-Uralic-173-8.csv',
        'powoco-Tujia-109-5.csv',
        'powoco-Romance-110-43.csv',
        'powoco-Huon-140-14.csv',
        'powoco-Chinese-180-18.csv']:
    
    tb = TableGroup.from_file(
            data_path('powoco', 'cldf', 'cldf-metadata.json'))
    print(ds)
    for item in tb.tables[0]:
        for segment in item['Segments']:
            if segment not in visited:
                visited.add(segment)
                print(segment)
                sound = clts[segment]
                if sound.type == 'unknownsound':
                    errors['unknown'] += [segment]
                elif not sound.name:
                    errors['problems'] += [segment]
                elif sound.generated:
                    errors['generated'] += [(segment, str(sound), sound.source, sound.name)]
                elif str(sound) != sound.grapheme:
                    errors['possible'] += [(segment, str(sound), sound.source,
                        sound.name, sound.alias, sound.normalized)]

print('---unkown---')
for i, error in enumerate(errors['unknown']):
    print(i+1, error)
print('---problem---')
for i, problem in enumerate(errors['problem']):
    print(i+1, problem)
print('---generated---')
table1 = [['NUMBER', 'SOURCE', 'CLTS/BIPA', 'SOURCE2', 'NAME', 'GOOD']]
table2 = [[x for x in table1[0]]]
for i, (a, b, c, d) in enumerate(errors['generated']):
    if a == b:
        table1 += [[i+1, a, b, c, d, a == b]]
    else:
        table2 += [[i+1, a, b, c, d, a == b]]
print(tabulate(table1[1:], headers=table1[0]))
print(tabulate(table2[1:], headers=table2[0]))

table1 = [['NUMBER', 'SOURCE', 'CLTS/BIPA', 'SOURCE2', 'NAME', 'GOOD']]
for i, (a, b, c, d, e, f) in enumerate(errors['possible']):
    table1 += [[i+1, a, b, c, d, e, f]]

print(tabulate(table1[1:], headers=table1[0]))

print('---visited---')
print(len(visited))
