# 配置示例+说明


```json
{
    "check_timeout": 5,
    "check_fail_count": 3,
    "server_wg_ip": "10.1.1.1",

    "ifname": {

        "interface": "",
        "private_key": "",
        "preshared_key": "可选",
        "listen_port": 8123,
        "address": ["10.1.1.1/24", "fc00::1/7"],
        "MTU": 1280,  # 当使用ipv6网络承载时(需要设置为1280)
        "fwmark": "可选,一般不配置"
    },
    
    "peers":[
        {
            "public_key": "必须",
            "preshared_key": "可选",
            "endpoint_addr": "wg.exmaple.com", # 这里只能使用 域名，server 是 DDNS的。
            "endpoint_port": 9999, # required only if endpoint_addr
            "persistent_keepalive": 25, #可选, 一般不配置
            "allowed_ips": ["10.1.1.0/24", "fc00::/7"], # 或者使用默认路由 0.0.0.0/0, ::/0
        }
    ]

}
```