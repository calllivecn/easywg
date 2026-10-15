import base64
import contextlib
import io
import re
import unittest
from unittest.mock import Mock, patch

import main
import util
import wgshow


def attrs(**values):
    message = Mock()
    message.get_attr.side_effect = values.get
    return message


class WgShowTests(unittest.TestCase):
    def setUp(self):
        self.public_key = base64.b64encode(b"p" * 32).decode()
        self.secret = base64.b64encode(b"s" * 32).decode()
        self.device = {
            "interface": "wg-home", "ip_address": ["10.10.0.1/24", "fd10::1/64"],
            "listen_port": 18000, "fwmark": 0x8123, "public_key": self.public_key,
            "private_key": self.secret,
            "peers": [{
                "public_key": self.public_key, "endpoint_addr": "2001:db8::10",
                "endpoint_port": 18000, "allowed_ips": ["fd20::/64"],
                "latest_handshake": 972, "rx_bytes": 1024, "tx_bytes": 2048,
                "persistent_keepalive": 25, "preshared_key": self.secret,
            }],
        }
        self.conf = {
            "ifname": {"interface": "wg-home", "private_key": self.secret},
            "peers": [
                {"info": {"comment": "错误节点"}, "peer": {"public_key": "another"}},
                {"info": {"comment": "香港中转"}, "peer": {
                    "public_key": self.public_key, "preshared_key": self.secret,
                    "endpoint_addr": "hk.example.com", "endpoint_port": 18000,
                }},
            ],
        }

    def test_card_matches_comment_by_public_key_and_masks_secrets(self):
        output = wgshow.render_interface(self.device, self.conf, now=1000)
        for value in ("WireGuard · wg-home", "香港中转", "hk.example.com:18000",
                      "[2001:db8::10]:18000", "fd20::/64", "28 秒前",
                      "↓ 1.00 KiB", "↑ 2.00 KiB", "25 秒", "0x8123"):
            self.assertIn(value, output)
        self.assertRegex(output, r"PRIVATE_KEY\s+\*{4}\n")
        self.assertRegex(output, r"PRESHARED_KEY\s+\*{3}\n")
        self.assertNotIn(self.secret, output)
        self.assertNotIn("错误节点", output)
        self.assertNotIn("\033[", output)
        self.assertIn("● 香港中转    近期握手", output)
        self.assertNotIn("● " + wgshow.short_key(self.public_key), output)
        self.assertRegex(output, r"PUBLIC_KEY\s+" + re.escape(self.public_key))

    def test_key_collection_never_retains_secrets_even_with_legacy_flag(self):
        def peer(public_key, preshared_key):
            return attrs(WGPEER_A_PUBLIC_KEY=public_key, WGPEER_A_PRESHARED_KEY=preshared_key)

        device = attrs(
            WGDEVICE_A_IFNAME="wg-home", WGDEVICE_A_PRIVATE_KEY=self.secret.encode(),
            WGDEVICE_A_PUBLIC_KEY=self.public_key.encode(),
            WGDEVICE_A_PEERS=[peer(self.public_key.encode(), self.secret.encode()),
                              peer(b"q" * 32, base64.b64encode(bytes(32))),
                              peer(b"r" * 32, None)],
        )
        with patch.object(wgshow, "WireGuard") as wireguard, \
                patch.object(util, "ip_addr_ifname", return_value=[("fd10::1", 64)]):
            wireguard.return_value.__enter__.return_value.info.return_value = [device]
            collected = wgshow.WgShow().show_wg("wg-home", private=True)
        self.assertEqual(collected["private_key"], "****")
        self.assertEqual(collected["peers"][0]["public_key"], self.public_key)
        self.assertEqual(collected["peers"][0]["preshared_key"], "***")
        self.assertNotIn("preshared_key", collected["peers"][1])
        self.assertNotIn("preshared_key", collected["peers"][2])
        self.assertNotIn(self.secret, repr(collected))
        self.assertEqual(collected["peers"][1]["public_key"], base64.b64encode(b"q" * 32).decode())

    def test_handshake_states_and_ages(self):
        for timestamp, expected_status, expected_age in (
            (0, "从未握手", "—"), (972, "近期握手", "28 秒前"),
            (820, "近期握手", "3 分 0 秒前"), (819, "握手较旧", "3 分 1 秒前"),
            (1001, "近期握手", "0 秒前"),
        ):
            with self.subTest(timestamp=timestamp):
                status, _, age = wgshow.handshake_status(timestamp, 1000)
                self.assertEqual((status, age), (expected_status, expected_age))

    def test_color_does_not_change_card_contents(self):
        plain = wgshow.render_interface(self.device, self.conf, now=1000)
        colored = wgshow.render_interface(self.device, self.conf, color=True, now=1000)
        self.assertIn("\033[32m", colored)
        self.assertEqual(re.sub(r"\x1b\[[0-9;]*m", "", colored), plain)
        self.assertNotIn(self.secret, colored)

    def test_missing_comment_and_preshared_key(self):
        self.device["peers"][0].pop("preshared_key")
        output = wgshow.render_interface(self.device, now=1000)
        self.assertIn("● 未知    近期握手", output)
        self.assertRegex(output, r"PUBLIC_KEY\s+" + re.escape(self.public_key))
        self.assertNotIn("PRESHARED_KEY", output)
        # 配置字段存在时，即使内核尚未提供该字段，也显示遮蔽值。
        self.assertIn("PRESHARED_KEY", wgshow.render_interface(self.device, self.conf, now=1000))
        self.conf["ifname"]["interface"] = "wg-other"
        self.assertNotIn("香港中转", wgshow.render_interface(self.device, self.conf, now=1000))

    def test_empty_peers(self):
        self.device["peers"] = []
        output = wgshow.render_interface(self.device, now=1000)
        self.assertIn("节点 0", output)
        self.assertIn("暂无 peer", output)

    def test_main_uses_configured_interface_and_plain_redirected_output(self):
        output = io.StringIO()
        with patch.object(util, "list_wg_all") as list_all, \
                patch.object(wgshow.WgShow, "show_wg", return_value=self.device) as show, \
                contextlib.redirect_stdout(output):
            wgshow.main(conf=self.conf)
        list_all.assert_not_called()
        show.assert_called_once_with("wg-home")
        self.assertIn("香港中转", output.getvalue())
        self.assertNotIn("\033[", output.getvalue())

    def test_cli_passes_optional_config_for_both_show_options(self):
        for option in ("--show", "--show-private"):
            with self.subTest(option=option), \
                    patch("sys.argv", ["wgpy", option, "/etc/wgs/home.toml"]), \
                    patch.object(main, "loadconf", return_value=self.conf), \
                    patch.object(wgshow, "main") as show:
                main.main()
                show.assert_called_once_with(conf=self.conf)

    def test_main_without_config_does_not_read_files(self):
        output = io.StringIO()
        with patch.object(util, "list_wg_all", return_value=["wg-home"]), \
                patch("builtins.open") as open_file, \
                patch.object(wgshow.WgShow, "show_wg", return_value=self.device), \
                contextlib.redirect_stdout(output):
            wgshow.main()
        open_file.assert_not_called()
        self.assertIn("● 未知", output.getvalue())
        self.assertIn(self.public_key, output.getvalue())


if __name__ == "__main__":
    unittest.main()
