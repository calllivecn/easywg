#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-27 14:33:33
# author calllivecn <c-all@qq.com>


import sqlite3
from pathlib import Path

def db_init(dbname: Path):
    conn = sqlite3.connect(dbname)

    cur = conn.cursor()

    cur.executescript(r"""
    create table ServerWg(
        id integer primary key autoincrement,
        ifname char(15) not null unique,
        address char(64) not null,
        network TEXT not null unique,
        ip char(256) not null unique,
        privatekey char(44) not null,
        publickey char(44) not null,
        listenport integer(2) not null,
        boot bool not null default false,
        comment TEXT);
    """)

    conn.commit()

    cur.executescript(r"""
    create table ClientWg(
        serverid integer,
        ifname char(15) not null,
        ip char(256) not null,
        privatekey char(44) not null,
        publickey char(44) not null,
        presharedkey char(44),
        listenport integer,
        persistentkeepalive integer,
        allowedips_s TEXT not null,
        allowedips_c TEXT not null,
        boot bool not null default true,
        comment TEXT);
    """)

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
