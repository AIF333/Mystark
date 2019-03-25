# stark 配置
from types import FunctionType,MethodType

from django.shortcuts import render,HttpResponse,redirect
from django.urls import path, reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from app01 import models

# path 的一级分发的namespace

class StarkConfig(object):
    '''
     封装单独的 数据库操作类
    '''
    # /展示的字段
    list_display=[]

    def __init__(self,mcls):
        self.mcls=mcls

        self._app_name = self.mcls._meta.app_label
        self._model_name = self.mcls._meta.model_name

        # 将增删改查的四个 url地址 别名，以及用来反向查询url的全量表示 namespace:name 放在初始化信息中，方便后面调用
        self._url_dict={
            "list_url_alias":"%s_%s_list" %(self._app_name,self._model_name) ,
            "add_url_alias":"%s_%s_add" %(self._app_name,self._model_name) ,
            "change_url_alias":"%s_%s_change" %(self._app_name,self._model_name) ,
            "del_url_alias":"%s_%s_del" %(self._app_name,self._model_name) ,
            "list_url":"stark:%s_%s_list" %(self._app_name,self._model_name) ,
            "add_url":"stark:%s_%s_add" %(self._app_name,self._model_name) ,
            "change_url":"stark:%s_%s_change" %(self._app_name,self._model_name) ,
            "del_url":"stark:%s_%s_del" %(self._app_name,self._model_name) ,
        }

    # 定义编辑字段和对应的url
    def change_func(self,is_header=False,row=None):
        if is_header:
            return "编辑"
        else:
            url="%s/change/"%(row.id,)
            return  mark_safe( '<a href="%s">编辑<a/>' % (url,))

    # 定义 删除字段和对应的url
    def del_func(self,is_header=False,row=None):
        if is_header:
            return "删除"
        else:
            # url="stark/%s/%s/%s/change/"%(self._app_name,self._model_name,row.id)
            url="%s/del/"%(row.id,)
            return  mark_safe( '<a href="%s">删除<a/>' % (url,))

    # 定义增删改查四个url  二级页面的路径前面需要加/ ，如 /add/
    @property
    def urls(self):

        pts = [
            path('', self.list_views,name=self._url_dict["list_url_alias"]),
            path('add/', self.add_views,name=self._url_dict["add_url_alias"]),
            path('<int:nid>/change/', self.change_views,name=self._url_dict["change_url_alias"]),
            path('<int:nid>/del/', self.del_views,name=self._url_dict["del_url_alias"]),
        ]

        pts.extend(self.extend_url())  # 拓展除了增删改查基本外的url
        return pts,None,None

    def extend_url(self):
        '''
        拓展基本的四个二级url，如果还有其他如导出，报表等路径，可在子类中实现
        :param path_list:
        :return:
        '''
        path_list=[]
        return list(path_list)

    @property # 获取类的 ModelForm
    def getModelForm(self):
        class TempModleForm(ModelForm):
            class Meta:
                model = self.mcls
                fields = "__all__"
        return TempModleForm

    # 视图函数至少有一个 request 参数
    def list_views(self,request):
        if request.method=="GET":
            list_obj=self.mcls.objects.all() # 获取表中所有记录

            # 如果用户未传入list_display 则默认展示全字段，并添加 编辑和删除功能,需注意区分函数和方法
            '''
            函数：1.定义在类外的都是函数      2.通过类调用的  Foo.func 也是函数，在调用时 self，需人工传入
            方法：通过实例（对象调用）的类的obj.func 就都是方法,方法里的self 不用再传入，会自动将 obj当做self传递
            '''
            if not self.list_display:
                self.list_display=[ self.mcls._meta.fields[i].name for i in range(len(self.mcls._meta.fields)) ]
                self.list_display.append(self.change_func)
                self.list_display.append(self.del_func)

            # 获取字段的 verbose_name
            head_list=[]
            for col in self.list_display:
                if isinstance(col,FunctionType): # 如果是用户重写传入的 方法
                    temp=col(self,is_header=True)
                elif isinstance(col,MethodType): # 如果是 类内部定义的方法
                    temp=col(is_header=True)
                else: # 如果是字符串，即表自身字段
                    temp=self.mcls._meta.get_field(col).verbose_name
                head_list.append(temp)

            # 将表记录取出放在列表中然后传入到前端，不能直接在前端用 obj.col ,这个会报错，因为 obj是动态的，col也是动态的
            data_list=[]
            for row in list_obj:
                temp=[]
                for col in self.list_display:
                    if isinstance(col,FunctionType): # 如果是用户重写传入的 方法
                        val = col(self,row=row)
                    elif isinstance(col,MethodType): # 如果是 类内部定义的方法
                        val = col(row=row)
                    else:  # 如果是字符串，即表自身字段
                        val=getattr(row, col)
                    temp.append(val)
                data_list.append(temp)

            add_url=reverse(self._url_dict["add_url"])
            return render(request,"list_views.html",{"data_list":data_list,"head_list":head_list,
                        "add_url": add_url})

    def add_views(self,request):

        if request.method=="GET":
            form=self.getModelForm
            return render(request,"add_views.html",{"form":form})
        else:
            form=self.getModelForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(reverse(self._url_dict["list_url"]))
            return render(request,"add_views.html",{"form":form})

        return HttpResponse("增加页面")


    def change_views(self,request,nid):

        obj = self.mcls.objects.filter(id=nid).first()

        form = self.getModelForm(instance=obj)
        if request.method=="GET":
            return render(request,"change_views.html",{'form':form})
        else:
            form = self.getModelForm(data=request.POST,instance=obj)
            if form.is_valid():
                form.save()
            return redirect(reverse(self._url_dict["list_url"]))

    def del_views(self,request,nid):
        filter_obj = self.mcls.objects.filter(id=nid)
        # 这里直接删除
        if filter_obj:
            filter_obj.delete()
        return redirect(reverse(self._url_dict["list_url"]))

