# 01 Quickstart 运行与 PyCharm 上手

本文基于当前仓库里的 [quickstart.py](../../quickstart.py) 实现来写。

先说结论：

- `quickstart.py` 是环境连通性示例，不是完整 benchmark 运行入口。
- 它不会调用大模型，也不需要 `OPENAI_API_KEY`。
- 它做的事情很简单：启动 `DesktopEnv`、加载一个示例任务、执行一次 `pyautogui.rightClick()`、然后关闭环境。

如果你的目标是先确认环境能跑起来，这个文件很合适。

## 先理解它到底跑了什么

`quickstart.py` 的核心流程只有四步：

1. 构造 `DesktopEnv`
2. `env.reset(task_config=example)`
3. `env.step("pyautogui.rightClick()")`
4. `env.close()`

这意味着：

- 它主要是在验证环境启动、任务注入、动作执行、观测获取这一整条链路。
- 它并不会真的把示例里的“安装 Spotify”任务自动做完。
- 所以你看到的成功，更像是“环境工作正常”，不是“Agent 解题成功”。

## 运行前要做哪些配置

这里先区分两类配置：

1. Python 运行环境
2. Provider 运行环境

`quickstart.py` 默认使用的是：

- `provider_name=vmware`
- `os_type=Ubuntu`
- `action_space=pyautogui`
- `headless=False`

也就是说，如果你什么都不传，它默认会尝试走 VMware/Fusion 这条链。

## 一、Python 环境配置

你至少需要先把项目依赖装好。

如果你已经按仓库当前状态安装好了 `.venv`，这一节可以跳过。

这个仓库当前更稳的是 Python 3.12，不是 3.13。

建议命令：

```bash
uv sync --python 3.12 --frozen
```

装完后确认解释器：

```bash
.venv/bin/python --version
```

预期应当类似：

```bash
Python 3.12.x
```

## 二、Provider 运行环境配置

这是 `quickstart.py` 真正能不能跑起来的关键。

### 推荐选择

如果你是在 macOS，尤其是 Apple 芯片机器上，建议优先用默认的 `vmware`，实际对应的是 VMware Fusion。

如果你是在 Linux/Windows 且有合适的虚拟化支持，可以考虑 `docker`。

但从当前仓库 README 的建议看：

- macOS 更推荐 VMware/Fusion
- Docker 更适合 Linux/Windows 或带 KVM 的服务器

### 1. 使用 VMware / Fusion 时你需要准备什么

你需要先在宿主机装好 VMware。

相关文档：

- [README.md](../../README.md)
- [desktop_env/providers/vmware/INSTALL_VMWARE.md](../../desktop_env/providers/vmware/INSTALL_VMWARE.md)

最关键的检查项是：

```bash
vmrun -T ws list
```

在 macOS 上通常对应 Fusion，底层代码会自动切换 `-T fusion`，但核心要求一样：

- `vmrun` 必须可用
- VMware/Fusion 必须已正确安装

### 2. 第一次运行会自动做什么

如果你不传 `--path_to_vm`，仓库会尝试自动找可用 VM。

对 `vmware` provider，当前实现会：

1. 在 `./vmware_vm_data/` 下查找已有可用 VM
2. 如果没有，就自动下载官方提供的基础镜像
3. 解压后重命名 VM 元数据
4. 启动 VM
5. 等待环境内服务就绪
6. 自动创建 `init_state` 快照

所以结论是：

- `--path_to_vm` 不是必填
- 首次运行会比较慢
- 首次运行需要网络、磁盘空间和 VMware 正常工作

### 3. 为什么会自动下载，以及代码在哪里触发

这里下载的不是 Python 依赖，而是 OSWorld 预制的 VMware 虚拟机镜像。

对你当前这台 macOS ARM 机器，默认会选：

```text
https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu-arm.zip
```

这条 URL 定义在：

- [desktop_env/providers/vmware/manager.py](../../desktop_env/providers/vmware/manager.py)

下载文件通常会落到：

```text
./vmware_vm_data/Ubuntu-arm.zip
```

解压后会生成类似下面这样的目录：

```text
./vmware_vm_data/Ubuntu0/
./vmware_vm_data/Ubuntu1/
```

这些目录里放的是可启动的 VMware VM 文件，不是普通项目缓存。

如果你想理解“为什么直接运行 `quickstart.py` 会开始下载”，调用链可以简化成这样：

