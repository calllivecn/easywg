import subprocess as sp


def wgcmd(cmd):
    cp = sp.run(["wg"] + cmd, capture_output=True, text=True, check=True)



def wg_add_peer(ifname, pubkey, )