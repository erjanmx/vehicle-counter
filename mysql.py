import MySQLdb

class mysql:
    cfg_mysql_host = 'localhost'
    cfg_mysql_database = ''
    cfg_mysql_username = ''
    cfg_mysql_password = ''

    def __init__(self):
        self.db = MySQLdb.connect(self.cfg_mysql_host, self.cfg_mysql_username, self.cfg_mysql_password,
                               self.cfg_mysql_database)

    def execute(self, query):
        cur = self.db.cursor()
        cur.execute(query)
        self.db.commit()
        res = []
        i = 0
        for row in cur.fetchall():
            res[i] = row
            i += 1

        return res

    def insert(self, direction):
        sql = 'INSERT INTO crosses (direction) values (' + direction + ')'
        return self.execute(sql)

