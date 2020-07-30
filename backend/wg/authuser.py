from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, UserManager
from django.views import View

from libwg.funcs import json, resok, reserr

class Login(View):

    # login
    def post(self, req):
        print("有使用CSRF: ", req.META.get("CSRF_COOKIE_USED"))

        js = req.META["WG_BODY"]
        username = js.get("un")
        password = js.get("pw")
        
        print("un:", username, "pw:", password)

        auth = authenticate(username=username, password=password)

        print("auth:", auth)

        if auth is None:
            return reserr("用户名或密码错误")
        else:
            login(req, auth)
            return json({"code": 0, "msg": "ok", "superuser": auth.is_superuser})

class Logout(View):
    # logout
    def get(self, req):
        logout(req)
        return resok()


class Logined(View):

    def get(self, req):

        if req.user.is_authenticated:
            return resok("已登录")
        else:
            return reserr("未登录")

"""
class UserManger(View):

    def dispatch(request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
"""