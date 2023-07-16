# server 使用 DDNS， 测试并试用和 client 的稳定性。这里是可行性研究!


### 工作方式说明

```
1. server为主要端，~~DDNS~~域名指向的就是它，形成星形网络。(之后可能会拓展)

2. server需要提供一个可以让client检测当前DDNS域名指向，是否联通(心跳线?)。

    (1) 设计应该是使用 UDP AEAD 加密报文的方式检测。
    (2) 方法1：目前还是测试阶段，为了编码简单，使用timestamp+sha256+(server_secret, client_secret)。
    (3) 方法2: subprocess 调用ping 测试(在wireguard 网络内)。

3. 添加server端的vpn防火墙部分, 先直接手动添加到防火墙。

4. IP变化时，怎么尽快的通知到peer端？(这个域名只能是指向一个ip地址)
    (1). 目前使用直接dns解析，这样会被系统缓存10分钟不行。修改用dnspython做dns查询(目前先使用dig 工具查询)。(这样的话可能需要用户指定，他所使用DNS 服务商的 nameserver ?)

5. DDNS不行，每一级 nameserver 都会缓存查询结果。导致更新到ip,太慢了。需要使用其他方式，通知到peer IP变化。
```