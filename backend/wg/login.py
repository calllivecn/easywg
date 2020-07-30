from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, UserManager
from django.views import View

from libwg.funcs import res, resok, reserr

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
            return res({"username": username, "superuser": auth.is_superuser, "msg": "ok"})

class Logout(View):
    # logout
    def get(self, req):
        logout(req)
        return resok()


class Logined(View):

    def get(self, req):

        if req.user.is_authenticated:
            return res({"username": req.user.username, "serupuser": req.user.is_superuser, "msg": "已登录"})
        else:
            return reserr("未登录")

"""
class UserManger(View):

    def dispatch(request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
"""