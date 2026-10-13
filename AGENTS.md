# 开发与验证

- 使用 Python 3.12（`.python-version`）；在仓库根目录执行 `uv sync --locked`，按 `uv.lock` 安装运行依赖及 PyInstaller 开发依赖。
- 项目没有安装后的 CLI 入口；从根目录运行 `uv run --locked python src/main.py --help`，启动时将 TOML 路径作为位置参数：`uv run --locked python src/main.py /path/to/wg.toml`。
- `src/` 使用同目录绝对导入（如 `import util`），不是 Python 包；单独导入模块时设置 `PYTHONPATH=src`。
- 心跳回归测试：`PYTHONPATH=src uv run --locked python -m unittest discover -s tests -v`；使用本地 IPv4/IPv6 UDP 和模拟内核操作，无需网络管理权限，但需启用 IPv6 loopback。单测可用 `-s tests -p test_checkalive.py -k <测试名片段>` 聚焦。
- 无 lint/typecheck 配置；基础验证：`uv run --locked python -m compileall -q src tests` 和上述 `--help`，不验证真实 WireGuard 网络行为。
- PyInstaller 打包需以 `src/` 为工作目录执行 `uv run --locked pyinstaller main.spec`，输出 `src/dist/wgpy`。旧 `build2pyz.sh` 在无缓存时依赖仓库已不存在的 `requirements.txt`，不能作为开箱即用的构建命令。

## 实际执行链路

- `src/main.py` → `src/server.py:server()`：通过 `asyncio.run()` 创建接口、配置 peers 与路由并运行心跳；SIGTERM 设置异步退出事件，退出或异常时清理心跳任务并删除接口。
- 网络操作集中在 `src/util.py`，通过 pyroute2 的 `IPRoute`/`WireGuard` 操作 Linux 内核；同步 pyroute2 API 不能在运行中的事件循环内直接调用，异步路径使用 `funcs.run_sync()` 在工作线程执行并在取消时等待操作完成。实际启动及 VPN 切换需要 Linux WireGuard 支持和网络管理权限，会修改接口、路由与策略规则。
- 心跳实现统一在 `src/checkalive.py`（asyncio socket + TaskGroup），协议在 `src/packet.py`；socket 绑定完成后才启动探测。检测失败达到阈值后重解析原始 endpoint 域名，DNS 与 peer 更新通过 `asyncio.to_thread()` 避免阻塞事件循环。
- Python 入口的 VPN 路径使用 pyroute2；`util.py` 中 nftables 导入已注释，README 中的 `python3-nftables` 要求不代表当前入口的运行依赖。

## 配置与部署易错点

- `design.md` 是设计草案，里面的管理子命令未在当前 CLI 实现；`conf.toml.md` 仅作结构参考，字段读取以 `main.py`、`server.py`、`checkalive.py` 为准。
- 心跳全局设置实际读取 TOML 顶层的 `check_port`、`check_timeout`、`check_failed_count`（默认 19000、5、6）；示例 `[info]` 下的 `check_listen_port` 等字段不会生效。
- 当前启动必须显式提供 `[ifname].MTU`：代码直接执行 `int(ifname.get("MTU"))`，并未实现示例所述的默认值。每个 peer 也须有 `info` 表，即使为空。
- 心跳服务仍无条件绑定 IPv6 socket，配置须提供 WireGuard IPv6 地址；`[peers.info].wg_check_ip` 使用对端隧道 IP，按地址族选择探测 socket，IPv4 探测还须配置本地 WireGuard IPv4 地址。
- 启动解析与断线重解析使用 `util.getaddrinfo()`，只接受一个解析地址；域名同时存在多个 A/AAAA 结果会被拒绝。
- `--vpn-up`/`--vpn-down` 操作已存在的接口，并只使用配置中的第一个 peer；`fwmark` 默认 `0x8123`，`table_id` 默认与其相同。
- `template/wg@.service` 的部署契约是 `/usr/local/sbin/wgpy /etc/wgs/%i.toml`；修改可执行文件名或配置路径时同步检查此模板。
