# 开发与验证

- 使用 Python 3.12（`.python-version`）；在仓库根目录执行 `uv sync --locked`，按 `uv.lock` 安装运行依赖及 PyInstaller 开发依赖。
- 项目没有安装后的 CLI 入口；从根目录运行 `uv run --locked python src/main.py --help`，启动时将 TOML 路径作为位置参数：`uv run --locked python src/main.py /path/to/wg.toml`。
- `src/` 使用同目录绝对导入（如 `import util`），不是 Python 包；单独导入模块时设置 `PYTHONPATH=src`。
- 当前没有自动化测试套件或 lint/typecheck 配置。基础验证：`uv run --locked python -m compileall -q src` 和上述 `--help`；聚焦语法检查可将 `src` 换成目标文件。这些检查不验证实际网络行为。
- PyInstaller 打包需以 `src/` 为工作目录执行 `uv run --locked pyinstaller main.spec`，输出 `src/dist/wgpy`。旧 `build2pyz.sh` 在无缓存时依赖仓库已不存在的 `requirements.txt`，不能作为开箱即用的构建命令。

## 实际执行链路

- `src/main.py` → `src/server.py:server()`：创建 WireGuard 接口、配置地址与 peers、添加路由、启动心跳线程；收到 SIGTERM 后通过事件退出并删除接口。
- 网络操作集中在 `src/util.py`，通过 pyroute2 的 `IPRoute`/`WireGuard` 操作 Linux 内核；实际启动及 VPN 切换需要 Linux WireGuard 支持和网络管理权限，会修改接口、路由与策略规则。
- 生效的心跳实现是 `src/checkalive.py`（selectors + 线程），协议在 `src/packet.py`；`src/checkalive-asynio.py` 不在主入口执行链路中。检测失败达到阈值后才重新解析 endpoint 域名并更新 peer。
- Python 入口的 VPN 路径使用 pyroute2；`util.py` 中 nftables 导入已注释，README 中的 `python3-nftables` 要求不代表当前入口的运行依赖。

## 配置与部署易错点

- `design.md` 是设计草案，里面的管理子命令未在当前 CLI 实现；`conf.toml.md` 仅作结构参考，字段读取以 `main.py`、`server.py`、`checkalive.py` 为准。
- 心跳全局设置实际读取 TOML 顶层的 `check_port`、`check_timeout`、`check_failed_count`（默认 19000、5、6）；示例 `[info]` 下的 `check_listen_port` 等字段不会生效。
- 当前启动必须显式提供 `[ifname].MTU`：代码直接执行 `int(ifname.get("MTU"))`，并未实现示例所述的默认值。每个 peer 也须有 `info` 表，即使为空。
- 心跳服务无条件绑定 IPv6 socket，主动探测使用 `sock6`；当前配置须提供 WireGuard IPv6 地址，主动探测的 `[peers.info].wg_check_ip` 应使用对端隧道 IPv6 地址。
- 启动解析与断线重解析使用 `util.getaddrinfo()`，只接受一个解析地址；域名同时存在多个 A/AAAA 结果会被拒绝。
- `--vpn-up`/`--vpn-down` 操作已存在的接口，并只使用配置中的第一个 peer；`fwmark` 默认 `0x8123`，`table_id` 默认与其相同。
- `template/wg@.service` 的部署契约是 `/usr/local/sbin/wgpy /etc/wgs/%i.toml`；修改可执行文件名或配置路径时同步检查此模板。
