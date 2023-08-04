#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-04 08:03:35
# author calllivecn <c-all@qq.com>


"""
定义 wg网络内部 数据包交换格式。
"""

import enum
import struct


class PackteType(enum.IntEnum):

    ALIVE = 0x01
    WP_PEER_INFO = enum.auto()



class Packet(struct.Strcut):
    """
    type: 1B
    length: 4B    
    payload: ...
    """
