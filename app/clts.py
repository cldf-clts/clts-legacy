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

if not args.get('plain'):
    print ''
    print '<html><body>'
    print '<style>th{background: gray;color:white;}td {border:2px solid gray;}'
    print '.comment {color:red;}'
    print '.keywords {color:darkgreen;}'
    print '</style>'
    print '<p>Querying <i>'+args['name']+'</i></p>'
    print '<table><tr><th>DATASET</th><th>PARAMETER</th><th>VALUE</th></tr>';
    for line in cursor.execute(
            'select * from data where name="'+args['name']+'";'):
        print '<tr>'
        print '<td>' + line[1].split(':')[0].encode('utf-8') +'</td>'
        print '<td>' + line[1].split(':')[1].encode('utf-8')+'</td>'
        print '<td>' + line[2].encode('utf-8')+'</td>'
        print '</tr>'
    print '</table></body></html>'

else:
    print 'Content-Disposition: attachment; filename="clts.json"'
    print
    out = {}
    for line in cursor.execute(
            'select * from data where name="'+args['name']+'";'):
        out[line[1]] = line[2]
    print json.dumps(out)





