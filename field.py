# coding=utf8


import itertools
import time
from error import *


class BaseField(object):
    """docstring for BaseField"""

    _counter = itertools.count()

    def __init__(self, **kwargs):
        object.__init__(self)
        self.null = False
        self._order = BaseField._counter.next()
        for k, v in kwargs.items():
            self[k] = v
        self._value = None

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        if self.__dict__.has_key(k):
            return self.__dict__[k]
        return None

    def __str__(self):
        return self.format()

    def default_value(self):
        return self['default']

    def value_type(self):
        raise UncompleteFieldException(self)

    def format(self, _id=''):
        s = ''
        if self['null'] is False:
            s += ' not null'
        if self['primary_key'] is True:
            s += ' primary key'
        if self['unique'] is True:
            s += ' unique'
        if self.isinstance('default', self.value_type()):
            if self.value_type() is not str:
                s += ' default ' + str(self.default_value())
            else:
                s += ' default \'%s\'' % str(self.default_value())

        return s

    def isinstance(self, k, t):
        if self[k]:
            if isinstance(self[k], t):
                return True
            raise InvalidTypeException(k, type(self[k]), t)
        return False

    def get_value(self):
        if not self._value:
            return self.default_value()
        return self._value

    def get_myvalue(self):
        """返回MySQL数据库中的类型"""
        return self.get_value()

    def set_value(self, v):
        self._value = v


    @classmethod
    def parse_operator(cls, s, v):
        """查找操作符"""
        if s == 'gt':
            return '>', v
        elif s == 'gte':
            return '>=', v
        elif s == 'lt':
            return '<', v
        elif s == 'lte':
            return '<=', v
        return '=', v


class IntegerBaseField(BaseField):
    """docstring for IntegerBaseField"""

    def format(self, _id=''):
        s = '%s %s' % (_id, self._integertype())
        if self.isinstance('max_length', int):
            s = '%s int(%d)' % (_id, self.max_length)

        if self['auto_increment'] is True:
            s += ' auto_increment'

        return s + BaseField.format(self)

    def value_type(self):
        return int


class IntegerField(IntegerBaseField):
    """docstring for IntegerField"""

    @staticmethod
    def _integertype():
        return 'int'


class BigIntegerField(IntegerBaseField):
    """docstring for BigIntegerField"""

    @staticmethod
    def _integertype():
        return 'bigint'


class DoubleField(BaseField):
    """docstring for DoubleField"""

    def __init__(self, a, b, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.a = int(a)
        self.b = int(b)
        if self.a < self.b:
            raise Exception('DoubleField: double(a,b), a must be greater than b')

    def format(self, _id):
        s = '%s double(%d, %d)' % (_id, self.a, self.b)
        return s + BaseField.format(self)


    def value_type(self):
        return float


class TimestampField(BigIntegerField):
    """docstring for TimestampField"""

    def __init__(self, **kwargs):
        super(TimestampField, self).__init__(**kwargs)

    def default_value(self):
        if self['auto'] is True:
            if not self['auto_time']:
                t = time.time()
                if self['ms'] is True:
                    t *= 1000
                self['auto_time'] = int(t)
            return self['auto_time']
        return self['default']


class BooleanField(BaseField):
    """docstring for BooleanField"""

    def format(self, _id=''):
        s = '%s tinyint(1)' % _id
        return s + BaseField.format(self)

    def value_type(self):
        return int


    def get_value(self):
        value = self._value
        if value is None:
            value = self.default_value()

        if value:
            return True
        return False

    def set_value(self, v):
        if v:
            self._value = 1
        else:
            self._value = 0


class CharField(BaseField):
    """docstring for CharField"""

    def format(self, _id=''):
        s = ''
        if not self.isinstance('max_length', int):
            pass
        s = '%s varchar(%d)' % (_id, self.max_length)

        return s + BaseField.format(self)


    def value_type(self):
        return str

    @classmethod
    def parse_operator(cls, s, v):
        """查找操作符"""
        if s == 'exact':
            return 'like', v 
        elif s == 'iexact':
            return 'ilike', v
        elif s == 'contains':
            return 'like', ('%' + v + '%')
        return BaseField.parse_operator(s, v)


class ForeignField(IntegerField):
    """docstring for Foreign"""

    def __init__(self, klass, **kwargs):
        IntegerField.__init__(self, **kwargs)
        self._klass = klass
        self._obj = None

    def format(self, _id):
        s = IntegerField.format(self, _id)
        s += ',foreign key(%s) references %s(pk)' % (_id, self._klass.__name__)
        return s


    def set_value(self, v):
        if isinstance(v, self._klass):
            self._value = v.pk
            self._obj = v
        elif isinstance(v, int) or isinstance(v,long):
            self._value = v
            if self._obj and self._obj.pk != v:
                self._obj = None
        elif isinstance(v, type(None)):
            self._value = None
            self._obj = None
        else:
            raise Exception('invalid type')


    def get_value(self):
        if self._value is None:
            return None
        if self._obj and self._obj.pk == self._value:
            return self._obj
        try:
            objs = self._klass.filter(pk=self._value)
            self._obj = objs[0]
        except:
            self._obj = None
        return self._obj

    def get_myvalue(self):
        return self._value


    @classmethod
    def parse_operator(cls, s, v):
        """查找操作符"""
        if isinstance(v, int) or isinstance(v, long):
            if s == 'pk':
                return '=', v
            elif s == 'pk__gt':
                return '>', v
            elif s == 'pk__gte':
                return '>=', v
            elif s == 'pk__lt':
                return '<', v
            elif s == 'pk__lte':
                return '<=', v
        elif s == '':
            return '=', v.pk
        raise UnsupportedOperatorException(s)


