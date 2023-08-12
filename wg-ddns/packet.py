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

    PING = 0x01
    WP_PEER_INFO = enum.auto()
    PING_REPLY = enum.auto()
    SERVER_PING = enum.auto()
    SERVER_PING_REPLY = enum.auto()
    WP_PEER_INFO_CONFIRM = enum.auto()
    


class PacketTypeError(Exception):
    pass


class Ping(struct.Struct):

    def __init__(self, typ=PacketType.PING):

        super().__init__("!BQ")

        self.typ = typ
        self.seq = 0

        self.buf = bytearray(self.size)
        self.pack_into(self.buf, 0, self.typ, self.seq)
    

    @staticmethod
    def reply(packet: bytes) -> Type["Ping"]:

        p = Ping()

        if packet[0] == PacketType.PING:
            p.typ = PacketType.PING_REPLY

        elif packet[0] == PacketType.SERVER_PING:
            p.typ = PacketType.SERVER_PING_REPLY

        typ, p.seq = p.unpack(packet[:p.size])
        p.pack_into(p.buf, 0, p.typ, p.seq)
        return p

    
    # @classmethod
    @staticmethod
    def server_reply(packet: bytes) -> Type["Ping"]:
        p = Ping(PacketType.SERVER_PING_REPLY)
        typ, p.seq = p.unpack(packet[:p.size])
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
    sender_pubkey: 32B
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