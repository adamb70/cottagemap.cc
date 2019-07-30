import json
from flask import Flask, render_template, request, jsonify, make_response
from flask_compress import Compress

import db_handler
import settings
from data_objects import GROUPED_REGIONS, INV_REGION_TABLES
from spider import crawl, multiprocess_crawl

cottages_map = Flask(__name__)
Compress(cottages_map)


def connect_db():
    if settings.DB_TYPE == 'postgres':
        db = db_handler.Postgres_Handler()
    elif settings.DB_TYPE == 'mysql':
        db = db_handler.MySQL_Handler()
    return db


@cottages_map.after_request
def add_header(response):
    # 43200 is default, but leaving this here for easier changing in the future
    response.cache_control.max_age = 43200
    return response


@cottages_map.route('/')
def map_view():
    db = connect_db()
    update_times = json.dumps({x: y.timestamp() for x, y in db.get_update_times()})

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
    return render_template('map.html', regions=regions, region_groups=region_groups, update_times=update_times)


@cottages_map.route('/update/', methods=['POST'])
def update_db():
    req = request.get_json()
    regions = req.get('regions', None)

    if not regions:
        return jsonify(status="fail")

    using_postgres = True if settings.DB_TYPE == 'postgres' else False

    # TODO: Uncomment this
    #update_regions = []
    #for group in regions:
    #    for region in GROUPED_REGIONS[group]:
    #        update_regions.append(INV_REGION_TABLES[region])

    #multiprocess_crawl(update_regions, settings.PROCESS_COUNT, using_postgres)

    return make_response(jsonify({'response': 'Updating...'}, 200))


if __name__ == '__main__':
    cottages_map.run()
