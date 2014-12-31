#coding=utf8


from field import *
from setting import *
import threading
import MySQLdb

thread_data = threading.local()


DB_NAME = None
DB_USER = None
DB_PASSWORD = None
DB_HOST = None

for k, v in MYSQL_SETTINGS.items():
    if k == 'name':
        DB_NAME = v
    elif k == 'user':
        DB_USER = v
    elif k == 'password':
        DB_PASSWORD = v
    elif k == 'host':
        DB_HOST = v

if not DB_NAME or not DB_USER or not DB_PASSWORD or not DB_HOST:
    raise Exception('MySQL setting not found')


class BaseModel:

    pk = IntegerField(primary_key = True,auto_increment = True)

    """docstring for BaseModel"""
    def __init__(self):
        self.__dict__ = {}

        self.__columns__ = {}

        bases = self.__class__.__bases__
        while bases:
            for b in bases:
                if issubclass(b, BaseModel):
                    for k, v in b.__dict__.items():
                        if issubclass(v.__class__, BaseField):
                            self.__columns__[k] = v

                    bases = b.__bases__
                    break

        for k, v in self.__class__.__dict__.items():
            if issubclass(v.__class__, BaseField):
                self.__columns__[k] = v

        for k, v in self.__columns__.items():
            self[k] = v.default_value()


    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        if self.__dict__.has_key(k):
            return self.__dict__[k]
        return None

    @staticmethod
    def get_connection():
        global DB_HOST,DB_PASSWORD,DB_USER,DB_NAME
        tdata = threading.local()
        myconn = None
        try:
            myconn = tdata.myconn
        except:
            tdata.myconn = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            tdata.myconn.autocommit(1)

        myconn = tdata.myconn
        return myconn


    def drop(self):
        statement = 'drop table if exists %s' % self.__class__.__name__

        myconn = BaseModel.get_connection()

        cursor = myconn.cursor()
        ret = cursor.execute(statement)
        cursor.close()
        return ret


    def create(self):
        myconn = BaseModel.get_connection()

        statement = 'create table %s' % self.__class__.__name__ 

        cols = []
        for k, v in self.__columns__.items():
            cols.append('%s %s' % (k, v.format()))

        statement += '(' + ','.join(cols) + ')'
        print statement

        cursor = myconn.cursor()
        ret = cursor.execute(statement)
        cursor.close()

        return ret