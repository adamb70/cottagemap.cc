import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

import settings
from data_objects import REGION_TABLES
from spider import Spider


def crawler_task():
    print('Starting crawl task')
    spider = Spider(use_postgres=True, driver=os.environ.get('DRIVER_TYPE', 'chrome'))
    for region in list(REGION_TABLES.keys()):
        print('Gathering late deals from', region)
        spider.populate_table(region, get_b64_images=False)



def run_web_script():
    os.system('gunicorn -c gunicorn.conf.py app:cottages_map')


def start_scheduler():
    # Attention: you cannot use a blocking scheduler here as that will block the script from proceeding.
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=crawler_task, trigger=CronTrigger(minute=10, day_of_week='tue'))
    scheduler.start()


def run():
    start_scheduler()
    run_web_script()


if __name__ == '__main__':
    run()
