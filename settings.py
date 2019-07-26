import os

GOOGLE_CHROME_BIN = ''
CHROMEDRIVER_PATH = 'chromedriver.exe'

DB_TYPE = os.environ.get('DB_TYPE', 'postgres')

SQL_HOST = 'localhost'
SQL_USER = 'root'
SQL_PASS = 'password'
SQL_DB = 'cottages'

DATABASE_URL = os.environ['DATABASE_URL']

PROCESS_COUNT = os.environ.get('PROCESS_COUNT', 4)
