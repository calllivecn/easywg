#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-16 19:47:37
# author calllivecn <calllivecn@outlook.com>

import socket
import ipaddress


from pyroute2 import (
    NDB,
    WireGuard,
)


def getifname_index(ifname):
    with NDB() as ndb:
        return ndb.interfaces[ifname]["index"]

def ip_list_all():
    """
    return:
    [
        {
            "address": "00:00:00:00:00:00",
            "flags": 65609,
            "ifname": "lo",
            "index": 1,
            "kind": null,
            "target": "localhost",
            "tflags": 0
        },
        {
            "address": "aa:aa:aa:aa:aa:aa",
            "flags": 4099,
            "ifname": "enp1s0",
            "index": 2,
            "kind": null,
            "target": "localhost",
            "tflags": 0
        }
    ]
    """
    ndb = NDB()
    r = (
        ndb.interfaces.summary()
        .select("index", "ifname", "address", "kind")
        .format("json")
    )
    return r


def ip_addr_add(ifname, CIDR):
    with NDB() as ndb:
        dev = ndb.interfaces[ifname]
        dev.add_ip(CIDR)
        # dev.set("state", "up")
        dev.commit()


def ip_link_add_wg(ifname, CIDR):
    with NDB() as ndb:
        dev = ndb.interfaces.create(ifname=ifname, kind="wireguard")
        dev.add_ip(CIDR)
        dev.set(state="up")
        dev.commit()


def ip_link_down_wg(ifname):
    with NDB() as ndb:
        dev = ndb.interfaces[ifname]
        dev.set(state="down")
        dev.remove()
        dev.commit()


def getifname_ip(ifname):
    """
    查询ipv4 + ipv6
    如果给定接口名不存在，返回空list: []
    return:
    [
        {
            "address": "192.168.8.7",
            "ifname": "wlp5s0",
            "prefixlen": 24
        },
        {
            "address": "fe80::ae76:253a:4c11:7772",
            "ifname": "wlp5s0",
            "prefixlen": 64
        }
    ]
    """
    ndb = NDB()
    r = (
        ndb.addresses.summary()
        .select("ifname", "address", "prefixlen")
        .filter(ifname=ifname)
        .format("json")
    )
    return r


# 测试当前网络环境能使用ipv6不
def try_ipv6_route(ip):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        # sock.connect(("2400:3200:baba::1", 2022))
        sock.connect((ip, 2022))
        return True
    except OSError:
        # 网络不可以达
        return False

    finally:
        sock.close()


# 从域名解析ipv4, ipv6
def gethostbyaddr(name):
    ipv4 = set()
    ipv6 = set()
    for info in socket.getaddrinfo(name, 0, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP):
        family = info[0]
        ip = info[4][0]

        if socket.AF_INET == family:
            ipv4.add(ip)
        elif socket.AF_INET6 == family:
            ipv6.add(ip)
    
    return tuple(ipv4), tuple(ipv6)



##################
# route 操作
##################

# server端 只需要添加 nets 的其他路由就行。
# 添加一个路由
def add_route_ifname(nets, ifname):
    with NDB() as ndb:
        r = ndb.routes.create(dst=nets, oif=getifname_index(ifname)).commit()

def add_route_via(nets, via):
    with NDB() as ndb:
        #r = ndb.routes.create(dst=nets, via=via).commit()
        r = ndb.routes.create(dst=nets)
        r.set(gateway=via)
        #r.set(proto=2) # proto字段的定义在内核中并没有实质的意义，只是一个显示字段。RTPROT_UNSPEC表示未指定； 其他值可以查看 vim /etc/iproute2/rt_protos
        r.commit()

def del_route(nets):
    with NDB() as ndb:
        r = ndb.routes[nets]
        r.remove()
        r.commit()


# 给client 实现的VPN mode, 才需要实现策略路由



##################
# Wireguard 操作
##################

def list_wg():
    ndb = NDB()
    r = (
        ndb.interfaces.summary()
        .filter(kind="wireguard")
        .select('index', 'ifname', 'address', 'kind')
        .format("json")
    )
    return r


def wg_fwmark(ifname, fwmark):
    with WireGuard() as wg:
        wg.set(ifname, fwmark=fwmark)

def wg_set(ifname, private_key, listen_port=None, fwmark=None):
    with WireGuard() as wg:
        wg.set(ifname, private_key=private_key, listen_port=listen_port, fwmark=fwmark)


def wg_peer(ifname, pubkey, peer):
    """
    client 端才需要指定 server 地址(endpoint_addr)
    **kwargs 这里都是可以选项:
    {
        'remove': false, # 可选

        'public_key': 'l5NCG5NmhSB4rbFVGZACPiKEL01+tQnjD6dRHCjXtkQ=',
        'preshared_key': 'Pz8/V2FudFRvVHJ5TXlBZXJvR3Jvc3NlQmljaGU/Pz8=', # 可选
        'endpoint_addr': '8.8.8.8', # 这里只能是IP, 不能是域名. # 可选
        'endpoint_port': 9999, # required only if endpoint_addr
        'persistent_keepalive': 25, # 可选
        'allowed_ips': ['::/0'],
    }
    """

    # 如果 endpoint_addr 是域名, 需要解析成ip
    # ipv6 也许会有问题
    addr = peer.get("endpoint_addr")
    ip = None
    # addr 说明需要指定对端地址
    if addr is not None:
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            # 说明是域名, 需要解析成IP才能给WG使用
            ipv4s, ipv6s = gethostbyaddr(addr)

            # 优先使用ipv6, 测试网络可达性。(背景是只有ipv4的机器也可能解析出ipv6地址，os 需要测试网络可达性)
            for ipv6 in ipv6s:
                if try_ipv6_route(ip):
                    ip = ipv6
                    break
            
            # 否则使用 ipv4
            if ip is None:
                ip = ipv4s[0]

        peer["endpoint_addr"] = ip

    # check allowed-ips 都是网络地址
    allowed_ips = peer.get("allowed_ips")
    peer["allowed_ips"] = allowed_ips
    if allowed_ips is not None:
        for network in allowed_ips:

           try:
               net = ipaddress.ip_network(network)
           except ValueError:
               raise ValueError(f"allowed-ips: {network} 不是网络地址， 或网络地址不正确。")
        
        # 这个接口上的，添加其他网络
        add_route_ifname(net, ifname)

        
    peer['public_key'] = pubkey
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


def wg_delete_peer(ifname, pubkey):
    peer = {}
    peer["public_key"] = pubkey
    peer["remove"] = True
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)



def test():

    print("="*10, "ip list:", "="*10)
    print(ip_list_all())

    print("="*10, "wg list:", "="*10)
    print(list_wg())

    # 需要 root
    # print("="*10, "wg create:", "="*10)
    # ip_link_add_wg("wg-test0", "10.1.3.0/24")
    # input("按回车继续。。。")
    # ip_link_down_wg("wg-test0")


if __name__ == "__main__":
    test()