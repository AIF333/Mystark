# stark 配置
from types import FunctionType,MethodType

from django.shortcuts import render,HttpResponse,redirect
from django.urls import path, reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from stark.utils.pagination import Pageination # 分页组件

# path 的一级分发的namespace

# list_views的工厂类，因为列表页面的代码太多，全部放在工厂类里
class FacListViews():
    '''分页功能'''

    # 分页对象
    page_obj = None
    def __init__(self,config,queryResult,request):
        '''
        :param config: 原类的实例，即StarkConfig的self
        :param queryResult: 表的查询结果querySet类型,如 models.Student.objects.all()

        '''
        self.config=config
        self.queryResult=queryResult
        self.request=request

    # 初始化分页对象，这个需要先执行
    def init_page_obj(self):
        pagedict = {}
        pagedict["url"] = self.request.path_info # request.path_info 可获取当前url的路径，如/host/?page=1的path_url=/host/
        pagedict["record_sum"] = self.queryResult.count()
        pagedict["current_page"] = self.request.GET.get("page")
        pagedict["request"] = self.request
        pagedict["max_pages"] = 11  # 默认11，可不传入
        pagedict["max_records"] = 10  # 默认10，可不传入

        self.page_obj = Pageination(**pagedict)

    # 返回前端的 分页html
    def get_page_html(self):
        html = self.page_obj.bootstrap_page()
        return html

    # 列表的头显示
    def head_list(self):
        # 先初始化page对象
        self.init_page_obj()

        if not self.config.list_display:
            self.config.list_display = [self.config.mcls._meta.fields[i].name for i in range(len(self.config.mcls._meta.fields))]

        # 三个基本列只添加一次，否则会在页面上刷新展示翻倍
        if not self.config.add_3display_flag:
            self.config.list_display.insert(0, self.config.checkbox_display)
            self.config.list_display.append(self.config.change_display)
            self.config.list_display.append(self.config.del_display)
            self.config.add_3display_flag = True

        # 获取字段的 verbose_name
        head_list = []
        for col in self.config.list_display:
            if isinstance(col, FunctionType):  # 如果是用户重写传入的 方法
                temp = col(self.config, is_header=True)
            elif isinstance(col, MethodType):  # 如果是 类内部定义的方法
                temp = col(is_header=True)
            else:  # 如果是字符串，即表自身字段
                temp = self.config.mcls._meta.get_field(col).verbose_name
            head_list.append(temp)

        return head_list

    # 列表的数据显示
    def data_list(self):
        # 将表记录取出放在列表中然后传入到前端，不能直接在前端用 obj.col ,这个会报错，因为 obj是动态的，col也是动态的
        data_list = []
        list_obj = self.queryResult[self.page_obj.start:self.page_obj.end]
        for row in list_obj:
            temp = []
            for col in self.config.list_display:
                if isinstance(col, FunctionType):  # 如果是用户重写传入的 方法
                    val = col(self.config, row=row)
                elif isinstance(col, MethodType):  # 如果是 类内部定义的方法
                    val = col(row=row)
                else:  # 如果是字符串，即表自身字段
                    val = getattr(row, col)
                temp.append(val)
            data_list.append(temp)
        return data_list

    # 增加按钮指定页面
    def get_add_url(self):
        add_url = reverse(self.config._url_dict["add_url"])
        return add_url


class StarkConfig(object):
    '''
     封装单独的 数据库操作类
    '''
    # /展示的字段
    list_display=[]
    # ModelForm模板
    model_form_cls=None

    # 添加三个基本列的标识
    add_3display_flag = False

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

    ########三个基本的列： 选择  编辑  删除  start########################
    def forloop_display(self,is_header=False,row=None): # 这个生成的顺序不好调整，暂时放着
        if is_header:
            return "序号"
        else:
            return 'forloop.counter'

    def checkbox_display(self,is_header=False,row=None):
        if is_header:
            return "选择"
        else:
            return  mark_safe('<input type="checkbox" name="pk" value=%s />' % (row.id,)  )

    # 定义编辑字段和对应的url
    def change_display(self,is_header=False,row=None):
        if is_header:
            return "编辑"
        else:
            url="%s/change/"%(row.id,)
            return  mark_safe( '<a href="%s">编辑<a/>' % (url,))

    # 定义 删除字段和对应的url
    def del_display(self,is_header=False,row=None):
        if is_header:
            return "删除"
        else:
            # url="stark/%s/%s/%s/change/"%(self._app_name,self._model_name,row.id)
            url="%s/del/"%(row.id,)
            return  mark_safe( '<a href="%s">删除<a/>' % (url,))

    ############# 三个基本的列： 选择  编辑  删除  end #############


    ###################  url配置相关 start ########################
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

    @property # 获取ModelForm类,如果定义了用定义的，没有则用默认的
    def getModelForm(self):
        if self.model_form_cls:
            return self.model_form_cls

        class TempModleForm(ModelForm):
            class Meta:
                model = self.mcls
                fields = "__all__"
        return TempModleForm

    ###################  url配置相关 end ########################

    ########t##  四个基本视图 增删改查 start ######################
    def list_views(self,request):
        if request.method=="GET":

            queryResult=self.mcls.objects.all()

            # 利用工厂函数生成分页的数据项和html
            flv=FacListViews(self,queryResult,request)
            # print(flv.get_page_html())

            return render(request,"list_views.html",{"flv":flv})

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

        obj = self.mcls.objects.filter(pk=nid).first()

        form = self.getModelForm(instance=obj)
        if request.method=="GET":
            return render(request,"change_views.html",{'form':form})
        else:
            form = self.getModelForm(data=request.POST,instance=obj)
            if form.is_valid():
                form.save()
            return redirect(reverse(self._url_dict["list_url"]))

    def del_views(self,request,nid):
        filter_obj = self.mcls.objects.filter(pk=nid)
        # 这里直接删除
        if filter_obj:
            filter_obj.delete()
        return redirect(reverse(self._url_dict["list_url"]))

    ########t##  四个基本视图 增删改查 end ######################


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

# 实例化一个site ，这里利用了单列模型，site生成后就不会再重复生成，也利用了字典的可变性
# 实现对 models 的添加，也是一种程序内部的数据交换方式
site=StarkSite()