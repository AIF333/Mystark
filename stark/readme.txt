一、组件功能；
    通过模拟django admin页面实现models类中数据页面自动显示，以及自动生成增删改查基本框架。
    并且支持自定义显示字段以及显示格式

二、操作方法:
    1.引入stark 这个app包

    2.在项目的settings下加入path配置，eg：
      path('stark/', include((V1.site.urls,'stark'),namespace="stark"))

    3.在自己的项目app目录下创建 stark.py 文件,在此文件下注册models和自定义显示的config类
      （不创建则默认用父类的显示）
      示例： myapp/stark.py
      '''
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

            # is_header 是否为表头  row 一条记录对象
            def gender_display(self,is_header=False,row=None):
                if is_header:
                    return "性别"
                else:
                    ''
                    if row.gender == 1 :
                        return "男"
                    else:
                        return "女"
                    对于 choice字段这种判断等价于 row.get_字段_display()
                    ''
                    return row.get_gender_display()

            def dp_display(self,is_header=False,row=None):
                if is_header:
                    return "部门"
                else:
                    return row.dp.title

            '''
            change_func传过去的是函数，因为在类内部，此时类还未创建，所以直接写就行
             （正常写成 UserInfoConfig.change_func）
             展示字段 不写则全字段展示，但是会存在不翻译问题，如 gender会显示0,1而不是男女 ，外键会展示 类对象，而不是 需要的字段
            '''
            list_display=['id','username','email',gender_display,dp_display]


            # 进行site注册，即往site字典里加入 models
            site.registry(models.UserInfo,UserInfoConfig)
            site.registry(models.Role)
        '''
三、实现原理：
    1.stark组件 stark/app.py 中定义 ready方法，会在项目所有的app启动时去读取解释能找到的所有stark.py文件
        def ready(self):
            #功能： 去程序中已注册的所有app(只要注册就行，不要求是只能stark这个app)目录中查找 stark.py 文件并解释
            from django.utils.module_loading import autodiscover_modules
            autodiscover_modules('stark')

    2.用户在自己的app下创建 stark.py 将会在app启动时解释该文件，因此提前生成好models的url。stark.py中需引入组件：
        from stark.service.V1 import site, StarkConfig
        其中 site 为models注册类的实例，引用的话将会按照单例模式进行，所有的注册models都会共用这一个实例。
             StarkConfig 为配置类，用户自定义展示字段和样式时需继承该类

        site注册后会在其内部字典 elf._registy 中进入如下存储，以 UserInfo 的model class为例：
        {  <class 'app01.models.UserInfo'>: <stark.service.V1.StarkConfig object at 0x0000000003D56240> }
        即 key=models.UserInfo  value=StarkConfig(models.UserInfo)

    3.根据 models.UserInfo  取出app名和表名
       app_name=models.UserInfo._meta.app_label    model_name=models.UserInfo._meta.model_name
       根据app_name/model_name 动态生成二级菜单路径  如： http://127.0.0.1:8000/stark/app01/userinfo/

    4.由于页面基本就是增删改查，所以框架里会在二级菜单路径下实现这四个url。这四个url会在StarkConfig类实现，
      即字典的vlaue：StarkConfig(models.UserInfo)
      定义增删改查的url配置，并为url取别名，方便反向解析:name=app01_userinfo_[list_add|change|del]
        pts = [
            path('', self.list_views,name=self._url_dict["list_url_alias"]),
            path('add/', self.add_views,name=self._url_dict["add_url_alias"]),
            path('<int:nid>/change/', self.change_views,name=self._url_dict["change_url_alias"]),
            path('<int:nid>/del/', self.del_views,name=self._url_dict["del_url_alias"]),
        ]
       并实现这四个基本操作的 链接方法和页面渲染。

    5.数据展示时即 list，会判断 list_display=[]  展示字段列,model_form_cls=None 表单格式类ModelForm，
      子类传入则用子类，否则用父类。
      list_display 未传入会默认取出该表所有字段进行展示，但可能会有问题，如choice字段不会展示翻译/外键关联等展示成 object
      此时用户可以自定义（参考 后面的 选择，编辑，删除三个基本操作，操作实例中也有例子）
      在编辑和新增如果需要自定义样式时可自定义样式类，并赋值给 model_form_cls 。父类默认样式如下：
            class TempModleForm(ModelForm):
                class Meta:
                    model = self.mcls
                    fields = "__all__"

    6.数据展示默认会有 选择 select，编辑 edit，删除 del三个基本操作，因此在StarkConfig里会有处理：
      list_display=["选择","传入的展示字段","编辑","删除"]
