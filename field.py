#coding=utf8



class BaseField:
    """docstring for BaseField"""
    def __init__(self, **kwargs):
        self.null = False
        for k, v in kwargs.items():
            self[k] = v

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

    def format(self, _id = ''):
        s = ''
        if self['null'] == False:
            s += ' not null'
        if self['primary_key'] == True:
            s += ' primary key'
        if self['unique'] == True:
            s += ' unique'
        if self.isinstance('default', self.value_type()):
            if self.value_type() is not str:
                s += ' default ' + str(self.default_value())
            else:
                s += ' default \'%s\'' % str(self.default_value())

        return s

    def isinstance(self, k , t):
        if self[k]:
            if isinstance(self[k], t):
                return True
            self.exception('%s must be type %s' % (k, str(t)))
        return False

    def klass_name(self):
        return self.__class__.__name__

    def exception(self, s):
        raise Exception('%s: %s' % (self.klass_name(), s))



class IntegerField(BaseField):
    """docstring for IntegerField"""

    def format(self, _id = ''):
        s = '%s int' % _id
        if self.isinstance('max_length', int):
            s = '%s int(%d)' % (_id, self.max_length)

        if self['auto_increment'] == True:
            s += ' auto_increment'

        return s + BaseField.format(self)


    def value_type(self):
        return int


class CharField(BaseField):
    """docstring for CharField"""

    def format(self, _id = ''):
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
        
        


        
