
from libwg import wgcmd


def addstartwg(ifname, privatekey, listenport, ip, peers):

    wgcmd.add_wg(ifname, ip)

    wgcmd.wg_set(ifname, privatekey, listenport)

    for peer in peers:
        wgcmd.wg_peer(ifname, peer["pubkey"], peer)
    

def startserver():
    from wg.models import ServerWg, ClientWg
    for boot in ServerWg.objects.filter(boot=True):
        boot_clientwgs = ClientWg.objects.filter(server=boot)

        peers = []
        for boot_clientwg in boot_clientwgs:
            peer = {}
            peer["pubkey"] = boot_clientwg.publickey
            peer["preshared_key"] = boot_clientwg.presharedkey
            peer["allowed_ips"] = boot_clientwg.allowedips_s
            peer["persistent_keepalive"] = boot_clientwg.persistentkeepalive

            peers.append(peer)

        addstartwg(boot.iface, boot.privatekey, boot.listenport, boot.ip, peers)


def stopserver():
    print("stop server")
    for _, iface, _ in wgcmd.list_wg():
        wgcmd.del_wg(iface)
