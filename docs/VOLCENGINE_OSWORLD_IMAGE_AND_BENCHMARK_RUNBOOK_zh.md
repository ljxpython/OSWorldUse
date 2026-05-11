# 火山云 OSWorld 镜像构建与 CUA Benchmark 运行手册

日期：2026-05-08

这份文档记录本次从 Ubuntu/OSWorld 镜像可用性排查，到火山云 ECS 创建、noVNC/x11vnc、网络、安全组、`volcengine` provider、CUA benchmark 验证的完整路径。

目标不是写一份泛泛而谈的云厂商说明，而是沉淀一条可以复现的工程流程：

- 构建一个可用于 OSWorld 的干净 Ubuntu 镜像
- 创建火山云 ECS 并让 OSWorld server、noVNC、桌面会话可达
- 区分 smoke test 和严肃 benchmark 的运行方式
- 明确全量 benchmark 前还必须验证什么

## 当前结论

本次已经验证：

- `volcengine` provider 可以创建火山云 ECS。
- `volcengine` provider 可以在本机 runner 场景下通过公网 IP 访问 OSWorld server。
- `x11vnc + noVNC` 可以提供 `5910/vnc.html` 远程桌面入口。
- `scripts/python/run_cua_blackbox_regression.py` 可以通过 `volcengine` provider 跑真实 CUA regression case。
- 已跑通单个真实 case：`libreoffice_writer/4bcb1253-a636-4df4-8cb0-a35c04dfef31`，得分约 `0.9977`，失败数为 `0`。
- 已跑通 Chrome case：`chrome/030eeff7-b492-4218-b312-701ec99ee0cc`，`9222/json/version` 可从 runner 侧访问，case 得分 `1.0`。
- 已跑通 VLC case：`vlc/59f21cfb-0120-4326-b255-a5b827b38967`，`8080/requests/status.xml` 可从 runner 侧访问，case 得分 `1.0`。

还不能直接宣称“全量 benchmark 已经完成验证”：

- 严肃 benchmark 需要干净镜像和实例重建隔离，不能用跑过任务的脏实例直接保存镜像。
- 多 case 连跑和 provider 自动删旧建新的隔离路径还需要基于干净镜像验证。

## 两种运行模式

### 1. `remote` provider：只做 smoke test

`remote` provider 连接一台已经存在的 OSWorld 机器，只验证链路，不管理 VM 生命周期：

- 不创建实例
- 不删除实例
- 不恢复快照
- 不保证每个任务前是干净状态

适用场景：

- 排查 OSWorld server 是否可用
- 验证 noVNC、截图、控制器、CUA bridge 链路
- 临时调试一个已有 ECS

不适用场景：

- 严肃 benchmark
- 多 case 连跑
- 需要任务之间状态隔离的评测

已有机器只能通过跳板机访问时，先在本地建端口转发：

```bash
ssh -N \
  -L "127.0.0.1:15000:127.0.0.1:5000" \
  -L "127.0.0.1:19222:127.0.0.1:9222" \
  -L "127.0.0.1:15910:127.0.0.1:5910" \
  -L "127.0.0.1:18080:127.0.0.1:8080" \
  -J "jumpecs-hl.byted.org" \
  "user@<ecs-public-ip>"
```

然后用本地端口跑 quickstart：

```bash
.venv/bin/python "quickstart.py" \
  --provider_name remote \
  --path_to_vm "127.0.0.1:15000:19222:15910:18080"
```

注意：有些跳板机不允许 SSH `session` channel，所以 `ssh jumpecs "nc ..."` 会失败。遇到这种情况不要纠结 `nc -z`，直接用 `ssh -N -L ...` 做本地端口转发。

### 2. `volcengine` provider：用于严肃 benchmark

`volcengine` provider 才是严肃 benchmark 路径：

- 无 `--path_to_vm` 时会基于 `VOLCENGINE_IMAGE_ID` 创建新 ECS。
- `reset()` 后如果环境已被使用，下一次任务会调用 `revert_to_snapshot()`。
- 当前实现里的 `revert_to_snapshot()` 会删除旧实例，再从镜像创建新实例。
- `close()` 默认会删除实例。

这条路径可以保证任务之间有更强的状态隔离，但会真实产生云资源创建和删除。

