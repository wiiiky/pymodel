#coding=utf8


class InvalidException(Exception):
    """docstring for InvalidException"""
    def __init__(self, name):
        super(InvalidException, self).__init__()
        self.name = name
        
    def __str__(self):
        return '%s is an invalid %s' % (self.name, self.type)


class InvalidRecordException(InvalidException):
    """docstring for InvalidRecordException"""
    def __init__(self, s):
        super(InvalidRowException, self).__init__(s)
        self.type = 'record';

class InvalidFieldException(InvalidException):
    """docstring for InvalidFieldException"""
    def __init__(self, s):
        super(InvalidFieldException, self).__init__(s)
        self.type = 'field'


class InvalidArgumentException(InvalidException):
    """docstring for InvalidArgumentException"""
    def __init__(self, s):
        super(InvalidArgumentException, self).__init__(s)
        self.type = 'argument'
        

class InvalidTypeException(Exception):
    """docstring for InvalidTypeException"""
    def __init__(self, k ,v , expected):
        super(InvalidTypeException, self).__init__()
        self.arg = k 
        self.type = v
        self.expected = expected


    def __str__(self):
        return '%s has an invalid type %s; expected %s' % (self.arg, str(self.type), str(self.expected))


class UncompleteFieldException(Exception):
    """docstring for UncompleteFieldException"""
    def __init__(self, obj):
        super(UncompleteFieldException, self).__init__()
        self.obj = obj


    def __str__(self):
        return '%s is an uncomplete field. should not be used directly' % self.obj.__class__.__name__


class UnsupportedOperatorException(Exception):
    """docstring for UnsupportedOperatorException"""
    def __init__(self, arg):
        super(UnsupportedOperatorException, self).__init__()
        self.arg = arg

    def __str__(self):
        return '%s is not a supported operator' % self.arg
        
        
        


        