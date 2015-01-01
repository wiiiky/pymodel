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

    def drop(self):
        statement = 'drop table if exists %s' % self.__class__.__name__

        BaseModel.db_execute(statement)


    def create(self):
        statement = 'create table %s' % self.__class__.__name__ 

        cols = []
        for k, v in self.__columns__.items():
            cols.append(v.format(k))

        statement += '(' + ','.join(cols) + ')'
        print statement

        BaseModel.db_execute(statement)


    @staticmethod
    def db_connection():
        global DB_HOST,DB_PASSWORD,DB_USER,DB_NAME
        tdata = threading.local()
        myconn = None
        try:
            myconn = tdata.myconn
        except:
            myconn = BaseModel.db_reconnect()

        return myconn

    @staticmethod
    def db_reconnect():
        global DB_HOST,DB_PASSWORD,DB_USER,DB_NAME
        tdata = threading.local()
        try:
            tdata.myconn = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            tdata.myconn.autocommit(1)
        except:
            tdata.myconn = None
        return tdata.myconn

    @staticmethod
    def db_execute(statement, args=None):
        myconn = BaseModel.db_connection()

        for i in range(0, 2):
            try:
                cursor = myconn.cursor()
                cursor.execute(statement, args)
                rows = cursor.fetchall()
                cursor.close()
            except MySQLdb.OperationalError as e:
                myconn = BaseModel.db_reconnect()
                continue
            return rows

        raise Exception('db_execute fails')