## 镜像构建流程

### 1. 获取基础 OSWorld 镜像

已有火山云指南位于：

- `desktop_env/providers/volcengine/VOLCENGINE_GUIDELINE_CN.md`

基础路径：

1. 下载 OSWorld Ubuntu qcow2 镜像。
2. 上传到火山云 TOS，TOS 地域必须和目标 ECS 地域匹配。
3. 在火山云控制台导入自定义镜像。
4. 用该镜像手动创建一台 ECS 做首次验证。
5. 验证通过后再保存为最终 benchmark 镜像。

### 2. 登录与 SSH

如果镜像内没有 SSH 服务，需要在 ECS 控制台或 noVNC 里进入桌面/终端后安装：

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
systemctl status ssh --no-pager
```

验证 SSH：

```bash
ssh -J "jumpecs-hl.byted.org" "user@<ecs-public-ip>"
```

镜像密码不要写入文档或提交到仓库。密码应通过 `.env` 的 `VOLCENGINE_DEFAULT_PASSWORD` 或云控制台配置管理。

### 3. OSWorld server

镜像必须提供 OSWorld server，默认端口是 `5000`。

在 ECS 内部验证：

```bash
curl -I "http://127.0.0.1:5000/screenshot"
```

在 runner 机器上验证：

```bash
curl -I --connect-timeout "5" --max-time "12" "http://<ecs-ip>:5000/screenshot"
```

期望结果：

- HTTP `200`
- `Content-Type: image/png`

如果这里不通，CUA、benchmark、evaluator 都不用看，先修 OSWorld server。

### 4. noVNC 与 x11vnc

noVNC 用于人工观察桌面，x11vnc 用于把当前 X11 桌面暴露给 noVNC。

安装依赖：

```bash
sudo apt update
sudo apt install -y x11vnc novnc websockify
```

用户级 systemd 服务建议放在：

- `/home/user/.config/systemd/user/x11vnc.service`
- `/home/user/.config/systemd/user/novnc.service`

`x11vnc.service` 示例：

```ini
[Unit]
Description=x11vnc for OSWorld desktop
After=graphical-session.target

[Service]
ExecStart=/usr/bin/x11vnc -display :0 -forever -shared -rfbport 5900 -nopw -noxdamage
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
```

`novnc.service` 示例：

```ini
[Unit]
Description=noVNC proxy for OSWorld desktop
After=x11vnc.service

[Service]
ExecStart=/usr/bin/websockify --web=/usr/share/novnc 5910 localhost:5900
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
```

启用服务：

```bash
systemctl --user daemon-reload
systemctl --user enable --now x11vnc.service novnc.service
sudo loginctl enable-linger user
```

验证：

```bash
systemctl --user status x11vnc.service --no-pager
systemctl --user status novnc.service --no-pager
curl -I "http://127.0.0.1:5910/vnc.html"
```

在 runner 机器上验证：

```bash
curl -I --connect-timeout "5" --max-time "12" "http://<ecs-public-ip>:5910/vnc.html"
```

期望结果：HTTP `200`。

### 5. 不要把调试后的脏状态保存成镜像

以下操作会污染镜像状态：

- 跑过 OSWorld benchmark case
- 打开过文档、浏览器、VLC
- 下载过任务文件
- 运行过 CUA 自动操作
- 改过桌面分辨率但未验证服务自启动

保存 benchmark 镜像前，应做到：

- ECS 是从干净基础镜像启动的。
- 只安装必要服务和依赖。
- OSWorld server、noVNC、x11vnc 均可自启动。
- 没有跑过 benchmark case。
- 清理浏览器、下载目录、桌面临时文件、shell history。
- 最后关机或停止实例，再在云控制台创建自定义镜像。

## 火山云 `.env` 配置

必需配置：

```bash
VOLCENGINE_ACCESS_KEY_ID=<your-access-key-id>
VOLCENGINE_SECRET_ACCESS_KEY=<your-secret-access-key>
VOLCENGINE_REGION=<region-id>
VOLCENGINE_IMAGE_ID=<custom-image-id>
VOLCENGINE_INSTANCE_TYPE=<ecs-instance-type>
VOLCENGINE_SUBNET_ID=<subnet-id>
VOLCENGINE_SECURITY_GROUP_ID=<security-group-id>
VOLCENGINE_ZONE_ID=<zone-id>
VOLCENGINE_DEFAULT_PASSWORD=<default-password>

