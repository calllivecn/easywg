
import time
import copy
import queue
import socket
import ipaddress
import selectors
from dataclasses import dataclass

import util
from log import logger
from packet import (
    PacketType,
    Ping,
)
import funcs

__all__ = [
    "CheckAlive",
    "QueuePeer",
    "PacketPeer",
]

@dataclass
class QueuePeer:
    q: queue.Queue
    peer_conf: dict

@dataclass
class PacketPeer:
    packettype: PacketType
    # wg_check_ip_port: tuple[str, int]
    wg_check_ip_port: socket._RetAddress


# 在线检测 内置版本
class CheckAlive:
    
    def __init__(self, conf: dict, serverhub=False):
        """
        只在wg接口ip上监听
        """
        # 当前配置
        self.conf = conf
        self.serverhub = serverhub

        self.se = selectors.DefaultSelector()
        self.socks = []
        self.sock4 = None
        self.sock6 = None

        # 有个时候，socket还没初始化完？使用event解决？
        self.event_server_ping = funcs.get_event()

        self.peers: dict[PacketPeer, QueuePeer] = {}


        # 需要更新域名的事件
        # self.update_peer_domain.set()
        self.cur_real_ip = ""

        # 多域名检测标志
        self._next_domain = 0


    def ping(self, sock: socket.socket, ppeer: PacketPeer):
        """
        peer 端被动检测
        """
        qp: QueuePeer = self.peers[ppeer]

        ping = Ping()

        failed_count = 0

        while True:
            
            sock.sendto(ping.buf, ppeer.wg_check_ip_port)
            while True:
                try:
                    data = qp.q.get(timeout=funcs.CHECK_TIMEOUT)
                except queue.Empty:
                    # 超时
                    failed_count += 1
                    logger.info(f"{qp.peer_conf} 检测线路时丢包 {failed_count}/{funcs.CHECK_FAILED_COUNT}...")
                    break

                
                reply = ping.reply(data)
                if ping.seq == reply.seq:

                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"--> {qp.peer_conf} 检测恢复...")

                    break
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= funcs.CHECK_FAILED_COUNT:
                logger.warning(f"--> {qp.peer_conf} 线路断开了...")
                self.update_domain(qp.peer_conf)
                failed_count = 0

            ping.next()

            time.sleep(funcs.CHECK_TIMEOUT)


    def server_ping(self, sock: socket.socket, ppeer: PacketPeer):
        """
        peer 端被动检测
        """
        logger.debug(f"等待 server 初始化完成: {self.event_server_ping} ...")
        self.event_server_ping.wait()
        logger.debug(f"server 初始化完成: {self.event_server_ping}")

        qp: QueuePeer = self.peers[ppeer]
        logger.debug(f"添加 {ppeer.wg_check_ip_port} check...")


        ping = Ping(PacketType.SERVER_PING)

        failed_count = 0

        while True:
            
            sock.sendto(ping.buf, ppeer.wg_check_ip_port)
            while True:
                try:
                    data = qp.q.get(timeout=funcs.CHECK_TIMEOUT)
                except queue.Empty:
                    # 超时
                    failed_count += 1
                    logger.info(f"{ppeer.wg_check_ip_port} 检测线路时丢包 {failed_count}/{funcs.CHECK_FAILED_COUNT}...")
                    break

                
                reply = ping.reply(data)
                if ping.seq == reply.seq:

                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"{ppeer.wg_check_ip_port} 检测恢复...")

                    break
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= funcs.CHECK_FAILED_COUNT:
                logger.warning(f" --> {ppeer.wg_check_ip_port} 线路断开了...")
                # logger.log(LEVEL_DEBUG2 ,f"{raddr} 退出")
                logger.debug(f"{ppeer.wg_check_ip_port} 退出")
                self.peers.pop(ppeer)
                return

            ping.next()

            time.sleep(funcs.CHECK_TIMEOUT)


    def server(self, wg_ipv6, wg_ipv4=None):
        if wg_ipv4 is not None:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock4.setblocking(False)
            sock4.bind((wg_ipv4, funcs.CHECK_PORT))
            self.se.register(sock4, selectors.EVENT_READ)
            self.socks.append(sock4)
            self.sock4 = sock4


        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock6.setblocking(False)
        sock6.bind((wg_ipv6, funcs.CHECK_PORT))
        self.se.register(sock6, selectors.EVENT_READ)
        self.socks.append(sock6)
        self.sock6 = sock6

        self.event_server_ping.set()


        while True:
            for key, event in self.se.select():
                sock: socket.socket = key.fileobj # type: ignore
                data, addr = sock.recvfrom(8192)

                # 要是指定类型的数据
                try:
                    typ = PacketType(data[0])
                except ValueError:
                    logger.debug(f"未知类型数据丢弃:{addr=} {data=}")
                    continue

                ppeer = PacketPeer(typ, addr)

                if typ == PacketType.PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)
                    
                    # 添加 server ping 线程
                    ppeer = PacketPeer(PacketType.SERVER_PING_REPLY, addr)
                    peer = self.peers.get(ppeer)
                    if peer is None:
                        self.peers[ppeer] = QueuePeer(queue.Queue(128), {})
                        funcs.start_thread(target=self.server_ping, args=(sock, ppeer), name="server_ping check()", daemon=True)

                elif typ == PacketType.PING_REPLY:
                    cpeer = self.peers.get(ppeer)
                    if cpeer is None:
                        logger.debug(f"没有这个线程：{ppeer=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{ppeer} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.SERVER_PING:
                    ping = Ping.reply(data)
                    sock.sendto(ping.buf, addr)

                elif typ == PacketType.SERVER_PING_REPLY:
                    cpeer = self.peers.get(ppeer)

                    if cpeer is None:
                        logger.debug(f"没有这个线程：{ppeer=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except queue.Full:
                            logger.debug(f"{ppeer} 接收队列已满, 丢弃 {data}")

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
            logger.warning(f"解析{endpoint}出错.")
            return

        
        # 如果没有解析到IP,给出提示
        if ip == []:
            logger.warning(f"{endpoint} 没有解析到IP.")
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


    def close(self):
        for sock in self.socks:
            self.se.unregister(sock)
            sock.close()
