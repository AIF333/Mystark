# print("app01:stark.py 执行")

from stark.service.V1 import site
from app01 import models

# 进行site注册，即往site字典里加入 models
site.registry(models.UserInfo)
site.registry(models.Role)




