#coding=utf8


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


def db_reconnect():
    global DB_HOST,DB_PASSWORD,DB_USER,DB_NAME
    tdata = threading.local()
    try:
        tdata.myconn = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        tdata.myconn.autocommit(1)
    except:
        tdata.myconn = None
    return tdata.myconn


def db_connection():
    """threading.local()线程专有数据"""
    global DB_HOST,DB_PASSWORD,DB_USER,DB_NAME
    tdata = threading.local()
    myconn = None
    try:
        myconn = tdata.myconn
    except:
        myconn = db_reconnect()

    return myconn

def db_execute(statement, args=None, **kwargs):
    myconn = db_connection()

    for i in range(0, 2):
        ret = None
        try:
            cursor = myconn.cursor()
            cursor.execute(statement, args)
            if ('lastrowid', True) in kwargs.items():
                ret = cursor.lastrowid
            else:
                ret = cursor.fetchall()
            cursor.close()
        except MySQLdb.OperationalError as e:
            myconn = db_reconnect()
            continue
        except Exception as e:
            raise Exception('%s: %s' % (statement, str(e)))
        return ret

    raise Exception('%s: %s' % (statement, str(e)))