#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-16 19:47:37
# author calllivecn <c-all@qq.com>

import socket
import ipaddress


from pyroute2 import (
    NDB,
    WireGuard,
)


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
    return ndb.interfaces.summary().format("json")


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
        dev.set("state", "up")
        dev.commit()


def ip_link_down_wg(ifname):
    with NDB() as ndb:
        dev = ndb.interfaces[ifname]
        dev.set("state", "down")
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
    return ndb.addresses.summary().select("ifname", "address", "prefixlen").filter(ifname=ifname).format("json")


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


def ip_list_wg():
   ndb = NDB()
   ifname = ndb.interfaces.summary()
   ifname = ifname.filter(kind="wireguard").select('index', 'ifname', 'address', 'kind')
   return ifname.format("json")


def wg_fwmark(ifname, fwmark):
    with WireGuard() as wg:
        wg.set(ifname, fwmark=fwmark)

def wg_set(ifname, private_key, listen_port=None, fwmark=0):
    with WireGuard() as wg:
        wg.set(ifname, private_key=private_key, listen_port=listen_port, fwmark=fwmark)


def wg_peer(ifname, pubkey, peer):
    """
    client 端才需要指定 server 地址(endpoint_addr)
    **kwargs 这里都是可以选项:
    {
        'remove': false,

        'public_key': 'l5NCG5NmhSB4rbFVGZACPiKEL01+tQnjD6dRHCjXtkQ=',
        'preshared_key': 'Pz8/V2FudFRvVHJ5TXlBZXJvR3Jvc3NlQmljaGU/Pz8=',
        'endpoint_addr': '8.8.8.8', # 这里只能是IP, 不能是域名.
        'endpoint_port': 9999,
        'persistent_keepalive': 25,
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
    peer["allowed_ips"] = peer.get("allowed_ips").split(",")
    #if allowed_ips is not None:
    #    for network in allowed_ips:
    #        try:
    #            ipaddress.ip_network(network)
    #        except ValueError:
    #            #raise ValueError(f"allowed-ips: {network} 不是网络地址， 或网络地址不正确。")
        
    peer['public_key'] = pubkey
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


def wg_delete_peer(ifname, pubkey):
    peer = {}
    peer["public_key"] = pubkey
    peer["remove"] = True
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


def add_default_table(ifname, table_id):
    with NDB() as ndb:
        ndb.route("add", )


def test():
    from pprint import pprint

    print("="*10, "ip list:", "="*10)
    pprint(ip_list_all())

    print("="*10, "wg list:", "="*10)
    pprint(ip_list_wg())

    print("="*10, "wg create:", "="*10)
    ip_link_add_wg("wg-test0", "10.1.3.0/24")
    input("按回车继续。。。")
    ip_link_down_wg("wg-test0")


if __name__ == "__main__":
    test()