#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-16 19:47:37
# update 2023-08-16 01:54:15
# author calllivecn <calllivecn@outlook.com>


import copy
import socket
import ipaddress

# from nftables import Nftables

from pyroute2 import (
    NDB,
    IPRoute,
    WireGuard,
)


from log import logger
from wggenkey import WireGuardKeyGenerator


##################
# ~~dns 直接查询，避免系统缓存的影响。~~ 不行哦，缓存的是你的上游nameserver.
# 命令行版本
##################

# 查询dns -> ip
def getaddrinfo(domainname):
    """
    只需要处理返回一个ip的情况
    return: [] or ["ip1"]
    """

    try:
        addrinfo = socket.getaddrinfo(domainname, 0, type=socket.SOCK_DGRAM)
    except socket.gaierror:
        logger.warning(f"{domainname} 没有解析到ip; 可能是系统没有网络连接")
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
        logger.warning("查询到多个IP, 这个场景下不应该多个IP, 请删除多余的记录只保留一个。")
        return []

    return ip[0]

##################
# cryptography 方式生成密钥对
##################

def genkey() -> tuple[str, str]:
    wg = WireGuardKeyGenerator()
    return wg.genkey(), wg.pubkey()

def pubkey(private_key: str) -> str:
    """
    生成公钥
    private_key: str, base64 编码的私钥
    return: str, base64 编码的公钥
    """
    wg = WireGuardKeyGenerator()
    return wg.pubkey(private_key)

def genpsk() -> str:
    """
    生成预共享密钥
    return: str, base64 编码的预共享密钥
    """
    return WireGuardKeyGenerator().genpsk()


"""
############
# ip route、　ip rule 、 命令行版本
###########

def ip(cmd):
    return run(cmd.split(), check=True)

def set_global_route_wg(ifname, table_id, fwmark):

   # ip route add default dev wg0 table 200
   ip(f"ip route add default dev {ifname} table {table_id}")
   ip(f"ip rule add not fwmark {fwmark} table {table_id}")
   ip(f"ip rule add table main suppress_prefixlength 0")


def unset_global_route_wg(ifname, table_id, fwmark):
    ip(f"ip route del default dev {ifname} table {table_id}")
    ip(f"ip rule del not fwmark {fwmark} table {table_id}")
    ip(f"ip rule del table main suppress_prefixlength 0")
"""


##################
# 接口和 ip 操作
##################

def getifname_index(ifname):
    with IPRoute() as ipr:
        return ipr.link_lookup(ifname=ifname)[0]


def ip_addr_ifname(ifname: str) -> list[tuple[str, int]]:
    """
    return: str, 返回接口的IPv4 IPv6地址
    """
    ips = []
    with IPRoute() as ipr:

        index = ipr.link_lookup(ifname=ifname)[0]     

        # 拿ipv4 时不能使用 fmaily 参数？不然拿到是空[]
        # for r in ipr.get_addr(label=ifname, fmaily=socket.AF_INET):
        # 如果使用index参数就能直接拿到ipv4 ipv6...
        for r in ipr.get_addr(index=index):
            ips.append((r.get_attr("IFA_ADDRESS"), r["prefixlen"]))

    if len(ips) == 0:
        logger.warning(f"接口 {ifname} 没有配置IP地址")
        return []

    return ips


def ip_addr_add(ifname: str, cidr: str):
    with IPRoute() as ipr:
        ipr.addr('add',
                 index=getifname_index(ifname),
                 address=cidr.split("/")[0],
                 prefixlen=int(cidr.split("/")[1]),
                )


def ip_link_mtu(ifname: str, mtu: int):
    with IPRoute() as ipr:
        ipr.link('set',
                 index=getifname_index(ifname),
                 mtu=mtu,
                )


def ip_link_add_wg(ifname):
    with IPRoute() as ipr:
        ipr.link('add',
                 index=getifname_index(ifname),
                 kind='wireguard',
                )


def ip_link_del_wg(ifname):
    with IPRoute() as ipr:
        ipr.link('del',
                 index=getifname_index(ifname),
                )


# 测试当前网络环境能使用ipv6不
def try_ipv6_route(ip) -> bool:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        # sock.connect(("2400:3200:baba::1", 19000))
        sock.connect((ip, 19000))
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



############
# ip route、　ip rule 、 pyroute2 版本
###########

# server端只需要添加 allowed_ips 的其他路由就行。
# 添加一个路由
def add_route_ifname(net, ifname):
    with IPRoute() as ipr:
        try:
            ipr.route('add', dst=net, oif=ipr.link_lookup(ifname=ifname)[0])
        except KeyError:
            # 如果路由已经存在，可能是因为之前添加过了。
            logger.debug(f"路由 {net} 已经存在，跳过添加。")
        except Exception as e:
            logger.error(f"添加路由失败: {net} {ifname} Except: {e}")
            raise


def add_route_via(net, via):
    with IPRoute() as ipr:
        try:
            ipr.route('add', dst=net, via=via)
        except KeyError:
            # 如果路由已经存在，可能是因为之前添加过了。
            logger.debug(f"路由 {net} 已经存在，跳过添加。")
        except Exception as e:
            logger.error(f"添加路由失败: {net} {via} Except: {e}")
            raise


def del_route(net):
    with IPRoute() as ipr:
        ipr.route('del', dst=net)


def allowed_ip_vpn_up(ifname: str, peer: dict):
    """
    使用 pyroute2 设置 WireGuard 接口的 allowed_ips。
    """
    p = copy.deepcopy(peer) # 确保不修改原始数据
    p["allowed_ips"] = ["0.0.0.0/0", "::/0"]

    wg_peer(ifname, p)


