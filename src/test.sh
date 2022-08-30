#!/bin/bash
# date 2022-08-29 21:17:45
# author calllivecn <c-all@qq.com>

DB="/tmp/init-test.db"


EXECUTE=$(printf 'sqlite3 -noheader -column %s' $DB)

FMT1='pragma foreign_keys=1;insert into Interface(ifname, host, network, ip, privatekey, publickey,listenport, boot, comment) values("wg0", "wg.easywg.com", "10.1.1.0/24", "10.1.1.1/24", "%s", "%s", 65535, true, "描述");'

$EXECUTE "$(printf "$FMT1" $(wg genkey) $(wg genkey))"

FMT2='pragma foreign_keys=1;insert into Peer(serverid, ifname, ip, privatekey, publickey, allowedips_s, allowedips_c) values(1, "wg2", "10.1.1.2/24", "%s", "%s", "10.1.1.2/32", "10.1.1.2/24");'

$EXECUTE "$(printf "$FMT2" $(wg genkey) $(wg genkey))"

FMT3='pragma foreign_keys=1;insert into Peer(serverid, ifname, ip, privatekey, publickey, allowedips_s, allowedips_c) values(1, "wg3", "10.1.1.2/24", "%s", "%s", "10.1.1.2/32", "10.1.1.2/24");'

$EXECUTE "$(printf "$FMT3" $(wg genkey) $(wg genkey))"
