
from pyroute2 import IPRoute
from pyroute2 import NDB

class IP:

    def __init__(self):
        self.ip = IPRoute()

    def __enter__(self):
        return self.ip
    
    def __exit__(self, exec_type, exec_value, exec_tb):
        self.ip.close()


def ip_link_lookup(ifname):
    with IP() as ip:
        return ip.link_lookup(ifname=ifname)[0]

def ip_link_add_wg(dev):
    with IP() as ip:
        ip.link("add", ifname=dev, kind="wiregurad")

def ip_addr_add(dev, addr, mark=24):
    with IP() as ip:
        ip.addr("add", ifname=dev, address=addr, mark=mark)

def ip_link_up(dev):
    with IP() as ip:
        ip.link("set", ifname=dev, state="up")

def ip_link_down(dev):
    with IP() as ip:
        ip.link("set", ifname=dev, state="down")


def ip_list_wg():
    ndb = NDB()
    if_wgs = []
    for _, _, index, ifname, mac, _, typ in ndb.interfaces.summary():
        if typ == "wireguard":
            if_wgs.append((index, ifname, typ))

    return if_wgs


def add_default_table(ifname, table_id):
    with IP() as ip:
        ip.route("add", )

def test():
    from pprint import pprint
    pprint(ip_list_wg())

if __name__ == "__main__":
    test()