def allowed_ip_vpn_down(ifname: str, peer: dict):
    p = copy.deepcopy(peer)
    wg_peer(ifname, p)


def set_global_route_wg_pyroute2(ifname: str, table_id: int, fwmark: int):
    """
    使用 pyroute2 设置全局路由和策略路由。
    对应命令行：
    ip route add default dev <ifname> table <table_id>
    ip rule add not fwmark <fwmark> table <table_id>
    ip rule add table main suppress_prefixlength 0
    """
    with IPRoute() as ipr:
        # 添加默认路由到指定的路由表
        # 命令: ip route add default dev <ifname> table <table_id>
        for family, default in [(socket.AF_INET, "0.0.0.0/0"), (socket.AF_INET6, "::/0")]:
            ipr.route('add',
                    dst=default,
                    oif=ipr.link_lookup(ifname=ifname)[0],  # 获取接口索引
                    table=table_id,
                    family=family
                    )
            logger.debug2(f"Added default route via {ifname} to table {table_id}")

            # 添加策略路由规则：非 fwmark 的流量使用指定的路由表
            # 命令: ip rule add not fwmark <fwmark> table <table_id>
            ipr.rule('add',
                    priority=1000,  # 规则的优先级，确保它在其他规则之前生效
                    # 这是一个 'not' 匹配，需要使用 'not_fwmark' 属性
                    fwmark=fwmark,
                    flags=2,  # 使用 'invert' 标志来表示 'not fwmark'
                    table=table_id,
                    family=family
                    )
            logger.debug2(f"Added rule: not fwmark {fwmark} -> table {table_id}")

            # 添加策略路由规则：抑制 main 表的 prefixlength 0 (即默认路由)
            # 这通常用于确保自定义路由表生效，而不会被 main 表的默认路由干扰
            # 命令: ip rule add table main suppress_prefixlength 0
            ipr.rule('add',
                    priority=2000,  # 确保在自定义规则之后
                    table=254,  # 使用 'main' 表
                    suppress_prefixlen=0,
                    family=family
                    )
            logger.debug2("Added rule: table main suppress_prefixlength 0")

def unset_global_route_wg_pyroute2(ifname: str, table_id: int, fwmark: int):
    """
    使用 pyroute2 取消设置全局路由和策略路由。
    对应命令行：
    ip route del default dev <ifname> table <table_id>
    ip rule del not fwmark <fwmark> table <table_id>
    ip rule del table main suppress_prefixlength 0
    """
    with IPRoute() as ipr:
        # 删除默认路由
        # 命令: ip route del default dev <ifname> table <table_id>

        try:

            for family, default in [(socket.AF_INET, "0.0.0.0/0"), (socket.AF_INET6, "::/0")]:
                ipr.route('del',
                        dst=default,
                        oif=ipr.link_lookup(ifname=ifname)[0],
                        table=table_id,
                        family=family
                        )
                logger.debug2(f"Deleted default route via {ifname} from table {table_id}")

            # 删除策略路由规则：非 fwmark 的流量使用指定的路由表
            # 命令: ip rule del not fwmark <fwmark> table <table_id>
                ipr.rule('del',
                        priority=1000, # 删除时也需要指定优先级，或者其他唯一标识
                        fwmark=fwmark,
                        invert=True,  # 使用 'invert' 来表示 'not fwmark'
                        table=table_id,
                        family=family
                        )
                logger.debug2(f"Deleted rule: not fwmark {fwmark} -> table {table_id}")

            # 删除策略路由规则：抑制 main 表的 prefixlength 0
            # 命令: ip rule del table main suppress_prefixlength 0
                ipr.rule('del',
                        priority=2000, # 删除时也需要指定优先级
                        table=254,  # 使用 'main' 表
                        suppress_prefixlength=0,
                        family=family
                        )
                logger.debug2("Deleted rule: table main suppress_prefixlength 0")

        except Exception as e:
            logger.debug2(f"Error deleting route: {e}")





##################
# Wireguard 操作
##################

def list_wg_all() -> list[str]:
    wg_list = []
    with IPRoute() as ipr:
        for wg in ipr.link("dump", kind="wireguard"):
            wg_list.append(wg.get_attr("IFLA_IFNAME"))
    
    return wg_list


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
    ~~每次重新设置的时候都得加上allowed_ips ? 那之后其他参数是不是也要添加？~~
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
    output = nft("add table inet easywg")
    output = nft("add chain inet easywg postrouting { type nat hook postrouting priority 10; policy accept; }}")

    if net.version == 4:
        ip_version = "ip"
    elif net.version == 6:
        ip_version = "ip6"
    else:
        raise NftablesError(f"不支持的网络协议版本：{network}")

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
    print("="*10, "ifname index:", "="*10)
    # print(f"""{getifname_index("wg-pyz")=}""")

    print("="*10, "ip list all:", "="*10)
    # print(ip_list_all(ndb))

    print("="*10, "ip addr ifname:", "="*10)
    print(ip_addr_ifname("wgpy"))

    # for ip_addrs in ip_addr_list():
    #     msg = pprint.pformat(ip_addrs)
    #     print("="*10, ":", "="*10)
    #     print(f"{msg}")

    print("="*10, "wg list:", "="*10)
    # print(list_wg(ndb))

    print("="*10, "getifname_ip list:", "="*10)
    # print(getifname_ip(ndb, "enp6s0"))

    # 需要 root
    # print("="*10, "wg create:", "="*10)
    # ip_link_add_wg("wg-test0", "10.1.3.0/24")
    # input("按回车继续。。。")
    # ip_link_down_wg("wg-test0")


if __name__ == "__main__":
    # test()
    test()