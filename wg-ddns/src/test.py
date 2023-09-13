#!/usr/bin/env python3
# coding=utf-8
# date 2023-09-13 20:06:16
# author calllivecn <c-all@qq.com>


from pyroute2 import (
    NDB,
    WireGuard,
)

ndb = NDB()

def list_wg():
    r = ndb.interfaces.summary()
    # r = ndb.interfaces.dump()
    r.filter(kind="wireguard")
    r.select("index", "ifname", "kind")
    r.format("json")
    return r



print(list_wg())

ndb.close()
