from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.db.models import Max


from libwg import funcs, wgcmd
from wg.models import ServerWg, ClientWg
from wg.startwg import startserver, stopserver


def checkargs(request, arg, choices):
    default = choices[0]
    arg = request.GET.get(arg, default)
    if arg in choices:
        return arg
    else:
        return default


class WgServerApi(View):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        temp = ""
        return render()
    
    def post(self, request):
        wg = request.META["WG_BODY"]

        iface = wg.get("iface")
        ip = wg.get("ip")
        privatekey = wg.get("privatekey")
        #publickey = 
        listenport = wg.get("listenport")
        persistentkeepalive = wg.get("persistentkeepalive", 35)

        boot = wg.get("boot", True)
        comment = wg.get("comment")
        

        if not iface:
            iface = "easywg"
        
        if not ip:
            for ips in models.ServerWg.objects.values_list("ip"):
                


        if not privatekey:
            privatekey = wgcmd.genkey()
            publickey = wgcmd.pubkey(privatekey)
        else:
            publickey = wgcmd.pubkey(privatekey)



        try:
            wg[""]
        except Exception:
            return reserr("ifname, privatekey, ip, ")

        models.ServerWg.objects.create(ifname="")



class WgClientApi(View):

    def dispatch_disable(self, request, *args, **kwargs):
        username = request.META.get("HTTP_WG_USERNAME")
        pw = request.header.get("HTTP_WG_PASSWORD")
        auth = authenticate(username=username, password=pw)
        if auth is None:
            return funcs.reserr("用户名或密码错误", -1)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        # value: shell or conf
        ls = ("conf", "shell", "qrcode")
        fmt = checkargs(request, "format", ls)

        ls = ("linux", "andriod", "windows", "ios", "macos")
        client = checkargs(request, "client", ls)

        return funcs.res([{"name":"wg0", "privatekey": "aslkjfisajefl", "imde": "lsidfj"}])


class WgClientConfig(View):

    def get(self, request):
        iface = request.GET.get("iface")
        user = request.user

        config = models.ClientWg.objects.get(user=user, ifname=iface)

        return res(config)




from threading import Thread

print("启动server ")
th = Thread(target=startserver, daemon=True)
th.start()