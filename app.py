import json
from flask import Flask, render_template

import db_handler
import settings

cottages_map = Flask(__name__)

if settings.DB_TYPE == 'postgres':
    db = db_handler.Postgres_Handler()
elif settings.DB_TYPE == 'mysql':
    db = db_handler.MySQL_Handler()


@cottages_map.route('/')
def map_view():
    regions = {}
    for table_name in db.get_tables():
        cottages = db.get_cottages(table_name[0])

        serialized_cottages = []
        for cottage in cottages.values():
            serialized_cottages.append(cottage.serialize())

        regions[table_name[0]] = serialized_cottages

    regions = json.dumps(regions, ensure_ascii=False)

    return render_template('map.html', regions=regions)


if __name__ == '__main__':
    cottages_map.run()
