import ipaddress

from django.http import JsonResponse

def json(j):
    return JsonResponse(j, json_dumps_params={"ensure_ascii": False, "indent": 4})

def res(data):
    j = {}
    j["code"] = 0
    j["msg"] ="ok"
    j["data"] = data
    return json(j)

def resok(msg="ok"):
    return json({"code": 0, "msg": msg})

def reserr(msg, code=-1):
    return json({"code": code, "msg": msg})



def serverwg2json(iface):
    """
    iface: ServerWg.objects.get()
    """
    iface_json = {
              "id": iface.id,
              "iface": iface.iface,
              "address": iface.address,
              "listenport": iface.listenport,
              "network": iface.network,
              "ip": iface.ip,
              "privatekey": iface.privatekey,
              "publickey": iface.publickey,
              "listenport": iface.listenport,
              "persistentkeepalive": iface.persistentkeepalive,
              "boot": iface.boot,
              "comment": iface.comment
          }

    return iface_json


def clientwg2json(iface):
    """
    iface: ClientWg.objects.get()
    """
    iface_json = {
              "id": iface.id,
              "iface": iface.iface,
              "ip": iface.ip,
              #"privatekey": iface.privatekey,
              "publickey": iface.publickey,
              #"presharedkey": iface.presharedkey,
              #"persistentkeepalive": iface.persistentkeepalive,
              "allowedips": iface.allowedips_c,
              "comment": iface.comment
          }
    return iface_json


def gateway(network):
    net = ipaddress.IPv4Network(network)
    ip = next(net.hosts())
    return str(ip) + "/" + net.with_prefixlen.split("/")[1]

def getipaddr(network):
    net = ipaddress.IPv4Network(network)
    gen = net.hosts()
    gateway = next(gen)

    for ip in gen:
        yield str(ip) + "/" + net.with_prefixlen.split("/")[1]


def getnet_s(address):
    return str(ipaddress.IPv4Interface(address))

def getnet_c():
    return str()