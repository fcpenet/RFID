import pymysql
import tkinter
import configreader

cr = configreader.ConfigReader()

cr.readconfig()
"""
    CREATE CONFIG FILE
    READ CONFIG FILE
    MANAGE DATABASE
    CREATE QUERIES/STORED PROCEDUCRES
    CREATE GUI
"""


try:
    cx = pymysql.connect(user=cr.username, password=cr.pw, host=cr.host ,database=cr.db)
except pymysql.Error as err:
    if err.args[0]== 1045: #wrong un pw
        print("Something is wrong with your user name or password")
    elif err.args[0]== 1049: #non-existent db
        print("Database does not exist")
    else:
         print(err)
else:
    cx.close()

'''for GUI '''
#top = tkinter.Tk()
#top.mainloop()
