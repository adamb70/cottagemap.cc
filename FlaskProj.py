import json
from collections import defaultdict
from flask import Flask, render_template

import settings
from db_handler import SQL_Handler

app = Flask('CottageMap')

@app.route('/')
def hello_world():
    sql = SQL_Handler()
    regions = {}
    for table_name in sql.get_tables():
        cottages = sql.get_cottages(table_name[0])

        serialized_cottages = []
        for cottage in cottages.values():
            serialized_cottages.append(cottage.serialize())

        regions[table_name[0]] = serialized_cottages

    regions = json.dumps(regions, ensure_ascii=False)

    return render_template('map.html', regions=regions)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
