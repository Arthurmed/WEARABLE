import MySQLdb

class Database():

    def __init__(self):

        self.db = None
        self.cur = None
        self.connected = False

    def connect_database(self, db_info ):
        self.db = MySQLdb.connect(host=str(db_info[0]),
                                    user=str(db_info[1]),
                                    passwd=str(db_info[2]),
                                    db=str(db_info[3]))
        self.cur = self.db.cursor()
        self.connected = True

    def write_data(self, data, table):

        try:
            self.cur.execute("""INSERT INTO %s VALUE %s""",(table, data))

        except:
            print ('no puedo escribir en database')