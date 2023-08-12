# 配置示例+说明


- 普通客户端配置

```json
{
    "check_port": 19000, # 可选， 默认为19000
    "check_timeout": 5, # 可选
    "check_failed_count": 6, # 可选

    "ifname": {

        "interface": "",
        "private_key": "",
        "preshared_key": "可选",
        "listen_port": 18000,
        "address": ["10.1.1.1/24", "fc01::1/64"],
        "MTU": 1280,  # 当使用ipv6网络承载时(可能需要调小一点)
        "fwmark": "可选,一般不配置"
    },
    
    "peers":[
        {
            # 非原版配置
            "comment": "对端 备注",
            "wg_check_ip": "fc00::2",
            "wg_check_port": 19000, # 可选， 默认为19000
            # 原版配置
            "public_key": "必须",
            "preshared_key": "可选",
            "endpoint_addr": "wg.exmaple.com",
            "endpoint_port": 18000,
            "persistent_keepalive": 25, #可选, 一般不配置
            "allowed_ips": ["10.1.1.0/24", "fc01::/64"], # 或者使用默认路由 0.0.0.0/0, ::/0
        }
    ]

}
```


- sever hub 配置

```json
{
    "check_timeout": 5,
    "check_fail_count": 6,
    "server_hub": true,

    "ifname": {

        "interface": "wg-route",
        "private_key": "sLGJjNc6NpJkwZdamO4O1oATtJAYOC+aTDu+KyYYsW4=",
        "address": ["10.1.3.1/24", "fc03::1/64"],
		"listen_port": 18000,
        "MTU": 1280
    },
    
    "peers":[
        {
            "comment": "miui",
            "public_key": "raQ016lCzkH0SXiejlBGO0Hmw5MQv3HI0bcjj+hi9xY=",
            "allowed_ips": ["10.1.3.2/32", "fc03::2/128"]
        }
    ]
}
```