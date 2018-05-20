import sqlite3


class Sqlitemanager(dbmanager.DbManager):
    def __init__(self):
        self.conn = sqlite3.connect('warehouse.sqlite')
        self._isConnected = True

    def connect(self):
        if(not self._isConnected):
            self.conn = sqlite3.connect('warehouse.sqlite')

