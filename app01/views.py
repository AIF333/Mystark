from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def test(request):
    from app01 import models
    # print(models.UserInfo._meta.app_label,models.UserInfo._meta.model_name)
    # print('----',models.UserInfo._meta.fields)
    # print('----0',models.UserInfo._meta.fields[0].name,type(models.UserInfo._meta.fields[0]))
    # print('++',models.UserInfo._meta.fields[1].verbose_name)
    print(models.UserInfo._meta.get_field("username").verbose_name)

    return HttpResponse("OK")