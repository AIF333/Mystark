from django.shortcuts import render,HttpResponse,redirect
from django.urls import path
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
    # 组合搜索
    comb_list=['gender','dp']

    # 搜素列
    search_list=["username","email"]

class HobbyConfig(StarkConfig):
    search_list = ["title"]

    #####################批量操作配置化#################################
    mutil_list=[
        {"func":"mutil_install","name":"批量装机"},
        {"func":"mutil_export","name":"批量导出"},
        {"func":"mutil_del","name":"批量删除"},
    ]
    def mutil_del(self,select_value,pk_list):
        print("批量删除开始")
        print(select_value)
        print(pk_list)
        obj=self.mcls.objects.filter(pk__in=pk_list)
        obj.delete()
    #####################批量操作配置化结束#################################


# 进行site注册，即往site字典里加入 models
site.registry(models.UserInfo,UserInfoConfig)
site.registry(models.Role)
site.registry(models.Department)
site.registry(models.Hobby,HobbyConfig)




