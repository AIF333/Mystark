from django.db import models

# Create your models here.
# 用户表
class UserInfo(models.Model):
    username=models.CharField(verbose_name="用户名",max_length=32)
    email=models.CharField(verbose_name="邮箱", max_length=32)

    gender_choice=(
        (1,"男"),
        (2,"女")
    )
    gender=models.IntegerField(verbose_name="性别",choices=gender_choice,default=1)
    dp=models.ForeignKey(verbose_name="部门dp",to="Department",default=1,on_delete=models.CASCADE)
    hobby=models.ManyToManyField(verbose_name="爱好",to="Hobby")
# 部门
class Department(models.Model):
    title=models.CharField(verbose_name="部门",max_length=32)

    def __str__(self):
        return self.title


# 角色表
class Role(models.Model):
    title=models.CharField(verbose_name="角色", max_length=32)

# 爱好表
class Hobby(models.Model):
    title=models.CharField(verbose_name="爱好",max_length=32)

    def __str__(self):
        return self.title