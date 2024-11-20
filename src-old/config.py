#!/usr/bin/env python3
# coding=utf-8
# date 2022-08-17 10:00:58
# author calllivecn <calllivecn@outlook.com>


import json


wgconf = {
    "id": 1,
    "interface":
    {
        "ifname": "<15byte>",
        "privkey": "<privkey>",
        "address": "easywg.example.com",
        "ip": "10.1.1.1/24",
        "listenport": "可选",
        "allowedips": ["10.1.1.0/24", "192.168.1.0/24"],
        "DNS": ["223.5.5.5", "ipv6"],
        "comment": "描述 可选",
    },
    "peers": [
        {
            "ifname": "<15byte>",
            "pubkey": "<pubkey",
            "pskkey": "[pskkey]",
            "address": "easywg.example.com",
            "ip": "10.1.1.1/24",
            "listenport": "可选",
            "endpoint": "donamename.com",
            "allowedips": ["10.1.1.10/32", "192.168.1.0/24"],
        }
    ]
}