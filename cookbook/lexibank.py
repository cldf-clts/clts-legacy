"""Test how well clts works on the data used in NorthEuralex"""

from pylexibank.util import data_path
from pyclts.clts import CLTS
from clldutils.csvw.metadata import TableGroup
from collections import defaultdict
clts = CLTS()

visited = set()
errors = defaultdict(list)

for ds in ['powoco-Bahnaric-200-24.csv',
        'powoco-Uralic-173-8.csv',
        'powoco-Tujia-109-5.csv',
        'powoco-Romance-110-43.csv',
        'powoco-Huon-140-14.csv',
        'powoco-Chinese-180-18.csv']:
    
    tb = TableGroup.from_file(
            data_path('powoco', 'cldf', ds+'-metadata.json'))
    for item in tb.tables[0]:
        for segment in item['Segments'].split(' '):
            if segment not in visited:
                visited.add(segment)
                sound = clts.get(segment)
                if sound.type == 'unknown':
                    errors['unkown'] += [segment]
                elif not sound.name:
                    errors['problems'] += [segment]
                elif sound.generated:
                    errors['generated'] += [(segment, str(sound), sound.name)]
print('---unkown---')
for i, error in enumerate(errors['unknown']):
    print(i+1, error)
print('---problem---')
for i, problem in enumerate(errors['problem']):
    print(i+1, problem)
print('---generated---')
for i, (a, b, c) in enumerate(errors['generated']):
    print(i+1, a, b, c)
print('---visited---')
print(len(visited))
