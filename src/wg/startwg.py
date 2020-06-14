from wg.models import ServerWg

from libwg import wgcmd


def addstartwg(ifname, privatekey, listenport, ip, peers):

    wgcmd.add_wg(ifname, ip)

    wgcmd.wg_set(ifname, privatekey, listenport)

    for peer in peers:
        wgcmd.wg_peer(peer)
    

def exit_del(ifname):
    wgcmd.del_wg(ifname)