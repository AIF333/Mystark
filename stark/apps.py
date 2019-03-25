from django.apps import AppConfig


class StarkConfig(AppConfig):
    name = 'stark'

 # settings在配置的app中会读取对应app.py里 这个config类。我们在这里添加一个 ready方法，就能实现
 # 对这个方法的执行。
    def ready(self):
        #功能： 去程序中已注册的所有app(只要注册就行，不要求是只能stark这个app)目录中查找 stark.py 文件并解释
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('stark')
