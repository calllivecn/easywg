
from subprocess import run, PIPE

from pyroute2 import IPDB, NDB, WireGuard


def genkey():
    p = run("wg genkey".split(), stdout=PIPE, text=True)
    return p.stdout

def pubkey(private_key):
    p = run("wg pubkey".split(), input=private_key, stdout=PIPE, text=True)
    return p.stdout

def genpsk():
    p = run("wg pskkey", stdout=PIPE, text=True)
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
        'endpoint_addr': '8.8.8.8',
        'endpoint_port': 9999,
        'persistent_keepalive': 25,
        'allowed_ips': ['::/0'],
    }
    """
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
   ip(f"ip route add def dev {ifname} table {table_id}")
   ip(f"ip rule add not fwmark {fwmark} table {table}")
   ip(f"ip rule add table main suppress_prefixlength 0")


def unset_global_route_wg(ifname, table_id):
    ip(f"ip route del default dev {ifname} table {table_id}")
    ip(f"ip rule del table main suppress_prefixlength 0")




def test(ifname="wg-test", table_id="1234"):

    ifname_private_key = genkey()

    peer_private_key = genkey()

    peer_public_key = pubkey(peer_private_key)


    add_wg(ifname, "10.1.2.1/24")

    wg_set(ifname, ifname_private_key)

    peer = {}
    peer["endpoint_addr"] = "calllive.cc"
    peer["endpoint_port"] = 8888
    peer["allowed_ips"] = ["10.1.2.0/24"]
    peer["persistent_keepalive"] = 25

    wg_peer(ifname, peer_public_key, peer)


if __name__ == "__main__":
    test()
