
import copy
import queue
import signal
import ipaddress


import funcs
import util
from log import logger


from checkalive import (
    CheckAlive,
    QueuePeer,
    PacketPeer,
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


    exit_event = funcs.get_event()

    signal.signal(signal.SIGTERM, lambda sig, frame: exit_event.set())
    
    self_ipv4 = None
    self_ipv6 = None
    # 配置 wg 接口ip地址
    for cidr in ifname["address"]:
        util.ip_addr_add(wg_name, cidr)

        ip = ipaddress.ip_address(cidr.split("/")[0])
        if ip.version == 4:
            if self_ipv4 is None:
                self_ipv4 = ip.exploded
        elif ip.version == 6:
            if self_ipv6 is None:
                self_ipv6 = ip.exploded

    util.wg_set(wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))
    logger.debug(f"配置接口：{wg_name}")

    checkalive = CheckAlive(conf)
    funcs.start_thread(target=checkalive.server, args=(self_ipv6, self_ipv4), name="CheckAlive.server()", daemon=True)

    for wg_conf in conf["peers"]:

        peer_conf = copy.deepcopy(wg_conf)
        info = peer_conf["info"]
        peer = peer_conf["peer"]
        
        endpoint_addr = peer.get("endpoint_addr")
        if endpoint_addr is not None:
            addr = util.getaddrinfo(endpoint_addr)

            if len(addr) == 0:
                logger.warning(f"没有查询到 {endpoint_addr} IP, 可能出错了。请检查")
            else:
                # fix 如果启动的时候没有解析到域名会不添加peer，就用本地地址。
                addr = "127.0.0.1"

            peer["endpoint_addr"] = addr
        
        logger.debug(f"配置peer: {peer}")
        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)
        

        # 为allowed_ips 中其他网络添加路由信息
        for cidr in peer.get("allowed_ips", []):
            net = ipaddress.ip_network(cidr)

            add_route_flag = True
            # 排除ifname地址自动添加的路由。
            for ifaddr in ifname["address"]:
                ifaddr = ipaddress.ip_interface(ifaddr)
                if ifaddr.network.overlaps(net):
                    logger.debug(f"跳过 {cidr}，因为与接口地址 {ifaddr.network} 重叠")
                    add_route_flag = False


            if add_route_flag:
                util.add_route_ifname(cidr, wg_name)
                logger.debug(f"添加 {cidr}")

        
        # 为每个peer 启动 checkalive
        wg_check_ip = info.get("wg_check_ip")
        if wg_check_ip:
            wg_check_port = info.get("wg_check_port", 19000)

            packetpeer = PacketPeer(PacketType.PING_REPLY, (wg_check_ip, wg_check_port))

            peer_value = QueuePeer(
                queue.Queue(128),
                wg_conf["peer"],
            )

            checkalive.peers[packetpeer] = peer_value

            logger.debug(f"为 {wg_check_ip}:{wg_check_port} 启动 checkalive")
            funcs.start_thread(target=checkalive.ping, args=(checkalive.sock6, packetpeer), name=f"check_alive-{wg_check_ip}", daemon=True)


    try:
        exit_event.wait()
    finally:
        util.ip_link_del_wg(wg_name)
        logger.debug(f"已删除接口：{wg_name}")

    logger.debug("server 线程已结束")