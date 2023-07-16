#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>

import sys
import time
import json
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
    util.ip_link_add_wg(wg_name)


    atexit.register(lambda :util.ip_link_del_wg(wg_name))
    
    for CIDR in ifname["address"]:
        util.ip_addr_add(wg_name, CIDR)

    util.wg_set(wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))

    for peer in conf["peers"]:
        util.wg_peer(wg_name, peer)
    

    while True:
        server_addr = conf["peers"][0]["endpoint_addr"]
        public_key = conf["peers"][0]["public_key"]

        check_alive(conf["server_wg_ip"])

        logger.info(f"重新解析域名，并更新wireguard。")

        logger.debug(f"{server_addr=} {public_key=}")

        util.wg_peer(wg_name, conf["peers"][0])
        
        """
        # 需要更新域名指向
        ipv4, ipv6 = util.get_ip_by_addr(server_addr)
        logger.debug(f"{ipv4=} {ipv6=}")

        # 缓存下，方便检测，域名有没有更新, 不用，压力给到 check_alive()

        # 优先使用ipv6
        if len(ipv6) > 0:
            logger.info(f"使用新地址：{ipv6[0]}")
            util.wg_peer_option(wg_name, public_key, {"endpoint_addr": ipv6[0]})

        elif len(ipv4) > 0:
            logger.info(f"使用地址：{ipv4[0]}")
            util.wg_peer_option(wg_name, public_key, {"endpoint_addr": ipv4[0]})
        else:
            logger.warning("没有解析到地址！")

        """

if __name__ == "__main__":            
    # 怎么没用 ？ logger.setLevel(logging.DEBUG)
    main()
