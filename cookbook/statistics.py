from pyclts import TranscriptionSystem, TranscriptionData
from collections import defaultdict
import tabulate

tss = {'bipa' : TranscriptionSystem('bipa'), 
        'gld' : TranscriptionSystem('gld'), 
        'asjp': TranscriptionSystem('asjp')
        }
tds = ['phoible', 'ruhlen', 'pbase', 'lapsyd', 'eurasian']

all_sounds = defaultdict(dict)
for ts_ in tss:
    ts = TranscriptionSystem(ts_)
    for s, snd in ts.items():
        if not snd.alias and not snd.type == 'marker':
            all_sounds[snd.name][ts.id] = s
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
    'EURASIAN']]
for i, s in enumerate(sorted(all_sounds, key=lambda x: len(all_sounds[x]),
    reverse=True)):
    if not tss['bipa'][s].alias:
        row = [i, s]
        for x in ['bipa', 'gld', 'asjp', 'phoible', 'ruhlen', 'pbase',
                'lapsyd', 'eurasian']:
            row += [all_sounds[s].get(x, '')]
        table += [row]
print(tabulate.tabulate(table, headers='firstrow', tablefmt='pipe' ))
        

