import pymysql
import sqlite3
class ItemDict(dict):
    _keys = {'epc':'varchar(50)', 'product':'varchar(20)', 'Location':'varchar(20)', 'hasCheckOut': 'int'}
    def __init__(self, *args):
        return

    def __setitem__(self, key, val):
        if key not in self._keys:
            raise KeyError
        dict.__setitem__(self, key, val)
        return

class ProductDict(dict):
    _keys = {'name':'varchar(30)'}
    def __init__(self, *args):
        return

    def __setitem__(self, key, val):
        if key not in self._keys:
            raise KeyError
        dict.__setitem__(self, key, val)
        return

class EPCDict(dict):
    _keys = {'epc':'varchar(24)'}
    def __init__(self, *args):
        return

    def __setitem__(self, key, val):
        if key not in self._keys:
            raise KeyError
        dict.__setitem__(self, key, val)
        return

class DbManager:
    _cx = 0
    _isConnected = False
    def __enter__(self):
        return self

    def __exit__(self):
        self._cx.close()
    def __init__(self, un, pw, host, db):

        self.un =  un
        self.pw = pw
        self.host = host
        self.db = db

        '''
            Create table first at the start
        '''

        startQuery  = "CREATE TABLE IF NOT EXISTS "

        """
        if(self.connect() == 0):
            query = "CREATE TABLE IF NOT EXISTS products(name varchar(30) unique, id int(11) auto_increment primary key)"
            self.executeCustomQuery(query)
            query = "CREATE TABLE IF NOT EXISTS items(epc varchar(50))"

        """
        return;

    def connect(self):
        if (self._isConnected == False):
            try:
                self._cx = pymysql.connect(user=self.un, password=self.pw,
                        host=self.host , database=self.db)
                self._isConnected = True
                return 0
            except pymysql.Error as err:
                if err.args[0]== 1045: #wrong un pw
                    print("Something is wrong with your user name or password")
                elif err.args[0]== 1049: #non-existent db
                    print("Database does not exist")
                else:
                    print(err)
                return -1


    def executeCustomQuery(self, query):
        if (self._isConnected == True):
            with self._cx.cursor(pymysql.cursors.DictCursor) as cursor:
                print(query)
                cursor.execute(query)
                result = cursor.fetchall()
                print(result)
                self._cx.commit()

                return (cursor.rowcount, result)
        else:
            print("Not connected to DB!")
            return (-1, ())

    def selectFrom(self, table, column={'*'}, where=''):
        if (self._isConnected == True):
            with self._cx.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "select {}  from {} {}" \
                    .format(",".join("{}".format(key) for key in column) \
                        , table \
                        ,where)

                cursor.execute(sql)
                result = cursor.fetchall()
                self._cx.commit()

                return result
        else:
            print("Not connected to DB!")
            return -1

    def getAll(self, orderby=''):
        if (self._isConnected == True):
            with self._cx.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "select r.title as Title, a.name as Author, t.name as Tag, f.name as Field from \
                        author a \
                        left join research r \
                        on a.researchid=r.title \
                        left join tag t  \
                        on r.tagid=t.name \
                        left join field f  \
                        on t.fieldid=f.name \
                        {}".format(orderby)
                cursor.execute(sql)
                result = cursor.fetchall()
                self._cx.commit()

                return (cursor.rowcount, result)
        else:
            print("Not connected to DB!")
            return (-1, ())

    def getAllWhere(self, where):
        if (self._isConnected == True):
            with self._cx.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "select EPC, Product, Location, count(Location) as Quantity from items where  {} group by EPC, Product, Location".format(where)
                cursor.execute(sql)
                result = cursor.fetchall()
                self._cx.commit()

                return (cursor.rowcount, result)
        else:
            print("Not connected to DB!")
            return (-1,())

    def AddToTable(self, table, item):
        if (self._isConnected == True):
            try:
                with self._cx.cursor() as cursor:
                    sql = "INSERT INTO {} ({}) VALUES ( {} )" \
                        .format(table \
                            , ",".join("{}".format(key) for key,val in item.items()) \
                            , ",".join("\"{}\"".format(val) for key, val in item.items()))

                    cursor.execute(sql)
                    self._cx.commit()

                return cursor.rowcount
            except pymysql.err.IntegrityError as err:
                print("Insertion failed: ", err)
                return -1
        return 0

    def deleteFromTable(self, table, column, value):
        if (self._isConnected == True):
            try:
                with self._cx.cursor() as cursor:
                    sql = "delete from {} where {} = \"{}\"".format(table, column, value)
                    cursor.execute(sql)
                    self._cx.commit()

                return (cursor.rowcount, "")
            except pymysql.err.IntegrityError as err:
                print("Deletion failed: ", err)
                if (1451 == err.args[0]):
                    return(-1, "Cannot delete! {} from {} is in use.".format(value, table))
                return (-1, "Error!")
        return (-1, "Error!")

    def updateInTable(self, table, column, value, cond_col, cond_value):
        if (self._isConnected == True):
            try:
                with self._cx.cursor() as cursor:
                    sql = "update {} set {}=\"{}\" where {} = \"{}\"".format(table, column, value, cond_col, cond_value)
                    cursor.execute(sql)
                    self._cx.commit()

                return cursor.rowcount
            except pymysql.err.IntegrityError as err:
                print("Insertion failed: ", err)
                return -1
        return -1

    def fetchFromTable(self, table):
        if (self._isConnected == True):
            try:
                with self._cx.cursor(pymysql.cursors.DictCursor) as cursor:
                    sql = "select * from {}".format(table)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    self._cx.commit()
                    print(result)
                    return (cursor.rowcount, result)
            except pymysql.err.IntegrityError as err:
                print("Fetch failed: ", err)
                return (-1, ())
        return (-1,())

    def populatedb(self):
        return
