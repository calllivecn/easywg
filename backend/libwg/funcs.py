from os import path
import ipaddress

import jinja2
from django.conf import settings
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
    s = str(ipaddress.IPv4Interface(address)).split("/")[0]
    addr = s + "/32"
    print("client[allowedips_s]: ", addr)
    return addr


def getnet_c():
    return str()



def render(template_name, obj):
    with open(path.sep.join([settings.BASE_DIR, "templates", template_name])) as f:
        temp_content = f.read()

    temp = jinja2.Template(temp_content)

    return temp.render(obj)