# 可选：系统盘大小，单位 GB。Ubuntu 通常为 30；Windows 镜像通常至少为 60。
VOLCENGINE_SYSTEM_VOLUME_SIZE=30
```

本次新增/使用的运行开关：

```bash
# runner 在同 VPC 内，使用私网 IP。默认值就是 1。
VOLCENGINE_USE_PRIVATE_IP=1

# runner 在本机 Mac 或 VPC 外，使用公网 IP。
VOLCENGINE_USE_PRIVATE_IP=0

# 调试已有实例时避免 close() 删除 ECS。
VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1
```

注意：

- `.env` 不能提交。
- AK/SK、密码、当前公网 IP 不要写进文档。
- `VOLCENGINE_ZONE_ID` 是可用区 ID，必须和子网、库存、实例规格匹配，例如 `cn-shanghai-b` 这一类值。

## 安全组配置

### runner 在同 VPC 内

这是更适合全量 benchmark 的部署方式。

入方向建议：

| 端口 | 来源 | 用途 |
| --- | --- | --- |
| 5000 | VPC CIDR | OSWorld server |
| 5910 | 管理端 IP 或 VPC CIDR | noVNC |
| 9222 | VPC CIDR | Chrome remote debugging |
| 8080 | VPC CIDR | VLC HTTP |
| 8081 | VPC CIDR | 附加服务 |
| 22 | 管理端 IP 或跳板机 | SSH |

provider 使用默认私网：

```bash
VOLCENGINE_USE_PRIVATE_IP=1
```

### runner 在本机 Mac 或 VPC 外

如果本机直接跑 benchmark，需要把 OSWorld 端口暴露到 runner 的出口 IP。

入方向建议：

| 端口 | 来源 | 用途 |
| --- | --- | --- |
| 5000 | `<runner-public-ip>/32` | OSWorld server |
| 5910 | `<runner-public-ip>/32` | noVNC |
| 9222 | `<runner-public-ip>/32` | Chrome remote debugging |
| 8080 | `<runner-public-ip>/32` | VLC HTTP |
| 8081 | `<runner-public-ip>/32` | 附加服务 |

本机查询出口 IP：

```bash
curl -s "https://api.ipify.org"
```

provider 使用公网：

```bash
VOLCENGINE_USE_PRIVATE_IP=0
```

安全提醒：

- `5000` 是 OSWorld 后端控制面。
- `9222` 是 Chrome 调试口。
- 这些端口不要对 `0.0.0.0/0` 长期开。
- 测完应收回或收窄规则。

## 创建 ECS

用 provider 创建一台新 ECS：

```bash
.venv/bin/python - <<'PY'
from dotenv import load_dotenv
load_dotenv(".env")

from desktop_env.providers.volcengine.manager import VolcengineVMManager

manager = VolcengineVMManager()
instance_id = manager.get_vm_path(screen_size=(1920, 1080))
print(f"INSTANCE_ID={instance_id}")
PY
```

这个命令会真实创建按量计费实例。创建后记录：

- instance id
- public IP
- private IP
- noVNC URL

查询 provider 使用的访问地址：

```bash
env VOLCENGINE_USE_PRIVATE_IP=0 .venv/bin/python - <<'PY'
from dotenv import load_dotenv
load_dotenv(".env")

from desktop_env.providers.volcengine.provider import VolcengineProvider

provider = VolcengineProvider()
print(provider.get_ip_address("<instance-id>"))
PY
```

## 连通性验证

公网或私网 IP 根据 runner 位置选择。

```bash
curl -I --connect-timeout "5" --max-time "12" "http://<ecs-ip>:5000/screenshot"
curl -I --connect-timeout "5" --max-time "12" "http://<ecs-public-ip>:5910/vnc.html"
```

端口级验证：

```bash
.venv/bin/python - <<'PY'
import socket

host = "<ecs-ip>"
for port in [5000, 5910, 9222, 8080, 8081]:
    sock = socket.socket()
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        print(f"{host}:{port} OPEN")
    except Exception as exc:
        print(f"{host}:{port} FAIL {type(exc).__name__}: {exc}")
    finally:
        sock.close()
