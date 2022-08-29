# wireguard 实现虚拟局域网和路由所有流量 （默认用户和密码：easywg）

## Server

1. 管理多个wg接口

2. 允许多个用户连接wg接口

3. 允许同一用户多次连接，组成用户的虚拟局域网。

4. 为一个接口（局域网）的客户端生产配置，和分配CIDR, 可以为每个接口上的用户分配static IP(添加 peer 时分配静态 IP)。

- 需要注意的问题：

>1) 不同wg接口（不同网段）的客户端允不允许互通？给个开关; 默认不允许？
>
>2) VPN模式下，客户端之间允不允许互通？这个应该允许。给个开关?
>
---

## Client 只需要实现 linux 端就可以, 其他平台官方有[WireGuard客户端下载地址](https://www.wireguard.com/install/)

1. 拿到分配的配置，和IP/CIDR地址。生成client自己的配置文件（包含为其分配的IP）。

2. 可以虚拟网络、VPN模式来回切换。

3. 还有一个shell版的相同功能的client。

### 使用方式一(页面)

- 可以在页面为PC、android、ios、mac os、生成 *.conf 配置下载, 在客户端直接导入使用。

- 可以在页面为移动端生成 二维码配置 实现快速添加。

### 使用方式二(cli)

- 通过 wg.pyz cli 方式 或 curl 方式下载配置。

    ```shell
    curl -H "USERNAME: $your_name" -H "PASSWORD: $your_pw" -o wg-cfg.conf \
    "https://<wg-service.com>/?format=conf&client=window"
    ```

- 可以为 linux 生成 shell 配置。

    ```shell
    curl -H "USERNAME: $your_name" -H "PASSWORD: $your_pw" -o wg-cfg.sh "https://<wg-service.com>/?format=shell"
    ```

### 使用方式三（wg.pyz)

- 1

    ```shell
    wg.pyz --output-config /path/to/user1-wg1.conf --service https://<wg-service.com>/
    交互式输入用户名，密码，拿到配置。
    ```

- 2

    >wg.service:
    >
    >Type=Oneshot
    >
    >RemainAfterExit=yes
    >
    >StartExec=/usr/local/sbin/wg.pyz --config /parh/to/user1-wg0.conf
