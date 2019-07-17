import MySQLdb


class SQL_Handler:
    def __init__(self):
        self.con = MySQLdb.connect(host='localhost', user='root', password='password', db='cottages', charset='utf8', use_unicode=True)
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
