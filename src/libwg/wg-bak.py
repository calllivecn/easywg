import os
import tempfile
import subprocess as sp


class TmpKey:

    def __init__(self, context):
        self.tmp = tempfile.NamedTemporaryFile(delete=False) 
        self.tmp.write(context)
        self.tmp.close()
    
    def __entry__(self):
        return self.tmp.name
    
    def __exit__(self, exec_type, exec_value, exec_tb):
        os.remove(self.tmp.name)

def wgcmd(cmd):
    cp = sp.run(["wg"] + cmd, capture_output=True, text=True, check=True)


def wg_add_peer(ifname, pubkey, allowed_ips, preshared_key, endpoint, persistent_keepalive=25):
    with TmpKey(pubkey) as f1, TmpKey(preshared_key) as f2:
        command = f"set {ifname} peer {f1} preshared-key {f2} endpoint {endpoint} persistent-keepalive {persistent_keepalive} allowed-ips {allowed_ips}"
        wgcmd(command.split())


def wg_remove_peer(ifname, pubkey):
    with TmpKey(pubkey) as f1:
        command = f"set {ifname} peer {f1} remove"
        wgcmd(command.split())
