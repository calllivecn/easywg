import asyncio
import copy
import ipaddress
import socket
from dataclasses import dataclass

import funcs
import util
from log import logger
from packet import PacketType, Ping

__all__ = ("CheckAlive", "CPeer", "PeerRaddr")


@dataclass
class CPeer:
    q: asyncio.Queue
    conf: dict | None = None


PeerRaddr = dict[tuple[PacketType, str, int], CPeer]


class CheckAlive:
    def __init__(self, conf: dict, serverhub=False):
        self.conf = conf
        self.serverhub = serverhub
        self.peers: PeerRaddr = {}
        self.current_ips: dict[str, str] = {}
        self.event_server_ping = asyncio.Event()
        self.socks = []
        self.sock4 = None
        self.sock6 = None
        self._tasks: set[asyncio.Task] = set()
        self._group = None
        self._stop_event = None

    def add_peer(self, address: str, port: int, conf: dict):
        # socket 返回压缩后的 IPv6 地址，配置中的地址也必须规范化。
        address = str(ipaddress.ip_address(address))
        key = (PacketType.PING_REPLY, address, port)
        self.peers[key] = CPeer(asyncio.Queue(128), copy.deepcopy(conf))

    def _start_task(self, coroutine):
        task = self._group.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def _wait_reply(self, q: asyncio.Queue, ping: Ping):
        # 乱序包不结束当前探测，也不能不断重置超时。
        async with asyncio.timeout(funcs.CHECK_TIMEOUT):
            while True:
                data = await q.get()
                if Ping.reply(data).seq == ping.seq:
                    return
                logger.debug(f"可能收到了乱序包: {data}, 继续接收...")

    async def ping(self, sock: socket.socket, key):
        await self._probe(sock, key, PacketType.PING)

    async def server_ping(self, sock: socket.socket, key):
        try:
            await self._probe(sock, key, PacketType.SERVER_PING)
        finally:
            self.peers.pop(key, None)

    async def _probe(self, sock: socket.socket, key, typ: PacketType):
        peer = self.peers[key]
        address = (key[1], key[2])
        ping = Ping(typ)
        failed_count = 0
        loop = asyncio.get_running_loop()

        while True:
            await loop.sock_sendto(sock, ping.buf, address)
            try:
                await self._wait_reply(peer.q, ping)
            except TimeoutError:
                failed_count += 1
                logger.info(f"{address} 检测线路时丢包 {failed_count}/{funcs.CHECK_FAILED_COUNT}...")
            else:
                if failed_count:
                    logger.info(f"--> {address} 检测恢复...")
                failed_count = 0

            if failed_count >= funcs.CHECK_FAILED_COUNT:
                logger.warning(f"--> {address} 线路断开了...")
                if typ == PacketType.SERVER_PING:
                    return
                await self.update_domain(peer.conf)
                failed_count = 0

            ping.next()
            await asyncio.sleep(funcs.CHECK_TIMEOUT)

    def _bind(self, family, address):
        sock = socket.socket(family, socket.SOCK_DGRAM)
        # 绑定失败时也由 finally 关闭已经创建的 socket。
        self.socks.append(sock)
        sock.setblocking(False)
        if family == socket.AF_INET6:
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        sock.bind((address, funcs.CHECK_PORT))
        return sock

    async def server(self, wg_ipv6, wg_ipv4=None, stop_event=None):
        self._stop_event = stop_event if stop_event is not None else asyncio.Event()
        try:
            if wg_ipv4 is not None:
                self.sock4 = self._bind(socket.AF_INET, wg_ipv4)
            self.sock6 = self._bind(socket.AF_INET6, wg_ipv6)

            async with asyncio.TaskGroup() as group:
                self._group = group
                for sock in self.socks:
                    self._start_task(self._handle_sock(sock))
                for key, peer in list(self.peers.items()):
                    if peer.conf is not None:
                        sock = self.sock6 if ipaddress.ip_address(key[1]).version == 6 else self.sock4
                        if sock is None:
                            raise ValueError(f"没有可用于探测 {key[1]} 的 WireGuard 地址")
                        self._start_task(self.ping(sock, key))
                self.event_server_ping.set()
                await self._stop_event.wait()
                for task in list(self._tasks):
                    task.cancel()
        finally:
            self._group = None
            await self.close()

    async def _handle_sock(self, sock):
        loop = asyncio.get_running_loop()
        while True:
            data, addr = await loop.sock_recvfrom(sock, 8192)
            if not data:
                continue
            try:
                typ = PacketType(data[0])
            except ValueError:
                logger.debug(f"未知类型数据丢弃: {addr=} {data=}")
                continue

            if typ not in (PacketType.PING, PacketType.PING_REPLY,
                           PacketType.SERVER_PING, PacketType.SERVER_PING_REPLY):
                continue
            if len(data) < Ping().size:
                logger.debug(f"不完整的心跳数据丢弃: {addr=} {data=}")
                continue

            if typ in (PacketType.PING, PacketType.SERVER_PING):
                await loop.sock_sendto(sock, Ping.reply(data).buf, addr)
                if typ == PacketType.PING:
                    key = (PacketType.SERVER_PING_REPLY, addr[0], addr[1])
                    if key not in self.peers:
                        self.peers[key] = CPeer(asyncio.Queue(128))
                        self._start_task(self.server_ping(sock, key))
            else:
                key = (typ, addr[0], addr[1])
                peer = self.peers.get(key)
                if peer is not None:
                    try:
                        peer.q.put_nowait(data)
                    except asyncio.QueueFull:
                        logger.debug(f"{key} 接收队列已满, 丢弃 {data}")

    async def update_domain(self, peer_conf: dict):
        endpoint = peer_conf["endpoint_addr"]
        try:
            ip = ipaddress.ip_address(endpoint).exploded
        except ValueError:
            logger.info(f"开始更新域名: {endpoint}")
            ip = await asyncio.to_thread(util.getaddrinfo, endpoint)

        if ip == []:
            logger.warning(f"{endpoint} 没有解析到IP.")
            return

        public_key = peer_conf["public_key"]
        previous = self.current_ips.get(public_key)
        if previous != ip:
            peer = copy.deepcopy(peer_conf)
            peer["endpoint_addr"] = ip
            logger.info(f"更新peer端新地址: {previous} --> {ip}")
            await funcs.run_sync(util.wg_peer_option, self.conf["ifname"]["interface"], public_key, peer)
            self.current_ips[public_key] = ip

    async def close(self):
        if self._stop_event is not None:
            self._stop_event.set()
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for sock in self.socks:
            sock.close()
        self.socks.clear()
        self.sock4 = None
        self.sock6 = None