# 定义字典来存储 models类
class StarkSite(object):
    '''
     用于封装所有的 数据库操作类
    '''
    def __init__(self):
        self._registy={}

    # 功能：将models 当做字典的key，同时字典的value 是封账了models的类对象实例
    # 这里 models 实际指的是 models.表名，如 models.Blog ,这个能作为字典的key，
    # 也说明了它是能hash的
    def registry(self,models,ClsConfig=None):
        '''
        :param models:  传入的models下的表对象，如 models.Blog
        :return: 无

        self._registy: {  <class 'app01.models.UserInfo'>: <stark.service.V1.StarkConfig object at 0x0000000003D56240> }
        '''
        if not ClsConfig:
            ClsConfig=StarkConfig
        self._registy[models]=ClsConfig(models)

    # 获取类，自动生成 path(url)添加都列表
    def get_urls(self):
        pts = []
        # pts.append(path('login/', self.login))
        # 循环变量类的字典 生成 path，key:数据库操作类  value：一个操作类对象
        '''
        path 和 url 第二个参数要的都是元祖，并且元祖可以递级，eg:
        path(    'idx1',  ([path(...),path(...),],appNone,nameNone)    )

        '''
        for model_class,model_obj in self._registy.items():
            app_name=model_class._meta.app_label
            model_name=model_class._meta.model_name
            temp = path('%s/%s/' % (app_name, model_name), model_obj.urls)
            pts.append(temp)

        return pts
    @property # property装饰器能将函数当做变量一样访问
    def urls(self):
        '''
        返回 所有注册的类自动生成的url元祖
        '''
        return self.get_urls()

    def login(self,request):
        return HttpResponse("登录页面")

# 实例化一个site ，这里利用了单列模型，site生成后就不会再重复生成，也利用了字典的可变性
# 实现对 models 的添加，也是一种程序内部的数据交换方式
site=StarkSite()