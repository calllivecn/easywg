#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>


import sys
import time
import json
import copy
import queue
import socket
import atexit
import logging
import argparse
import ipaddress
import threading
import selectors
import subprocess
from pathlib import Path

from typing import (
    Any,
    Tuple,
    Dict,
)


import util
from packet import (
    PacketType,
    Packet,
    Ping,
    PacketTypeError,
)


CHECK_PORT = 19000
CHECK_TIMEOUT = 5
CHECK_FAILED_COUNT = 6


LEVEL_DEBUG2 = logging.DEBUG - 1


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
        time.sleep(CHECK_TIMEOUT)


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

            elif data[0] == PacketType.MULTICAST_ALIVE:
                logger.debug(f"收到MUTLI_ALIVE: {addr=}")
                continue

            else:
                packte_loss = True

        except socket.timeout:
            packte_loss = True


        if packte_loss:
            logger.info(f"{wg_peer_ip} 检测线路时丢包...")
            failed_count += 1

        if failed_count >= CHECK_FAILED_COUNT:
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
        
        time.sleep(CHECK_TIMEOUT)



Address = Any
if sys.version_info < (3, 10):
    PeerRaddr = Any
else:
    PeerRaddr = Dict[tuple[PacketType, str, int], queue.Queue]

def serverhub_daemon(wg_ip):
    pass


def start_thread(*args, **kwargs):
    th = threading.Thread(*args, **kwargs)
    th.start()
    return th