PY
```

解释：

- `5000 OPEN` 且 `/screenshot` 为 HTTP `200`，说明 OSWorld server 可用。
- `5910 OPEN` 且 `/vnc.html` 为 HTTP `200`，说明 noVNC 可用。
- `9222 Connection refused` 不一定是错误。Chrome 任务通常会在 setup 阶段启动 Chrome 和 socat。
- `8080 Connection refused` 不一定是错误。VLC HTTP 接口通常在 VLC 任务启动后才监听。
- `8081 Connection refused` 目前不是阻断项。当前代码和 case 未发现实际调用 `8081`，它只是云厂商指南里的附加服务预留端口。
- `timeout` 通常是安全组、路由、ACL、跳板链路问题。

## CUA 单 case 验证

先跑一个不依赖 Chrome/VLC 的 case，验证主链路：

```bash
env \
  VOLCENGINE_USE_PRIVATE_IP=0 \
  VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1 \
  .venv/bin/python "scripts/python/run_cua_blackbox_regression.py" \
  --provider_name volcengine \
  --path_to_vm "<instance-id>" \
  --domain libreoffice_writer \
  --example_id "4bcb1253-a636-4df4-8cb0-a35c04dfef31" \
  --num_envs 1 \
  --max_steps 20 \
  --env_ready_sleep 10 \
  --settle_sleep 5 \
  --log_level INFO
```

`VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1` 只适合调试已有实例，避免 `env.close()` 删除这台 ECS。

期望结果：

- CUA bridge server 启动成功。
- setup 下载、上传、打开文件成功。
- 截图成功。
- 录屏成功。
- `result.txt` 生成。
- `summary.json` 中 `failed_tasks=0`。

结果目录：

```text
results_cua_regression/pyautogui/screenshot/cua-blackbox-regression/
```

本次验证过的结果形态：

```text
total_tasks=1
scored_tasks=1
failed_tasks=0
pending_tasks=0
average_score≈0.9977
```

## Chrome/VLC 补充验证

全量 benchmark 前至少再跑：

1. Chrome case，验证 setup 阶段 `9222` 能被拉起。
2. VLC 或媒体相关 case，验证 `8080` 相关路径。
3. 两到三个跨 domain case 连跑，验证实例重建和状态隔离。

已验证结果：

| Domain | Case | 验证端口 | 结果 |
| --- | --- | --- | --- |
| `chrome` | `030eeff7-b492-4218-b312-701ec99ee0cc` | `9222` | `score=1.0` |
| `vlc` | `59f21cfb-0120-4326-b255-a5b827b38967` | `8080` | `score=1.0` |

Chrome case 示例：

```bash
env \
  VOLCENGINE_USE_PRIVATE_IP=0 \
  VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1 \
  .venv/bin/python "scripts/python/run_cua_blackbox_regression.py" \
  --provider_name volcengine \
  --path_to_vm "<instance-id>" \
  --domain chrome \
  --example_id "030eeff7-b492-4218-b312-701ec99ee0cc" \
  --num_envs 1 \
  --max_steps 20 \
  --env_ready_sleep 10 \
  --settle_sleep 5 \
  --log_level INFO
```

如果 Chrome case setup 后仍无法连接 `9222`，优先查：

- Chrome 是否已启动。
- `socat tcp-listen:9222,fork tcp:localhost:1337` 是否运行。
- 安全组是否放通 runner 到 `9222`。
- Chrome 启动参数是否含 `--remote-debugging-port=1337`。

## 严肃 benchmark 跑法

严肃 benchmark 不建议传入一个已经被任务污染的 `--path_to_vm`。

推荐方式：

1. 先保存干净镜像。
2. 设置 `.env` 中 `VOLCENGINE_IMAGE_ID=<clean-image-id>`。
3. 让 `VolcengineVMManager` 按需创建新实例。
4. 不设置 `VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1`，让 provider 在结束后删除实例。
5. runner 如果在 VPC 外，必须让新建实例的公网 `5000/9222/8080/8081` 对 runner 出口 IP 可达。

单环境全量 regression：

```bash
env \
  VOLCENGINE_USE_PRIVATE_IP=0 \
  .venv/bin/python "scripts/python/run_cua_blackbox_regression.py" \
  --provider_name volcengine \
  --num_envs 1 \
  --max_steps 20 \
  --env_ready_sleep 10 \
  --settle_sleep 5 \
  --log_level INFO
