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
        iface = request.GET.get("iface")
        if iface is None:
            l = []
            for queryset in ServerWg.objects.all():
                i = {}

                i["iface"] = queryset.iface
                i["net"] = queryset.net
                i["publickey"] = queryset.publickey
                i["persistentkeepalive"] = queryset.persistentkeepalive
                i["boot"] = queryset.boot
                i["comment"] = queryset.comment

                l.append(i)

            return funcs.res(l)
        else:
            #print(f"查{iface}接口信息.")
            try:
                iface = ServerWg.objects.get(iface=iface)
            except ServerWg.DoesNotExist:
                return funcs.reserr(f"没有{iface}接口")

            iface_j = {
                "iface": iface.iface,
                "net": iface.net,
                "privatekey": iface.privatekey,
                "listenport": iface.listenport,
                "persistentkeepalive": iface.persistentkeepalive,
                "boot": iface.boot,
                "comment": iface.comment
            }

            return funcs.res(iface_j)

    def post(self, request):
        wg = request.META["WG_BODY"]

        i = {}

        if not wg.get("iface"):
            suffix = ServerWg.objects.aggregate(Max("id")).get("id__max")
            if suffix is None:
                i["iface"] = "easywg0"
            else:
                i["iface"] = "easywg" + str(suffix + 1)

        net = wg.get("net")
        if net is None:
            return funcs.reserr("network 是必须的")
        else:
            if ServerWg.objects.filter(net=net):
                return funcs.reserr(f"network {net} 已存在！")
            else:
                i["net"] = net
        
        if not wg.get("privatekey"):
            i["privatekey"] = wgcmd.genkey()
            i["publickey"] = wgcmd.pubkey(i["privatekey"])
        else:
            i["publickey"] = wgcmd.pubkey(i["privatekey"])

        i["persistentkeepalive"] = wg.get("persistentkeepalive", 35)
        i["boot"] = wg.get("boot", True)
        i["comment"] = wg.get("comment", "")
        
        lp = wg.get("listenport")
        if lp:
            if ServerWg.objects.filter(listenport=lp):
                return funcs.reserr(f"listenport {lp} 冲突")
        else:
            lp = ServerWg.objects.aggregate(Max("listenport")).get("listenport__max")
            if lp is None:
                i["listenport"] = 8324
            else:
                i["listenport"] = lp + 1


        print("添加一个接口：", i)
        wgservser = ServerWg(**i)
        wgservser.save()

        return funcs.res(i)

    def put(self, request):
        pass

    def delete(self, request):

        iface = request.META["WG_BODY"].get("iface")

        if iface is None:
            return funcs.reserr("删除server接口需要接口名")
        
        try:
            iface_model = ServerWg.objects.get(iface=iface)
        except ServerWg.DoesNotExist:
            return funcs.reserr(f"没有 {iface} server 接口")

        iface_model.delete()
        return funcs.resok()

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

        config = ClientWg.objects.get(user=user, ifname=iface)

        return funcs.res(config)


