#!/usr/bin/env python3
# coding=utf-8
# date 2023-09-13 20:06:16
# author calllivecn <c-all@qq.com>



from pyroute2 import (
    NDB,
    WireGuard,
)

import util
from log import logger


ndb = NDB()

def list_wg():
    r = (
        ndb.interfaces.summary()
        # ndb.interfaces.dump()
        .filter(kind="wireguard")
        .select("index", "ifname", "kind")
        .format("json")
    )
    return r


import pprint

def show_wg(ifname):
    """
    wg:
    {'attrs': [('WGDEVICE_A_LISTEN_PORT', 18000),
           ('WGDEVICE_A_FWMARK', 0),
           ('WGDEVICE_A_IFINDEX', 6),
           ('WGDEVICE_A_IFNAME', 'wg-pyz'),
           ('WGDEVICE_A_PRIVATE_KEY', b'SGjim+kz/TYafPCp8i5s2ga5HNl/lRE8L1rYL4SNcXk='),
           ('WGDEVICE_A_PUBLIC_KEY', b'vylLRq36NG76807VDAhmFrJfcanlGTIVIVXCZqNa5nY='),
           ('WGDEVICE_A_PEERS', [{'attrs': [('WGPEER_A_PUBLIC_KEY', b'aEhoRpWJiJGAMD4MLw0WpmWcsLrUUGArb7rzuBITOiw='), ('WGPEER_A_PRESHARED_KEY', b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='), ('WGPEER_A_LAST_HANDSHAKE_TIME', {'tv_sec': 1694717024, 'tv_nsec': 765360652, 'latest handshake': 'Fri Sep 15 02:43:44 2023'}), ('WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL', 0), ('WGPEER_A_TX_BYTES', 167968360), ('WGPEER_A_RX_BYTES', 183858848), ('WGPEER_A_PROTOCOL_VERSION', 1), ('WGPEER_A_ENDPOINT', {'family': 10, 'port': 18000, 'flowinfo': 0, 'addr': '240e:3ba:30b1:4b40:e4d2:649f:e95b:bd39', 'scope_id': 0}), ('WGPEER_A_ALLOWEDIPS', [{'attrs': [('WGALLOWEDIP_A_CIDR_MASK', 24), ('WGALLOWEDIP_A_FAMILY', 2), ('WGALLOWEDIP_A_IPADDR', '0a:01:03:00')], 'addr': '10.1.3.0/24'}, {'attrs': [('WGALLOWEDIP_A_CIDR_MASK', 64), ('WGALLOWEDIP_A_FAMILY', 10), ('WGALLOWEDIP_A_IPADDR', 'fc:03:00:00:00:00:00:00:00:00:00:00:00:00:00:00')], 'addr': 'fc03::/64'}], 32768)]}], 32768)],
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
        
        else:
            logger.debug(f"跳过: {k=} {v=}")


    addrs = []
    with NDB() as ndb:
        for addr in util.ip_addr_ifname(ndb, ifname):
            logger.debug(f"{addr=} {addr.address=}, {addr.prefixlen=}")
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

    return wg_conf


list_wg_list = list_wg()
logger.debug(f"""{"="*20}""")
logger.debug(f"{type(list_wg_list)=}")

wg_conf = show_wg("wg-pyz")
logger.debug(f"""{"="*20}""")
logger.debug(pprint.pformat(wg_conf))

ndb.close()
