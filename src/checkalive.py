
import time
import copy
import queue
import socket
import threading
import ipaddress
import selectors
from dataclasses import dataclass

import util
from log import logger
from packet import (
    PacketType,
    Ping,
)

__all__ = [
    "CheckAlive",
    "PeerRaddr",
    "CPeer",
]


@dataclass
class CPeer:
    q: queue.Queue
    conf: dict | None = None


PeerRaddr = dict[tuple[PacketType, str, int], CPeer]

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


        # 当前配置
        self.conf = None
    
        # 需要更新域名的事件
        # self.update_peer_domain.set()
        self.cur_real_ip = ""

        # 多域名检测标志
        self._next_domain = 0


    def ping(self, sock: socket.socket, cpeer: PeerRaddr):
        """
        peer 端被动检测
        """
        peer = self.peers[cpeer]

        raddr = (cpeer[1], cpeer[2])

        q = peer.q

        ping = Ping()

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

                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"--> {raddr} 检测恢复...")

                    break
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= CHECK_FAILED_COUNT:
                logger.warning(f"--> {raddr} 线路断开了...")
                self.update_domain(peer.conf)
                failed_count = 0

            ping.next()

            time.sleep(CHECK_TIMEOUT)


    def server_ping(self, sock: socket.socket, cpeer: PeerRaddr):
        """
        peer 端被动检测
        """
        peer = self.peers[cpeer]
        raddr = (cpeer[1], cpeer[2])
        logger.debug(f"添加 {raddr} check...")

        ping = Ping(PacketType.SERVER_PING)

        failed_count = 0

        while True:
            
            sock.sendto(ping.buf, raddr)
            while True:
                try:
                    data = peer.q.get(timeout=CHECK_TIMEOUT)
                except queue.Empty:
                    # 超时
                    failed_count += 1
                    logger.info(f"{raddr} 检测线路时丢包 {failed_count}/{CHECK_FAILED_COUNT}...")
                    break

                
                reply = ping.reply(data)
                if ping.seq == reply.seq:

                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"{raddr} 检测恢复...")

                    break
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= CHECK_FAILED_COUNT:
                logger.warning(f" --> {raddr} 线路断开了...")
                # logger.log(LEVEL_DEBUG2 ,f"{raddr} 退出")
                logger.debug(f"{raddr} 退出")
                self.peers.pop(cpeer)
                return

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
                logger.debug(f"UDP: 接收到的 {addr=} {data=}")

                # 要是指定类型的数据
                try:
                    typ = PacketType(data[0])
                except ValueError:
                    logger.info(f"未知类型数据丢弃. {data=}")
                    continue

                peeraddr = (typ, addr[0], addr[1])

                if typ == PacketType.PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)
                    
                    # 添加 server ping 线程
                    ping_peeraddr = (
                        PacketType.SERVER_PING_REPLY,
                        addr[0],
                        addr[1],
                        )
                    peer = self.peers.get(ping_peeraddr)
                    if peer is None:
                        self.peers[ping_peeraddr] = CPeer(queue.Queue(128))
                        th = threading.Thread(target=self.server_ping, args=(sock, ping_peeraddr), name="server_ping check()")
                        th.start()

                elif typ == PacketType.PING_REPLY:
                    cpeer = self.peers.get(peeraddr)
                    if cpeer is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.SERVER_PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)

                elif typ == PacketType.SERVER_PING_REPLY:
                    cpeer = self.peers.get(peeraddr)

                    if cpeer is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.WP_PEER_INFO:
                    # serverhub.put((data, addr))
                    pass
                else:
                    logger.debug(f"当前还未处理类型数据包，丢弃。{data=}")


    def update_domain(self, peer_conf: dict):
        """
        如果是ip直接返回，是域名才解析。
        """
        endpoint = peer_conf["endpoint_addr"]

        try:
            ip = ipaddress.ip_address(endpoint).exploded
        except ValueError:
            next_endpoint = self.__next_domain(endpoint)
            logger.debug(f"解析地址: {next_endpoint}")
            ip = util.getaddrinfo(next_endpoint)
            self._next_domain += 1
        
        # 如果没有解析到IP,给出提示
        if ip == []:
            logger.warning(f"没有解析到IP.")
            return

        if self.cur_real_ip != ip:

            wg_name = self.conf["ifname"]["interface"]

            peer = copy.deepcopy(peer_conf)
            peer["endpoint_addr"] = ip

            logger.info(f"更新peer端新地址: {self.cur_real_ip} --> {ip}")
            util.wg_peer_option(wg_name, peer["public_key"], peer)

            self.cur_real_ip = ip

        else:
            logger.debug(f"没有更新地址: {ip}")


    def __next_domain(self, domain: str):
        prefix, suffix = domain.split(".", 1)

        if self._next_domain >= 10:
            self._next_domain = 0

        return f"{prefix}-{self._next_domain:02}.{suffix}"


    def close(self):
        for sock in self.socks:
            self.se.unregister(sock)
            sock.close()
