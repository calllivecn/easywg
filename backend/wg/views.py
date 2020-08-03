import io
import base64

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Max, F

import qrcode

from libwg import funcs, wgcmd
from wg import wgop
from wg.models import ServerWg, ClientWg

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
        wg = request.META["WG_BODY"]
        return wgop.serverwg_delete(wg)


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
    
    def put_disable(self, request):
        username = request.user.username
        wg = request.META["WG_BODY"]
        return wgop.clientwg_change(username, wg)

    def delete(self, request):
        wgid = request.META["WG_BODY"].get("ifaceid", "")

        if wgid == "":
            return funcs.reserr("需要iface id")

        return wgop.clientwg_delete(wgid)


class WgClientConfig(View):

    def get(self, request):

        iface_str = request.GET.get("iface", "")
        if iface_str == "":
            return funcs.reserr("需要指定接口！")
        
        fmt = request.GET.get("format", "")
        if fmt == "":
            fmt = "conf"
        elif fmt not in ("conf", "qrcode", "shell"):
            return funcs.reserr("format 只能是 conf 或 qrcode 或 shell")

        try:
            iface = ClientWg.objects.get(user=request.user, iface=iface_str)
        except ClientWg.DoesNotExist:
            return funcs.reserr("指定的接口名不存在！")
    
    
        conf = {}
        conf["publickey"] = iface.server.publickey
        conf["address"] = iface.ip
        conf["privatekey"] = iface.privatekey
        conf["presharedkey"] = iface.presharedkey
        conf["allowedips"] = iface.allowedips_c
        conf["endpoint"] = iface.server.address.split("/")[0] + ":" + str(iface.server.listenport)
        conf["persistentkeepalive"] = iface.persistentkeepalive


        if fmt == "qrcode":
            make_conf = funcs.render("client.conf", conf)
            qr = qrcode.QRCode(box_size=4, border=1)
            qr.make(fit=True)
            qr.add_data(make_conf)

            img = qr.make_image()

            with io.BytesIO() as buf:
                img.save(buf)
                base64img = base64.b64encode(buf.getvalue())
        
            return HttpResponse(base64img)

        elif fmt == "conf":
            make_conf = funcs.render("client.conf", conf)
            res = HttpResponse(make_conf)
            res["Content-Type"] = "application/octet-stream"
            res['Content-Disposition'] = f'attachment; filename="{iface_str}.conf"'
            return res

        elif fmt == "shell":
            conf["iface"] = iface_str
            shell = funcs.render("client.shell", conf)
            print(shell)
            res = HttpResponse(shell)
            res["Content-Type"] = "application/octet-stream"
            res['Content-Disposition'] = f'attachment; filename="{iface_str}.sh"'
            return res


class WgClientCli(View):

    def dispatch(self, request, *args, **kwargs):
        username = request.META.get("HTTP_WG_USERNAME")
        pw = request.META.get("HTTP_WG_PASSWORD")
        self.auth = authenticate(username=username, password=pw)
        if self.auth is None:
            return funcs.reserr("用户名或密码错误")
        else:
            return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        pass