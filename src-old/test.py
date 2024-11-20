#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-17 01:58:54
# author calllivecn <calllivecn@outlook.com>

from pyroute2 import (
    NDB,
    WireGard,
)

def getifname_index(ifname):
    with NDB() as ndb:
        return ndb.interfaces[ifname]["index"]

# 添加一个路由
def add_route_ifname(nets, ifname):
    with NDB() as ndb:
        r = ndb.routes.create(dst=nets, oif=getifname_index(ifname))
        r.commit()
        print(r)

def add_route_via(nets, via):
    with NDB() as ndb:
        #r = ndb.routes.create(dst=nets, via=via).commit()
        r = ndb.routes.create(dst=nets)
        r.set(gateway=via)
        #r.set(proto=2) # proto字段的定义在内核中并没有实质的意义，只是一个显示字段。RTPROT_UNSPEC表示未指定； 其他值可以查看 vim /etc/iproute2/rt_protos
        r.commit()
        print(r)

def del_route(nets):
    with NDB() as ndb:
        r = ndb.routes[nets]
        r.remove()
        r.commit()

if __name__ == "__main__":
    #add_route_ifname("192.168.9.0/24", "wlp5s0")
    add_route_via("10.1.2.0/24", "192.168.8.10")
    #del_route("10.1.2.0/24")
