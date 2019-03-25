from django.forms import ModelForm
from app01 import models

class  UserInfoMF(ModelForm):
    model=models.UserInfo
    fields="__all__"
