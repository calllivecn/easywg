#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <c-all@qq.com>

import sys
import time
import json
import subprocess
from pathlib import Path


import util


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
            failed_count += 1
            if failed_count >= 3:
                return

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
    
    for CIDR in ifname["address"]:
        util.ip_addr_add(wg_name, CIDR)

    util.wg_set(wg_name, ifname["private_key"], listen_port=ifname.get("listen_port"), fwmark=ifname.get("fwmark"))
    for peer in conf["peers"]:
        util.wg_peer(wg_name, peer)
    

    while True:
        check_alive(conf["server_wg_ip"])

        server_addr = conf["peers"][0]["endpoint"]
        # 需要更新域名指向
        ipv4, ipv6 = util.get_ip_by_addr(server_addr)

        # 缓存下，方便检测，域名有没有更新, 不用，压力给到 check_alive()

        # 优先使用ipv6
        if len(ipv6) > 0:
            util.wg_peer_option("endpoint", ipv6.pop())

        elif len(ipv4) > 0:
            util.wg_peer_option("endpoint", ipv4.pop())
        else:
            print("没有解析到域名！")


if __name__ == "__main__":            
    main()
