# coding=utf8


from field import *
from mysql import *
from collections import OrderedDict
from copy import copy
from inspect import isclass
from olist import ObjectList
from error import InvalidFieldException, InvalidRecordException, InvalidArgumentException


class BaseModel(object):
    """docstring for BaseModel"""

    pk = IntegerField(primary_key=True, auto_increment=True)

    def __init__(self, **kwargs):
        self._fields = self.getfields()
        for k, v in self._fields.items():
            if issubclass(v.__class__, BaseField):
                self.__dict__[k] = copy(v)
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise InvalidFieldException(k)


    def __getattribute__(self, key):
        if key == '_fields':
            return object.__getattribute__(self, key)
        if hasattr(self,'_fields') and self._fields.has_key(key):
            attr = self.__dict__[key]
            return attr.get_value()
        return object.__getattribute__(self, key)


    def __setattr__(self, k, v):
        if not hasattr(self, '_fields'):
            return object.__setattr__(self, k, v)
        if self._fields.has_key(k):
            self.__dict__[k].set_value(v)
            return

        return object.__setattr__(self, k, v)

    @classmethod
    def getfields(cls):
        """获取所有的列（按声明顺序）"""
        fields = []
        bases = cls.__bases__
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
        for k, v in cls.__dict__.items():
            if not isclass(v) and issubclass(v.__class__, BaseField):
                fields.append((k, v))
        fields.sort(lambda x, y: x[1]._order - y[1]._order)

        od = OrderedDict()
        for k, v in fields:
            od[k] = v

        return od

    @staticmethod
    def parse_argumnent(arg):
        i = arg.find('__')
        if i>0:
            return arg[:i], arg[i+2:]
        elif i<0:
            return arg, ''
        raise InvalidArgumentException(arg)

    @classmethod
    def filter(cls, **kwargs):
        statement = 'select '
        allfields = cls.getfields()
        fields = []
        for k, v in allfields.items():
            fields.append(k)

        statement += ','.join(fields) + ' from ' + cls.__name__

        args = []
        where = None
        if len(kwargs) > 0:
            where = []
            for k, v in kwargs.items():
                k, operator = cls.parse_argumnent(k)
                operator, v = allfields[k].parse_operator(operator, v)
                where.append('%s %s %%s' % (k, operator))
                args.append(v)
        if where:
            statement += ' where ' + ' and '.join(where)

        rows = db_execute(statement, args)
        l = ObjectList()
        for row in rows:
            c = cls()
            i = 0
            for k, v in allfields.items():
                setattr(c, k, row[i])
                i += 1
            l.append(c)

        return l

    @classmethod
    def all(cls):
        """获取所有的记录,filter的简单封装"""
        return cls.filter()

    @classmethod
    def get(cls,**kwargs):
        """获取当个记录，如果没有找到返回None"""
        objs = cls.filter(**kwargs)
        if len(objs)>0:
            return objs[0]
        return None


    @classmethod
    def drop(cls):
        statement = 'drop table if exists %s' % cls.__name__

        db_execute(statement)


    @classmethod
    def create(cls):
        statement = 'create table %s' % cls.__name__

        cols = []
        for k, v in cls.getfields().items():
            cols.append(v.format(k))

        if cls.__dict__.has_key('Meta') and isclass(cls.__dict__['Meta']):
            meta = cls.__dict__['Meta']
            if meta.__dict__.has_key('abstract') and meta.__dict__['abstract'] == True:
                return
            if meta.__dict__.has_key('unique_together'):
                unique_together = list(meta.__dict__['unique_together'])
                cols.append('unique(' + ','.join(unique_together) + ')')

        statement += '(' + ','.join(cols) + ')'
        print statement

        db_execute(statement)


    def save(self):
        """保存一条记录，如果已经在则更新;如果一条记录已经存在，永远不要改变主键"""
        klass = self.__class__
        fields = self._fields
        fieldnames = []
        fieldvalues = []
        for k, v in fields.items():
            fieldnames.append(k)
            fieldvalues.append(self.__dict__[k].get_myvalue())  # 这里要获取MySQL对应的数据值

        if self.pk is None:  # insert
            statement = 'insert into ' + klass.__name__
            statement += '(' + ','.join(fieldnames) + ')'
            statement += ' values(' + ('%s,' * len(fieldnames))[:-1] + ')'
            self.pk = db_execute(statement, fieldvalues, lastrowid=True)
        else:  # update
            statement = 'update ' + klass.__name__
            fieldset = []
            for k in fieldnames:
                fieldset.append(k + '=%s')
            statement += ' set ' + ','.join(fieldset)
            statement += ' where pk=' + str(self.pk)
            db_execute(statement, fieldvalues)


    def delete(self):
        """删除记录"""
        if self.pk is None:
            raise InvalidRecordException('')
        statement = 'delete from %s where pk = %%s' % self.__class__.__name__
        values = [self.pk]

        db_execute(statement, values)