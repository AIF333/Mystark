# print("app01:stark.py 执行")
from django.shortcuts import render,HttpResponse,redirect
from django.urls import path
from django.utils.safestring import mark_safe

from stark.service.V1 import site, StarkConfig
from app01 import models

# 自定义UserInfo的配置类
class UserInfoConfig(StarkConfig):

    def extend_url(self): # 扩展字段方法
        path_list=[
            path('sayHi/', self.sayHi),
        ]
        return path_list

    def sayHi(self,request):
        return HttpResponse("Hi!")

    def change_func(self,is_header=False,row=None):
        if is_header:
            return "编辑"
        else:
            # url="stark/%s/%s/%s/change/"%(self._app_name,self._model_name,row.id)
            url="%s/change/"%(row.id,)
            return  mark_safe( '<a href="%s">编辑<a/>' % (url,))

    def del_func(self,is_header=False,row=None):
        if is_header:
            return "删除"
        else:
            # url="stark/%s/%s/%s/change/"%(self._app_name,self._model_name,row.id)
            url="%s/del/"%(row.id,)
            return  mark_safe( '<a href="%s">删除<a/>' % (url,))

    list_display=['id','username','email',change_func,del_func] # 展示字段


# 进行site注册，即往site字典里加入 models
site.registry(models.UserInfo,UserInfoConfig)
site.registry(models.Role)




