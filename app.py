import json
from flask import Flask, render_template

from db_handler import Postgres_Handler

cottages_map = Flask(__name__)

@cottages_map.route('/')
def map_view():
    sql = Postgres_Handler()
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
    cottages_map.run(host='0.0.0.0')
