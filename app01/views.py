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

    obj=models.UserInfo.objects.filter(id=6).first()
    print(obj)
    # print(obj.hobbys)
    # for row in obj:
    #     print(row)
    #     hobbys=row.hobby.all().values_list("title")
    #     for hobby in hobbys:
    #         print(hobby)

    return HttpResponse("OK")