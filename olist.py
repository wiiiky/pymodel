#coding=utf8


from mysql import *
from error import InvalidTypeException


class ObjectList(object):
    """docstring for ObjectList"""
    def __init__(self, klass, statement, args, allfields):
        super(ObjectList, self).__init__()
        self._klass = klass
        self._statement = statement
        self._args = args
        self._allfields = allfields
        self._orderby = 'order by pk'   # default
        self._limit = ''

        self._list = None
        self._iter = 0

    def __getitem__(self, i):
        if not (isinstance(i, int) or isinstance(i, long)):
            raise InvalidTypeException('index', type(i), int)
        self.check()        # 第一次引用的时候才真正查询数据库

        return self._list[i]

    def __str__(self):
        self.check()
        return str(self._list)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        self.check()
        self._iter = 0
        return self

    def __len__(self):
        self.check()
        return len(self._list)

    def next(self):
        if self._iter >= len(self._list):
            raise StopIteration
        v = self._list[self._iter]
        self._iter += 1
        return v

    def check(self):
        if self._list is None:
            self.execute()

    def execute(self):
        statement = '%s %s %s' % (self._statement, self._orderby, self._limit)
        args = self._args
        rows = db_execute(statement, args)
        self._list = []
        for row in rows:
            c = self._klass()
            i = 0
            for k, v in self._allfields.items():
                setattr(c, k, row[i])
                i += 1
            self.append(c)

    def append(self, v):
        self._list.append(v)

    def order_by(self, order):
        if order.startswith('-'):
            self._orderby = ' order by %s desc' % order[1:]  
        else:
            self._orderby = ' order by %s' % order  
        return self

    def limit(self, lmt):
        self._limit = ' limit %d' % lmt
        return self

    def count(self):
        return self.__len__()


    def filter(self, **kwargs):
        args = []
        where = None
        if len(kwargs) > 0:
            where = []
            allfields = self._klass.getfields()
            for k, v in kwargs.items():
                k, operator = self._klass.parse_argumnent(k)
                operator, v, st = allfields[k].parse_operator(operator, v)
                if not st:
                    where.append('%s %s %%s' % (k, operator))
                else:
                    where.append('%s %s %s' % (k, operator, st))
                args.extend(v)
        if where:
            if 'where' in self._statement:
                self._statement += ' and '
            else:
                self._statement += ' where '
            self._statement += ' and '.join(where)
            self._args.extend(args)

        return self
