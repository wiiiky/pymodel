# coding=utf8


import itertools
import time


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
        self.exception('uncompleted')

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
            self.exception('%s must be type %s' % (k, str(t)))
        return False

    def get_value(self):
        if not self._value:
            return self.default_value()
        return self._value

    def set_value(self, v):
        self._value = v

    def exception(self, s):
        raise Exception('%s: %s' % (self.__class__.__name__, s))


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
            raise Exception('CharField')
        s = '%s varchar(%d)' % (_id, self.max_length)

        return s + BaseField.format(self)


    def value_type(self):
        return str


class ForeignField(IntegerField):
    """docstring for Foreign"""

    def __init__(self, klass, **kwargs):
        IntegerField.__init__(self, **kwargs)
        self.klass = klass

    def format(self, _id):
        s = IntegerField.format(self, _id)
        s += ',foreign key(%s) references %s(pk)' % (_id, self.klass.__name__)
        return s
