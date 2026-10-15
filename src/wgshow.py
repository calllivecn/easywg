#!/usr/bin/env python3
# coding=utf-8

import base64
import os
import sys
import time
import unicodedata

from pyroute2 import WireGuard

import util


__all__ = ("WgShow",)

RECENT_HANDSHAKE_SECONDS = 180


def human_byte_size(size: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if size < 1024 or unit == "PiB":
            return f"{size:.0f} B" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024

    return ""


def key_text(key) -> str:
    if isinstance(key, bytes):
        # pyroute2 通常返回 base64 字节串，也兼容原始 32 字节密钥。
        return base64.b64encode(key).decode("ascii") if len(key) == 32 else key.decode("ascii")
    return str(key or "")


def has_preshared_key(key) -> bool:
    if not key:
        return False
    if isinstance(key, bytes) and len(key) == 32:
        return any(key)
    try:
        return any(base64.b64decode(key, validate=True))
    except (ValueError, TypeError):
        return True


def short_key(key) -> str:
    key = key_text(key)
    return f"{key[:8]}…{key[-8:]}" if len(key) > 20 else key or "—"


def endpoint_text(address, port) -> str:
    if not address:
        return "未设置"
    if ":" in address and not address.startswith("["):
        address = f"[{address}]"
    return f"{address}:{port}" if port is not None else address


def handshake_status(timestamp, now):
    if not timestamp:
        return "从未握手", "90", "—"
    seconds = max(0, int(now - timestamp))
    if seconds < 60:
        age = f"{seconds} 秒前"
    elif seconds < 3600:
        age = f"{seconds // 60} 分 {seconds % 60} 秒前"
    elif seconds < 86400:
        age = f"{seconds // 3600} 小时 {seconds % 3600 // 60} 分前"
    else:
        age = f"{seconds // 86400} 天 {seconds % 86400 // 3600} 小时前"
    if seconds <= RECENT_HANDSHAKE_SECONDS:
        return "近期握手", "32", age
    return "握手较旧", "33", age


class WgShow:
    def show_wg(self, ifname, private=False) -> dict:
        # 保留旧调用签名，但展示数据中始终不保留真实私钥和预共享密钥。
        with WireGuard() as wg:
            device = wg.info(ifname)[0]

        conf = {
            "interface": device.get_attr("WGDEVICE_A_IFNAME"),
            "fwmark": device.get_attr("WGDEVICE_A_FWMARK") or 0,
            "listen_port": device.get_attr("WGDEVICE_A_LISTEN_PORT"),
            "private_key": "****",
            "public_key": key_text(device.get_attr("WGDEVICE_A_PUBLIC_KEY")),
            "ip_address": [f"{addr}/{prefix}" for addr, prefix in util.ip_addr_ifname(ifname)],
            "peers": [],
        }
        for peer in device.get_attr("WGDEVICE_A_PEERS") or []:
            endpoint = peer.get_attr("WGPEER_A_ENDPOINT") or {}
            handshake = peer.get_attr("WGPEER_A_LAST_HANDSHAKE_TIME") or {}
            item = {
                "public_key": key_text(peer.get_attr("WGPEER_A_PUBLIC_KEY")),
                "persistent_keepalive": peer.get_attr("WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL") or 0,
                "endpoint_addr": endpoint.get("addr"),
                "endpoint_port": endpoint.get("port"),
                "allowed_ips": [ip.get("addr") for ip in peer.get_attr("WGPEER_A_ALLOWEDIPS") or []],
                "tx_bytes": peer.get_attr("WGPEER_A_TX_BYTES") or 0,
                "rx_bytes": peer.get_attr("WGPEER_A_RX_BYTES") or 0,
                "latest_handshake": handshake.get("tv_sec", 0),
            }
            if has_preshared_key(peer.get_attr("WGPEER_A_PRESHARED_KEY")):
                item["preshared_key"] = "***"
            conf["peers"].append(item)
        self.wg_conf = conf
        return conf


def render_interface(device, conf=None, *, color=False, now=None) -> str:
    now = time.time() if now is None else now

    def paint(text, code):
        return f"\033[{code}m{text}\033[0m" if color else str(text)

    def clean(text):
        # 备注等配置文本按单行展示，避免控制字符破坏卡片布局。
        return "".join(c if not unicodedata.category(c).startswith("C") else " " for c in str(text))

    def field(label, value, indent=2):
        width = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in label)
        return " " * indent + paint(label, "90") + " " * max(2, 14 - width) + str(value)

    configured = {}
    if conf and conf.get("ifname", {}).get("interface") == device["interface"]:
        configured = {key_text(p["peer"]["public_key"]): p for p in conf.get("peers", [])}

    peers = device.get("peers", [])
    states = [handshake_status(p.get("latest_handshake"), now) for p in peers]
    counts = {name: sum(s[0] == name for s in states) for name in ("近期握手", "握手较旧", "从未握手")}
    rule = paint("─" * 66, "90")
    lines = [paint(f"WireGuard · {device['interface']}", "1;36"), rule,
             field("地址", " · ".join(device.get("ip_address", [])) or "—"),
             field("监听", f"UDP {device.get('listen_port', 0)}"),
             field("公钥", short_key(device.get("public_key"))),
             field("PRIVATE_KEY", "****"),
             field("FwMark", hex(device.get("fwmark", 0))), "",
             f"  节点 {len(peers)}    " + " · ".join(f"{name} {count}" for name, count in counts.items()), rule]

    for peer, (status, status_color, age) in zip(peers, states):
        source = configured.get(key_text(peer.get("public_key")), {})
        peer_conf = source.get("peer", {})
        comment = source.get("info", {}).get("comment")
        name = clean(comment).strip() if comment else ""
        name = name or "未知"
        lines.extend(["", f"  {paint('●', status_color)} {paint(name, '1')}    {paint(status, status_color)}"])
        current_endpoint = endpoint_text(peer.get("endpoint_addr"), peer.get("endpoint_port"))
        configured_endpoint = endpoint_text(peer_conf.get("endpoint_addr"), peer_conf.get("endpoint_port"))
        lines.append(field("Endpoint", clean(configured_endpoint if peer_conf.get("endpoint_addr") else current_endpoint), 4))
        if peer_conf.get("endpoint_addr") and configured_endpoint != current_endpoint:
            lines.append(field("当前地址", current_endpoint, 4))
        lines.extend([
            field("隧道网段", " · ".join(peer.get("allowed_ips", [])) or "—", 4),
            field("最近握手", paint(age, status_color), 4),
            field("流量", paint(f"↓ {human_byte_size(peer.get('rx_bytes', 0))}", "36") + "    "
                  + paint(f"↑ {human_byte_size(peer.get('tx_bytes', 0))}", "35"), 4),
            field("Keepalive", f"{peer['persistent_keepalive']} 秒" if peer.get("persistent_keepalive") else "关闭", 4),
            field("PUBLIC_KEY", key_text(peer.get("public_key")) or "—", 4),
        ])
        if "preshared_key" in peer or "preshared_key" in peer_conf:
            lines.append(field("PRESHARED_KEY", "***", 4))
    if not peers:
        lines.extend(["", "  暂无 peer"])
    lines.extend(["", paint("  状态依据最近握手时间（3 分钟内为近期），不代表实时心跳结果。", "90")])
    return "\n".join(lines)


def main(bool_=False, conf=None):
    # --show-private 兼容旧参数，所有展示入口统一遮蔽密钥。
    interfaces = [conf["ifname"]["interface"]] if conf is not None else util.list_wg_all()
    if not interfaces:
        print("未发现 WireGuard 接口")
        return
    color = sys.stdout.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
    ws = WgShow()
    for index, name in enumerate(interfaces):
        if index:
            print()
        print(render_interface(ws.show_wg(name), conf, color=color))


if __name__ == "__main__":
    main()
