#coding=utf8


from field import *
from mysql import *


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

        rows = db_execute(statement,args)
        l = []
        for row in rows:
            c = self.__class__()
            for i in range(0, len(row)):
                c[self._fields[i][0]] = row[i]
            l.append(c)

        return l

    def drop(self):
        statement = 'drop table if exists %s' % self.__class__.__name__

        db_execute(statement)


    def create(self):
        statement = 'create table %s' % self.__class__.__name__ 

        cols = []
        for k, v in self._fields:
            cols.append(v.format(k))

        statement += '(' + ','.join(cols) + ')'
        print statement

        db_execute(statement)