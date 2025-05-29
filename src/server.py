
import sys
import copy
import queue
import signal
import atexit
import ipaddress


import funcs
import util
from log import logger


from checkalive import (
    CheckAlive,
    CPeer,
)
from packet import (
    PacketType,
)

def serverhub_daemon(wg_ip):
    pass


def server(conf):
    # 配置wg
    ifname = conf["ifname"]
    wg_name = ifname["interface"]

    # add wg
    util.ip_link_add_wg(wg_name)

    # set MTU
    wg_mtu = int(ifname.get("MTU"))
    if wg_mtu is not None:
        util.ip_link_mtu(wg_name, wg_mtu)


    atexit.register(lambda :util.ip_link_del_wg(wg_name))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    
    self_ipv4 = None
    self_ipv6 = None
    # 配置 wg 接口ip地址
    for CIDR in ifname["address"]:
        util.ip_addr_add(wg_name, CIDR)

        ip = ipaddress.ip_address(CIDR.split("/")[0])
        if ip.version == 4:
            if self_ipv4 is None:
                self_ipv4 = ip.exploded
        elif ip.version == 6:
            if self_ipv6 is None:
                self_ipv6 = ip.exploded

    util.wg_set(wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))
    logger.debug(f"配置接口：{wg_name}")

    checkalive = CheckAlive()
    checkalive.conf = conf
    th_server = funcs.start_thread(target=checkalive.server, args=(self_ipv6, self_ipv4), name="CheckAlive.server()")
    logger.debug(f"CheckAlive 线程已启动: {th_server.name}")

    for wg_conf in conf["peers"]:

        peer_conf = copy.deepcopy(wg_conf)
        info = peer_conf["info"]
        peer = peer_conf["peer"]
        
        endpoint_addr = peer.get("endpoint_addr")
        if endpoint_addr is not None:
            addr = util.getaddrinfo(endpoint_addr)

            if len(addr) == 0:
                logger.warning(f"没有查询到 {endpoint_addr} IP, 可能出错了。请检查")
                continue

            peer["endpoint_addr"] = addr
        
        logger.debug(f"配置peer: {peer}")
        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)

        
        # 为每个peer 启动 checkalive
        wg_check_ip = info.get("wg_check_ip")
        if wg_check_ip:
            wg_check_port = info.get("wg_check_port", 19000)

            cpeer = (
                PacketType.PING_REPLY,
                wg_check_ip,
                wg_check_port,
                )

            peer_value = CPeer(
                queue.Queue(128),
                wg_conf["peer"],
            )

            checkalive.peers[cpeer] = peer_value

            logger.debug(f"为 {wg_check_ip}:{wg_check_port} 启动 checkalive")
            funcs.start_thread(target=checkalive.ping, args=(checkalive.sock6, cpeer), name=f"check_alive-{wg_check_ip}")

    th_server.join()