```

如果 runner 部署在同 VPC 内：

```bash
env \
  VOLCENGINE_USE_PRIVATE_IP=1 \
  .venv/bin/python "scripts/python/run_cua_blackbox_regression.py" \
  --provider_name volcengine \
  --num_envs 1 \
  --max_steps 20 \
  --env_ready_sleep 10 \
  --settle_sleep 5 \
  --log_level INFO
```

## 保存云镜像前检查清单

保存镜像前逐项确认：

- `curl -I http://127.0.0.1:5000/screenshot` 返回 `200`。
- `curl -I http://127.0.0.1:5910/vnc.html` 返回 `200`。
- `systemctl --user status x11vnc.service` 正常。
- `systemctl --user status novnc.service` 正常。
- `sudo loginctl show-user user | grep Linger=yes` 能确认 linger 已开启。
- 重启 ECS 后上述服务仍能自动恢复。
- 没有跑过 benchmark case，或者已经从干净状态重新配置。
- `.env` 中准备使用的 `VOLCENGINE_IMAGE_ID` 指向这个干净镜像。

## 常见问题

### 1. `nc: illegal option -- z`

不同系统的 `nc` 版本参数不一致。不要把 `nc -z` 当成可靠跨环境检查。

优先用：

```bash
.venv/bin/python - <<'PY'
import socket

sock = socket.socket()
sock.settimeout(5)
sock.connect(("<host>", 5000))
print("connected")
PY
```

### 2. `channel 0: open failed: unknown channel type: session`

跳板机不允许 SSH session channel。不要用：

```bash
ssh "jumpecs-hl.byted.org" "nc -v -w 2 <host> 5000"
```

改用本地端口转发：

```bash
ssh -N -L "127.0.0.1:15000:<target-ip>:5000" "jumpecs-hl.byted.org"
```

### 3. `5000` 超时但 `5910` 正常

通常是安全组只放了 noVNC，没放 OSWorld server。

修复：

- 同 VPC runner：放通 VPC CIDR 到 `5000`。
- 本机 runner：放通 runner 出口 IP `/32` 到 `5000`。

### 4. `9222` 或 `8080` 是 Connection refused

这不一定是安全组问题。`Connection refused` 表示已经打到机器，但没有进程监听该端口。

常见原因：

- Chrome/VLC 还没有被对应 task setup 启动。
- `socat` 没启动。
- 应用启动失败。

判断方式：

- 跑对应 Chrome/VLC case，而不是只在空桌面上测端口。
- 如果 setup 后仍拒绝连接，再查服务进程和日志。

### 5. Benchmark 结束后实例被删了

这是 `volcengine` provider 的默认行为。调试已有实例时设置：

```bash
VOLCENGINE_KEEP_INSTANCE_ON_CLOSE=1
```

严肃 benchmark 不建议设置这个变量，因为保留脏实例会破坏状态隔离。

## 代码改动记录

本次为跑通火山云 CUA benchmark 做过的关键改动：

- `desktop_env/providers/volcengine/provider.py`
  - 支持 `VOLCENGINE_USE_PRIVATE_IP`，本机 runner 可选择公网 IP。
  - 支持 `VOLCENGINE_KEEP_INSTANCE_ON_CLOSE`，调试时避免关闭环境删除实例。
- `scripts/python/run_multienv_cua_blackbox.py`
  - `--provider_name` 增加 `aliyun`、`volcengine`、`remote`。
- `desktop_env/providers/remote/`
  - 增加连接已有 OSWorld server 的 provider，用于 smoke test。

## 最终建议

当前已经具备“小规模分批 benchmark”的条件，但全量前不要偷懒：

1. 从干净实例保存最终镜像。
2. 用最终镜像创建新 ECS。
3. 跑 `libreoffice_writer` 单 case 验证主链路。
4. 跑 Chrome 单 case 验证 `9222`。
5. 跑媒体/VLC case 验证 `8080`。
6. 跑 2-3 个跨 domain case 验证实例重建。
7. 最后再跑全量 regression 或完整 benchmark。
