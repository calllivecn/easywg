from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View

from libwg.funcs import json, resok, reserr

class Login(View):

    # logout
    def get(self, req):
        logout(req)
        return resok()

    # login
    def post(self, req):

        username = req.META.get("HTTP_WG_UN")
        password = req.META.get("HTTP_WG_PW")

        if username is None:
            username = req.META["WG_BODY"].get("un")
            password = req.META["WG_BODY"].get("pw")
        
        print("un:", username, "pw:", password)

        auth = authenticate(username=username, password=password)

        print("auth:", auth)

        if auth is None:
            return reserr("用户名或密码错误")
        else:
            login(req, auth)
            return resok("ok")


class Auth(View):

    def post(self, req):

        if req.user.is_authenticated:
            return resok("已登录")
        else:
            return resok("未登录")

class UserManger(View):

    def dispatch(request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)