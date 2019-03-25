# stark 配置
from django.shortcuts import render,HttpResponse,redirect
from django.urls import path


class StarkConfig(object):
    '''
     封装单独的 数据库操作类
    '''

    def __init__(self,mcls):
        self.mcls=mcls

    # 定义增删改查四个url  二级页面的路径前面需要加/ ，如 /add/
    @property
    def urls(self):

        pts = [
            path('', self.list_views),
            path('add/', self.add_views),
            path('<int:nid>/change/', self.change_views),
            path('<int:nid>/del/', self.del_views),
        ]

        pts.extend(self.extend_url())  # 拓展除了增删改查基本外的url
        return pts,None,None

    def extend_url(self,path_list=None):
        '''
        拓展基本的四个二级url，如果还有其他如导出，报表等路径，可在子类中实现
        :param path_list:
        :return:
        '''
        if not path_list:
            path_list=[]
        return list(path_list)

    # 视图函数至少有一个 request 参数
    def list_views(self,request):
        return HttpResponse("列表页面")

    def add_views(self,request):
        return HttpResponse("增加页面")

    def change_views(self,request,nid):
        return HttpResponse("编辑页面")

    def del_views(self,request,nid):
        return HttpResponse("删除页面")


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
    def registry(self,models):
        '''
        :param models:  传入的models下的表对象，如 models.Blog
        :return: 无

        self._registy: {  <class 'app01.models.UserInfo'>: <stark.service.V1.StarkConfig object at 0x0000000003D56240> }
        '''
        self._registy[models]=StarkConfig(models)

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

        return pts,None,None
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