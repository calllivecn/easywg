#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-16 19:47:37
# update 2023-08-16 01:54:15
# author calllivecn <c-all@qq.com>

import os
import copy
import socket
import logging
import ipaddress
from subprocess import (
    run,
    PIPE,
    CalledProcessError
)

# from nftables import Nftables

from pyroute2 import (
    NDB,
    IPRoute,
    WireGuard,
)


logger = logging.getLogger("wg-pyz")


##################
# ~~dns 直接查询，避免系统缓存的影响。~~ 不行哦，缓存的是你的上游nameserver.
##################

# def dnsquery(domainname, dnsserver):
def dnsquery(domainname):
    """
    只需要处理返回一个ip的情况
    return: [] or ["ip1"]
    """

    # ipv4
    try:
        # p = run(["dig", "+short", f"@{dnsserver}", domainname, "A"], stdout=PIPE, text=True, check=True)
        p = run(["dig", "+short", domainname, "A"], stdout=PIPE, text=True, check=True)
    except CalledProcessError as e:
        logger.warning(f"查询 {domainname} 域名异常: {e}")
        ipv4 = []
    else:
        ipv4 = p.stdout.strip().split()

    # ipv6
    try:
        p = run(["dig", "+short", domainname, "AAAA"], stdout=PIPE, text=True, check=True)
    except CalledProcessError as e:
        logger.warning(f"查询 {domainname} 域名异常: {e}")
        ipv6 = []
    
    else:
        ipv6 = p.stdout.strip().split()


    ip  = ipv4 + ipv6
    """
    if len(ip) != 1:
        logger.warning(f"在此应用场景下，域名只能对应一个ip。ipv4 + ipv6 也只需要一个")

    return ip[0]
    """
    if len(ip) == 0:
        logger.warning(f"没有查询到 {domainname} IP")
        return []
    elif len(ip) > 1:
        logger.warning(f"没有查询到多个IP, 这个场景下不应该, 请删除多余的记录只保留一个。")
        return []

    return ip[0]


# 查询dns -> ip
def getaddrinfo(domainname):
    """
    只需要处理返回一个ip的情况
    return: [] or ["ip1"]
    """

    try:
        addrinfo = socket.getaddrinfo(domainname, 0, type=socket.SOCK_DGRAM)
    except socket.gaierror:
        logger.warning(f"{domainname} 没有解析到ip")
        return []
    except socket.timeout:
        logger.warning(f"{domainname} 解析超时")
        return []

    ipv4 = []
    ipv6 = []
    for info in addrinfo:
        if info[0] == socket.AF_INET:
            ipv4.append(info[4][0])
        elif info[0] == socket.AF_INET6:
            ipv6.append(info[4][0])

    ip  = ipv4 + ipv6

    logger.debug(f"查询到: {ip=}")
    """
    if len(ip) != 1:
        logger.warning(f"在此应用场景下，域名只能对应一个ip。ipv4 + ipv6 也只需要一个")

    return ip[0]
    """
    if len(ip) == 0:
        logger.warning(f"没有查询到 {domainname} IP")
        return []
    elif len(ip) > 1:
        logger.warning(f"查询到多个IP, 这个场景下不应该多个IP, 请删除多余的记录只保留一个。")
        return []

    return ip[0]

##################
# 先使用命令方式生成密钥对，以后在添加 cryptography 生成方式
##################

def genkey():
    # 3.7 later
    p = run("wg genkey".split(), stdout=PIPE, text=True, check=True)
    # 3.6
    # p = run("wg genkey".split(), stdout=PIPE, universal_newlines=True, check=True)
    return p.stdout.rstrip(os.linesep)

def pubkey(private_key):
    p = run("wg pubkey".split(), input=private_key, stdout=PIPE, text=True, check=True)
    return p.stdout.rstrip(os.linesep)

def genpsk():
    p = run("wg genpsk".split(), stdout=PIPE, text=True, check=True)
    return p.stdout.rstrip(os.linesep)

############
# ip route、　ip rule
###########

def ip(cmd):
    cp = run(cmd.split(), check=True)

def set_global_route_wg(ifname, table_id, fwmark):

   # ip route add default dev wg0 table 200
   ip(f"ip route add default dev {ifname} table {table_id}")
   ip(f"ip rule add not fwmark {fwmark} table {table_id}")
   ip(f"ip rule add table main suppress_prefixlength 0")


def unset_global_route_wg(ifname, table_id, fwmark):
    ip(f"ip route del default dev {ifname} table {table_id}")
    ip(f"ip rule del not fwmark {fwmark} table {table_id}")
    ip(f"ip rule del table main suppress_prefixlength 0")



##################
# 接口和 ip 操作
##################

def getifname_index(ifname):
    with NDB() as ndb:
        return ndb.interfaces[ifname]["index"]

def ip_list_all():
    """
    这里的address 是MAC 地址
    return:
    [
        {
            "address": "00:00:00:00:00:00",
            "ifname": "lo",
            "index": 1,
            "kind": null
        },
        {
            "address": "7c:10:c9:1e:9e:de",
            "ifname": "enp6s0",
            "index": 2,
            "kind": null
        },
        {
            "address": "8c:c6:81:15:83:b7",
            "ifname": "wlp5s0",
            "index": 3,
            "kind": null
        }
    ]
    """
    with NDB() as ndb:
        r = (
            ndb.interfaces.summary()
            .select("index", "ifname", "address", "kind")
            .format("json")
        )
    return r

