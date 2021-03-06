import MySQLdb
import psycopg2

import settings
from data_objects import OfferRow, LateOffer, REGION_TABLES


class MySQL_Handler:
    def __init__(self):
        self.con = MySQLdb.connect(host=settings.SQL_HOST, user=settings.SQL_USER, password=settings.SQL_PASS,
                                   db=settings.SQL_DB, charset='utf8', use_unicode=True)
        self.cur = self.con.cursor()

    def create_table(self, table_name):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS %s (
            ID INT UNIQUE NOT NULL AUTO_INCREMENT,
            title VARCHAR(500) NOT NULL,
            lat DECIMAL(10, 8) NOT NULL,
            lon DECIMAL(11, 8) NOT NULL,
            location VARCHAR(500) NULL,
            url VARCHAR(500) NOT NULL,
            slug VARCHAR(500) NOT NULL,
            ref VARCHAR(100) NOT NULL,
            description TEXT NULL,
            weekly_low MEDIUMINT NULL,
            weekly_high MEDIUMINT NULL,
            sleeps varchar(100) NULL,
            bedrooms varchar(100) NULL,
            dog BOOLEAN NULL,
            child BOOLEAN NULL,
            wifi BOOLEAN NULL,
            late_offer VARCHAR(500) NULL,
            late_nights SMALLINT NULL,
            late_price MEDIUMINT NULL,
            late_savings_tag VARCHAR(100) NULL,
            image MEDIUMBLOB NULL,
            img_url VARCHAR(500) NULL,
            PRIMARY KEY (ID)) """ % (table_name,))

    def create_log_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS log_table (
            table_name VARCHAR(500) UNIQUE NOT NULL,
            last_updated DATETIME NOT NULL,
            PRIMARY KEY (table_name))""")

    def reset_table(self, table_name):
        """ Drops and recreates table. Use clear_table if the columns dont need changing. """
        self.cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.con.commit()
        self.create_table(table_name)

    def clear_table(self, table_name):
        self.cur.execute(f"TRUNCATE TABLE {table_name}")
        self.con.commit()

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()

    @property
    def columns(self):
        return ["ID", "title", "lat", "lon", "location", "url", "slug", "ref", "description", "weekly_low",
                "weekly_high", "sleeps", "bedrooms", "dog", "child", "wifi", "late_offer", "late_nights", "late_price",
                "late_savings_tag", "image", "img_url"]

    def get_tables(self):
        self.cur.execute("SHOW TABLES")
        return self.cur.fetchall()

    def get_region_tables(self):
        all_tables = [table[0] for table in self.get_tables()]
        ret = []
        for region in REGION_TABLES.values():
            if region in all_tables:
                ret.append(region)
        return ret

    def update_log(self, table_name):
        self.create_log_table()
        self.cur.execute(f"""
        INSERT INTO log_table (table_name, last_updated) VALUES('{table_name}', NOW())
        ON DUPLICATE KEY UPDATE last_updated=NOW()""")
        self.commit()

    def get_update_times(self):
        self.create_log_table()
        self.cur.execute("SELECT * FROM log_table")
        return self.cur.fetchall()

    def save_offers(self, offers, table_name):
        row = "INSERT INTO {TABLE_NAME} ({columns}) VALUES (DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
            TABLE_NAME=table_name, columns=",".join(self.columns))

        for offer in offers:
            self.cur.execute(row, tuple(vars(offer).values()))

        self.commit()
        self.update_log(table_name)

    def load_offers(self, table_name, use_b64_image=False):
        excludes = ['ID']
        if not use_b64_image:
            excludes.append('image')
        col_list = [col for col in self.columns if col not in excludes]
        columns = ', '.join(col_list)

        q = f"SELECT {columns} FROM {table_name}"
        self.cur.execute(q)
        rows = self.cur.fetchall()

        offers = []
        for r in rows:
            dic = dict(zip(col_list, r))
            offer = OfferRow(**dic)
            offers.append(offer)
        return offers

    def get_cottages(self, table_name, use_b64_image=False):
        cottages = {}
        for offer in self.load_offers(table_name, use_b64_image=use_b64_image):
            try:
                cottage = cottages[offer.ref]
            except KeyError:
                cottages[offer.ref] = offer.to_cottage()
                cottage = cottages[offer.ref]

            new_offer = LateOffer()
            new_offer.offer = offer.late_offer
            new_offer.nights = offer.late_nights
            new_offer.price = offer.late_price
            new_offer.savings_tag = offer.late_savings_tag
            cottage.late_offers.append(new_offer)

        return cottages


# noinspection PyMissingConstructor
class Postgres_Handler(MySQL_Handler):
    def __init__(self):
        self.con = psycopg2.connect(settings.DATABASE_URL, sslmode='require')
        self.cur = self.con.cursor()

    def create_table(self, table_name):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS %s (
            ID SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            lat DECIMAL(10, 8) NOT NULL,
            lon DECIMAL(11, 8) NOT NULL,
            location VARCHAR(500) NULL,
            url VARCHAR(500) NOT NULL,
            slug VARCHAR(500) NOT NULL,
            ref VARCHAR(100) NOT NULL,
            description TEXT NULL,
            weekly_low INTEGER NULL,
            weekly_high INTEGER NULL,
            sleeps varchar(100) NULL,
            bedrooms varchar(100) NULL,
            dog BOOLEAN NULL,
            child BOOLEAN NULL,
            wifi BOOLEAN NULL,
            late_offer VARCHAR(500) NULL,
            late_nights SMALLINT NULL,
            late_price INTEGER NULL,
            late_savings_tag VARCHAR(100) NULL,
            image BYTEA NULL,
            img_url VARCHAR(500) NULL) """ % (table_name,))

    def create_log_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS log_table (
            table_name VARCHAR(500) PRIMARY KEY NOT NULL ,
            last_updated TIMESTAMPTZ NOT NULL)""")

    def update_log(self, table_name):
        self.create_log_table()
        self.cur.execute(f"""
        INSERT INTO log_table (table_name, last_updated) VALUES('{table_name}', NOW())
        ON CONFLICT (table_name) DO UPDATE SET last_updated=NOW()""")
        self.commit()

    def get_tables(self):
        self.cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        return self.cur.fetchall()
