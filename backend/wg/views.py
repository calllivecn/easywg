from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Max, F

from libwg import funcs, wgcmd
from wg import wgop
from wg.models import ServerWg, ClientWg
from wg.startwg import startserver, stopserver

def getuser(username):
    return User.objects.get(username=username)



class WgServerApi(LoginRequiredMixin, View):

    def get(self, request):
        iface = request.GET.get("iface", "")
        if iface == "":
            l = []
            for queryset in ServerWg.objects.all():
                l.append(funcs.serverwg2json(queryset))

            return funcs.res(l)
        else:
            #print(f"查{iface}接口信息.")
            try:
                iface = ServerWg.objects.get(iface=iface)
            except ServerWg.DoesNotExist:
                return funcs.reserr(f"没有{iface}接口")

            return funcs.res(funcs.serverwg2json(iface))

    def post(self, request):
        wg = request.META["WG_BODY"]
        return wgop.serverwg_add(wg) 

    def put(self, request):
        wg = request.META["WG_BODY"]
        return wgop.serverwg_change(wg)

    def delete(self, request):

        iface = request.META["WG_BODY"].get("iface", "")

        if iface == "":
            return funcs.reserr("删除server接口需要接口名")
        
        try:
            iface_model = ServerWg.objects.get(iface=iface)
        except ServerWg.DoesNotExist:
            return funcs.reserr(f"没有 {iface} server 接口")

        iface_model.delete()
        return funcs.resok()

class WgClientApi(LoginRequiredMixin, View):

    """
    @login_required
    def dispatch(self, request, *args, **kwargs):
        print("已登录。： ", request.user)
        return super().dispatch(request, *args, **kwargs)
    """

    def get(self, request):
        user = request.user
        #print("username:", user.username, dir(user), "user id:", user.id)

        data = []
        # get all
        for serverid in ClientWg.objects.filter(user__username=user.username).values("server").distinct():
            server = ServerWg.objects.get(id=serverid["server"])

            info = {}

            info["serverid"] = server.id
            info["serverwg"] = server.iface
            info["address"] = server.address
            info["ip"] = server.ip
            info["publickey"] = server.publickey
            
            info["ifaces"] = []

            for peer in ClientWg.objects.filter(user__username=user.username, server=server):
                iface = funcs.clientwg2json(peer)
                info["ifaces"].append(iface)
            
            data.append(info)

        return funcs.res(data)


    def post(self, request):
        username = request.user.username
        wg = request.META["WG_BODY"]
        return wgop.clientwg_add(username, wg)
    
    def put(self, request):
        username = request.user.username
        wg = request.META["WG_BODY"]
        return wgop.clientwg_change(username, wg)

    def delete(self, request):
        wgid = request.META["WG_BODY"].get("ifaceid", "")
        if wgid == "":
            return funcs.reserr("需要iface id")
        
        try:
            wgid = int(wgid)
        except Exception:
            return funcs.reserr("iface id 是个整数")

        try:
            clientwg = ClientWg.objects.get(id=wgid)
        except Exception:
            return funcs.reserr(f"iface id: {wgid} 不存在")
        
        clientwg.delete()

        return funcs.resok()


def checkargs(request, arg, choices):
    default = choices[0]
    arg = request.GET.get(arg, default)
    if arg in choices:
        return arg
    else:
        return default

class WgClientConfig(View):

    def dispatch(self, request, *args, **kwargs):
        username = request.META.get("HTTP_WG_USERNAME")
        pw = request.META.get("HTTP_WG_PASSWORD")
        self.auth = authenticate(username=username, password=pw)
        if self.auth is None:
            return funcs.reserr("用户名或密码错误")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # value: shell or conf
        ls = ("conf", "shell", "qrcode")
        fmt = checkargs(request, "format", ls)

        ls = ("andriod", "linux", "windows", "ios", "macos")
        ostype = checkargs(request, "ostype", ls)

        iface = request.GET.get("iface", "")
        if iface == "":
            return funcs.reserr("需要指定接口！")

        try:
            iface = ClientWg.objects.get(user=self.auth, iface=iface)
        except ClientWG.DoesNotExist:
            return funcs.reserr("指定的接口名不存在！")
        
        
        conf = {}

        conf["publickey"] = iface.server.publickey

        if ostype in ("andriod", "windows", "ios", "macos"):
            conf["address"] = iface.server.ip

        conf["privatekey"] = iface.privatekey
        conf["presharedkey"] = iface.presharedkey
        conf["allowedips"] = iface.allowedips_c
        conf["endpoint"] = iface.server.address.split("/")[0] + ":" + str(iface.server.listenport)
        conf["persistentkeepalive"] = iface.persistentkeepalive

        make_conf = funcs.render("client.conf", conf)

        return HttpResponse(make_conf)