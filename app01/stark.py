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

    def gender_display(self,is_header=False,row=None):
        if is_header:
            return "性别"
        else:
            '''
            if row.gender == 1 :
                return "男"
            else:
                return "女"
            对于 choice字段这种判断等价于 row.get_字段_display()
            '''
            return row.get_gender_display()

    def dp_display(self,is_header=False,row=None):
        if is_header:
            return "部门"
        else:
            return row.dp.title
    def hobby_display(self,is_header=False,row=None):
        if is_header:
            return "爱好"
        else:
            return row.hobby.all().values_list("title")
    '''
    change_func传过去的是函数，因为在类内部，此时类还未创建，所以直接写就行
     （正常写成 UserInfoConfig.change_func）
     展示字段 不写则全字段展示，但是会存在不翻译问题，如 gender会显示0,1而不是男女 ，外键会展示 类对象，而不是 需要的字段
    '''
    list_display=['id','username','email',gender_display,dp_display]




class RoleConfig(StarkConfig):

    def change_func(self,is_header=False,row=None):
        if is_header:
            return "编辑"
        else:
            url="%s/change/"%(row.id,)
            return  mark_safe( '<a href="%s">编辑<a/>' % (url,))

    def del_func(self,is_header=False,row=None):
        if is_header:
            return "删除"
        else:
            # url="stark/%s/%s/%s/change/"%(self._app_name,self._model_name,row.id)
            url="%s/del/"%(row.id,)
            return  mark_safe( '<a href="%s">删除<a/>' % (url,))

    # list_display=['id','title',change_func,del_func] # 展示字段


# 进行site注册，即往site字典里加入 models
site.registry(models.UserInfo,UserInfoConfig)
site.registry(models.Role,RoleConfig)




