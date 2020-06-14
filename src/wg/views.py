from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpRequest, JsonResponse


from libwg.funcs import res, resok, reserr
from wg.models import User


def checkargs(request, arg, choices):
    default = choices[0]
    arg = request.GET.get(arg, default)
    if arg in choices:
        return arg
    else:
        return default


class WgServerApi(View):

    @login_required
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        
        return render()


class WgClientApi(View):

    def dispatch(self, request, *args, **kwargs):
        username = request.MATE.get("HTTP_WG_USERNAME")
        pw = request.header.get("HTTP_WG_PASSWORD")
        auth = authenticate(username=username, password=pw)
        if auth is None:
            return reserr( -1, "用户名或密码错误")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        # value: shell or conf
        ls = ("conf", "shell", "qrcode")
        fmt = checkargs(request, "format", ls)

        ls = ("linux", "andriod", "windows", "ios", "macos")
        client = checkargs(request, "client", ls)