1. [quickstart.py](../../quickstart.py) 里没有传 `--path_to_vm` 时，`path_to_vm` 默认为 `None`
2. [quickstart.py](../../quickstart.py) 用这个参数构造 `DesktopEnv`
3. [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py) 在 `path_to_vm` 为空时，会调用 `self.manager.get_vm_path(...)`
4. [desktop_env/providers/__init__.py](../../desktop_env/providers/__init__.py) 会根据 `provider_name=vmware` 创建 `VMwareVMManager`
5. [desktop_env/providers/vmware/manager.py](../../desktop_env/providers/vmware/manager.py) 的 `get_vm_path(...)` 发现本地没有可用 VM 时，会调用 `_install_vm(...)`
6. `_install_vm(...)` 里的 `__download_and_unzip_vm()` 会真正发起下载、解压、改名

如果你想看代码里的关键位置，重点看这些点：

- [quickstart.py:38](../../quickstart.py)
- [quickstart.py:45](../../quickstart.py)
- [desktop_env/desktop_env.py:169](../../desktop_env/desktop_env.py)
- [desktop_env/providers/__init__.py:14](../../desktop_env/providers/__init__.py)
- [desktop_env/providers/vmware/manager.py:122](../../desktop_env/providers/vmware/manager.py)
- [desktop_env/providers/vmware/manager.py:425](../../desktop_env/providers/vmware/manager.py)

下载之后还会继续做几件事：

1. 解压镜像
2. 修改 VM 元数据，避免和原始模板冲突
3. 启动 VM
4. 等待 `vmrun getGuestIPAddress ... -wait` 返回 IP
5. 轮询 `http://<vm-ip>:5000/screenshot`，确认 OSWorld 服务就绪
6. 自动创建 `init_state` 快照

也就是说，你看到“在下载”，本质上是在做第一次的 OSWorld 环境初始化。

### 4. 如果网络访问 Hugging Face 有问题

镜像下载是从 Hugging Face 拉的。

如果你的网络访问 `huggingface.co` 不稳定，可以设置：

```bash
HF_ENDPOINT=https://hf-mirror.com
```

这个变量对自动下载 VM 镜像有帮助。

### 5. 如果你想传自己的 VM

可以用：

```bash
--path_to_vm /absolute/path/to/your.vmx
```

但这条路比自动下载仓库自带镜像复杂得多。

因为你自己的 VM 必须满足 OSWorld 的环境约束，包括但不限于：

- 固定用户名和密码约定
- 环境内控制服务正常启动
- 可访问性树支持
- 端口与依赖软件配置正确

相关背景可看：

- [desktop_env/server/README.md](../../desktop_env/server/README.md)

如果你只是想先跑通，不建议一开始就走自定义 VM。

### 6. 基于你当前机器的直接配置

如果你已经通过 `vmrun list` 看到了自己的 VM：

```text
/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx
```

那么 `--path_to_vm` 就直接传这个 `.vmx` 的绝对路径：

```bash
--path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

对应的完整命令可以直接写成：

```bash
uv run python quickstart.py \
  --provider_name vmware \
  --path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

如果你在 PyCharm 里配置 `Parameters`，也直接填：

```text
--provider_name vmware --path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

## 三、命令行里怎么运行

最简单的跑法：

```bash
uv run python quickstart.py --provider_name vmware
```

如果你已经激活了虚拟环境，也可以：

```bash
python quickstart.py --provider_name vmware
```

如果你想显式指定 VM 路径：

```bash
uv run python quickstart.py \
  --provider_name vmware \
  --path_to_vm /absolute/path/to/Ubuntu.vmx
```

基于你当前机器，建议你优先用这条：

```bash
uv run python quickstart.py \
  --provider_name vmware \
  --path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

## 四、PyCharm 里怎么运行

如果你想在 PyCharm 里直接点运行，建议按下面配置。

### 1. 先把解释器切到项目 `.venv`

在 PyCharm 里打开：

`Settings` -> `Project` -> `Python Interpreter`

选择：

- `Add Interpreter`
- `Existing`
- 指向项目里的解释器

路径通常是：

```text
/Users/.../osworld/.venv/bin/python
```

确认后，PyCharm 就会使用项目已经装好的依赖。

### 2. 新建 Run Configuration

打开：

`Run` -> `Edit Configurations`

新增一个 `Python` 配置，推荐这样填：

- `Name`: `quickstart-vmware`
- `Script path`: 项目根目录下的 `quickstart.py`
- `Working directory`: 项目根目录
- `Python interpreter`: 项目的 `.venv/bin/python`

### 3. Parameters 怎么填

如果你走默认 VMware：

```text
--provider_name vmware
```

如果你要指定 VM 路径：

```text
--provider_name vmware --path_to_vm /absolute/path/to/Ubuntu.vmx
```

基于你当前机器，可以直接填成：

