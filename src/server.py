#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-17 04:19:44
# author calllivecn <calllivecn@outlook.com>


"""
怎么规划
使用 |cmd 2byte|payload| 先简单定义几个操作：

1. 添加一个 client peer 
2. 删除一个 client peer(delpeer <pubkey>)
3. peer [enable, disable, boot] <pubkey>
5. list <interface>
# interface 操作
6. interface add pickle({"CIDR": "10.1.1.1/24", port": <port>, "PersistentKeepalive": 35})
6. interface [enable, disable, boot] <ifname>
7. list-interfaces

8. 使用 pickle 简化 json 配置通信过程
"""


import socket
import pickle

