# stark 配置
from copy import deepcopy
from types import FunctionType,MethodType

from django.db.models import Q, ForeignKey
from django.shortcuts import render,HttpResponse,redirect
from django.urls import path, reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from stark.utils.pagination import Pageination # 分页组件
from django.db.models.fields import IntegerField # 判断组合搜素的字段类型 choice为IntegerField


# path 的一级分发的namespace

# 做组合搜索的字段类型处理的类对象，需可迭代，实现 __iter__ 方法
class FiledRow():
    # 全部 时剔除的字段值列表
    pop_value=[]
    def __init__(self,config,col,filed_obj,is_choice=False):
        '''

        :param config: 引用对象
        :param col: 字段 如 gender ， dp
        :param filed_obj: models的字段对象 如 app01.UserInfo.gender （IntegerField类型） 、app01.UserInfo.dp（ForeignKey类型）
        :param is_choice:  是否为choice对象（IntegerField类型）
        '''
        self.config=config
        self.col=col
        self.field_obj=filed_obj
        self.is_choice=is_choice
        self.request_dpcp = deepcopy(self.config.request.GET) # 拷贝request.GET，通过这个修改key值，防止get参数丢失
        self.request_dpcp._mutable = True
        self.parms=self.request_dpcp.urlencode()
        self._url_dict=self.config._url_dict # 列表页面

    def __iter__(self):
        # yield mark_safe('<a class ="comb_row" href="#">全部</a>')
        if self.is_choice:  # choice类型
            #字段在里面才去除,在里面也就说明选择的不是全部，全部就不用 active，else就需要active
            if self.col in self.request_dpcp :
                # 添加 全部的选择按钮，全部时，则需要把url中该属性给去掉 如选择性别的全部  ?gender=2&key=3 => ?key=3
                self.pop_value=self.request_dpcp.pop(self.col) # pop_value ['2']
                # print("pop_value",pop_value)
                self.parms = self.request_dpcp.urlencode()
                html = '<a class ="comb_row" href="%s?%s">全部</a>' % (self._url_dict, self.parms)
            else:
                html = '<a class ="comb_row active" href="%s?%s">全部</a>' % (self._url_dict, self.parms)
            yield mark_safe(html)

            # 添加具体值的标签 如((1,男),(2,女))
            v_tuples=self.field_obj.choices
            for v in v_tuples: # (1,男)s
                nid=v[0]
                text=v[1]
                self.request_dpcp[self.col]=nid
                self.parms = self.request_dpcp.urlencode()
                print(nid,self.pop_value,"----")
                if str(nid) in self.pop_value: # 如果在全部标签 剔除的值里，说明选择的是这个按钮
                    html='<a class ="comb_row active" href="%s?%s">%s</a>'%(self._url_dict,self.parms,text)
                else:
                    html = '<a class ="comb_row" href="%s?%s">%s</a>' % (self._url_dict, self.parms, text)
                yield mark_safe(html)


# list_views的工厂类，因为列表页面的代码太多，全部放在工厂类里
class FacListViews():

    # 分页对象 || 组合搜索的html
    page_obj = None
    comb_html_list = []

    def __init__(self,config,request,queryResult):
        '''
        :param config: 原类的实例，即StarkConfig的self
        :param queryResult: 表的查询结果querySet类型,如 models.Student.objects.all()

        '''
        self.config=config
        self.request=request
        self.queryResult=queryResult
        self.search_list=self.config.search_list # 搜索框
        self.mutil_list=self.config.mutil_list # 批量操作 下拉框
        self._url_dict = reverse(self.config._url_dict["list_url"]) # 列表页面的url

        temp=request.GET.get("search_key",'')
        if temp:  # 剔除空格
            self.search_key = temp.strip()
        else:
            self.search_key=''

    # 获取当前页面的数据，如有查询则数据会有变化,这个是第一个执行的,放在 head_list 里
    def init_queryResult(self):
        # 如果用户定义了查询列，则可进行查询
        if self.config.search_list:
            if self.search_key: # 如果查询有输入值
                con = Q()
                con.connector = 'OR'
                for col in self.config.search_list:
                    # print('----', ('%s__contains' % (col,), search_key))
                    con.children.append(('%s__contains' % (col,), self.search_key))
                self.queryResult = self.queryResult.filter(con)

    def get_comb_html(self):
        if self.config.comb_list:
            for col in self.config.comb_list:
                _field=self.config.mcls._meta.get_field(col) # app01.UserInfo.gender 、app01.UserInfo.dp 等这种字段类型

                # yield 相当于停顿的return 但是后面的代码会执行
                # print(_field,type(_field))
                if isinstance(_field,IntegerField):
                    print(_field,"IntegerField")
                    yield FiledRow(self,col,_field,is_choice=True)
                elif isinstance(_field,ForeignKey):
                    print(_field,"ForeignKey")
                    yield FiledRow(self,col,_field,is_choice=False)
                else:
                    print("无效的输入，未做处理的字段类型！",_field,"---" )

    # 初始化分页对象，这个是第二个执行，依赖get_queryResult的查询结果集
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
        self.init_queryResult()
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
    # 搜索列表
    search_list=[]
    # 批量操作列表
    mutil_list=[]
    # 组合搜索
    comb_list=[]



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
    def get_mutil_func(self,request):
        if self.mutil_list:
            # select_value 下拉框选择值 pk 选择器选择值
            select_value = request.POST.get("select_value", '')
            pk_list = request.POST.getlist("pk", '')
            print(select_value, pk_list)
            mutil_func = getattr(self, select_value, 'None')

            if isinstance(mutil_func, FunctionType):
                # print("FunctionType----")
                mutil_func(self, select_value, pk_list)
            elif isinstance(mutil_func, MethodType):
                # print("MethodTyope--")
                mutil_func(select_value, pk_list)
            else:
                print("nothing to do !")
    ########t##  四个基本视图 增删改查 start ######################
    def list_views(self,request):

        if request.method == "POST": # 执行批量操作
            self.get_mutil_func(request)

        queryResult = self.mcls.objects.all()
        flv = FacListViews(self, request,queryResult)

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