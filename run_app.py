import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

import settings
from data_objects import REGION_TABLES
from spider import multiprocess_crawl


def crawler_task():
    multiprocess_crawl(list(REGION_TABLES.keys()), settings.PROCESS_COUNT, use_postgres=True)


def run_web_script():
    os.system('gunicorn -c gunicorn.conf.py app:cottages_map')


def start_scheduler():
    # Attention: you cannot use a blocking scheduler here as that will block the script from proceeding.
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=crawler_task, trigger=CronTrigger(hour=5, day_of_week='mon'))
    scheduler.start()


def run():
    start_scheduler()
    run_web_script()


if __name__ == '__main__':
    run()
