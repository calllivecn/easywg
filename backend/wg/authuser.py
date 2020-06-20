from django.contrib.auth import authenticate
from django.views import View

from libwg.funcs import json, resok, reserr

class Auth(View):

    def get(self, req):

        username = req.META.get("HTTP_WG_USERNAME")
        password = req.META.get("HTTP_WG_PASSWORD")

        auth = authenticate(username=username, password=password)
        auth = None
        if auth is None:
            return reserr("用户名或密码错误")
        else:
            return resok("ok")
