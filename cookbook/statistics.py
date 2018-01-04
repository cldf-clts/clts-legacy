from pyclts import TranscriptionSystem, TranscriptionData
from collections import defaultdict
import tabulate

tss = {'bipa' : TranscriptionSystem('bipa'), 
        'gld' : TranscriptionSystem('gld'), 
        'asjp': TranscriptionSystem('asjp')
        }
tds = ['phoible', 'ruhlen', 'pbase', 'lapsyd', 'eurasian', 'nidaba']

all_sounds = defaultdict(dict)
for ts_ in tss:
    ts = TranscriptionSystem(ts_)
    for s, snd in ts.items():
        if not snd.alias and not snd.type == 'marker':
            all_sounds[snd.name][ts.id] = s
            if ts.id != 'bipa' and not tss['bipa'][snd.name].type == 'unknownsound':
                all_sounds[snd.name]['bipa'] = tss['bipa'][snd.name].s

for td_ in tds:
    td = TranscriptionData(td_)
    for name in td.names:
        if not 'marker' in name:
            all_sounds[name][td.id] = ', '.join([x['grapheme'] for x in
                td.data[name]])
            for ts_, ts in tss.items():
                if not ts.id in all_sounds[name]:
                    try:
                        s = ts[name].s
                        if not ts[s].type == 'unknownsound':
                            all_sounds[name][ts.id] = s
                    except:
                        pass
table = [[
    'NO.',
    'NAME',
    'BIPA',
    'GLD',
    'ASJP',
    'PHOIBLE',
    'RUHLEN',
    'PBASE',
    'LAPSYD',
    'EURASIAN', 'NIDABA']]
for i, s in enumerate(sorted(all_sounds, key=lambda x: len(all_sounds[x]),
    reverse=True)):
    if not tss['bipa'][s].alias:
        row = [i, s]
        for x in ['bipa', 'gld', 'asjp', 'phoible', 'ruhlen', 'pbase',
                'lapsyd', 'eurasian', 'nidaba']:
            row += [all_sounds[s].get(x, '')]
        table += [row]

print(tabulate.tabulate(table, headers='firstrow', tablefmt='pipe' ))
print('')        
print('# Co-occurrence statistics')
print('TD 1 | TD 2 | Sounds | Overlap')
print('--- | --- | --- | --- ')
matrix = [[0 for x in range(4)] for y in range(4)]
for i, sA in enumerate(['phoible', 'eurasian', 'pbase', 'lapsyd', 'nidaba']):
    for j, sB in enumerate(['phoible', 'eurasian', 'pbase', 'lapsyd', 'nidaba']):
        if i < j:
            coms = len([x for x in all_sounds if all_sounds[x].get(sA) and
                all_sounds[x].get(sB)])
            alls = len([x for x in all_sounds if all_sounds[x].get(sA) or
                all_sounds[x].get(sB)])
            print(sA, '|', sB,'|',  coms, '|', '{0:.2f}'.format(coms / alls))
