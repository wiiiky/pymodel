#coding=utf8


from field import *
from mysql import *


class BaseModel(object):
    """docstring for BaseModel"""

    pk = IntegerField(primary_key = True,auto_increment = True)

    _fields = []

    def __init__(self):
        for k, v in self._getfields():
            self[k] = v.default_value()

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__[k]


    @classmethod
    def _getfields(klass):
        """初始化列"""
        if not klass._fields:
            bases = klass.__bases__
            flag = True
            while flag:
                flag = False
                for b in bases:
                    if issubclass(b, BaseModel):
                        for k, v in b.__dict__.items():
                            if issubclass(v.__class__, BaseField):
                                klass._fields.append((k, v))
                        bases = b.__bases__
                        flag = True
                        break
            for k, v in klass.__dict__.items():
                if issubclass(v.__class__, BaseField):
                    klass._fields.append((k, v))
            klass._fields.sort(lambda x, y: x[1]._order - y[1]._order)

        return klass._fields


    @classmethod
    def filter(klass, **kwargs):
        statement = 'select '
        fields = []
        for k, v in klass._getfields():
            fields.append(k)

        statement += ','.join(fields) + ' from ' + klass.__name__

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
            c = klass()
            for i in range(0, len(row)):
                c[klass._fields[i][0]] = row[i]
            l.append(c)

        return l

    @classmethod
    def drop(klass):
        statement = 'drop table if exists %s' % klass.__name__

        db_execute(statement)


    @classmethod
    def create(klass):
        statement = 'create table %s' % klass.__name__ 

        cols = []
        for k, v in klass._getfields():
            cols.append(v.format(k))

        statement += '(' + ','.join(cols) + ')'
        print statement

        db_execute(statement)


    def save(self):
        """保存一条记录，如果已经在则更新,如果一条记录已经存在，永远不要改变主键"""
        klass = self.__class__
        fields = klass._getfields()
        fieldnames = []
        fieldvalues = []
        for k, v in fields:
            fieldnames.append(k)
            fieldvalues.append(self[k])

        if self.pk is None: # insert
            statement = 'insert into ' + klass.__name__
            statement +='(' + ','.join(fieldnames) + ')'
            statement += ' values(' + ('%s,' * len(fieldnames))[:-1] + ')'
            self.pk = db_execute(statement, fieldvalues, lastrowid = True)
        else:               # update
            statement = 'update ' + klass.__name__
            fieldset = []
            for k in fieldnames:
                fieldset.append(k + '=%s')
            statement += ' set ' + ','.join(fieldset)
            statement += ' where pk=' + str(self.pk)
            db_execute(statement, fieldvalues)