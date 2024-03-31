#!/usr/bin/env python3
# coding=utf-8
# date 2023-09-13 20:06:16
# author calllivecn <calllivecn@outlook.com>


import json
import copy


from pyroute2 import (
    NDB,
    WireGuard,
)

import util
from log import logger


__all__ = (
    "WgShow"
)

class WgShow:

    def __init__(self):

        self.ndb = NDB()
    

    def close(self):
        self.ndb.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # logger.debug(f"执行退出清理：{exc_type=} {exc_value=} {traceback=}")
        self.close()


    def list_wg(self):
        r = (
            self.ndb.interfaces.summary()
            # ndb.interfaces.dump()
            .filter(kind="wireguard")
            .select("index", "ifname", "kind")
            .format("json")
        )
        return json.loads(str(r))



    def show_wg(self, ifname):
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

        # return wg

        # wg 从pyroute2 里 解析 出来 dict 的 信息格式
        # 之后还需要添加，address, 
        wg_conf = {}
        for k, v in wg["attrs"]:
            if "IFNAME" in k:
                wg_conf["interface"] = v

            elif "PRIVATE_KEY" in k:
                wg_conf["private_key"] = v

            elif "PUBLIC_KEY" in k:
                wg_conf["public_key"] = v

            elif "LISTEN_PORT" in k:
                wg_conf["listen_port"] = v

            elif "WGDEVICE_A_FWMARK" in k:
                wg_conf["fwmark"] = v

            elif "WGDEVICE_A_PEERS" in k:
                peers = v
            
            elif "PRESHARED_KEY" in k:
                peers["preshared_key"] = v

            else:
                logger.debug(f"跳过: {k=} {v=}")


        addrs = []
        with NDB() as ndb:
            for addr in util.ip_addr_ifname(ndb, ifname):
                # logger.debug(f"{addr=} {addr.address=}, {addr.prefixlen=}")
                addrs.append("/".join([addr.address, str(addr.prefixlen)]))

        wg_conf["address"] = addrs

        peers_conf = []
        wg_conf["peers"] = peers_conf
        for peer in peers:
            peer_conf = {}
            for k, v in peer["attrs"]:
                if "PUBLIC_KEY" in k:
                    peer_conf["public_key"] = v

                elif "PRESHARED_KEY" in k:
                    if v != b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=":
                        peer_conf["preshared_key"] = v

                elif "PROTOCOL_VERSION" in k:
                    peer_conf["wg_protocol_version"] = v

                elif "ENDPOINT" in k:
                    peer_conf["endpoint_addr"] = v["addr"]
                    peer_conf["endpoint_port"] = v["port"]

                elif "ALLOWEDIPS" in k:
                    ips = []
                    for nets in v:
                        ips.append(nets["addr"])

                    peer_conf["allowed_ips"] = ips 

                # elif "HANDSHAKE_TIME" in k:
                    # peer_conf["handshake_time"]

                # elif "PERSISTENT_KEEPALIVE_INTERVAL" in k:

                elif "WGPEER_A_TX_BYTES" == k:
                    peer_conf["tx_bytes"] = v

                elif "WGPEER_A_RX_BYTES" == k:
                    peer_conf["rx_bytes"] = v


            peers_conf.append(peer_conf)

        wg_conf["peers"] = peers_conf

        self.peers_conf = peer_conf
        return wg_conf


    def get_wg_conf(self):
        """
        返回可转发的配置信息
        """
        confs = copy.deepcopy(self.peers_conf)

        data = []
        for conf in confs:
            conf.pop("private_key")
            conf.pop("")

    
    def wg_conf_transport(self):

        self.get_wg_conf
        


def main():
    import pprint
    with WgShow() as ws:

        list_wg_list = ws.list_wg()
        logger.debug(f"""{"="*20}""")
        logger.debug(f"{type(list_wg_list)=} {list_wg_list=}")


        for wg_kind in list_wg_list:
            wg_conf = ws.show_wg(wg_kind["ifname"])
            logger.debug(f"""{"="*10} {wg_kind["ifname"]} {"="*10}""")
            logger.debug("\n" + pprint.pformat(wg_conf))
    

if __name__ == "__main__":
    main()

