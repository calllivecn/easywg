#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>

import sys
import time
import json
import copy
import atexit
import logging
import subprocess
from pathlib import Path


import util

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


# 在线检测
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
        time.sleep(1)
    

def main():

    try:
        conf = loadconf()
    except Exception:
        print("配置错误")
        sys.exit(1)
    
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
        
        dns = peer["endpoint_addr"]
        addr = util.dnsquery(dns)
        if len(addr) == 0:
            logger.warning(f"没有查询到 {server_addr} IP, 可能出错了。请检查")
            continue


        peer["endpoint_addr"] = addr
        
        logger.debug(f"{peer=}")
        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)
    

    while True:
        # 目前测试阶段，只先做一个peer端的处理
        peer = copy.deepcopy(conf["peers"][0])
        server_addr = peer["endpoint_addr"]
        public_key = peer["public_key"]

        check_alive(conf["server_wg_ip"])

        logger.debug(f"{server_addr=} {public_key=}")

        logger.info(f"重新解析域名，并更新wireguard。")

        addr = util.dnsquery(server_addr)
        if len(addr) == 0:
            logger.warning(f"没有查询到 {server_addr} IP, 可能出错了。请检查")
            # sys.exit(1)
            return
        
        logger.info(f"新地址: {addr}")
        peer["endpoint_addr"] = addr
        logger.debug(f"{peer=}")

        with util.WireGuard() as wg:
            wg.set(wg_name, peer=peer)
        

if __name__ == "__main__":            
    # 怎么没用 ？ logger.setLevel(logging.DEBUG)
    main()
