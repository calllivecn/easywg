#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-30 06:48:38
# author calllivecn <c-all@qq.com>


import sys
import time

from dnslib import (
    A,
    AAAA,
    RR,
    QTYPE,
    RCODE,
)
from dnslib.server import (
    DNSLogger,
    DNSServer,
)

class TestResolver:
    def resolve(self, request, handler):

        reply = request.reply()
        qname = request.q.qname
        qtype = request.q.qtype

        if qname == 'www.test123.com' and QTYPE[qtype]=='A':
            answer = RR(rname=qname,rtype=QTYPE.A, ttl=60, rdata=A('192.7.0.2'))
            reply.add_answer(answer)
            return reply
        
        elif qname == 'www.test123.com' and QTYPE[qtype]=='AAAA':
            answer = RR(rname=qname, rtype=QTYPE.AAAA, ttl=60, rdata=AAAA('fd00:acf1:23::12'))
            reply.add_answer(answer)
            return reply
        ## 调价其他的域名对应的IP，在这里加if语句增加
        
        else:
        ## 未匹配到时的返回值
        # reply.header.rcode = getattr(RCODE, 'NXDOMAIN')
            reply.header.rcode = RCODE.NXDOMAIN
            return reply
 

def main():
    resolver = TestResolver()
    logger = DNSLogger(prefix=False)
    dns_server = DNSServer(resolver,port=15353, address='0.0.0.0', logger=logger)
    dns_server.start_thread()
    try:
        while True:
            time.sleep(600)
            sys.stderr.flush()
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(0)
if __name__ == '__main__':
    main()