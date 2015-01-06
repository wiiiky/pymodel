#coding=utf8


import inspect
from model import BaseModel
from field import ForeignField


def getforeigns(cls):
    """获取一个模型中所有的外键"""
    allfields = cls.getfields()
    l = []
    for k,v in allfields.items():
        if isinstance(v, ForeignField):
            l.append(v._klass)

    return l

def modelcompare(x, y):
    """通过外键以及互相之间的依赖性确定前后关系"""
    xf = getforeigns(x)
    yf = getforeigns(y)
    if y in xf:
        return 1
    if x in yf:
        return -1
    return 0


def formodels(module, f, r=False):
    """遍历所有的数据模型"""
    l = []
    for k, v in module.__dict__.items():
        if inspect.isclass(v) and issubclass(v, BaseModel) and v is not BaseModel:
            l.append(v)
    l.sort(lambda x, y: modelcompare(x,y))
    if r:
        l.reverse()
    for v in l:
        f(v)


def syncdb(module): 
    """module是定义了数据模型的模块,syncdb将创建所有的数据表"""
    formodels(module,lambda v: v.create())


def rmdb(module):
    """module是定义了数据模型的模块,rmdb将删除所有的数据表"""
    formodels(module,lambda v: v.drop(), True)