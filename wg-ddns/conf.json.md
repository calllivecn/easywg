# 配置示例+说明


```json
{
    "check_timeout": 5,
    "check_fail_count": 3,
    "server_hub": false, # 可选，默认为false

    "ifname": {

        "interface": "",
        "private_key": "",
        "preshared_key": "可选",
        "listen_port": 8123,
        "address": ["10.1.1.1/24", "fc01::1/64"],
        "MTU": 1280,  # 当使用ipv6网络承载时(需要设置为1280)
        "fwmark": "可选,一般不配置"
    },
    
    "peers":[
        {
            "public_key": "必须",
            "preshared_key": "可选",
            "endpoint_addr": "wg.exmaple.com",
            "endpoint_port": 9999, # required only if endpoint_addr
            "persistent_keepalive": 25, #可选, 一般不配置
            "allowed_ips": ["10.1.1.0/24", "fc01::/64"], # 或者使用默认路由 0.0.0.0/0, ::/0
            # 非原版配置
            "wg_check_ip": "fc00::2",
            "endpoint_addr_is_static": False
        }
    ]

}
```