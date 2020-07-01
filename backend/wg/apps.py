from django.apps import AppConfig
from django.db.models.signals import post_migrate


DEFAULT_USER = "easywg"

def init_db(sender, **kwargs):
    from django.contrib.auth.models import User
    #if sender == 'User.__name__':
    #    print("sender: ", sender)

    print("创建默认 superuser")
    if not User.objects.filter(username=DEFAULT_USER):
        easywg = User.objects.create_superuser(username=DEFAULT_USER, password=DEFAULT_USER)
        easywg.save()



    #if User.objects.exists():
    #else:
    #    print("User models 不在")
    #    User.objects.create()
    #    if not User.objects.filter(username="zx"):
    #        User.objects.create_superuser(username="zx", password="easywg")



class WgConfig(AppConfig):
    name = 'wg'

    def ready(self):
        """
        
        """

        print("执行 wg.apps.WgConfig.ready()")

        from django.contrib.auth.models import User
        post_migrate.connect(init_db, sender=self, dispatch_uid="easywg_init_user_models")
