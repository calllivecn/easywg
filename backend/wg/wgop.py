from django.db.models import Max
from django.contrib.auth.models import User

from wg.models import ClientWg, ServerWg
from libwg import wgcmd, funcs

def checkargs(request, arg, choices):
    default = choices[0]
    arg = request.GET.get(arg, default)
    if arg in choices:
        return arg
    else:
        return default

def config(iface, request):
    # value: shell or conf
    ls = ("conf", "shell")
    fmt = checkargs(request, "format", ls)

    ls = ("notlinux", "andriod", "linux", "windows", "ios", "macos")
    ostype = checkargs(request, "ostype", ls)

    iface = request.GET.get("iface", "")

    try:
        iface = ClientWg.objects.get(user=request.user, iface=iface)
    except ClientWg.DoesNotExist:
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

    return conf


def serverwg_add(wg):
    i = {}

    iface = wg.get("iface", "")
    if iface:
        if ServerWg.objects.filter(iface=iface):
            return funcs.reserr(f"接口名： {iface} 已存在。")
        else:
            i["iface"] = iface
    else:
        # 如果 iface 为空 就自动生成
        suffix = ServerWg.objects.aggregate(Max("id")).get("id__max")
        if suffix:
            p = 1
            tmp = "easywg" + str(suffix + p)
            while ServerWg.objects.filter(iface=tmp):
                p += 1
                tmp = "easywg" + str(suffix + p)

            i["iface"] = tmp
        else:
            i["iface"] = "easywg0"

    address = wg.get("address", "")
    if address == "":
        return funcs.reserr("address 是必须的")
    else:
        i["address"] = address

    network = wg.get("network", "")
    if network == "":
        return funcs.reserr("network 是必须的")
    else:
        if ServerWg.objects.filter(network=network):
            return funcs.reserr(f"network {network} 已存在！")
        else:
            i["network"] = network
    
    i["ip"] = funcs.gateway(i["network"])
    
    prikey = wg.get("privatekey")
    if not prikey:
        i["privatekey"] = wgcmd.genkey()
        i["publickey"] = wgcmd.pubkey(i["privatekey"])
    else:
        try:
            i["publickey"] = wgcmd.pubkey(prikey)
        except Exception:
            return funcs.reserr("privatekey 长度不对或格式不正确")

        i["privatekey"] = prikey

    i["persistentkeepalive"] = wg.get("persistentkeepalive", 35)
    i["boot"] = wg.get("boot", True)
    i["comment"] = wg.get("comment", "")
    
    lp = wg.get("listenport", "")

    
    if lp == "":
        lp = ServerWg.objects.aggregate(Max("listenport")).get("listenport__max")

        if lp:
            i["listenport"] = lp + 1
        else:
            i["listenport"] = 8324

    else:

        try:
            listenport = int(lp)
        except Exception:
            return funcs.reserr("listenport 必须是 8324 ~ 65535 的数")


        if ServerWg.objects.filter(listenport=listenport):
            return funcs.reserr(f"listenport {lp} 冲突")
        else:
            i["listenport"] = listenport


    print("添加一个接口：", i)
    wgserver = ServerWg(**i)
    wgserver.save()
    i["id"] = wgserver.id
    return funcs.res(i)



def serverwg_change(wg):

    iface_id = wg.get("id")

    try:
        iface = ServerWg.objects.get(id=iface_id)
    except ServerWg.DoesNotExist:
        return funcs.reserr("需要修改的接口不存在，请检查输入。")
    
    iface_name = wg.get("iface", "")
    if iface_name == "":
        return funcs.reserr("需要修改的接口名不能为空")
    
    iface_old_name  = iface.iface

    iface.iface = iface_name


    address = wg.get("address", "")
    if address == "":
        return funcs.reserr("address 是必须的")
    else:
        iface.address = address

    network = wg.get("network", "")
    if network == "":
        return funcs.reserr("network 是必须的")

    # 检查是否有其他接口使用了这个net
    if ServerWg.objects.filter(network=network).exclude(iface=iface_old_name):
        return funcs.reserr("需要修改的网络已存在，请检查输入。")

    iface.network = network

    prikey = wg.get("privatekey")
    if prikey:
        iface.privatekey = prikey
        try:
            iface.publickey = wgcmd.pubkey(prikey)
        except Exception:
            return funcs.reserr("privatekey 长度不对或格式不正确")
    else:
        iface.privatekey = wgcmd.genkey()
        iface.publickey = wgcmd.pubkey(iface.privatekey)

    iface.persistentkeepalive = wg.get("persistentkeepalive", 35)
    iface.boot = wg.get("boot", True)
    iface.comment = wg.get("comment", "")
    

    lp = wg.get("listenport", "")

    if lp == "":
        lp_id = ServerWg.objects.aggregate(Max("listenport")).get("listenport__max")
        iface.listenport = lp_id + 1

    else:
        try:
            lp = int(lp)
        except Exception:
            return funcs.reserr("listenport 必须是 8324 ~ 65535 的数")

        if ServerWg.objects.filter(listenport=lp).exclude(iface=iface_old_name):
            return funcs.reserr(f"listenport: {lp} 已存在， 请检查输入。")
        else:
            iface.listenport = lp

    iface.save()
    return funcs.resok()


