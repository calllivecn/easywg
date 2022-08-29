
from subprocess import run, PIPE

from pyroute2 import IPDB, NDB, IPRoute, WireGuard

def genkey():
    p = run("wg genkey".split(), stdout=PIPE, text=True)
    return p.stdout

def pubkey(private_key):
    p = run("wg pubkey".split(), input=private_key, stdout=PIPE, text=True)
    return p.stdout

def genpsk():
    p = run("wg pskkey", stdout=PIPE, text=True)
    return p.stdout


def add_wg(ifname, CIDR):

    with NDB() as ndb:
        wg = ndb.interfaces.create(ifname=ifname, kind="wireguard")
        wg.add_ip(CIDR)
        wg.set(state="up")
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

def wg_peer(ifname, pubkey, **kwargs):
    """
    **kwargs 这里都是可以选项:
    {
        'remove': false,
        'preshared_key': 'Pz8/V2FudFRvVHJ5TXlBZXJvR3Jvc3NlQmljaGU/Pz8=',
        'endpoint_addr': '8.8.8.8',
        'endpoint_port': 9999,
        'persistent_keepalive': 25,
        'allowed_ips': ['::/0'],
    }
    """
    peer = {}
    peer['public_key'] = pubkey
    peer.update(**kwargs)
    with WireGuard() as wg:
        wg.set(ifname, peer=peer)

###############
# route vpn 模式使用
###############
def global_route_wg(ifname, fwmark, table_id):
    wg_fwmark(ifname, fwmark)

    oif = get_index4ifname(ifname)

    with IPRoute() as ip:
        ip.route("add", dst="0.0.0.0/0", oif=oif, table=table_id)
        ip.rule("add", table=table_id, fwmark=fwmark, action="RT_SCOPE_NOWHERE")
        # 到这里不行了。 pyroute２ 还是有很多问题。
        ip.rule("add", action="FRA_SUPPRESS_PREFIXLENGTH")
        input("回车 continue... ")

        ip.route("delete", dst="0.0.0.0/0", oif=oif, table=table_id)
        #db.rules.create()

if __name__ == "__main__":
    add_wg("wg500", "1.1.1.1/24")

    private_key = genkey()
    public_key = pubkey(private_key)

    wg_set("wg500", private_key)

    global_route_wg("wg500", 0x123, 123)

    del_wg("wg500")
