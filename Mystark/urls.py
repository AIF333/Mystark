"""Mystark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from stark.service import V1
from app01 import views as app_views
# url/path 本质 前面是地址，后面其实是一个元祖
# (  [path]  ,  app名(None),  别名(None,通过reverse反向解析) )
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/',app_views.test),
    # path('stark/', V1.site.urls),
    # 指定  namespace这个很蛋疼的形式
    path('stark/', include((V1.site.urls,'stark'),namespace="stark")),
]
