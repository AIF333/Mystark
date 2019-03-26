from django.test import TestCase

# # Create your tests here.
# import os, django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Mystark.settings")
# django.setup()
#
#
# from app01 import models
# print(models.UserInfo)
#
# print("11111")


# class Foo():
#     instance=None
#
#     @staticmethod
#     def getInstance():
#         if not  Foo.instance:
#             Foo.instance=Foo()
#         return Foo.instance
# a=Foo().getInstance()
# b=Foo().getInstance()
# print(a,b)

# class Singleton(object):
#     #如果该类已经有了一个实例则直接返回,否则创建一个全局唯一的实例
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls,'_instance'):
#             cls._instance = super(Singleton,cls).__new__(cls)
#         return cls._instance
#
# class MyClass(Singleton):
#     def __init__(self,name):
#         if name:
#             self.name = name
#
# a = MyClass('a')
# print(a)
# print(a.name)
#
# b = MyClass('b')
# print(b)
# print(b.name)
#
# print(a)
# print(a.name)

#
# def foo():
#     pass
#
# class Coo():
#     def foo(self):
#         pass
#
# print(type(foo))
# print(type(Coo().foo))
# print(type(Coo.foo))

