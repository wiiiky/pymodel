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


class BaseModel(object):
    """docstring for BaseModel"""

    pk = IntegerField(primary_key = True,auto_increment = True)

    def __init__(self):
        self._fields = []   # 记录列名以及类型

        bases = self.__class__.__bases__
        flag = True
        while flag:
            flag = False
            for b in bases:
                if issubclass(b, BaseModel):
                    for k, v in b.__dict__.items():
                        if issubclass(v.__class__, BaseField):
                            self._fields.append((k,v))

                    bases = b.__bases__
                    flag = True
                    break

        for k, v in self.__class__.__dict__.items():
            if issubclass(v.__class__, BaseField):
                self._fields.append((k,v))

        self._fields.sort(lambda x, y : x[1]._order - y[1]._order)
        for k, v in self._fields:
            self[k] = v.default_value()

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self[k]

    def filter(self, **kwargs):
        statement = 'select '
        fields = []
        for k, v in self._fields:
            fields.append(k)

        statement += ','.join(fields) + ' from ' + self.__class__.__name__

        args = []
        where = None
        if len(kwargs)>0:
            where = []
            for k, v in kwargs.items():
                where.append('%s = %%s' % k)
                args.append(v)
        if where:
            statement += ' where ' + ' and '.join(where)

        rows = BaseModel.db_execute(statement,args)
        l = []
        for row in rows:
            c = self.__class__()
            for i in range(0, len(row)):
                c[self._fields[i][0]] = row[i]
            l.append(c)

        return l

    def drop(self):
        statement = 'drop table if exists %s' % self.__class__.__name__

        BaseModel.db_execute(statement)


    def create(self):
        statement = 'create table %s' % self.__class__.__name__ 

        cols = []
        for k, v in self._fields:
            cols.append(v.format(k))

        statement += '(' + ','.join(cols) + ')'
        print statement

        BaseModel.db_execute(statement)


    @staticmethod
    def db_connection():
        """threading.local()线程专有数据"""
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