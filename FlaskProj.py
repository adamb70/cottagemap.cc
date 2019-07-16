import MySQLdb
from flask import Flask, render_template


locs = []
def addLocs(table):
    for n in table:
        locs.append([n[1], n[2], n[10].replace(' ', '').split(',')[0], n[10].replace(' ', '').split(',')[1], n[3].replace('- \xa3', ''), n[7]])


con = MySQLdb.connect('localhost', 'root', 'password', 'cottages')
cur = con.cursor()


cur.execute("""SHOW TABLES""")
for table_name in cur.fetchall():
    q = "SELECT * FROM %s" % table_name[0]
    cur.execute(q)
    results = cur.fetchall()
    addLocs(results)


app = Flask('CottageMap')

@app.route('/')
def hello_world():
    return render_template('map.html', locs=locs)


if __name__ == '__main__':
    app.run()
