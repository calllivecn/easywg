import socket
import ipaddress
from subprocess import run, PIPE

from nftables import Nftables
from pyroute2 import IPDB, NDB, WireGuard


def genkey():
    p = run("wg genkey".split(), stdout=PIPE, text=True)
    return p.stdout

def pubkey(private_key):
    p = run("wg pubkey".split(), input=private_key, stdout=PIPE, text=True)
    return p.stdout

def genpsk():
    p = run("wg genpsk".split(), stdout=PIPE, text=True)
    return p.stdout

def add_wg(ifname, ip):

    with IPDB() as db:
        wg = db.create(ifname=ifname, kind="wireguard")
        wg.add_ip(ip)
        wg.up()
        wg.commit()

def del_wg(ifname):
    with NDB() as db:
        with db.interfaces[ifname] as iface:
            iface.remove()

def list_wg():
    ndb = NDB()
    if_wgs = []
    for _, _, index, ifname, mac, _, typ in ndb.interfaces.summary():
        if typ == "wireguard":
            if_wgs.append((index, ifname, typ))

    return if_wgs

def get_index4ifname(iface):
    for index, ifname, _ in list_wg():
        if iface == ifname:
            return index

def wg_fwmark(ifname, fwmark):
    with WireGuard() as wg:
        wg.set(ifname, fwmark=fwmark)

def wg_set(ifname, private_key, listen_port=None, fwmark=0):
    with WireGuard() as wg:
        wg.set(ifname, private_key=private_key, listen_port=listen_port, fwmark=fwmark)

def wg_peer(ifname, pubkey, peer):
    """
    **kwargs 这里都是可以选项:
    {
        'remove': false,
        'preshared_key': 'Pz8/V2FudFRvVHJ5TXlBZXJvR3Jvc3NlQmljaGU/Pz8=',
        'endpoint_addr': '8.8.8.8', # 这里只能是IP, 不能是域名.
        'endpoint_port': 9999,
        'persistent_keepalive': 25,
        'allowed_ips': ['::/0'],
    }
    """
    # 如果endpoint_addr 是 域名，解析成ip
    # ipv6 也许会有问题
    addr = peer.get("endpoint_addr")
    if addr is not None:
        try:
            ipaddress.ip_address(addr)
            ip = addr
        except ValueError:
            ip = socket.gethostbyname(addr)
        
        peer["endpoint_addr"] = ip
    

    # check allowed-ips 都是网络地址
    allowed_ips = peer.get("allowed_ips")
    if allowed_ips is not None:
        for network in allowed_ips:
            try:
                ipaddress.ip_network(network)
            except ValueError:
                raise ValueError(f"allowed-ips: {network} 不是网络地址， 或网络地址不正确。")
        
    peer['public_key'] = pubkey
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)


############
#
# ip route、　ip rule
#
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
        raise NftableError(f"执行错误: {err}")
    return output


def add_forwarding(ifname, network):
    """
    eg: ifname = easywg0, network = 10.1.1.0/24
    """

    try:
        net = ipaddress.ip_network(network)
    except ValueError:
        raise NftableError(f"网络地址不正确：{network}")

    # nftable v0.9.3 (ubuntu 20.04) 可以不用分ip ip6。inet 是可以直接用于 nat 
    #output = nft(f"add table inet easywg")
    #output = nft(f"add chain inet easywg postrouting {{ type nat hook postrouting priority 10; policy accept; }}")

    #if net.version == 4:
    #    ip_version = "ip"
    #elif net.version == 6:
    #    ip_version = "ip6"

    #output = nft(f"add rule inet easywg postrouting oif {ifname} {ip_version} saddr {network} counter masquerade")

    # nftable v0.8.2 (ubuntu 18.04) 是不支持inet 用于 nat 的。
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


def remove_forwarding(table_name="easywg"):
    nft(f"delete table ip {table_name}")
    nft(f"delete table ip6 {table_name}")




############
#
# test 
#
############


def test_server():

    s_private_key = genkey()

    s_public_key = pubkey(s_private_key)

    c_private_key = genkey()

    c_public_key = pubkey(c_private_key)

    psk_key = genpsk()

    ifname = "server-wg0"
    add_wg(ifname, "10.1.2.1/24")

    wg_set(ifname, s_private_key, 8324)

    peer = {
        "preshared_key": psk_key,
        "endpoint_addr": "www.baidu.com",
        "endpoint_port": 8324,
        "persistent_keepalive": 25,
        "allowed_ips": ["10.1.2.2/32"]
    }

    wg_peer(ifname, c_public_key, peer)

    input("server wireguard 启动完成, 测试后，按回车退出: [enter:]")

    del_wg(ifname)
    print(f"删除 {ifname} 退出。")



def test_client(ifname="wg-test", table_id="1234", fwmark=0x1234):

    ifname_private_key = genkey()

    peer_private_key = genkey()

    peer_public_key = pubkey(peer_private_key)


    add_wg(ifname, "10.1.2.1/24")

    wg_set(ifname, ifname_private_key)

    peer = {}
    peer["endpoint_addr"] = "47.12.2.14"
    peer["endpoint_port"] = 8888
    peer["allowed_ips"] = ["10.1.2.0/24"]
    peer["persistent_keepalive"] = 25

    wg_peer(ifname, peer_public_key, peer)

    set_global_route_wg(ifname, table_id, fwmark)
    input("已添加全局route， 测试完后，按车回清除全书路由：")
    unset_global_route_wg(ifname, table_id, fwmark)


if __name__ == "__main__":
    test_server()
    #test_client()
