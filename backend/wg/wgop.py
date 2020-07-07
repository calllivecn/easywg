from django.db.models import Max


from wg.models import ClientWg, ServerWg
from libwg import wgcmd, funcs


def serverwg_add(wg):
    i = {}

    iface = wg.get("iface")
    if iface:
        if ServerWg.objects.filter(iface=iface):
            return funcs.reserr(f"接口名： {iface} 已存在。")
        else:
            i["iface"] = iface
    else:
        # 如果 iface 为空 就自动生成
        suffix = ServerWg.objects.aggregate(Max("id")).get("id__max")
        if suffix is None:
            i["iface"] = "easywg0"
        else:
            p = 1
            tmp = "easywg" + str(suffix + p)
            while ServerWg.objects.filter(iface=tmp):
                p += 1
                tmp = "easywg" + str(suffix + p)

            i["iface"] = tmp


    net = wg.get("net")
    if net is None:
        return funcs.reserr("network 是必须的")
    else:
        if ServerWg.objects.filter(net=net):
            return funcs.reserr(f"network {net} 已存在！")
        else:
            i["net"] = net
    
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



def serverwg_modify(wg):

    iface_id = wg.get("id")

    try:
        iface = ServerWg.objects.get(id=iface_id)
    except ServerWg.DoesNotExist:
        return funcs.reserr("需要修改的接口不存在，请检查输入。")
    
    iface_name = wg.get("iface")
    if iface_name is None:
        return funcs.reserr("需要修改的接口名不能为空")
    
    iface_old_name  = iface.iface

    iface.iface = iface_name

    net = wg.get("net")
    if net is None:
        return funcs.reserr("network 是必须的")

    # 检查是否有其他接口使用了这个net
    if ServerWg.objects.filter(net=net).exclude(iface=iface_old_name):
        return funcs.reserr("需要修改的网络已存在，请检查输入。")

    iface.net = net

    prikey = wg.get("privatekey")
    if prikey:
        iface.privatekey = prikey
        iface.publickey = wgcmd.pubkey(prikey)
    else:
        iface.privatekey = wgcmd.genkey()
        iface.publickey = wgcmd.pubkey(iface.privatekey)

    iface.persistentkeepalive = wg.get("persistentkeepalive", 35)
    iface.boot = wg.get("boot", True)
    iface.comment = wg.get("comment", "")
    

    lp = wg.get("listenport")

    if lp is None:
        lp_id = ServerWg.objects.aggregate(Max("listenport")).get("listenport__max")
        iface.listenport = lp_id + 1

    else:
        if ServerWg.objects.filter(listenport=lp).exclude(iface=iface_old_name):
            return funcs.reserr(f"listenport: {lp} 已存在， 请检查输入。")
        else:
            iface.listenport = lp

    iface.save()
    return funcs.resok()