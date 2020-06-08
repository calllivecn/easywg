# wireguard 实现虚拟局域网和路由所有流量（像VPN一样工作）

## Server

1. 管理多个wg接口

2. 允许多个用户连接wg接口

3. 为一个接口（局域网）的客户端生产配置，和分配IP/CIDR

- 需要注意的问题：

>1) 不同wg接口（不同网段）的客户端允不允许互通？给个开关; 默认不允许？
>
>2) VPN模式下，客户端之间允不允许互通？这个应该允许。给个开关。
>

### Server管理client的方式

- 可以生成二维码配置给移动端

- 可以为PC生成 wg0.conf的配置

- 可以生成shell配置

---

## Client 好像只需要实现linux端就可以, 其他平台到这下载：[wireguard](https://www.wireguard.com/install/)

1. 