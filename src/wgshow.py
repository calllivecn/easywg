#!/usr/bin/env python3
# coding=utf-8
# date 2023-09-13 20:06:16
# author calllivecn <calllivecn@outlook.com>


import copy

from datetime import (
    datetime,
    timedelta,
)

from pyroute2 import (
    WireGuard,
)

import util
from log import logger


__all__ = (
    "WgShow",
    )


def human_byte_size(size: int|float) -> str:
    """
    将字节数转换为人类可读的格式
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f}"


class WgShow:

    def show_wg(self, ifname, private=False) -> dict:
        self._private = private

        """
        wg show:
        {'attrs': [('WGDEVICE_A_LISTEN_PORT', 18000),
               ('WGDEVICE_A_FWMARK', 0),
               ('WGDEVICE_A_IFINDEX', 6),
               ('WGDEVICE_A_IFNAME', 'wg-pyz'),
               ('WGDEVICE_A_PRIVATE_KEY', b'000000000000000000000000000000'),
               ('WGDEVICE_A_PUBLIC_KEY', b'000000000000000000000000000000'),
               ('WGDEVICE_A_PEERS', [{'attrs': [('WGPEER_A_PUBLIC_KEY', b'000000000000000000000000000000'), ('WGPEER_A_PRESHARED_KEY', b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='), ('WGPEER_A_LAST_HANDSHAKE_TIME', {'tv_sec': 1694717024, 'tv_nsec': 765360652, 'latest handshake': 'Fri Sep 15 02:43:44 2023'}), ('WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL', 0), ('WGPEER_A_TX_BYTES', 167968360), ('WGPEER_A_RX_BYTES', 183858848), ('WGPEER_A_PROTOCOL_VERSION', 1), ('WGPEER_A_ENDPOINT', {'family': 10, 'port': 18000, 'flowinfo': 0, 'addr': '240e:3ba:30b1:4b40:e4d2:649f:e95b:bd39', 'scope_id': 0}), ('WGPEER_A_ALLOWEDIPS', [{'attrs': [('WGALLOWEDIP_A_CIDR_MASK', 24), ('WGALLOWEDIP_A_FAMILY', 2), ('WGALLOWEDIP_A_IPADDR', '0a:01:03:00')], 'addr': '10.1.3.0/24'}, {'attrs': [('WGALLOWEDIP_A_CIDR_MASK', 64), ('WGALLOWEDIP_A_FAMILY', 10), ('WGALLOWEDIP_A_IPADDR', 'fc:03:00:00:00:00:00:00:00:00:00:00:00:00:00:00')], 'addr': 'fc03::/64'}], 32768)]}], 32768)],
        'cmd': 0,
        'header': {'error': None,
                   'flags': 2,
                   'length': 372,
                   'pid': 2728308,
                   'sequence_number': 255,
                   'stats': Stats(qsize=0, delta=0, delay=0),
                   'target': 'localhost',
                   'type': 35},
        'reserved': 0,
        'version': 1}

        -----------------
        wg_conf:[
            {'address': ['10.x.x.x/24', 'fcxx::xx/64'],
            'fwmark': 0,
            'interface': 'wg-pyz',
            'listen_port': 18000,
            'peers': [{'allowed_ips': ['10.x.x.x/24', 'fcxx::xx/64'],
                       'endpoint_addr': 'xxxx:xxxx/64',
                       'endpoint_port': 18000,
                       'public_key': b'00000000000000000000000000000000000000',
                       'rx_bytes': 25328587220,
                       'tx_bytes': 958578428,
                       'wg_protocol_version': 1}],
            'private_key': b'000000000000000000000000000000000000000000',
            'public_key': b'000000000000000000000000000000000000'}
        ]
        """

        with WireGuard() as wg:
            wg = wg.info(ifname)[0]

        wg_conf = {}
        wg_conf["interface"] = wg.get_attr('WGDEVICE_A_IFNAME')
        wg_conf["fwmark"] = wg.get_attr('WGDEVICE_A_FWMARK')
        wg_conf["if_index"] = wg.get_attr('WGDEVICE_A_IFINDEX')
        wg_conf["listen_port"] = wg.get_attr('WGDEVICE_A_LISTEN_PORT')
        wg_conf["private_key"] = wg.get_attr('WGDEVICE_A_PRIVATE_KEY') if self._private else "**********"
        wg_conf["public_key"] = wg.get_attr('WGDEVICE_A_PUBLIC_KEY')

        addrs = []
        for addr, prefixlen in util.ip_addr_ifname(ifname):
            addrs.append("/".join([addr, str(prefixlen)]))

        wg_conf["ip_address"] = addrs


        peers = wg.get_attr("WGDEVICE_A_PEERS")
        peers_conf = []
        for peer in peers:
            peer_conf = {}
            peer_conf["wg_protocol_version"] = peer.get_attr('WGPEER_A_PROTOCOL_VERSION')
            peer_conf["public_key"] = peer.get_attr('WGPEER_A_PUBLIC_KEY')
            peer_conf["preshared_key"] = peer.get_attr('WGPEER_A_PRESHARED_KEY') if self._private else "**********"
            peer_conf["persistent_keepalive"] = peer.get_attr('WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL')

            endpoint = peer.get_attr('WGPEER_A_ENDPOINT')
            if endpoint:
                peer_conf["endpoint_addr"] = endpoint.get("addr")
                peer_conf["endpoint_port"] = endpoint.get("port")

            allowed_ips = peer.get_attr('WGPEER_A_ALLOWEDIPS')
            allowed_ips_list = []
            for allowed_ip in allowed_ips:
                allowed_ips_list.append(allowed_ip.get('addr'))
            
            peer_conf["allowed_ips"] = allowed_ips_list

            # 统计信息
            peer_conf["tx_bytes"] = human_byte_size(peer.get_attr('WGPEER_A_TX_BYTES'))
            peer_conf["rx_bytes"] = human_byte_size(peer.get_attr('WGPEER_A_RX_BYTES'))
            
            # 其他信息
            tv_sec = peer.get_attr('WGPEER_A_LAST_HANDSHAKE_TIME')["tv_sec"]
            now = datetime.now().timestamp()
            latest = timedelta(seconds=round(now - tv_sec))
            peer_conf["latest_handshake"] = f"{latest} 之前"

            peers_conf.append(peer_conf)

        wg_conf["peers"] = peers_conf

        self.wg_conf = wg_conf
        return self.wg_conf


    def get_wg_conf(self):
        """
        返回可转发的配置信息
        """
        confs = copy.deepcopy(self.wg_conf)

        data = []
        for conf in confs:
            conf.pop("private_key")
            conf.pop("")

    
    def wg_conf_transport(self):

        self.get_wg_conf



def main(bool_=False):
    import pprint

    list_wg_list = util.list_wg_all()
    logger.debug(f"""{"="*20}""")
    logger.debug(f"{type(list_wg_list)=} {list_wg_list=}")


    ws = WgShow()
    for wg in list_wg_list:
        wg_conf = ws.show_wg(wg, bool_)
        print(f"""{"="*10} {wg} {"="*10}""")
        print(pprint.pformat(wg_conf))
    

if __name__ == "__main__":
    main()

