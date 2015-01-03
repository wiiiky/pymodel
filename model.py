#coding=utf8


from field import *
from mysql import *
from collections import OrderedDict
from copy import copy
from inspect import isclass



class BaseModel(object):
    """docstring for BaseModel"""

    pk = IntegerField(primary_key = True,auto_increment = True)

    def __init__(self, **kwargs):
        self._fields = []
        self._fields = self.getfields()
        for k, v in self._fields:
            if issubclass(v.__class__, BaseField):
                f = copy(v)
                self.__dict__[k] = f
        for k, v in kwargs.items():
            if hasattr(self, k) :
                setattr(self, k, v)
            else:
                raise Exception('unknown field %s' % k)


    def __getattribute__(self, k):
        if k == '_fields':
            return object.__getattribute__(self,k)
        for _k, v in self._fields:
            if _k == k:
                attr = self.__dict__[k]
                return attr.get_value()
        return object.__getattribute__(self,k)


    def __setattr__(self, k, v):
        if not hasattr(self, '_fields'):
            return object.__setattr__(self, k, v)
        for _k, _v in self._fields:
            if _k == k:
                self.__dict__[k].set_value(v)
                return

        return object.__setattr__(self, k, v)

    @classmethod
    def getfields(klass):
        """初始化列"""
        fields = []
        bases = klass.__bases__
        flag = True
        while flag:
            flag = False
            for b in bases:
                if issubclass(b, BaseModel):
                    for k, v in b.__dict__.items():
                        if issubclass(v.__class__, BaseField):
                            fields.append((k, v))
                    bases = b.__bases__
                    flag = True
                    break
        for k, v in klass.__dict__.items():
            if not isclass(v) and issubclass(v.__class__, BaseField):
                fields.append((k, v))
        fields.sort(lambda x, y: x[1]._order - y[1]._order)

        return fields


    @classmethod
    def filter(klass, **kwargs):
        statement = 'select '
        allfields = klass.getfields()
        fields = []
        for k, v in allfields:
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
                setattr(c, allfields[i][0], row[i])
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
        for k, v in klass.getfields():
            cols.append(v.format(k))

        if klass.__dict__.has_key('Meta') and isclass(klass.__dict__['Meta']):
            meta = klass.__dict__['Meta']
            if meta.__dict__.has_key('abstract') and meta.__dict__['abstract'] == True:
                return
            if meta.__dict__.has_key('unique_together'):
                unique_together = list(meta.__dict__['unique_together'])
                cols.append('unique(' + ','.join(unique_together) + ')')

        statement += '(' + ','.join(cols) + ')'
        print statement

        db_execute(statement)


    def save(self):
        """保存一条记录，如果已经在则更新,如果一条记录已经存在，永远不要改变主键"""
        klass = self.__class__
        fields = klass.getfields()
        fieldnames = []
        fieldvalues = []
        for k, v in fields:
            fieldnames.append(k)
            fieldvalues.append(getattr(self, k))

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