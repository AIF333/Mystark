from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def test(request):
    from app01 import models
    print(models.UserInfo._meta.app_label,models.UserInfo._meta.model_name)

    return HttpResponse("OK")