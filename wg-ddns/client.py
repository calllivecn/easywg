#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>

import sys
import time
import json
import copy
import struct
import socket
import atexit
import logging
import argparse
import subprocess
from pathlib import Path


import util


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
    """

    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(CHECK_TIMEOUT)

    # 每12分钟解析下域名，看看有没有改变。
    t1 = time.time()

    # 一个序列包
    seq = 0

    failed_count = 0
    check_fail_flag = False

    while True:
        try:

            sock.sendto(struct.pack("!Q", seq), (wg_peer_ip, CHECK_PORT))
            data, addr = sock.recvfrom(8192)
            if addr[0] == wg_peer_ip and seq == struct.unpack("!Q", data)[0]:
                pass
            else:
                check_fail_flag = True

        except socket.timeout:
            check_fail_flag = True

        seq += 1

        if check_fail_flag:
            logger.info(f"{wg_peer_ip} 检测好像断开了...")
            failed_count += 1

            if failed_count >= CHECK_FAIL_COUNT:
                logger.warning(f"{wg_peer_ip} 线路断开了...")
                return
            else:
                check_fail_flag = False
                continue

        if failed_count > 0:
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


# 在线检测 内置版本
def check_alive_server(wg_local_ip):

    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((wg_local_ip, CHECK_PORT))

    while True:
        data, addr = sock.recvfrom(8192)
        sock.sendto(data, addr)
    
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

        logger.info(f"重新解析域名，并更新wireguard。")
        
        logger.info(f"新地址: {new_peer_ip}")
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
    parse.add_argument("conf", metavar="config", nargs="+", help="config")

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