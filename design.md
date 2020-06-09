# wireguard 实现虚拟局域网和路由所有流量（像VPN一样工作）

## Server

1. 管理多个wg接口

2. 允许多个用户连接wg接口

3. 允许同一用户多次连接，组成用户的虚拟局域网。

4. 为一个接口（局域网）的客户端生产配置，和分配IP/CIDR, 可以为每个接口上的用户分配固定IP。

- 需要注意的问题：

>1) 不同wg接口（不同网段）的客户端允不允许互通？给个开关; 默认不允许？
>
>2) VPN模式下，客户端之间允不允许互通？这个应该允许。给个开关。
>

### Server管理client的方式

- 可以生成二维码配置给移动端

- 可以为PC生成 wg0.conf 的配置

    使用方式：

    ```shell
    curl -H "USERNAME: $your_name" -H "PASSWORD: $your_pw" -o wg-cfg.conf \
    "https://wg-service.com/?format=conf&client=window&ip-type=auto"
    ```

- 可以为 linux 生成 shell 配置

    在使用shell方式时，先在server设置使用静态ip。

    ```shell
    curl -H "USERNAME: $your_name" -H "PASSWORD: $your_pw" -o wg-cfg.sh "https://wg-service.com/?format=shell"
    ```

---

## Client 好像只需要实现linux端就可以, 其他平台到这下载：[wireguard](https://www.wireguard.com/install/) 好像也只需要实现VPN模式就行，静态ip时可以使用shell配置方式。

1. 拿到分配的配置，和IP/CIDR地址。生成client自己的配置文件（包含为其分配的IP）。
2. 可以虚拟网络、VPN模式来回切换。

### 使用方式:

```shell
wg.pyz --output-config /path/to/user1-wg1.conf --service https://wg-service.com/
交互式输入用户名，密码，拿到配置。
```

>wg.service:
>
>Type=Oneshot
>
>StartExec=/usr/local/sbin/wg.pyz --config /parh/to/user1-wg0.conf