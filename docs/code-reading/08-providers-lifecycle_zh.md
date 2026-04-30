# 08 Providers 与生命周期解读

这一篇接在 [07 Controllers 与 Guest Server 解读](./07-controllers-and-server_zh.md) 后面看最自然。

因为到这一步你已经知道：

- guest 里的 server 是怎么工作的
- controller 怎么通过 HTTP 去驱动它

接下来最自然的问题就是：

- 这台 guest 本身是怎么来的？
- VMware、Docker、AWS 这些 provider 到底区别在哪？
- 为什么有的 `path_to_vm` 真的是文件路径，有的其实是实例 ID？

这篇就专门讲 provider 生命周期这一层。

## 先记住最重要的抽象

provider 层可以先粗暴记成两部分：

- `VMManager`
- `Provider`

定义在：

- [desktop_env/providers/base.py](../../desktop_env/providers/base.py)

你可以把它们理解成：

- `VMManager`
  负责“资源从哪里来”
- `Provider`
  负责“资源怎么运行起来”

这是这一层最关键的边界。

## 一、`VMManager` 和 `Provider` 各管什么

### 1. `Provider`

抽象定义在：

- [base.py:4](../../desktop_env/providers/base.py#L4)

它要求每个 provider 至少实现这些方法：

- `start_emulator(...)`
- `get_ip_address(...)`
- `save_state(...)`
- `revert_to_snapshot(...)`
- `stop_emulator(...)`

这组接口对应的都是“运行态生命周期”。

你可以把它理解成：

- 启动
- 探测地址
- 存快照
- 回滚
- 停止

### 2. `VMManager`

抽象定义在：

- [base.py:47](../../desktop_env/providers/base.py#L47)

它要求实现：

- `initialize_registry(...)`
- `add_vm(...)`
- `delete_vm(...)`
- `occupy_vm(...)`
- `list_free_vms(...)`
- `check_and_clean(...)`
- `get_vm_path(...)`

这组接口对应的是“资源分配与登记”。

你可以把它理解成：

- 有哪些 VM 资源
- 哪些是空闲的
- 哪些被谁占了
- 没有空闲资源时要不要新建一个

## 二、`create_vm_manager_and_provider(...)` 是入口总开关

对应：

- [desktop_env/providers/__init__.py](../../desktop_env/providers/__init__.py)

这里把字符串：

- `vmware`
- `virtualbox`
- `aws`
- `azure`
- `docker`
- `aliyun`
- `volcengine`

映射成真正的：

- manager 实例
- provider 实例

所以从 `DesktopEnv` 往下看，所有 provider 逻辑的入口就是这里。

## 三、`DesktopEnv` 是怎么调用 provider 层的

最值得对照看的几个位置在：

- [desktop_env/desktop_env.py:154](../../desktop_env/desktop_env.py#L154)
- [desktop_env/desktop_env.py:169](../../desktop_env/desktop_env.py#L169)
- [desktop_env/desktop_env.py:198](../../desktop_env/desktop_env.py#L198)
- [desktop_env/desktop_env.py:222](../../desktop_env/desktop_env.py#L222)

整个流程大致是：

1. 创建 manager/provider
2. 如果没有传 `path_to_vm`，调用 `manager.get_vm_path(...)`
3. 调 `provider.start_emulator(...)`
4. 调 `provider.get_ip_address(...)`
5. 后面 reset 时，必要的话调 `provider.revert_to_snapshot(...)`

所以：

- manager 决定“拿哪个资源”
- provider 决定“怎么把它用起来”

## 四、三种典型 provider 形态

这一层最值得你建立的是三种模式：

1. 本地虚拟机模式
2. Docker 容器承载 VM 模式
3. 云实例模式

它们的生命周期差异非常大。

## 五、本地虚拟机模式：VMware

先看 VMware，因为它是你最容易碰到的一条链。

对应文件：

- [desktop_env/providers/vmware/manager.py](../../desktop_env/providers/vmware/manager.py)
- [desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py)

### 1. VMware manager 负责什么

它的核心职责有三类：

1. 管理本地 registry
2. 管理本地 VM 目录
3. 在没有空闲 VM 时自动下载并生成新 VM

### 2. 本地 registry 是什么

关键常量在：

- [manager.py:41](../../desktop_env/providers/vmware/manager.py#L41)
- [manager.py:42](../../desktop_env/providers/vmware/manager.py#L42)
- [manager.py:43](../../desktop_env/providers/vmware/manager.py#L43)

也就是：

- `.vmware_vms`
- `.vmware_lck`
- `./vmware_vm_data`

这里的设计很直白：

- `.vmware_vms`
  记录有哪些 VM、它们是否空闲
- `.vmware_lck`
  保护并发访问
- `vmware_vm_data`
  放实际 VM 文件

### 3. 为什么 VMware manager 会自动下载镜像

对应：

- [manager.py:119](../../desktop_env/providers/vmware/manager.py#L119)
- [manager.py:425](../../desktop_env/providers/vmware/manager.py#L425)

当 `get_vm_path(...)` 发现没有空闲 VM 时，会：

1. 生成新的 VM 名字
2. 下载官方镜像 zip
3. 解压
4. 修改 VMX 元数据
5. 启动一次
6. 等 guest server 就绪
7. 创建 `init_state` 快照

也就是说：

- VMware manager 不只是“查表”
- 它本身带资源初始化能力

### 4. VMware provider 负责什么

对应：

- [desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py)

它更纯粹，是一个 `vmrun` 适配器。

重点方法：

- [provider.py:47](../../desktop_env/providers/vmware/provider.py#L47) `start_emulator`
- [provider.py:72](../../desktop_env/providers/vmware/provider.py#L72) `get_ip_address`
- [provider.py:87](../../desktop_env/providers/vmware/provider.py#L87) `save_state`
- [provider.py:93](../../desktop_env/providers/vmware/provider.py#L93) `revert_to_snapshot`
- [provider.py:100](../../desktop_env/providers/vmware/provider.py#L100) `stop_emulator`

### 5. VMware 生命周期的核心特征

VMware 这条链最值得记住的几个点：

- `path_to_vm` 是真实 `.vmx` 文件路径
- 快照是本地 hypervisor 快照
- IP 通过 `vmrun getGuestIPAddress` 拿
- 停止是 `vmrun stop`
- 回滚不会换资源 ID，仍然是同一条 VM 路径

## 六、另一种本地虚拟机模式：VirtualBox

对应：

- [desktop_env/providers/virtualbox/provider.py](../../desktop_env/providers/virtualbox/provider.py)

VirtualBox 和 VMware 的心智模型很像：

- manager 管本地 VM 分配
- provider 通过命令行工具操作 VM

区别主要在命令工具：

- VMware 用 `vmrun`
- VirtualBox 用 `VBoxManage`

例如：

- [virtualbox/provider.py:58](../../desktop_env/providers/virtualbox/provider.py#L58) `startvm`
- [virtualbox/provider.py:83](../../desktop_env/providers/virtualbox/provider.py#L83) `guestproperty get ... IP`
- [virtualbox/provider.py:109](../../desktop_env/providers/virtualbox/provider.py#L109) snapshot restore

所以你可以把 VirtualBox 看成：

- 和 VMware 同构的一条本地 hypervisor 实现

## 七、Docker 模式：不是 VM 文件路径，而是磁盘镜像

对应文件：

- [desktop_env/providers/docker/manager.py](../../desktop_env/providers/docker/manager.py)
- [desktop_env/providers/docker/provider.py](../../desktop_env/providers/docker/provider.py)

这条链和 VMware 差异非常大。

### 1. Docker manager 的职责比 VMware 更轻

关键逻辑在：

- [docker/manager.py:116](../../desktop_env/providers/docker/manager.py#L116)

它做的事主要是：

1. 确定要用 Ubuntu 还是 Windows 的 qcow2 镜像
2. 如果本地没有，就下载
3. 返回镜像目录路径

#### 镜像下载实战：断点续传（curl）与兜底脚本（Python）

Docker/云端导入镜像（例如 Volcengine 走 TOS 导入 qcow2）时，最容易卡住的反而是“下大文件”。

当前仓库里用到的 qcow2（zip 包）下载入口在：

- Ubuntu：`https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu.qcow2.zip`
- Windows：`https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip`

建议你把它们统一下载到项目根目录的 `./docker_vm_data/`（与 `desktop_env/providers/docker/manager.py` 的默认目录一致）。

**方案一（推荐）：curl 断点续传 + “Empty reply from server” 的安全恢复**

1) 续传下载（可反复重跑）：

```bash
mkdir -p docker_vm_data

curl --http1.1 -L --fail --retry 100 --retry-all-errors --retry-delay 5 \
  -C - --max-time 0 \
  -o "docker_vm_data/Ubuntu.qcow2.zip" \
  "https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu.qcow2.zip"

curl --http1.1 -L --fail --retry 100 --retry-all-errors --retry-delay 5 \
  -C - --max-time 0 \
  -o "docker_vm_data/Windows-10-x64.qcow2.zip" \
  "https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip"
```

2) 如果遇到 `curl: (52) Empty reply from server`，建议先“回退文件到上一次确认的断点位置”再继续，避免把重定向响应的小文本误写进 zip：

```bash
# 先取当前已下载大小（macOS）
sz=$(stat -f%z "docker_vm_data/Windows-10-x64.qcow2.zip")

# 回退到这个大小（确保文件尾部干净），然后再继续 -C - 续传
truncate -s "$sz" "docker_vm_data/Windows-10-x64.qcow2.zip"

# 继续下载（同上）
curl --http1.1 -L --fail --retry 100 --retry-all-errors --retry-delay 5 \
  -C - --max-time 0 \
  -o "docker_vm_data/Windows-10-x64.qcow2.zip" \
  "https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip"
```

> 备注：如果网络访问 `huggingface.co` 不稳定，可尝试设置 `HF_ENDPOINT=https://hf-mirror.com`（部分下载逻辑会读取这个变量）。

**方案二（兜底）：Python requests 续传脚本（可限制下载字节用于快速验证）**

下面脚本不依赖 `aria2c`，会先 HEAD 拿总大小，再用 `Range` 做断点续传；遇到网络错误会 sleep 并重试。

仓库内已提供可直接使用的脚本：`scripts/python/download_hf_qcow2.py`。

用法示例：

- 正常下载（会一直下到完整文件）：
  - `uv run python scripts/python/download_hf_qcow2.py ...`
- 快速验证脚本没问题（只下 1MB 就退出）：
  - 把 `--max-bytes 1048576` 加上即可

```python
import argparse
import os
import time
import requests


def head_total_size(url: str, timeout: int = 20) -> int:
    r = requests.head(url, allow_redirects=True, timeout=timeout)
    r.raise_for_status()
    return int(r.headers.get("content-length") or 0)


def download_with_resume(url: str, out: str, max_bytes: int | None, chunk_mb: int, sleep_sec: float):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    total = head_total_size(url)
    print("total_bytes=", total)

    sess = requests.Session()

    while True:
        pos = os.path.getsize(out) if os.path.exists(out) else 0
        if total and pos >= total:
            print("done, size=", pos)
            return

        # 如果只想验证脚本是否可用：到达 max_bytes 就退出
        if max_bytes is not None and pos >= max_bytes:
            print("reached max_bytes, size=", pos)
            return

        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with sess.get(url, stream=True, allow_redirects=True, timeout=(10, 60), headers=headers) as r:
                r.raise_for_status()
                with open(out, "ab" if pos else "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_mb * 1024 * 1024):
                        if not chunk:
                            continue
                        if max_bytes is not None:
                            remaining = max_bytes - f.tell()
                            if remaining <= 0:
                                print("reached max_bytes, size=", f.tell())
                                return
                            if len(chunk) > remaining:
                                f.write(chunk[:remaining])
                                print("reached max_bytes, size=", f.tell())
                                return
                        f.write(chunk)
            time.sleep(sleep_sec)
        except Exception as e:
            print("error:", type(e).__name__, e)
            time.sleep(5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-bytes", type=int, default=None)
    p.add_argument("--chunk-mb", type=int, default=8)
    p.add_argument("--sleep-sec", type=float, default=0.5)
    args = p.parse_args()
    download_with_resume(args.url, args.out, args.max_bytes, args.chunk_mb, args.sleep_sec)


if __name__ == "__main__":
    main()
```

（快速验证示例：只下载 1MB，检查网络/权限/重定向链路都 OK）

```bash
uv run python scripts/python/download_hf_qcow2.py \
  --url "https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip" \
  --out "docker_vm_data/Windows-10-x64.qcow2.zip.test1m" \
  --max-bytes 1048576
```

下载完成后，记得解压得到真正的 `.qcow2`：

```bash
unzip -o docker_vm_data/Ubuntu.qcow2.zip -d docker_vm_data
unzip -o docker_vm_data/Windows-10-x64.qcow2.zip -d docker_vm_data
```

这里没有复杂 registry。

很多 `VMManager` 抽象方法在 Docker 里实际上是空实现：

- [docker/manager.py:92](../../desktop_env/providers/docker/manager.py#L92)

这说明 Docker 这条链的资源管理模型和本地多 VM registry 很不同。

### 2. Docker provider 真正在干什么

关键逻辑在：

- [docker/provider.py:87](../../desktop_env/providers/docker/provider.py#L87)

它不是启动一个 `.vmx`，而是：

1. 分配宿主机端口
2. 启动一个 Docker 容器
3. 把 qcow2 镜像绑定到容器里
4. 等容器里的 guest server 就绪

### 3. Docker provider 的 `path_to_vm` 语义是什么

这里的 `path_to_vm` 不是 VM 配置文件，而是：

- qcow2 镜像路径

然后被挂进容器：

- [docker/provider.py:115](../../desktop_env/providers/docker/provider.py#L115)

也就是绑定到：

```text
/System.qcow2
```

### 4. 为什么 Docker provider 的 `get_ip_address()` 很奇怪

对应：

- [docker/provider.py:145](../../desktop_env/providers/docker/provider.py#L145)

它返回的不是单纯 IP，而是：

```text
localhost:{server_port}:{chromium_port}:{vnc_port}:{vlc_port}
```

这是因为 Docker 这条链本质上依赖端口映射，而不是 guest 私网 IP。

你在 `DesktopEnv._start_emulator()` 里也能看到它会把这个字符串拆开：

- [desktop_env.py:204](../../desktop_env/desktop_env.py#L204)

### 5. Docker 生命周期的核心特征

这条链最值得记住的几个点：

- `path_to_vm` 是磁盘镜像，不是 hypervisor VM 配置文件
- “启动”本质是起容器
- “IP”本质是 localhost + 端口映射
- 没有真正的 hypervisor snapshot
- 回滚的本质是 stop 掉容器，重起一个干净实例

## 八、云实例模式：AWS

对应文件：

- [desktop_env/providers/aws/manager.py](../../desktop_env/providers/aws/manager.py)
- [desktop_env/providers/aws/provider.py](../../desktop_env/providers/aws/provider.py)

这条链又和前两种都不一样。

### 1. AWS manager 为什么几乎没有 registry 逻辑

看这里：

- [aws/manager.py:188](../../desktop_env/providers/aws/manager.py#L188)

你会发现很多 `VMManager` 方法都是 `pass`。

这是因为 AWS 这条链默认模型不是：

- 管一批本地静态 VM

而是：

- 需要就去申请一个新实例

所以它的核心只有：

- [aws/manager.py:232](../../desktop_env/providers/aws/manager.py#L232) `get_vm_path(...)`

而这里返回的也不是文件路径，而是：

- EC2 instance ID

### 2. `path_to_vm` 在 AWS 里其实是实例 ID

这一点非常重要。

例如：

- `i-0abc123...`

这就是后面 provider 里所有 API 的对象。

所以别被变量名 `path_to_vm` 误导。

它在云 provider 中更多是“资源标识符”。

### 3. AWS provider 的职责

对应：

- [aws/provider.py:21](../../desktop_env/providers/aws/provider.py#L21)

它负责：

- 启动实例
- 查实例 IP
- 通过 AMI 做 save/revert
- terminate 实例

### 4. AWS 的“回滚快照”为什么很不一样

关键逻辑在：

- [aws/provider.py:103](../../desktop_env/providers/aws/provider.py#L103)

这里的回滚不是：

- 把当前实例恢复到某个本地快照

而是：

1. 终止旧实例
2. 用指定 AMI 启动一个新实例
3. 返回新的 instance ID

这就是为什么 `Provider.revert_to_snapshot(...)` 的返回值不是摆设。

在 `DesktopEnv._revert_to_snapshot()` 里，如果 provider 返回了新的 path/id：

- [desktop_env.py:225](../../desktop_env/desktop_env.py#L225)

环境会更新自己的 `self.path_to_vm`。

### 5. AWS 生命周期的核心特征

这条链最值得记住的几个点：

- `path_to_vm` 实际是 EC2 instance ID
- 启动/停止通过 EC2 API 完成
- IP 通过 `describe_instances` 拿
- 回滚不是恢复同一个实例，而是重建实例
- snapshot 对应的是 AMI，而不是本地 hypervisor 快照

## 九、Azure / Aliyun / Volcengine 为什么可以看成同一家族

虽然实现细节不同，但它们在抽象层面都更接近 AWS，而不是 VMware/Docker。

原因是：

- 资源是云实例
- `path_to_vm` 更像资源 ID
- 生命周期依赖云 API
- 回滚通常依赖镜像 / 快照 / 重建资源

例如 Azure manager：

- [azure/manager.py](../../desktop_env/providers/azure/manager.py)

也保留了 `VMManager` 结构，但语义明显更偏云资源管理，而不是本地文件路径。

所以你可以把 provider 大致分成两大家族：

### 本地资源家族

- VMware
- VirtualBox

### 远端资源家族

- AWS
- Azure
- Aliyun
- Volcengine

而 Docker 则更像：

- 本地容器化 guest 运行时

## 十、为什么 `is_environment_used` 对 provider 层很重要

在环境里有个很关键的状态：

- [desktop_env.py:158](../../desktop_env/desktop_env.py#L158)

`self.is_environment_used`

它决定下次 `reset()` 时，要不要真的做回滚。

### 1. 为什么本地 VM 默认是已使用

对应：

- [desktop_env.py:161](../../desktop_env/desktop_env.py#L161)

本地虚拟机 provider：

- `vmware`
- `virtualbox`

默认会被视为“脏的”，因为它们是复用同一台本地 guest。

### 2. 为什么 Docker / AWS 默认是未使用

这些 provider 更容易从“全新实例”开始：

- Docker 可以起新容器
- AWS 可以重建实例

所以环境会更积极地跳过不必要的 snapshot 回滚。

## 十一、三种生命周期放在一起对比

### 1. VMware / VirtualBox

- 资源标识：本地 VM 文件路径
- manager：维护本地 registry
- provider：调 hypervisor CLI
- 回滚：本地快照恢复
- IP：由 guest tools / hypervisor 提供

### 2. Docker

- 资源标识：qcow2 镜像目录
- manager：确保镜像存在
- provider：起容器并映射端口
- 回滚：停容器再起新实例
- IP：`localhost + ports`

### 3. AWS / 云实例

- 资源标识：实例 ID
- manager：申请新实例
- provider：调云 API
- 回滚：基于镜像/AMI 重建实例
- IP：云实例网络信息

## 十二、这一层最值得你自己动手看的 4 个点

### 实验 1：对照 `path_to_vm` 的语义

分别看：

- VMware
- Docker
- AWS

目标：

- 彻底摆脱“它一定是文件路径”这个误解

### 实验 2：对照 `get_vm_path(...)`

分别看：

- [vmware/manager.py:425](../../desktop_env/providers/vmware/manager.py#L425)
- [docker/manager.py:116](../../desktop_env/providers/docker/manager.py#L116)
- [aws/manager.py:232](../../desktop_env/providers/aws/manager.py#L232)

目标：

- 看资源是怎么来的

### 实验 3：对照 `get_ip_address(...)`

分别看：

- VMware provider
- Docker provider
- AWS provider

目标：

- 看“连接 guest”这件事在不同底座上为什么完全不同

### 实验 4：对照 `revert_to_snapshot(...)`

分别看：

- VMware
- Docker
- AWS

目标：

- 理解“回滚”在不同 provider 中的真实含义

## 十三、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，provider 生命周期这一层第一轮就算过关：

1. `VMManager` 和 `Provider` 的职责边界是什么？
2. 为什么 VMware manager 要维护 `.vmware_vms` 这种 registry？
3. 为什么 Docker provider 返回的“IP”其实是 `localhost + ports`？
4. 为什么 AWS 的 `path_to_vm` 其实是 instance ID？
5. 为什么 AWS 的回滚会返回新的资源标识？
6. 为什么 `DesktopEnv._revert_to_snapshot()` 要支持 path/id 更新？

## 十四、下一步该读什么

如果继续沿“非 agent 深入”的路线走，最自然的下一步有两个：

1. `evaluation_examples`
   去看 benchmark 任务数据本身是怎么组织的
2. `actions`
   去看 `computer_13` 这种结构化动作空间是怎么定义的

如果你问我现在更推荐哪个：

我建议先看 `evaluation_examples`。

因为到这一步，你已经把：

- 环境
- runner
- evaluator
- controller/server
- provider

都串起来了。

这时候回头看“任务数据是怎么驱动整个系统的”，会特别顺。 
