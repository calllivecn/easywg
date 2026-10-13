import asyncio
import signal
import socket
import threading
import unittest
from unittest.mock import AsyncMock, patch

import funcs
import util
from checkalive import CheckAlive
from packet import PacketType, Ping
from server import _server


class CheckAliveTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.check = CheckAlive({"ifname": {"interface": "wg-test"}})

    async def asyncTearDown(self):
        await self.check.close()

    async def test_udp_round_trip_and_shutdown(self):
        loop = asyncio.get_running_loop()
        stop = asyncio.Event()
        client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        client.setblocking(False)
        client.bind(("::1", 0))
        port = client.getsockname()[1]
        self.check.add_peer("0:0:0:0:0:0:0:1", port, {})
        with patch.object(funcs, "CHECK_PORT", 0):
            task = asyncio.create_task(self.check.server("::1", "127.0.0.1", stop))
            try:
                await asyncio.wait_for(self.check.event_server_ping.wait(), 1)
                sock6 = self.check.sock6
                sock4 = self.check.sock4
                data, addr = await asyncio.wait_for(loop.sock_recvfrom(client, 8192), 1)
                self.assertEqual(data[0], PacketType.PING)
                await loop.sock_sendto(client, Ping.reply(data).buf, addr)
                # 无效数据不应使收包任务退出。
                for invalid in (b"", b"\xff", b"\x01"):
                    await loop.sock_sendto(client, invalid, addr)
                await loop.sock_sendto(client, Ping().buf, addr)
                types = set()
                for _ in range(2):
                    data, _ = await asyncio.wait_for(loop.sock_recvfrom(client, 8192), 1)
                    types.add(data[0])
                    if data[0] == PacketType.SERVER_PING:
                        await loop.sock_sendto(client, Ping.reply(data).buf, addr)
                self.assertEqual(types, {PacketType.PING_REPLY, PacketType.SERVER_PING})
            finally:
                stop.set()
                await asyncio.wait_for(task, 1)
                client.close()
        self.assertEqual(sock6.fileno(), -1)
        self.assertEqual(sock4.fileno(), -1)
        self.assertFalse(self.check._tasks)
        self.assertNotIn((PacketType.SERVER_PING_REPLY, "::1", port), self.check.peers)

    async def test_out_of_order_reply_waits_for_current_sequence(self):
        q = asyncio.Queue()
        ping = Ping()
        ping.next()
        await q.put(Ping().buf)
        with patch.object(funcs, "CHECK_TIMEOUT", 0.1):
            task = asyncio.create_task(self.check._wait_reply(q, ping))
            await asyncio.sleep(0)
            self.assertFalse(task.done())
            await q.put(Ping.reply(ping.buf).buf)
            await task

    async def test_ipv4_probe_and_cancellation(self):
        loop = asyncio.get_running_loop()
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.setblocking(False)
        client.bind(("127.0.0.1", 0))
        self.check.add_peer("127.0.0.1", client.getsockname()[1], {})
        with patch.object(funcs, "CHECK_PORT", 0):
            task = asyncio.create_task(self.check.server("::1", "127.0.0.1"))
            try:
                await asyncio.wait_for(self.check.event_server_ping.wait(), 1)
                data, addr = await asyncio.wait_for(loop.sock_recvfrom(client, 8192), 1)
                self.assertEqual(data[0], PacketType.PING)
                self.assertEqual(addr[0], "127.0.0.1")
                await loop.sock_sendto(client, Ping.reply(data).buf, addr)
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
                client.close()
        self.assertFalse(self.check.socks)
        self.assertFalse(self.check._tasks)

    async def test_stale_replies_do_not_reset_timeout(self):
        q = asyncio.Queue()
        ping = Ping()
        ping.next()

        async def stale_replies():
            while True:
                await q.put(Ping().buf)
                await asyncio.sleep(0.001)

        producer = asyncio.create_task(stale_replies())
        try:
            with patch.object(funcs, "CHECK_TIMEOUT", 0.02):
                with self.assertRaises(TimeoutError):
                    await asyncio.wait_for(self.check._wait_reply(q, ping), 0.2)
        finally:
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)

    async def test_domain_update_is_per_peer_and_off_event_loop(self):
        main_thread = threading.get_ident()
        threads = []

        def resolve(domain):
            threads.append(threading.get_ident())
            self.assertEqual(domain, "wg.example.test")
            return "192.0.2.1"

        def update(*args):
            threads.append(threading.get_ident())

        first = {"endpoint_addr": "wg.example.test", "public_key": "first"}
        second = dict(first, public_key="second")
        with patch.object(util, "getaddrinfo", side_effect=resolve), \
                patch.object(util, "wg_peer_option", side_effect=update) as setter:
            await self.check.update_domain(first)
            await self.check.update_domain(second)
            await self.check.update_domain(first)
        self.assertEqual(setter.call_count, 2)
        self.assertTrue(all(thread != main_thread for thread in threads))
        self.assertEqual(first["endpoint_addr"], "wg.example.test")

    async def test_failed_probe_triggers_domain_update(self):
        stop = asyncio.Event()
        client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        client.bind(("::1", 0))
        peer = {"endpoint_addr": "wg.example.test", "public_key": "first"}
        self.check.add_peer("::1", client.getsockname()[1], peer)

        async def update(conf):
            self.assertEqual(conf, peer)
            stop.set()

        try:
            with patch.object(funcs, "CHECK_PORT", 0), \
                    patch.object(funcs, "CHECK_TIMEOUT", 0.01), \
                    patch.object(funcs, "CHECK_FAILED_COUNT", 2), \
                    patch.object(self.check, "update_domain", side_effect=update) as updater:
                await asyncio.wait_for(self.check.server("::1", stop_event=stop), 1)
                updater.assert_awaited_once()
        finally:
            client.close()

    async def test_receive_failure_closes_sockets(self):
        with patch.object(funcs, "CHECK_PORT", 0), \
                patch.object(self.check, "_handle_sock", new=AsyncMock(side_effect=RuntimeError("receive failed"))):
            with self.assertRaises(ExceptionGroup):
                await self.check.server("::1")
        self.assertFalse(self.check.socks)
        self.assertFalse(self.check._tasks)

    async def test_setup_failure_deletes_created_interface(self):
        conf = {"ifname": {"interface": "wg-test"}}
        with patch.object(util, "ip_link_add_wg") as add, \
                patch.object(util, "ip_link_del_wg") as delete:
            with self.assertRaises(TypeError):
                await _server(conf)
        add.assert_called_once_with("wg-test")
        delete.assert_called_once_with("wg-test")

    async def test_heartbeat_failure_deletes_interface(self):
        conf = {"ifname": {"interface": "wg-test", "MTU": 1280,
                           "address": ["::1/128"], "private_key": "test"}, "peers": []}
        with patch.object(util, "ip_link_add_wg"), \
                patch.object(util, "ip_link_mtu"), \
                patch.object(util, "ip_addr_add"), \
                patch.object(util, "wg_set"), \
                patch.object(util, "ip_link_del_wg") as delete, \
                patch.object(CheckAlive, "server", new=AsyncMock(side_effect=RuntimeError("failed"))):
            with self.assertRaises(RuntimeError):
                await _server(conf)
        delete.assert_called_once_with("wg-test")

    async def test_sigterm_stops_service_and_restores_handler(self):
        conf = {"ifname": {"interface": "wg-test", "MTU": 1280,
                           "address": ["::1/128"], "private_key": "test"}, "peers": []}
        previous = signal.getsignal(signal.SIGTERM)

        async def heartbeat(ipv6, ipv4, stop):
            signal.raise_signal(signal.SIGTERM)
            await asyncio.wait_for(stop.wait(), 1)

        with patch.object(util, "ip_link_add_wg"), \
                patch.object(util, "ip_link_mtu"), \
                patch.object(util, "ip_addr_add"), \
                patch.object(util, "wg_set"), \
                patch.object(util, "ip_link_del_wg") as delete, \
                patch.object(CheckAlive, "server", side_effect=heartbeat):
            await _server(conf)
        delete.assert_called_once_with("wg-test")
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)

    async def test_cancelled_sync_operation_finishes_before_cleanup(self):
        started = threading.Event()
        release = threading.Event()
        finished = threading.Event()

        def operation():
            started.set()
            release.wait(1)
            finished.set()

        task = asyncio.create_task(funcs.run_sync(operation))
        try:
            self.assertTrue(await asyncio.to_thread(started.wait, 1))
            task.cancel()
            await asyncio.sleep(0)
            self.assertFalse(task.done())
        finally:
            release.set()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertTrue(finished.is_set())

    async def test_pyroute2_read_only_query_from_async_service(self):
        # 使用真实同步 API，避免 mock 掩盖嵌套事件循环错误；仅查询链路。
        def query():
            with util.IPRoute() as ipr:
                return ipr.get_links()

        self.assertTrue(await funcs.run_sync(query))


if __name__ == "__main__":
    unittest.main()
