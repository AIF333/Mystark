from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username=models.CharField(verbose_name="用户名",max_length=32)
    email=models.CharField(verbose_name="邮箱", max_length=32)

class Role(models.Model):
    title=models.CharField(verbose_name="角色", max_length=32)