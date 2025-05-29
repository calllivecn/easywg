#!/usr/bin/env python3
# coding=utf-8
# date 2023-08-16 01:55:59
# author calllivecn <calllivecn@outlook.com>


import sys
import argparse

from log import (
    logger,
    DEBUG,
)
import funcs
from funcs import (
    Argument,
    loadconf,
    Path,
)
import util
from server import server


def main():

    parse = Argument(
        usage="%(prog)s",
        epilog="https://github.com/calllivecn/easywg",
    )

    parse.add_argument("--server", action="store_true", help="启动服务端")

    parse.add_argument("--genkey", action="store_true", help="生成密钥对")
    parse.add_argument("--pubkey", metavar="<private_key>", action="store", help="从指定私钥生成公钥")
    parse.add_argument("--genpsk", action="store_true", help="生成预共享密钥")

    parse.add_argument("--show", action="store_true", help="查看当前wg接口")

    parse.add_argument("--debug", action="store_true", help="debug 模式")
    parse.add_argument("--parse", action="store_true", help=argparse.SUPPRESS)

    parse.add_argument("conf", nargs="?", type=Path, help="wg 配置文件，toml文件。")


    args = parse.parse_args()

    if args.parse:
        print(args)
        sys.exit(0)
    
    if args.debug:
        logger.setLevel(DEBUG)

    if args.server:
        try:
            conf = loadconf(args.conf)
        except Exception:
            print("配置错误")
            sys.exit(1)

        funcs.CHECK_PORT = conf.get("check_port", 19000)
        funcs.CHECK_TIMEOUT = conf.get("check_timeout", 5)
        funcs.CHECK_FAILED_COUNT = conf.get("check_failed_count", 6)

        server(conf)

    elif args.genkey:
        privkey, pubkey = util.genkey()
        print(f"私钥: {privkey}")
        print(f"公钥: {pubkey}")

    elif args.pubkey:
        try:
            pubkey = util.pubkey(args.pubkey)
            print(f"公钥: {pubkey}")
        except Exception as e:
            print(f"生成公钥失败: {e}")

    elif args.genpsk:
        psk = util.genpsk()
        print(f"预共享密钥: {psk}")
    
    elif args.show:
        import wgshow
        wgshow.main()

    else:
        parse.print_help()
        sys.exit(0)

if __name__ == "__main__":            
    main() 