def clientwg_add(username, wg):

    client = {}

    user_obj = User.objects.get(username=username)

    client["user"] = user_obj

    serverid = wg.get("serverid", "")
    if serverid == "":
        return funcs.reserr("从属server接口是必须的")

    try:
        serverid = int(serverid)
    except Exception:
        return funcs.reserr("从属server接口是必须的")

    try:
        server_obj = ServerWg.objects.get(id=serverid)
    except Exception:
        return funcs.reserr(f"没有id: {serverid} 的server接口")
    
    client["server"] = server_obj

    iface = wg.get("iface", "")

    if iface == "":
        suffix = ClientWg.objects.aggregate(Max("id"), ).get("id__max")
        if suffix:
            p = 1
            tmp = "wg" + str(suffix + p)
            while ServerWg.objects.filter(iface=tmp):
                p += 1
                tmp = "wg" + str(suffix + p)
            client["iface"] = tmp
        else:
            client["iface"] = "wg0"
    else:
        if ClientWg.objects.filter(user=user_obj, iface=iface):
            return funcs.reserr(f"{iface} 已存在！")
        else:
            client["iface"] = iface
    
    genip = funcs.getipaddr(server_obj.network)
    for ip in genip:
        if ClientWg.objects.filter(ip=ip):
            print(f"ip: {ip} 已经存在, 查看下一个")
        else:
            break

    client["ip"] = ip


    client["allowedips_s"] = funcs.getnet_s(client["ip"])

    client["allowedips_c"] = server_obj.network
    
    client["privatekey"] = wgcmd.genkey()
    client["publickey"] = wgcmd.pubkey(client["privatekey"])
    client["presharedkey"] = wgcmd.genpsk()

    client["comment"] = wg.get("comment", "")
    clientwg = ClientWg(**client)
    clientwg.save()
    return funcs.res(funcs.clientwg2json(clientwg))


def clientwg_change(username, wg):
    client = {}

    user_obj = User.objects.get(username=username)

    serverid = wg.get("serverid", "")

    if serverid == "":
        return funcs.reserr("从属server接口是必须的")

    try:
        serverid = int(serverid)
    except Exception:
        return funcs.reserr("从属server接口是必须的")

    try:
        server_obj = ServerWg.objects.get(id=serverid)
    except Exception:
        return funcs.reserr(f"没有id: {serverid} 的server接口")
    
    client["server"] = server_obj

    iface = wg.get("iface", "")

    if iface == "":
        return funcs.reserr("接口名不能为空！")
    else:
        if ClientWg.objects.filter(user=user_obj, iface=iface):
            return funcs.reserr(f"{iface} 已存在！")
        else:
            client["iface"] = iface
    
    """
    privatekey = wg.get("privatekey")
    if privatekey == "":
        return funcs.reserr("privatekey 不能为空")
    else:
        try:
            client["privatekey"] = wgcmd.genkey()
        except Exception:
            return funcs.reserr("privatekey 错误")
        
        client["publickey"] = wgcmd.pubkey(client["privatekye"])
    
    presharedkey = wg.get("presharedkey")
    if presharedkey == "":
        return funcs.reserr("presharedkey 不能为空")
    else:
        try:
            client["presharedkey"] = 
    """

    return funcs.resok()
    
    