from django.db.models import IntegerField
from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def test(request):
    from app01 import models
    # print(models.UserInfo._meta.app_label,models.UserInfo._meta.model_name)
    # print('----',models.UserInfo._meta.fields)
    # l=[models.UserInfo._meta.fields[i].name for i in range(len(models.UserInfo._meta.fields))]
    # print(l)
    # print('----0',models.UserInfo._meta.fields[0].name,type(models.UserInfo._meta.fields[0]))
    # print('++',models.UserInfo._meta.fields[1].verbose_name)
    # print(models.UserInfo._meta.get_field("username").verbose_name)
    # obj=models.Hobby.objects.filter(pk__in=[1,2,3])
    # print(obj)

    gender_obj=models.UserInfo._meta.get_field("gender")
    dp_obj=models.UserInfo._meta.get_field("dp")

    from django.db.models.fields import IntegerField

    print(gender_obj,type(gender_obj)) # django.db.models.fields.IntegerField
    print(gender_obj.choices,type(gender_obj.choices),isinstance(gender_obj,IntegerField)) # ((1, '男'), (2, '女')) <class 'tuple'>
    print(dp_obj,type(dp_obj)) # django.db.models.fields.related.ForeignKey
    print(models.UserInfo.objects.all().values_list("dp__title"))
    # for item in
    from django.db.models.fields import IntegerField


    # obj=models.UserInfo.objects.filter(id=6).first()
    # print(obj)
    # print(obj.hobbys)
    # for row in obj:
    #     print(row)
    #     hobbys=row.hobby.all().values_list("title")
    #     for hobby in hobbys:
    #         print(hobby)

    # 导入 copy 利用深拷贝完成对 request.GET的复制，以免直接修改了request.GET不安全
    # import copy
    # request_dpcp=copy.deepcopy(request.GET)
    # request_dpcp._mutable=True # 这是 QuerySet的类变量，置为True时 value才能别修改
    # print(request_dpcp)  # 输出如： <QueryDict: {'page': ['2'], 'key': ['xxxxx']}>
    # request_dpcp['page']=3 #点击下一页时只修改 page
    # print(request_dpcp)  # 输出如： <QueryDict: {'page': ['3'], 'key': ['xxxxx']}>
    # print(request_dpcp.urlencode()) #内置方法改成url，输出如： page=3&key=xxxxx&f=2


    return HttpResponse("OK")