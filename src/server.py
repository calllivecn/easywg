import asyncio
import copy
import signal
import ipaddress

import funcs
import util
from log import logger
from checkalive import CheckAlive


def server(conf):
    asyncio.run(_server(conf))


def _set_peer(wg_name, peer):
    with util.WireGuard() as wg:
        wg.set(wg_name, peer=peer)


async def _server(conf):
    ifname = conf["ifname"]
    wg_name = ifname["interface"]
    exit_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    previous_sigterm = signal.getsignal(signal.SIGTERM)
    loop.add_signal_handler(signal.SIGTERM, exit_event.set)
    checkalive = CheckAlive(conf)
    interface_created = False

    def create_interface():
        nonlocal interface_created
        util.ip_link_add_wg(wg_name)
        interface_created = True

    try:
        await funcs.run_sync(create_interface)
        wg_mtu = int(ifname.get("MTU"))
        await funcs.run_sync(util.ip_link_mtu, wg_name, wg_mtu)

        self_ipv4 = None
        self_ipv6 = None
        for cidr in ifname["address"]:
            await funcs.run_sync(util.ip_addr_add, wg_name, cidr)
            ip = ipaddress.ip_address(cidr.split("/")[0])
            if ip.version == 4 and self_ipv4 is None:
                self_ipv4 = ip.exploded
            elif ip.version == 6 and self_ipv6 is None:
                self_ipv6 = ip.exploded

        await funcs.run_sync(util.wg_set, wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))
        logger.debug(f"配置接口：{wg_name}")

        for wg_conf in conf["peers"]:
            peer_conf = copy.deepcopy(wg_conf)
            info = peer_conf["info"]
            peer = peer_conf["peer"]

            endpoint_addr = peer.get("endpoint_addr")
            if endpoint_addr is not None:
                addr = await asyncio.to_thread(util.getaddrinfo, endpoint_addr)
                if len(addr) == 0:
                    logger.warning(f"没有查询到 {endpoint_addr} IP, 可能出错了。请检查")
                    # 暂时占位，之后由心跳任务重解析原始域名。
                    addr = "127.0.0.1"
                peer["endpoint_addr"] = addr

            logger.debug(f"配置peer: {peer}")
            await funcs.run_sync(_set_peer, wg_name, peer)

            for cidr in peer.get("allowed_ips", []):
                net = ipaddress.ip_network(cidr)
                add_route_flag = True
                for ifaddr in ifname["address"]:
                    ifaddr = ipaddress.ip_interface(ifaddr)
                    if ifaddr.network.overlaps(net):
                        logger.debug(f"跳过 {cidr}，因为与接口地址 {ifaddr.network} 重叠")
                        add_route_flag = False
                if add_route_flag:
                    await funcs.run_sync(util.add_route_ifname, cidr, wg_name)
                    logger.debug(f"添加 {cidr}")

            wg_check_ip = info.get("wg_check_ip")
            if wg_check_ip:
                wg_check_port = info["wg_check_port"]
                checkalive.add_peer(wg_check_ip, wg_check_port, wg_conf["peer"])
                logger.debug(f"为 {wg_check_ip}:{wg_check_port} 添加异步 checkalive")

        await checkalive.server(self_ipv6, self_ipv4, exit_event)

    finally:
        try:
            await checkalive.close()
        finally:
            loop.remove_signal_handler(signal.SIGTERM)
            signal.signal(signal.SIGTERM, previous_sigterm)
            if interface_created:
                await funcs.run_sync(util.ip_link_del_wg, wg_name)
                logger.debug(f"已删除接口：{wg_name}")

    logger.debug("server 已结束")
