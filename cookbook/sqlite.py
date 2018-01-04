from pyclts import *
from pyclts.util import app_path
import sqlite3

tss = {'bipa' : TranscriptionSystem('bipa'), 
        'gld' : TranscriptionSystem('gld'), 
        'asjp': TranscriptionSystem('asjp')
        }
tds = {k: TranscriptionData(k) for k in ['phoible', 'ruhlen', 'pbase',
    'lapsyd', 'eurasian', 'nidaba']}

db = sqlite3.connect(app_path('data.sqlite3').as_posix())
cursor = db.cursor()
try:
    cursor.execute('drop table data;')
except:
    pass
cursor.execute('create table data (name text, parameter text, value text);')
visited = set()
for ts_, ts in tss.items():
    print(ts.id)
    for s, snd in ts.items():
        if not snd.type == 'marker':
            if not snd.alias:
                cursor.execute(
                        'insert into data values(?, ?, ?);',
                        (snd.name, ts.id+':grapheme', s)
                        )
            else:
                cursor.execute(
                        'insert into data values(?, ?, ?);',
                        (snd.name, ts.id+':alias', s)
                        )
            visited.add((ts.id, snd.name))
            if ('bipa', snd.name) not in visited:
                    visited.add(('bipa', snd.name))
                    cursor.execute(
                            'insert into data values(?, ?, ?);',
                            (snd.name, 'bipa:grapheme', tss['bipa'][snd.name].s))


for td_, td in tds.items():
    print(td.id)
    for name in [n for n in td.names if not 'marker' in n]:
        for vals in td.data[name]:
            for key in vals:
                cursor.execute(
                    'insert into data values(?, ?, ?);',
                    (name, td.id+':'+key, vals[key])
                    )
        for ts_, ts in tss.items():
            if (ts.id, name) not in visited:
                visited.add((ts.id, name))
                try:
                    s = ts[name].s
                    if '<!>' in s:
                        raise 
                    if not ts[s].type == 'unknownsound':
                        cursor.execute(
                                'insert into data values(?, ?, ?);',
                                (name, ts.id+':grapheme', ts[s].s)
                                )
                except:
                    pass
db.commit()


