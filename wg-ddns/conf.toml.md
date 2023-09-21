
```ini
# 非原版配置
[info]
# check_listen_port = 19000 # 可选
# check_timeout = 5 # 可选
# check_failed_count = 6 # 可选

# 是不是peers hub 信息交换节点, 默认： false
# server_hub = false

# wireguard 的 interface 原版配置
[ifname]
interface = "wg-pyz"
private_key = "private key"

# 可选
# preshared_key = "" 

# 可选，在有防火墙的情况下，还是指定下端口，并在防火墙上开放对应的UDP端口
# listen_port = 18000

address = ["10.1.1.1/24", "fc01::1/64"]

# 当使用ipv6网络承载时(可能需要调小一点, 如: 1200) 默认是ipv4的 1420
# MTU = 1420

# 可选， 一般不配置, 值 0~2^31-1
# fwmark = 


# wireguard 的 peers 配置
# 这是第一个 peer 配置
[[peers]]
[peers.info]
comment = "这是peer端的备注"

# 检测连通性时，当前peer端的ip和port信息。
# 在 server_hub 端，不需要配置
# wg_check_ip = "fc01::1"
# wg_check_port = 19000


# wireguard 的 peer 原版配置
[peers.peer]
public_key = "public key"

# 可选
# preshared_key = "" 

# 可选, 一般不配置
# persistent_keepalive = 25

endpoint_addr = "ip or domainname"
endpoint_port = 18000
allowed_ips = ["10.1.1.0/24", "fc01::/64"]


# 这是第二个 peer 配置
[[peers]]
[peers.info]
comment = "这是peer2端的备注"
# wg_check_ip = "fc01::1"

[peers.peer]
public_key = "public key"
endpoint_addr = "ip or domainname"
endpoint_port = 18000
allowed_ips = ["10.1.1.0/24", "fc01::/64"]
```