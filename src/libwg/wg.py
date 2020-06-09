from subprocess import run, PIPE

from pyroute2 import NDB, WireGuard

def genkey():
    p = run("wg genkey".split(), stdout=PIPE, text=True)
    return p.stdout

def pubkey(private_key):
    p = run("wg pubkey", input=private_key.encode(), stdout=PIPE, text=True)
    return p.stdout

def genpsk():
    p = run("wg pskkey", stdout=PIPE, text=True)
    return p.stdout

def add_wg(ifname, ip):

    with NDB() as db:
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


def wg_set(ifname, private_key, listen_port, fwmark=0):
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
# route mange
###############
def 


if __name__ == "__main__":
    add_wg("wg500", "1.1.1.0/24")
    del_wg("wg500")
