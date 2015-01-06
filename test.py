#coding=utf8

from model import *
from field import *


# 创建好test数据库，以及相应的test帐号（或者修改setting.py）
# 然后在当前目录下执行python解释器，并且import test就会执行 测试例子


class Class(BaseModel):
    grade = IntegerField(max_length = 2)
    teacher = CharField(max_length = 50)

class Student(BaseModel):
    name = CharField(max_length = 100)
    age = IntegerField(max_length = 3, default = 20)

    klass = ForeignField(Class, null = True)

    deleted = BooleanField(default = False)

from manage import rmdb, syncdb
import sys

__module__ = sys.modules[__name__]


rmdb(__module__)
syncdb(__module__)


c = Class(grade = 1,teacher ='Good')
c.save()
s = Student(name = 'wiky',klass = c)
s.save()
s = Student(name = 'Lucy', klass = c)
s.save()
s = Student(name = 'Lily', klass = c)
s.save()

for c in Class.filter():
    print c.grade,c.teacher

s = Student.filter(klass__pk = c.pk)
for s in Student.filter(klass__pk = c.pk).order_by("-pk"):
    print s.pk,s.name,s.age,s.klass.teacher,s.deleted

s.delete()

for s in Student.filter(klass = c):
    print s.pk,s.name,s.age,s.klass.teacher,s.deleted
