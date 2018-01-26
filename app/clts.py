#!/usr/bin/python2.6
import cgitb
cgitb.enable()
import cgi
import sqlite3
import datetime
import json
from docutils.core import publish_parts

print "Content-type: text/html; charset=utf-8"

# get the args of the url, convert nasty field storage to plain dictionary,
# there is probably a better solution, but this works for the moment
xargs = dict(
        name = '',
        plain = '',
        dbase = '',
        )
args = {}
tmp_args = cgi.FieldStorage()
for arg in xargs:
    tmp = tmp_args.getvalue(arg)
    if tmp:
        args[arg] = tmp

dbpath = 'data.sqlite3'

# connect to the sqlite database
db = sqlite3.connect(dbpath)
cursor = db.cursor()

dbase = args.get('dbase', ':')

if not args.get('name'):
    print ''
    print 'No sound submitted.'

else:
    if '_' in args['name']:
        name = args['name'].replace('_', ' ')
    else:
        name = args['name']
    
    
    if not args.get('plain'):
        print ''
        print '<html><body>'
        print '<style>th{background: gray;color:white;}td {border:2px solid gray;}'
        print '.comment {color:red;}'
        print '.keywords {color:darkgreen;}'
        print '</style>'
        print '<p>Querying CLTS for <i>'+name+'</i>:</p>'
        print '<table><tr><th>DATASET</th><th>PARAMETER</th><th>VALUE</th><th>VERSION</th><th>DATE</th></tr>';
        color = 'white'
        for line in cursor.execute(
                'select * from data where name="'+name+'";'):
            if dbase in line[1]:
                print '<tr>'
                dset, param = [x.encode('utf-8') for x in line[1].split(':')]
                value = line[2].encode('utf-8')
                print '<td>' + dset +'</td>'
                if dset == 'color':
                    color = value
                if param in ['url', 'image', 'sound']:
                    value = '<a target="_blank" href="'+value+'">'+value+'</a>'
                elif param in ['grapheme', 'sound-class']:
                    value = '<span class="sound">'+value+'</span>'
                print '<td>' + param +'</td>'
                print '<td>' + value +'</td>'
                print '<td>' + line[3].encode('utf-8')+'</td>'
                print '<td>' + line[4].encode('utf-8')+'</td>'
                print '</tr>'
        print '</table>'
        print '<style>.sound {background-color:'+color+';}</style>'
        print '</body></html>'
    
    else:
        print 'Content-Disposition: attachment; filename="clts.json"'
        print
        out = {}
        for line in cursor.execute(
                'select * from data where name="'+name+'";'):
            out[line[1]] = [line[2], line[3], line[4]]
        print json.dumps(out)





