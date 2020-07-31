from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, UserManager
from django.views import View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from libwg.funcs import json, res, resok, reserr

class Login(View):

    # login
    def post(self, req):
        js = req.META["WG_BODY"]
        username = js.get("un")
        password = js.get("pw")

        auth = authenticate(username=username, password=password)

        if auth is None:
            return reserr("用户名或密码错误")
        else:
            login(req, auth)
            if not settings.DEBUG:
                if username == "easywg" and password == "easywg":
                    return json({"code": 302, "router": "/accounts/chpassword/"})

            return res({"username": username, "superuser": auth.is_superuser})

class Logout(LoginRequiredMixin, View):
    # logout
    def get(self, req):
        logout(req)
        return resok()


class Logined(View):

    def get(self, req):

        if not settings.DEBUG:
            if req.user.username == "easywg" and req.user.password == "easywg":
                print("初始密码请修改。")
                return json({"code": 302, "router": "/accounts/chpassword/"})

        if req.user.is_authenticated:
            return res({"username": req.user.username, "serupuser": req.user.is_superuser})
        else:
            return reserr("未登录")

class Chpassword(LoginRequiredMixin, View):

    def get(self, req):
        auth = req.user

        if not auth.is_authenticated:
            return json({"code": 302, "router": "login"})

        return res({"userid": auth.id, "username": auth.username})
    
    def post(self, req):
        js = req.META["WG_BODY"]

        userid = js.get("id", "")
        username = js.get("un", "")
        password1 = js.get("pw1", "")
        password2 = js.get("pw2", "")

        if userid == "":
            return reserr("需要用户id!")
        
        if username == "":
            return reserr("需要用户名!")

        if password1 == "":
            return reserr("需要用户密码!")
        
        # chekc 旧密码是否正确
        auth = authenticate(username=username, password=password1)

        if auth is None:
            return reserr("原密码错误！")

        u = User.objects.get(id=userid)
        u.username = username
        u.set_password(password2)
        u.save()
        # 修改成功后 跳转到 login 重新登录
        logout(req)
        return resok()

"""
class UserManger(View):

    def dispatch(request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
"""