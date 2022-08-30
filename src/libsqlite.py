#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-27 14:33:33
# author calllivecn <c-all@qq.com>


import sqlite3
from pathlib import Path


INIT_SQLS= r"""
create table Interface(
    id integer primary key autoincrement,
    ifname char(15) not null unique CHECK(LENGTH(ifname) <= 15),
    host TEXT not null,
    network TEXT not null unique,
    ip TEXT not null unique,
    privatekey char(44) not null CHECK(LENGTH(privatekey) == 44),
    publickey char(44) not null CHECK(LENGTH(publickey) == 44),
    listenport integer(2) not null unique CHECK(1 <= listenport AND listenport <= 65535),
    boot bool not null default false,
    comment TEXT,
    created timestamp,
    updated timestamp);

create table Peer(
    serverid integer,
    ifname char(15) not null unique CHECK(LENGTH(ifname) <= 15),
    ip char(256) not null,
    privatekey char(44) not null CHECK(LENGTH(privatekey) == 44),
    publickey char(44) not null CHECK(LENGTH(publickey) == 44),
    presharedkey char(44) CHECK(LENGTH(presharedkey) == 44),
    listenport integer(2) CHECK(1 <= listenport AND listenport <= 65535),
    persistentkeepalive integer(2) CHECK(20 <= listenport AND listenport <= 65535),
    allowedips_s TEXT not null,
    allowedips_c TEXT not null,
    boot bool not null default true,
    comment TEXT,
    created timestamp,
    updated timestamp,
    FOREIGN KEY(serverid) REFERENCES Interface(id) ON DELETE CASCADE);

CREATE TRIGGER serverwg_created AFTER insert
ON Interface
BEGIN
    update Interface set created=datetime('now', 'localtime'), updated=datetime('now', 'localtime') where new.id=Interface.id;
END;

CREATE TRIGGER serverwg_updated AFTER update
ON Interface 
BEGIN
    update Interface set updated=datetime('now', 'localtime') where new.id=Interface.id;
END;

CREATE TRIGGER clientwg_created AFTER insert
ON Peer 
BEGIN
    update Peer set created=datetime('now', 'localtime'), updated=datetime('now', 'localtime') where new.serverid=Peer.serverid;
END;

CREATE TRIGGER clientwg_updated AFTER update
ON Peer 
BEGIN
    update Peer set updated=datetime('now', 'localtime') where new.serverid=Peer.serverid;
END;
"""

def db_init(dbname: Path):
    conn = sqlite3.connect(dbname)

    # 打开sqlite3 外键
    conn.execute("PRAGMA FOREIGN_KEYS=ON;")
    conn.commit()

    cur = conn.cursor()
    try:
        cur.executescript(INIT_SQLS)
    finally:
        conn.commit()
        cur.close()
        conn.close()



def add():
    pass

def delete():
    pass

def update():
    pass

def query():
    pass


if __name__ == "__main__":
    db_init(Path("/tmp/init-test.db"))
