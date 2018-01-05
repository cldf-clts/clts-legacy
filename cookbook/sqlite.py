import pyclts
from pyclts import *
from pyclts.util import app_path
import sqlite3
import datetime

TIME = datetime.datetime.today().strftime('%y-%m-%d %H:%M')
VERSION = pyclts.__version__

tss = {'bipa' : TranscriptionSystem('bipa'), 
        'gld' : TranscriptionSystem('gld'), 
        'asjp': TranscriptionSystem('asjp')
        }
tds = {k: TranscriptionData(k) for k in ['phoible', 'ruhlen', 'pbase',
    'lapsyd', 'eurasian', 'nidaba', 'diachronica', 'multimedia']}

cls = {
        'sca': TranscriptionData('sca'),
        'asjp': TranscriptionData('asjp'),
        'dolgo': TranscriptionData('dolgo'),
        'prosody': TranscriptionData('prosody'),
        'cv': TranscriptionData('cv'),
        'color': TranscriptionData('color')
        }

db = sqlite3.connect(app_path('data.sqlite3').as_posix())
cursor = db.cursor()
try:
    cursor.execute('drop table data;')
except:
    pass
cursor.execute('create table data (name text, parameter text, value text, version text, date text);')
visited = set()
for ts_, ts in tss.items():
    print(ts.id)
    for s, snd in ts.items():
        if not snd.type == 'marker':
            if not snd.alias:
                cursor.execute(
                        'insert into data values(?, ?, ?, ?, ?);',
                        (snd.name, ts.id+':grapheme', s, VERSION, TIME)
                        )
            else:
                cursor.execute(
                        'insert into data values(?, ?, ?, ?, ?);',
                        (snd.name, ts.id+':alias', s, VERSION, TIME)
                        )
            visited.add((ts.id, snd.name))
            if ('bipa', snd.name) not in visited:
                    visited.add(('bipa', snd.name))
                    cursor.execute(
                            'insert into data values(?, ?, ?, ?, ?);',
                            (snd.name, 'bipa:grapheme',
                                tss['bipa'][snd.name].s,
                                VERSION,
                                TIME))


for td_, td in tds.items():
    print(td.id)
    for name in [n for n in td.names if not 'marker' in n]:
        for vals in td.data[name]:
            for key in vals:
                cursor.execute(
                    'insert into data values(?, ?, ?, ?, ?);',
                    (name, td.id+':'+key, vals[key], VERSION, TIME)
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
                                'insert into data values(?, ?, ?, ?, ?);',
                                (name, ts.id+':grapheme', ts[s].s,
                                    VERSION, TIME)
                                )
                except:
                    pass

for t_, name in visited:
    for td_, td in cls.items():
        if t_ == 'bipa':
            try:
                sc = td[name]
                cursor.execute('insert into data values (?, ?, ?, ?, ?);',
                        (name, td.id + ':' + 'sound-class', sc, VERSION, TIME))
            except:
                pass

db.commit()

db = sqlite3.connect(app_path('data.sqlite3').as_posix())
db.cursor().execute('vacuum')
db.commit()
