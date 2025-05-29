
import asyncio
import copy
import socket
import ipaddress
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
    "PeerRaddr",
    "CPeer",
]


@dataclass
class CPeer:
    q: asyncio.Queue
    conf: dict | None = None


PeerRaddr = dict[tuple[PacketType, str, int], CPeer]

class CheckAlive:
    def __init__(self, serverhub=False):
        self.peers: PeerRaddr = {}
        self.serverhub = serverhub
        self.conf = None
        self.cur_real_ip = ""
        self._next_domain = 0
        self.event_server_ping = asyncio.Event()
        self.socks = []
        self.sock4 = None
        self.sock6 = None

    async def ping(self, sock: socket.socket, cpeer):
        peer = self.peers[cpeer]
        raddr = (cpeer[1], cpeer[2])
        q = peer.q
        ping = Ping()
        failed_count = 0

        while True:
            await asyncio.get_event_loop().sock_sendto(sock, ping.buf, raddr)
            try:
                data = await asyncio.wait_for(q.get(), timeout=funcs.CHECK_TIMEOUT)
            except asyncio.TimeoutError:
                failed_count += 1
                logger.info(f"{raddr} 检测线路时丢包 {failed_count}/{funcs.CHECK_FAILED_COUNT}...")
            else:
                reply = ping.reply(data)
                if ping.seq == reply.seq:
                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"--> {raddr} 检测恢复...")
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= funcs.CHECK_FAILED_COUNT:
                logger.warning(f"--> {raddr} 线路断开了...")
                await self.update_domain(peer.conf)
                failed_count = 0

            ping.next()
            await asyncio.sleep(funcs.CHECK_TIMEOUT)

    async def server_ping(self, sock: socket.socket, cpeer):
        logger.debug(f"等待 server 初始化完成: {self.event_server_ping} ...")
        await self.event_server_ping.wait()
        logger.debug(f"server 初始化完成: {self.event_server_ping}")

        peer = self.peers[cpeer]
        raddr = (cpeer[1], cpeer[2])
        logger.debug(f"添加 {raddr} check...")

        ping = Ping(PacketType.SERVER_PING)
        failed_count = 0

        while True:
            await asyncio.get_event_loop().sock_sendto(sock, ping.buf, raddr)
            try:
                data = await asyncio.wait_for(peer.q.get(), timeout=funcs.CHECK_TIMEOUT)
            except asyncio.TimeoutError:
                failed_count += 1
                logger.info(f"{raddr} 检测线路时丢包 {failed_count}/{funcs.CHECK_FAILED_COUNT}...")
            else:
                reply = ping.reply(data)
                if ping.seq == reply.seq:
                    if failed_count > 0:
                        failed_count = 0
                        logger.info(f"{raddr} 检测恢复...")
                else:
                    logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

            if failed_count >= funcs.CHECK_FAILED_COUNT:
                logger.warning(f" --> {raddr} 线路断开了...")
                logger.debug(f"{raddr} 退出")
                self.peers.pop(cpeer)
                return

            ping.next()
            await asyncio.sleep(funcs.CHECK_TIMEOUT)

    async def server(self, wg_ipv6, wg_ipv4=None):
        loop = asyncio.get_event_loop()
        if wg_ipv4 is not None:
            sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock4.setblocking(False)
            sock4.bind((wg_ipv4, funcs.CHECK_PORT))
            self.socks.append(sock4)
            self.sock4 = sock4

        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock6.setblocking(False)
        sock6.bind((wg_ipv6, funcs.CHECK_PORT))
        self.socks.append(sock6)
        self.sock6 = sock6

        self.event_server_ping.set()

        async def handle_sock(sock):
            while True:
                data, addr = await loop.sock_recvfrom(sock, 8192)
                try:
                    typ = PacketType(data[0])
                except ValueError:
                    logger.debug(f"未知类型数据丢弃:{addr=} {data=}")
                    continue

                peeraddr = (typ, addr[0], addr[1])

                if typ == PacketType.PING:
                    ping = Ping.reply(data)
                    await loop.sock_sendto(sock, ping.buf, addr)
                    ping_peeraddr = (
                        PacketType.SERVER_PING_REPLY,
                        addr[0],
                        addr[1],
                    )
                    peer = self.peers.get(ping_peeraddr)
                    if peer is None:
                        self.peers[ping_peeraddr] = CPeer(asyncio.Queue(128))
                        asyncio.create_task(self.server_ping(sock, ping_peeraddr))

                elif typ == PacketType.PING_REPLY:
                    cpeer = self.peers.get(peeraddr)
                    if cpeer is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except asyncio.QueueFull:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.SERVER_PING:
                    ping = Ping.reply(data)
                    await loop.sock_sendto(sock, ping.buf, addr)

                elif typ == PacketType.SERVER_PING_REPLY:
                    cpeer = self.peers.get(peeraddr)
                    if cpeer is None:
                        logger.debug(f"没有这个线程：{peeraddr=}")
                    else:
                        try:
                            cpeer.q.put_nowait(data)
                        except asyncio.QueueFull:
                            logger.debug(f"{peeraddr} 接收队列已满, 丢弃 {data}")

                elif typ == PacketType.WP_PEER_INFO:
                    pass
                else:
                    logger.debug(f"当前还未处理类型数据包，丢弃。{data=}")

        tasks = []
        if self.sock4:
            tasks.append(asyncio.create_task(handle_sock(self.sock4)))
        if self.sock6:
            tasks.append(asyncio.create_task(handle_sock(self.sock6)))
        await asyncio.gather(*tasks)

    async def update_domain(self, peer_conf: dict):
        endpoint = peer_conf["endpoint_addr"]
        try:
            ip = ipaddress.ip_address(endpoint).exploded
        except ValueError:
            next_endpoint = self.__next_domain(endpoint)
            logger.debug(f"解析地址: {next_endpoint}")
            ip = await asyncio.get_event_loop().run_in_executor(None, util.getaddrinfo, next_endpoint)
            self._next_domain += 1

        if ip == []:
            logger.warning(f"没有解析到IP.")
            return

        if self.cur_real_ip != ip:
            wg_name = self.conf["ifname"]["interface"]
            peer = copy.deepcopy(peer_conf)
            peer["endpoint_addr"] = ip
            logger.info(f"更新peer端新地址: {self.cur_real_ip} --> {ip}")
            await asyncio.get_event_loop().run_in_executor(None, util.wg_peer_option, wg_name, peer["public_key"], peer)
            self.cur_real_ip = ip
        else:
            logger.debug(f"没有更新地址: {ip}")

    def __next_domain(self, domain: str):
        prefix, suffix = domain.split(".", 1)
        if self._next_domain >= 10:
            self._next_domain = 0
        return f"{prefix}-{self._next_domain:02}.{suffix}"

    async def close(self):
        for sock in self.socks:
            sock.close()

