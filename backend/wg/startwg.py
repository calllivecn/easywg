
from libwg import wgcmd


def addstartwg(ifname, privatekey, listenport, ip, peers):

    wgcmd.add_wg(ifname, ip)

    wgcmd.wg_set(ifname, privatekey, listenport)

    for peer in peers:
        wgcmd.wg_peer(ifname, peer["pubkey"], peer)
    

def exit_del(ifname):
    wgcmd.del_wg(ifname)

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
    from wg.models import ServerWg
    for boot in ServerWg.objects.filter(boot=True):
        exit_del(boot.ifname)