# 在线检测 内置版本
class CheckAlive:
    
    def __init__(self, serverhub=False):
        """
        只在wg接口ip上监听
        """
        self.se = selectors.DefaultSelector()
        self.socks = []
        self.sock4 = None
        self.sock6 = None

        self.peers: PeerRaddr = {}

        self.serverhub = serverhub
    
        # 需要更新域名的事件
        # self.update_peer_domain.set()


    def check_peer(self, wg_peer_ip: str):
        """
        peer 端主动检测
        """
        ip = ipaddress.ip_address(wg_peer_ip)

        if ip.version == 6:
            sock = self.sock6
        elif ip.version == 4:
            sock = self.sock4
        
        failed_count = 0

        ping = Ping()

        while True:

            try:
                # sock.sendto(ping.buf, (ip.exploded, CHECK_PORT))
                sock.send(ping.buf)

                while True:
                    reply = sock.recv(8192)

                    if reply == ping:
                        ping.next()
                        failed_count = 0
                        logger.info(f"{wg_peer_ip} 检测恢复...")
                        break
                    else:
                        logger.debug(f"可能收到了乱序包: {reply}")
            
            except socket.timeout:
                    
                failed_count += 1

                logger.info(f"{wg_peer_ip} 检测线路时丢包 {failed_count}/{CHECK_FAILED_COUNT}...")

                # 如果持续丢6个包(30s) 就算线路断开，通知下update更新(如果这个peer有配置Endpoint)。
                if failed_count > CHECK_FAILED_COUNT:
                    # 重新解析域名，重新连接。
                    # self.update_peer_domain(pubkey, domainname)
                    logger.warning(f"{wg_peer_ip} 线路断开了...")
                    break

                continue
            
            except OSError as e:
                logger.debug(f"这是server hub 端，有可能peer还没有。 {e}")
                break

            time.sleep(CHECK_TIMEOUT)
        
        logger.debug(f"本地 --> {wg_peer_ip} 检测线程退出.")

        sock.close()
    

    def ping(self, sock: socket.socket, typ: PacketType, peeraddr: PeerRaddr, q: queue.Queue):
        """
        peer 端被动检测
        """
        _, ip, port = peeraddr
        raddr = (ip, port)

        ping = Ping(typ)

        failed_count = 0

        while True:
            
            sock.sendto(ping.buf, raddr)
            while True:
                try:
                    data = q.get(timeout=CHECK_TIMEOUT)
                except queue.Empty:
                    # 超时
                    failed_count += 1
                    logger.info(f"{raddr} 检测线路时丢包 {failed_count}/{CHECK_FAILED_COUNT}...")
                    break

                
                reply = ping.reply(data)
                if ping.seq == reply.seq:

                    if failed_count > CHECK_FAILED_COUNT:
                        failed_count = 0
                        logger.info(f"{raddr} 检测恢复...")

                    break
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")


            ping.next()

            time.sleep(CHECK_TIMEOUT)


    def server(self, wg_ipv6, wg_ipv4=None):
        if wg_ipv4 is not None:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock4.setblocking(False)
            sock4.bind((wg_ipv4, CHECK_PORT))
            self.se.register(sock4, selectors.EVENT_READ)
            self.socks.append(sock4)
            self.sock4 = sock4


        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock6.setblocking(False)
        sock6.bind((wg_ipv6, CHECK_PORT))
        self.socks.append(sock6)
        self.sock6 = sock6

        self.se.register(sock6, selectors.EVENT_READ)

        while True:
            for key, event in self.se.select():
                sock = key.fileobj
                data, addr = sock.recvfrom(8192)
                logger.log(LEVEL_DEBUG2, f"UDP: 接收到的 {addr=} {data=}")

                # 要是指定类型的数据
                try:
                    typ = PacketType(data[0])
                except ValueError:
                    logger.debug(f"未知类型数据丢弃. {data=}")
                    continue

                peeraddr = (typ, addr[0], addr[1]) # 

                if typ == PacketType.PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)
                    
                    # 添加 server ping 线程
                    ping_peeraddr = (PacketType.SERVER_PING_REPLY, addr[0], addr[1])
                    peer = self.peers.get(ping_peeraddr)
                    if peer is None:
                        q = queue.Queue(128)
                        self.peers[ping_peeraddr] = q
                        start_thread(target=self.ping, args=(sock, PacketType.SERVER_PING, ping_peeraddr, q), name="server peer_check()")

                elif typ == PacketType.PING_REPLY:
                    q = self.peers.get(peeraddr)
                    if q is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.SERVER_PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)

                elif typ == PacketType.SERVER_PING_REPLY:
                    q = self.peers.get(peeraddr)

                    if q is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.WP_PEER_INFO:
                    # serverhub.put((data, addr))
                    pass
                else:
                    logger.debug(f"当前还未处理类型数据包，丢弃。{data=}")

    def close(self):
        for sock in self.socks:
            self.se.unregister(sock)
            sock.close()


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
    start_thread(target=checkalive.server, args=(self_ipv6, self_ipv4), name="CheckAlive.server()")

    for peer_bak in conf["peers"]:

        peer = copy.deepcopy(peer_bak)
        
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
        wg_check_ip = peer.get("wg_check_ip")
        if wg_check_ip:
            wg_check_port = peer.get("wg_check_port", 19000)

            peeraddr = (PacketType.PING_REPLY, wg_check_ip, wg_check_port)
            q = queue.Queue(128)
            checkalive.peers[peeraddr] = q

            logger.debug(f"为 {wg_check_ip}:{wg_check_port} 启动 checkalive")
            start_thread(target=checkalive.ping, args=(checkalive.sock6, PacketType.PING, peeraddr, q), name=f"check_alive-{wg_check_ip}")


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

    global CHECK_PORT
    global CHECK_TIMEOUT
    global CHECK_FAILED_COUNT

    if args.server:
        server(args.server)
        sys.exit(0)
    else:
    
        try:
            conf = loadconf()
        except Exception:
            print("配置错误")
            sys.exit(1)

        CHECK_PORT = conf.get("check_port", 19000)

        try:
            CHECK_TIMEOUT = conf["check_timeout"]
        except KeyError:
            pass

        try:
            CHECK_FAILED_COUNT = conf["check_failed_count"]
        except KeyError:
            pass

        server(conf)


if __name__ == "__main__":            
    main() 