import json
from flask import Flask, render_template
from flask_compress import Compress

import db_handler
import settings
from data_objects import GROUPED_REGIONS

cottages_map = Flask(__name__)
Compress(cottages_map)


def connect_db():
    if settings.DB_TYPE == 'postgres':
        db = db_handler.Postgres_Handler()
    elif settings.DB_TYPE == 'mysql':
        db = db_handler.MySQL_Handler()
    return db


@cottages_map.route('/')
def map_view():
    db = connect_db()
    regions = {}
    for table_name in db.get_region_tables():
        cottages = db.get_cottages(table_name, use_b64_image=False)

        serialized_cottages = []
        for cottage in cottages.values():
            serialized_cottages.append(cottage.serialize(use_b64_image=False))

        regions[table_name] = serialized_cottages

    regions = json.dumps(regions, ensure_ascii=False)
    region_groups = json.dumps(GROUPED_REGIONS)
    db.close()
    return render_template('map.html', regions=regions, region_groups=region_groups)


if __name__ == '__main__':
    cottages_map.run()
