import MySQLdb

import settings
from data_objects import OfferRow, LateOffer


class SQL_Handler:
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
            dog BOOL NULL,
            child BOOL NULL,
            wifi BOOL NULL,
            late_offer VARCHAR(500) NULL,
            late_nights SMALLINT NULL,
            late_price MEDIUMINT NULL,
            late_savings_tag VARCHAR(100) NULL,
            PRIMARY KEY (ID)) """ % (table_name,))

    def clear_table(self, table_name):
        self.cur.execute("DELETE from %s" % (table_name,))
        self.cur.execute("ALTER TABLE %s AUTO_INCREMENT = 1" % (table_name,))
        self.con.commit()

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()

    @property
    def columns(self):
        return ["ID", "title", "lat", "lon", "location", "url", "slug", "ref", "description", "weekly_low",
                "weekly_high", "sleeps", "bedrooms", "dog", "child", "wifi", "late_offer", "late_nights", "late_price",
                "late_savings_tag"]

    def get_tables(self):
        self.cur.execute("""SHOW TABLES""")
        return self.cur.fetchall()

    def save_offers(self, offers, table_name):
        row = "INSERT INTO {TABLE_NAME} ({columns}) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
            TABLE_NAME=table_name, columns=",".join(self.columns))

        for offer in offers:
            self.cur.execute(row, vars(offer).values())

        self.commit()

    def load_offers(self, table_name):
        q = "SELECT * FROM %s" % table_name
        self.cur.execute(q)
        rows = self.cur.fetchall()

        offers = []
        for r in rows:
            offer = OfferRow(*r)
            offers.append(offer)
        return offers

    def get_cottages(self, table_name):
        cottages = {}
        for offer in self.load_offers(table_name):
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