def ip_list_addr():
    with IPRoute() as ipr:
        # ipr.get_addr(label="eth0")
        ipr.get_addr()


def ip_addr_add(ifname, CIDR):
    with NDB() as ndb:
        dev = ndb.interfaces[ifname]
        dev.add_ip(CIDR)
        dev.commit()

def ip_link_mtu(ifname: str, mtu: int):
    with NDB() as ndb:
        dev = ndb.interfaces[ifname]
        dev.set(mtu=mtu)
        dev.commit()


def ip_link_add_wg(ifname):
    with NDB() as ndb:
        dev = ndb.interfaces.create(ifname=ifname, kind="wireguard")
        dev.set(state="up")
        dev.commit()


def ip_link_del_wg(ifname):
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
def get_ip_by_addr(domainname):
    ipv4 = set()
    ipv6 = set()
    for info in socket.getaddrinfo(domainname, 0, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP):
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

# server端只需要添加 allowed_ips 的其他路由就行。
# 添加一个路由
def add_route_ifname(net, ifname):
    with NDB() as ndb:
        ndb.routes.create(dst=net, oif=getifname_index(ifname)).commit()

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


# 给 client 实现的VPN mode, 才需要实现策略路由



##################
# Wireguard 操作
##################

def list_wg():
    """
    这里的address 是MAC 地址
    """
    with NDB() as ndb:
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


def wg_peer(ifname, peer):
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
            ipv4s, ipv6s = get_ip_by_addr(addr)

            # 优先使用ipv6, 测试网络可达性。(背景是只有ipv4的机器也可能解析出ipv6地址，需要测试网络可达性)
            for ipv6 in ipv6s:
                if try_ipv6_route(ipv6):
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
           with NDB() as ndb:
               cidr = ndb.routes.get(network)
               if cidr is None:
                   add_route_ifname(net.compressed, ifname)

        
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


def wg_delete_peer(ifname, pubkey):
    peer = {}
    peer["public_key"] = pubkey
    peer["remove"] = True
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


def wg_peer_option(ifname, peer_pubkey, opt_val: dict):
    """
    eg: opt_val {"endpoint_addr": "1.2.3.4"}
    每次重新设置的时候都得加上allowed_ips ? 那之后其他参数是不是也要添加？
    是的每次，重设置都要添加是所有必须的参数
    """
    opt_val["public_key"] = peer_pubkey
    logger.debug(f"{opt_val=}")
    with WireGuard() as wg:
        wg.set(ifname, peer=opt_val)

    


###########
#
# nftables 配置DNAT转发
#
###########

class NftablesError(Exception):
    pass


def nft(cmd):
    nft = Nftables()
    nft.set_json_output(1)
    rc, output, err = nft.cmd(cmd)
    if rc != 0:
        raise NftablesError(f"执行错误: {err}")
    return output


def add_forwarding(ifname, network):
    """
    eg: ifname = easywg0, network = 10.1.1.0/24
    """

    try:
        net = ipaddress.ip_network(network)
    except ValueError:
        raise NftablesError(f"网络地址不正确：{network}")

    # nftable v0.9.3 (ubuntu 20.04) 可以不用分ip ip6。inet 是可以直接用于 nat 
    output = nft(f"add table inet easywg")
    output = nft(f"add chain inet easywg postrouting {{ type nat hook postrouting priority 10; policy accept; }}")

    if net.version == 4:
        ip_version = "ip"
    elif net.version == 6:
        ip_version = "ip6"

    output = nft(f"add rule inet easywg postrouting oif {ifname} {ip_version} saddr {network} counter masquerade")

    # nftable v0.8.2 (ubuntu 18.04) 是不支持inet 用于 nat 的。
    """
    for ip46 in ("ip", "ip6"):
    
        output = nft(f"add table {ip46} easywg")
        
        output = nft(f"add chain {ip46} easywg postrouting {{ type nat hook postrouting priority 10; policy accept; }}")

        output = nft(f"add chain {ip46} easywg forward {{ type filter hook forward priority 10; policy accept; }}")
        
        if ip46 == "ip" and net.version == 4:
            output = nft(f"add rule {ip46} easywg postrouting oif {ifname} {ip46} saddr {network} counter masquerade")
            output = nft(f"add rule {ip46} easywg forward {ip46} saddr {network} counter accept")
        elif ip46 == "ip6" and net.version == 6:
            output = nft(f"add rule {ip46} easywg postrouting oif {ifname} {ip46} saddr {network} counter masquerade")
            output = nft(f"add rule {ip46} easywg forward {ip46} saddr {network} counter accept")
    """


def remove_forwarding(table_name="easywg"):
    nft(f"delete table ip {table_name}")
    nft(f"delete table ip6 {table_name}")



##################
#
# 单元测试
#
##################


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
    # test()
    # getifname_ip("enp6s0")
    list_wg()