```text
--provider_name vmware --path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

### 4. Environment variables 一般怎么填

默认 `quickstart.py` 不需要模型 API Key。

大多数情况下可以留空。

如果你下载 VM 镜像需要镜像站，可以加：

```text
HF_ENDPOINT=https://hf-mirror.com
```

### 5. 运行时会看到什么

第一次运行通常会比较慢，因为可能发生：

- 下载 VM 镜像
- 解压镜像
- 启动 VMware/Fusion
- 等待虚拟机里的服务启动
- 创建 `init_state` 快照

所以第一次运行卡几分钟并不一定是坏事。

如果是第二次运行，通常会快很多。

## 五、PyCharm 里更稳的用法

建议先用 `Run`，不要一上来就 `Debug`。

原因很简单：

- 第一次运行会下载大文件
- 会启动外部虚拟机
- 调试器会把第一次体验弄得更慢、更难判断问题

更稳的顺序是：

1. 先用 `Run` 跑通一次
2. 确认 VM 能启动、环境能 reset、脚本能正常退出
3. 再切到 `Debug`

## 六、当前脚本里一个容易踩坑的点

`quickstart.py` 当前的 `headless` 参数定义是：

```python
parser.add_argument("--headless", type=bool, default=False)
```

这不是一个理想的 `argparse` 写法。

因为：

- `--headless True` 会得到 `True`
- `--headless False` 在很多情况下也会被解析成 `True`

所以当前建议是：

- 如果你不需要 headless，就完全不要传 `--headless`
- 先使用默认值 `False`

也就是说，最稳的方式就是：

```bash
uv run python quickstart.py --provider_name vmware
```

而不是：

```bash
uv run python quickstart.py --provider_name vmware --headless False
```

后者看起来像关闭 headless，但实际并不可靠。

再补一层实际含义：

- `headless=False`
  会尽量以带图形界面的方式启动 VMware/Fusion 虚拟机窗口。
- `headless=True`
  会在底层 `vmrun start` 后面追加 `nogui`，也就是无界面启动。

但这里有一个很实际的行为要注意：

- 如果你的 VM 本来就已经在运行，provider 会直接复用它。
- 这时无论你传不传 `--headless`，都不会重新按 `nogui` 启动一次。

所以对你当前这台已经在运行的 VM 来说：

- 最稳的是完全不要传 `--headless`
- 直接复用当前 VM 即可

也就是说，你当前最推荐的命令还是：

```bash
uv run python quickstart.py \
  --provider_name vmware \
  --path_to_vm "/Users/bytedance/Virtual Machines.localized/Ubuntu 64 位 ARM 26.04.vmwarevm/Ubuntu 64 位 ARM 26.04.vmx"
```

## 七、常见报错应该先查什么

### 1. `vmrun` 找不到

现象通常类似：

- `command not found: vmrun`
- 启动 provider 时报错

先检查：

```bash
which vmrun
```

如果终端里有、PyCharm 里没有，说明是 PyCharm 的环境变量没继承到。

这种情况下可以：

- 从终端启动 PyCharm
- 或者在 PyCharm 的运行配置里补 PATH

### 2. 首次运行长时间无响应

先判断是不是在做首次下载或解压。

默认 VM 可能会被自动下载到：

- `./vmware_vm_data/`
- 或者 Docker 模式下的 `./docker_vm_data/`

如果这些目录里正在增长大文件，通常不是卡死，而是在准备镜像。

### 3. 自定义 VM 启动了，但环境 reset 失败

这种情况大概率不是 Python 依赖问题，而是你的 VM 不符合 OSWorld 环境约束。

优先建议：

- 先改回仓库自动下载的官方镜像
- 不要第一步就调自定义 VM

### 4. 运行后只看到右键，没有完成任务

这是正常的。

因为 `quickstart.py` 只是：

- 加载一个示例任务
- 人工执行一个固定动作 `pyautogui.rightClick()`

它不是完整 Agent 流程。

如果你想运行真正的 Agent 评测，下一步应该看：

- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

## 八、推荐的最小上手路径

如果你的目标只是“先确认环境没问题”，建议顺序如下：

1. 用 `.venv` 解释器
2. 装好 VMware/Fusion
3. 确认 `vmrun` 可用
4. 在终端先跑：

```bash
uv run python quickstart.py --provider_name vmware
```

5. 跑通后，再在 PyCharm 建运行配置

这是最稳的路线。

## 九、一句话判断你现在缺什么

如果你问“我跑 `quickstart.py` 前到底要不要配很多模型能力？”

答案是不需要。

你真正必须准备的是：

- 正确的 Python 环境
- 正常可用的 VMware/Fusion 或其他 provider
- 可下载或可访问的 VM 镜像

而不是模型 API Key。
