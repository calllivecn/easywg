# server 使用 DDNS， 测试并试用和 client 的稳定性。这里是可行性研究!


### 工作方式说明

```
1. server为主要端，DDNS域名指向的就是它，形成星形网络。(之后可能会拓展)

2. server需要提供一个可以让client检测当前DDNS域名指向，是否联通(心跳线?)。

    (1) 设计应该是使用 UDP AEAD 加密报文的方式检测。
    (2) 方法1：目前还是测试阶段，为了编码简单，使用timestamp+sha256+(server_secret, client_secret)。
    (3) 方法2: subprocess 调用ping 测试(在wireguard 网络内)。

3. 添加server端的vpn防火墙部分, 先直接手动添加到防火墙。
```