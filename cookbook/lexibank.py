"""Test how well clts works on the data used in NorthEuralex"""

from pylexibank.util import data_path
from pyclts import TranscriptionSystem as TS
from csvw.metadata import TableGroup
from collections import defaultdict
from tabulate import tabulate
from unicodedata import normalize
clts = TS()

visited = set()
errors = defaultdict(list)
new_table = [[
    'source',
    'type',
    'grapheme',
    'bipa',
    'nfd-normalized',
    'clts-normalized',
    'aliased',
    'generated',
    'stressed',
    'name',
    'codepoints'
    ]]

for ds in ['powoco', 'bowernpny', 'baidial', 'mixezoquean', 'galuciotupi',
        'palaung', 'gldhmongmien', 'yinku' ]:
    
    tb = TableGroup.from_file(
            data_path(ds, 'cldf', 'cldf-metadata.json'))
    print(ds, len(visited))
    for item in tb.tables[0]:
        for segment in item['Segments']:
            if segment not in visited:
                visited.add(segment)
                sound = clts[segment]
                #print(segment, sound.source, sound.codepoints)
                if sound.type == 'unknownsound':
                    new_table += [[segment, 'unknownsound', '', '', '', '', '',
                        '', '', '', '']]
                elif sound.type == 'marker':
                    new_table += [[segment, 'marker', '', '', '', '', '', '',
                    '', '', '', '']]
                else:
                    assert normalize('NFD', segment) == sound.source
                    if segment != sound.source:
                        nfd = '+'
                    else:
                        nfd = ''
                    new_table += [[segment, sound.type, sound.grapheme,
                        str(sound), 
                        nfd,
                        '+' if sound.normalized else '',
                        '+' if sound.alias else '',
                        '+' if sound.generated else '',
                        '+' if sound.stress == 'primary-stress' else '',
                        sound.name,
                        sound.codepoints
                        ]]
                        
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

with open('test_data.tsv', 'w') as f:
    f.write('\t'.join(new_table[0])+'\n')
    for line in sorted(new_table[1:], key=lambda x: tuple(x[1:])):
        f.write('\t'.join(line)+'\n')
