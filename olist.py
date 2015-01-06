#coding=utf8


from error import InvalidTypeException


class ObjectList(object):
    """docstring for ObjectList"""
    def __init__(self):
        super(ObjectList, self).__init__()
        self.list = []
        self.iter = 0

    def __getitem__(self, i):
        if not (isinstance(i, int) or isinstance(i, long)):
            raise InvalidTypeException('index', type(i), int)
        return self.list[i]

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        self.iter = 0
        return self

    def __len__(self):
        return len(self.list)

    def next(self):
        if self.iter >= len(self.list):
            raise StopIteration
        v = self.list[self.iter]
        self.iter += 1
        return v

    def append(self, v):
        self.list.append(v)

    def order_by(self, order):
        if order.startswith('-'):
            key = lambda x : - getattr(x, order[1:])
        else:
            key = lambda x : getattr(x, order)
        self.list.sort(key = key)
        return self
