# server 使用 DDNS， 测试并试用和 client 的稳定性。这里是可行性研究!


### 工作方式说明


1. server为主要端，~~DDNS~~域名指向的就是它，形成星形网络。(之后可能会拓展)

2. server需要提供一个可以让client检测当前WireGuard是否联通(心跳线?)。

    (1) 设计应该是使用 UDP AEAD 加密报文的方式检测。但：目前还是测试阶段，为了编码简单
    (2) 使用timestamp+sha256+(server_secret, client_secret)。
    (3) subprocess 调用ping 测试(在wireguard 网络内)。

3. 添加server端的vpn模式的防火墙部分, 先直接手动添加到防火墙。

4. IP变化时，怎么尽快的通知到peer端？(这个域名只能是指向一个ip地址)

    ~~(1). 目前使用直接dns解析，这样会被系统缓存10分钟不行。修改用dnspython做dns查询(目前先使用dig 工具查询)。(这样的话可能需要用户指定，他所使用DNS 服务商的 nameserver ?)~~

5. DDNS不行，每一级 nameserver 都会缓存查询结果。导致更新到ip,太慢了。需要使用其他方式，通知到peer IP变化。


### 工作方式重新设计

1. ~~ipv6 在变更地址时，会保留之前的地址一段时间。这里利用这段时间更新ddns。~~
    这样也会有一个问题，就是每次server端的接口发生变更时，ipv6都会改变。这时靠ddns会有10分钟的断开时间。
    (2023-08-04; 这个好像也不完全成立，或者说只对了一半。在ipv6的lifetime 到期时本地接口会在PD下生产新的ipv6地址，些时之前的地址还是能用的。就是1说的情况，但是，
    运营商会定期或者不定期的断开拨号，让宽带重新连接，这时ISP会重新给一个PD，接口地址更新后，就不会留下之前PD的路由信息了。)
    (2023-08-06；发现一个新的现象：ddns更新后，有的地址会查询到新ip, 然后下次查询到之前的旧ip。在下次又查到新ip。这样。)

2. 现在加上server hub 端也会主动发送alive检测。在看看效果。(2023-08-06)

2. 之后拓展会不会添加上，由一个server 网络信息提供者的角色？在peer之间交换信息，让网络能形成每个peer对其他所有peer端的直接。？


### 几个条件

- 本地每个peer 的 endpoint ip 的变化检测 -- 这个不需要
- 网络联通性检测 一个 interface 对所有 peer 的联通性。
- 本地承载wg的 ip 变化检测, 这种只要两端不同时发生ip变化，连通性就能保持。 -- ok
  - 这个会影响peer的联通性吗？需要做实验检测。(2023-08-11 验证可以)
  - 目前看只需要两端都指定ListenPort就行(需要在防火墙里放通对应的UDP端口)
  - 如果只有一端指定 如A端 listenport 并开放了对应UDP端口，B端没有开放。那当A端ipv6地址变化时，A端就连接不上B端了(因为防火墙 or NAT)，些时B端也连不上A端了(因为A ip 变了)。
  - 如果不指定ListenPort(这时会由系统随机分配)，那就不能有防火墙。

- DDNS域名的变化(需要在通性检测失败的前提下，才工作效。)



### 踩的坑

- 在使用ipv6承载wireguard时，最好是修改下MTU=1280(1280是ipv6 定义的"最大传输单元"的最小大小)

- wireguard 不能在多个peer 端里的 allowed-ips 里添加同样的路由网段。在添加是不会报错，但是只会在最后一个设置的peer上。