# wireguard 实现虚拟局域网和路由所有流量

## Server

1. 管理多个wg接口

2. 为一个接口（局域网）的客户端生产配置，和分配CIDR, 可以为每个接口上的用户分配static IP(添加 peer 时分配静态 IP)。

3. 目前先使用示加密通信，之后使用加密网络通信(使用管理密码认证管理人员)，采用C/S架构。

- 需要注意的问题：

>1) 不同wg接口（不同网段）的客户端允不允许互通？给个开关; 默认不允许？
>
>2) VPN模式下，客户端之间允不允许互通？这个应该允许。给个开关?
>


---

## 管理方式

- 管理peer

```shell
wg.pyz add
wg.pyz add --allowed-ips 10.1.2.0/24 10.1.3.0/24 --keepalive 25 --endpoint mc.calllive.cc:8321
wg.pyz update --pubkey <pubkey> --allowed-ips
gw.pyz remove --pubkey <pubkey>
```

- 管理
```shell
wg.pyz interface add
wg.pyz interface
```

---

## Client 只需要实现 linux 端就可以, 其他平台官方有[WireGuard客户端下载地址](https://www.wireguard.com/install/)

1. 拿到分配的配置，和IP/CIDR地址。生成client自己的配置文件（包含为其分配的IP）。

2. 可以虚拟网络、VPN模式来回切换。

3. 还有一个shell版的相同功能的client。

### 使用方式一(cli)

- 通过 wg.pyz cli 方式

- 可以为 linux 生成 shell 配置,  配置信息可以 是环境变量。

    ```shell
    export WG_USER=<easywg> WG_PASSWORD=<your passwword> WG_SERVER_URL=<easywg.example.cn:8324>

    wg.pyz --shell wg0.sh <peername> # 生成直接配置WG的脚本 推荐
    wg.pyz --qr <peername> # 生成二维码配置
    wg.pyz --conf wg0.conf <peername> # 使用 wg-quick up wg0 的方式配置
    ```

### 使用方式二（使用 wg.pyz 配置 Wireguard)

- 配置 wg.service:

    ```Service
    [Service]
    Type=Oneshot
    RemainAfterExit=yes
    StartExec=/usr/local/sbin/wg.pyz --config /parh/to/user1-wg0.conf

    [Install]
    WantedBy=multi-user.target
    ```

