#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>


import sys
import time
import json
import copy
import socket
import atexit
import logging
import argparse
import threading
import subprocess
from pathlib import Path

from typing import (
    Any,
    Tuple,
    Dict,
)

import asyncio
from asyncio import (
    DatagramProtocol,
    DatagramTransport,
)


import util
from packet import (
    PackteType,
    Packet,
    Ping,
    PacketTypeError,
)


CHECK_PORT = 18123
CHECK_INTERVAL = 5
CHECK_TIMEOUT = 5
CHECK_FAIL_COUNT = 3


def getlogger(level=logging.INFO):
    logger = logging.getLogger("wg-pyz")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d-%H:%M:%S")
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    #logger.setLevel(logging.DEBUG)

    consoleHandler.setFormatter(formatter)

    # consoleHandler.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)
    logger.setLevel(level)
    return logger

logger = getlogger(logging.DEBUG)


# 加载配置文件
def loadconf(conf: Path = Path(sys.argv[1])):

    with open(conf) as f:
        return json.load(f)


# 在线检测 cmd 版本
def check_alive(server_wg_ip):
    failed_count = 0
    while True:
        try:
            subprocess.run(f"ping -W 5 -c 1 {server_wg_ip}".split(), stdout=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError:
            logger.info(f"{server_wg_ip} 检测好像断开了...")
            failed_count += 1
            if failed_count >= 3:
                logger.warning(f"{server_wg_ip} 线路断开了...")
                return
            else:
                continue

        if failed_count > 0:
            logger.info(f"{server_wg_ip} 检测恢复...")

        failed_count = 0
        time.sleep(CHECK_INTERVAL)


# 在线检测 内置版本
def check_alive2(wg_peer_ip, endpoint_addr, domainname):
    """
    wg_peer_ip:
    peer_ip:

    return: new peer_ip

    检测线路丢包，并行跑域名解析。
    """

    # 拿到连接 远程地址时 会用到的本地laddr
    udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp.connect((wg_peer_ip, CHECK_PORT))
    laddr = udp.getsockname()
    udp.close()

    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((laddr[0], CHECK_PORT))
    sock.settimeout(CHECK_TIMEOUT)

    # 每12分钟解析下域名，看看有没有改变。
    t1 = time.time()

    # 一个序列包
    alive = Ping()

    failed_count = 0
    packte_loss = True

    while True:
        try:

            sock.sendto(alive.buf, (wg_peer_ip, CHECK_PORT))
            data, addr = sock.recvfrom(8192)

            if addr[0] == wg_peer_ip and data == alive:
                alive.next()
                packte_loss = False

            elif data[0] == PackteType.MULTICAST_ALIVE:
                logger.debug(f"收到MUTLI_ALIVE: {addr=}")
                continue

            else:
                packte_loss = True

        except socket.timeout:
            packte_loss = True


        if packte_loss:
            logger.info(f"{wg_peer_ip} 检测线路时丢包...")
            failed_count += 1

        if failed_count >= CHECK_FAIL_COUNT:
            logger.warning(f"{wg_peer_ip} 线路断开了...")

        if failed_count > 0 and packte_loss is False:
            logger.info(f"{wg_peer_ip} 检测恢复...")
            failed_count = 0

        # 检测域名是否更新
        t2 = time.time()

        if (t2 - t1) > 12*60:

            new_peer_ip = util.getaddrinfo(domainname)
            if new_peer_ip != endpoint_addr:
                return new_peer_ip

            t1 = t2
        
        time.sleep(CHECK_INTERVAL)



Address = Any

class QueuqPair:
    
    def __init__(self, size=500):
        self.r = asyncio.Queue(size)
        self.w = asyncio.Queue(size)
    


class UDPAddressPair:

    def __init__(self, transport, addr, pair: Tuple[asyncio.Queue, asyncio.Queue]):
        self.transport = transport
        self.peers = Dict[Address, QueuqPair] = {}
        self.pair = pair
        self.w_pair, self.r_pair = pair

    async def udp_recv(self, nbytes: int) -> bytes:
        return await self.r_pair.get()
    

    async def udp_send(self, data: bytes):
        self.transport.sendto(data, self.peeraddr)

    def _add_peers(self, new_peer_addr: Address):
        self.peers[new_peer_addr] = self.pair


class AliveServerHandle(DatagramProtocol):

    def __init__(self) -> None:
        super().__init__()

        self._is_client = False

        # self.ping = Ping()
        self.peers = {}
        self.pairs: Tuple[Tuple, asyncio.Queue] = {}

    def connection_made(self, transport: DatagramTransport) -> None:
        self.transport = transport

        # 启动 server_hub 协程
        # asyncio.ensure_future(self.multicast_server())


    def datagram_received(self, data: bytes, addr: Tuple) -> None:

        ip, port = addr[0], addr[1]

        # typ = struct.unpack("!B", data[0:1])
        typ = data[0]

        if typ == PackteType.PING:
            self.transport.sendto(data, addr)
            logger.debug(f"收到PING: {ip}:{port}")

            peer_addr = self.peers.get(addr)
            if peer_addr is None:
                self.peers[addr] = addr
                logger.debug(f"新添加server --> peer 的MULTICAST_SERVER: {addr=}")
                asyncio.ensure_future(self.multicast_server(addr))


        elif typ == PackteType.MULTICAST_ALIVE:
            logger.debug(f"收到MULTICAST_ALIVE: {ip}:{port}")
        
        else:
            logger.debug(f"其他UDP包：{ip}:{port} --> {data=}")


    async def accept(self):
        assert not self._is_client


    async def multicast_server(self, addr):
        """
        # 每5秒发送组播，已使用wg hub 重新主动连接 各个peer
        # async def multicast_server(transport: DatagramTransport):
        """
        mutlicast = Ping(PackteType.MULTICAST_ALIVE)

        while True:
            # self.transport.sendto(mutlicast.buf, ("ff02::1", CHECK_PORT))
            self.transport.sendto(mutlicast.buf, addr)
            asyncio.wait()
            await asyncio.sleep(CHECK_INTERVAL)

    async def read(self, nbytes: int) -> bytes:
        pass


async def async_server(sock):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(AliveServerHandle, sock=sock)

    future = loop.create_future()
    try:
        await future
    except Exception:
        pass
    finally:
        transport.close()


# 在线检测 内置版本
def check_alive_server(wg_ipv6, wg_ipv4=None):
    """
    只在wg接口ip上监听
    """
    ths = []
    if wg_ipv4 is not None:
        sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock4.bind((wg_ipv4, CHECK_PORT))
        th4 = threading.Thread(target=lambda: asyncio.run(async_server(sock4)), daemon=True)
        th4.start()
        ths.append(th4)


    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock6.bind((wg_ipv6, CHECK_PORT))

    th6 = threading.Thread(target=lambda: asyncio.run(async_server(sock6)), daemon=True)
    th6.start()
    ths.append(th6)

    for th in ths:
        th.join()


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
    
    for CIDR in ifname["address"]:
        util.ip_addr_add(wg_name, CIDR)


    util.wg_set(wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))

    for peer_bak in conf["peers"]:

        peer = copy.deepcopy(peer_bak)
        
        endpoint_addr = peer["endpoint_addr"]

        # addr = util.dnsquery(dns)
        addr = util.getaddrinfo(endpoint_addr)

        if len(addr) == 0:
            logger.warning(f"没有查询到 {endpoint_addr} IP, 可能出错了。请检查")
            continue


        peer["endpoint_addr"] = addr
        
        logger.debug(f"{peer=}")
        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)
    

    while True:
        # 目前测试阶段，只先做一个peer端的处理
        peer = copy.deepcopy(conf["peers"][0])
        endpoint_addr = peer["endpoint_addr"]
        public_key = peer["public_key"]

        new_peer_ip = check_alive2(conf["server_wg_ip"], addr, endpoint_addr)

        logger.debug(f"{endpoint_addr=} {new_peer_ip=} {public_key=}")

        logger.info(f"新地址更新wireguard: {new_peer_ip}")

        peer["endpoint_addr"] = new_peer_ip
        logger.debug(f"{peer=}")

        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)
        
        addr = new_peer_ip
        


def main():
    # 怎么没用 ？ logger.setLevel(logging.DEBUG)

    parse = argparse.ArgumentParser(
        usage="%(prog)s",
        epilog="https://github.com/calllivecn/easywg"
    )

    parse.add_argument("--server", metavar="server_ip", help="listen bind wg interface IP")

    # parse.add_argument("--conf", metavar="server_ip", help="listen bind wg interface IP")
    parse.add_argument("conf", metavar="config", nargs="*", help="config")

    parse.add_argument("--parse", action="store_true", help=argparse.SUPPRESS)

    args = parse.parse_args()

    if args.parse:
        print(args)
        sys.exit(0)

    if args.server:
        check_alive_server(args.server)
        sys.exit(0)
    else:
    
        try:
            conf = loadconf()
        except Exception:
            print("配置错误")
            sys.exit(1)

        server(conf)


if __name__ == "__main__":            
    main()