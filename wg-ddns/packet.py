#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-04 08:03:35
# author calllivecn <c-all@qq.com>


"""
定义 wg网络内部 数据包交换格式。
"""

import sys
import enum
import struct

from typing import (
    # Self
    Type,
    TypeVar,
    Union,
)

Self = TypeVar("Self")


class PacketType(enum.IntEnum):

    ALIVE = 0x01
    PING = ALIVE
    WP_PEER_INFO = enum.auto()
    PING_REPLY = enum.auto()
    MULTICAST_ALIVE = enum.auto()
    MULTICAST_ALIVE_REPLY = enum.auto()


class PacketTypeError(Exception):
    pass


class Ping(struct.Struct):

    def __init__(self, typ=PacketType.PING):

        super().__init__("!BQ")

        self.typ = typ
        self.seq = 0

        self.buf = bytearray(self.size)
        self.pack_into(self.buf, 0, self.typ, self.seq)
    

    @classmethod
    def reply(cls, ping_packet: bytes) -> Type["Ping"]:
        ping = cls(PacketType.PING_REPLY)
        typ, ping.seq = cls.unpck(ping_packet[:cls.size])
        return ping

    
    @classmethod
    def frombuf(cls, packet: bytes) -> Type["Ping"]:
        typ, seq = cls.unpack(packet[:cls.size])
        p = cls(typ)
        p.seq = seq
        return p

    
    def next(self):
        self.seq += 1
        if self.seq > sys.maxsize:
            self.seq = 0

        self.pack_into(self.buf, 0, self.typ, self.seq)
    

    # def __eq__(self, other: bytes|Type["Ping"]): # py3.10 才支持
    def __eq__(self, other: Union[bytes, Type["Ping"]]):
        if isinstance(other, bytes):
            return self.buf == other

        elif isinstance(other, Ping):
            return self.buf == other.buf
        



class Packet(struct.Struct):
    """
    type: 1B
    length: 4B    
    payload: ...
    """

    def __init__(self):
        pass




if __name__ == "__main__":
    ping = Ping()
    ping2 = Ping()
    print(ping.buf, ping == ping2)
    ping.next()
    print(ping.buf, ping == ping2)

    import struct
    bi = struct.pack("!BQ", 1, 1)
    print(ping.buf, ping == bi)