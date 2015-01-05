from model import *
from field import *



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

for c in Class.filter():
    print c.grade,c.teacher

for s in Student.filter(klass__pk = c.pk):
    print s.name,s.age,s.klass.teacher,s.deleted


for s in Student.filter(klass = c):
    print s.name,s.age,s.klass.teacher,s.deleted
