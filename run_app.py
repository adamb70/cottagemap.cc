import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

import settings
from data_objects import REGION_TABLES
from spider import crawl


def crawler_task():
    print('Starting crawl task')
    for region in list(REGION_TABLES.keys()):
        crawl(region, settings.PROCESS_COUNT)


def run_web_script():
    os.system('gunicorn -c gunicorn.conf.py app:cottages_map')


def start_scheduler():
    # Attention: you cannot use a blocking scheduler here as that will block the script from proceeding.
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=crawler_task, trigger=CronTrigger(minute=13, day_of_week='mon'))
    scheduler.start()


def run():
    start_scheduler()
    run_web_script()


if __name__ == '__main__':
    run()
