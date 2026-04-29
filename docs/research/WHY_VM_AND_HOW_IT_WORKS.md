# 为什么要用虚拟机来跑 OSWorld，以及它在内部是怎么工作的

## 1. 这篇文档要回答什么

这篇文档专门回答下面三个问题：

1. 为什么 OSWorld 这类桌面 benchmark 不能直接在你的本地宿主机上做正式测试
2. 为什么它要依赖虚拟机 / 云端环境
3. 在当前项目里，虚拟机路线到底执行了哪些命令、HTTP 请求和环境恢复动作

本文不是泛泛讲“虚拟机的好处”，而是结合当前仓库源码来讲这个项目的真实运行机制。

---

## 2. 先说结论

### 2.1 为什么不推荐直接在本地宿主机测试

对于 OSWorld 这类系统级 GUI benchmark，**直接在你的宿主机本地桌面做正式测试并不可靠**。

不是说技术上永远做不到，而是：

- 任务状态不可恢复
- 宿主机会被污染
- benchmark 复现性差
- 自动评估信号容易失真
- 批量运行和并行运行难以控制

所以它的默认设计是：

- 用一个**独立桌面环境**
- 每个任务前先恢复到干净初始态
- 再让 agent 在该环境里做操作
- 最后自动检查结果

### 2.2 为什么虚拟机是默认主路径

因为虚拟机天然满足这几个 benchmark 最核心的需求：

1. **环境隔离**
2. **可恢复**
3. **可复现**
4. **可批量调度**
5. **不污染宿主机**

这也是为什么当前项目支持的 provider 都围绕“可恢复环境”展开：

- VMware
- VirtualBox
- Docker
- AWS
- Azure

---

## 3. 为什么不能直接在本地宿主机测试

### 3.1 无法保证干净初始状态

OSWorld 的任务默认要求：

- 每个任务开始前，桌面环境都回到一个固定状态

这在当前项目里是靠：

- `snapshot`
- `revert_to_snapshot`

实现的。

如果你直接跑宿主机：

- 上一个任务改了浏览器设置
- 创建了文件
- 打开了应用
- 修改了桌面布局
- 写入了历史记录

那么下一个任务就会吃到这些脏状态。

这不是“偶尔有点误差”，而是 benchmark 本身会变味。

### 3.2 宿主机会被 benchmark 任务污染

当前任务会做的事情不止是“点几下”：

- 启动 Chrome / LibreOffice / VS Code / GIMP / VLC / Thunderbird
- 创建和修改文件
- 写入桌面目录
- 改浏览器设置
- 操作系统级命令执行
- shell / python 命令执行

如果这些都落到你的日常工作环境里：

- 桌面会被弄乱
- 文件会被覆盖
- 浏览器 profile 会被污染
- 账号状态可能被改
- proxy / 登录配置可能被写坏

### 3.3 自动评估的前提会失效

很多任务的 evaluator 都假定：

- 环境是标准初始态
- 应用版本一致
- 文件路径固定
- guest 里服务、插件、配置已经准备好

如果你直接跑宿主机，本地环境偏差会导致：

- agent 其实做对了，但 evaluator 判错
- agent 其实没做对，但因为宿主机已有残留状态而误判成功

### 3.4 并行运行和批量运行基本不可控

OSWorld 支持：

- 单任务运行
- 多任务批量运行
- 多环境并行运行

如果直接跑在宿主机：

- 你没有多份隔离桌面
- 没法安全并行
- 没法同时运行多个 benchmark worker

---

## 4. 当前项目为什么选择“虚拟机 + 远程控制”的结构

这个项目不是“直接在本地 Python 里 import pyautogui 然后乱点”。

它的结构本质上是：

1. Host 侧 runner
2. Host 侧 `DesktopEnv`
3. Provider 启动 guest 环境
4. Guest 内部运行一个 server
5. Host 通过 HTTP 控制 guest
6. Agent 从 guest 拿截图和 accessibility tree
7. Agent 输出动作
8. Host 再把动作发回 guest 执行

这套设计的核心目的就是：

- **host 负责编排**
- **guest 负责被控执行**
- **snapshot 负责状态恢复**

---

## 5. 当前项目里虚拟机路线是怎么工作的

下面按时间顺序讲。

### 5.1 阶段一：Runner 启动

入口通常是：

- `quickstart.py`
- `run.py`
- `scripts/python/run_multienv.py`

其中：

- `quickstart.py` 用来做最小 smoke test
- `run.py` 用来串行跑 benchmark
- `run_multienv.py` 用来并行跑 benchmark

它们都会创建：

- `DesktopEnv`
- Agent

然后把 benchmark 任务送进执行循环。

### 5.2 阶段二：DesktopEnv 创建环境

核心在：

- `desktop_env/desktop_env.py`

`DesktopEnv.__init__()` 做的事：

1. 记录 provider 信息
2. 确定 screen size、密码、端口
3. 通过 provider 工厂拿到：
   - `manager`
   - `provider`
4. 确定 VM 路径
5. 调 `_start_emulator()`

也就是说：

**一旦你创建 `DesktopEnv`，它就开始接管虚拟环境生命周期。**

### 5.3 阶段三：Provider 启动虚拟机

以 VMware 为例，provider 逻辑在：

- `desktop_env/providers/vmware/provider.py`

真实执行的命令是：

#### 1. 查看当前运行中的 VM

```bash
vmrun -T ws list
```

在 macOS host 上则会变成：

```bash
vmrun -T fusion list
```

#### 2. 启动 VM

```bash
vmrun -T ws start "<path_to_vm>"
```

如果 headless：

```bash
vmrun -T ws start "<path_to_vm>" nogui
```

#### 3. 获取 guest IP

```bash
vmrun -T ws getGuestIPAddress "<path_to_vm>" -wait
```

#### 4. 保存 snapshot

```bash
vmrun -T ws snapshot "<path_to_vm>" init_state
```

#### 5. 恢复 snapshot

```bash
vmrun -T ws revertToSnapshot "<path_to_vm>" init_state
```

#### 6. 停止 VM

```bash
vmrun -T ws stop "<path_to_vm>"
```

对于 macOS host，`ws` 会替换为 `fusion`。

### 5.4 阶段四：首次安装虚拟机镜像

如果你没有现成 VM，VMware manager 会做这些事：

1. 从 Hugging Face 下载官方镜像压缩包
2. 断点续传下载
3. 解压
4. 重命名 VM 元数据
5. 启动 VM
6. 等 guest server 就绪
7. 创建 `init_state` snapshot

也就是说，**第一次跑不是只启动 VM，而是会自动完成环境安装。**

以 Ubuntu ARM 为例，代码会自动下载：

- `Ubuntu-arm.zip`

Windows 则会下载：

- `Windows-x86.zip`

---

## 6. Guest 内到底跑了什么

### 6.1 Guest 内有一个桌面控制 server

关键文件：

- `desktop_env/server/main.py`

这个 server 会暴露一批 HTTP 接口给 host 调用。

### 6.2 Host 读取观测时调用的接口

#### 截图

```http
GET /screenshot
```

#### 无障碍树

```http
GET /accessibility
```

#### 终端输出

```http
GET /terminal
```

#### 下载文件

```http
POST /file
```

### 6.3 Host 执行动作时调用的接口

#### 执行命令

```http
POST /execute
```

#### 执行并验证命令

```http
POST /execute_with_verification
```

#### 启动应用

```http
POST /setup/launch
```

#### 上传文件

```http
POST /setup/upload
```

#### 打开文件

```http
POST /setup/open_file
```

#### 激活窗口 / 关闭窗口

```http
POST /setup/activate_window
POST /setup/close_window
```

#### 执行 Python / Bash

```http
POST /run_python
POST /run_bash_script
```

这说明：

- guest 不是黑盒
- host 在 benchmark 过程中会非常频繁地向 guest 发 HTTP 请求

---

## 7. SetupController 在任务开始前做了什么

关键文件：

- `desktop_env/controllers/setup.py`

`SetupController.setup()` 的逻辑是：

1. 先轮询 guest 的 `/terminal`
2. 确认 server 活着
3. 读取任务里的 `config`
4. 逐步执行每个 setup action

任务里的 setup action 类型包括：

- `download`
- `upload_file`
- `change_wallpaper`
- `open`
- `launch`
- `execute`
- `execute_with_verification`
- `sleep`
- `act`
- `replay`
- `activate_window`
- `close_window`
- `proxy`
- `chrome_open_tabs`
- `chrome_close_tabs`
- `googledrive`
- `login`
- `update_browse_history`

这意味着 benchmark 开始前，环境不是“自然打开”，而是：

**由 SetupController 把 guest 环境明确布置到任务要求的状态。**

---

## 8. 一个任务是怎么真正跑起来的

单任务执行主线在：

- `lib_run_single.py`

按顺序是：

1. `env.reset(task_config=example)`
2. `agent.reset(...)`
3. 等 guest 环境稳定
4. `obs = env._get_obs()`
5. `agent.predict(instruction, obs)`
6. 得到动作列表
7. `env.step(action)`
8. 保存截图和轨迹
9. 循环直到 done / max_steps
10. `env.evaluate()`
11. 写入 `result.txt`
12. 结束录像

所以这个 benchmark 的真正执行闭环是：

**任务 JSON -> 环境 reset -> 观测获取 -> agent 决策 -> 动作执行 -> evaluator 判分**

---

## 9. 为什么 snapshot 是这套机制的核心

虚拟机在这个项目里的真正价值，不只是“有个独立桌面”，而是：

### 9.1 snapshot 让任务之间彼此隔离

如果没有 snapshot：

- 任务 A 改了浏览器默认搜索引擎
- 任务 B 再来测试“把默认搜索引擎改成 Bing”

你根本不知道当前起点是什么。

### 9.2 snapshot 让 benchmark 可重复

只要 snapshot 一样：

- 环境起点就一样
- 失败可以复现
- 结果可以对比

### 9.3 snapshot 支撑批量 benchmark

因为每次任务都能回到固定状态，所以：

- 可以持续跑很多任务
- 可以中断后继续
- 可以多 worker 跑

### 9.4 snapshot 支撑自动评估可信度

自动 evaluator 的可信度很大程度取决于：

- 初始态是不是标准化

这也是为什么虚拟机不是“可有可无的工程细节”，而是 benchmark 可信度的一部分。

---

## 10. 如果改成直接在宿主机本地跑，会发生什么

### 10.1 你要自己重造 snapshot 能力

宿主机没有天然的 benchmark reset。

你得自己处理：

- 桌面文件清理
- 浏览器 profile 恢复
- 应用关闭与重开
- 系统设置回滚
- 缓存和历史记录清理

### 10.2 你要改掉远程 guest 的控制模型

现在整个项目默认是：

- host 控制 guest

如果直接宿主机跑，你得把：

- provider
- controller
- server
- setup
- reset

这几层逻辑重新收拢成“本地单机场景”。

### 10.3 benchmark 可信度会下降

即便你技术上能改通，它也更像：

- 本地调试环境
- demo 环境

而不是严格意义上的 benchmark 环境。

---

## 11. 一条完整的“虚拟机 benchmark 流程图（文字版）”

可以把当前项目理解成这条流水线：

1. Runner 读取任务列表
2. 创建 `DesktopEnv`
3. Provider 启动 VM
4. Provider 获取 guest IP
5. Host 通过 HTTP 连上 guest server
6. `reset()` 时恢复 snapshot
7. `SetupController` 按任务 `config` 布置环境
8. Host 获取 screenshot / a11y / terminal
9. Agent 基于观测输出动作
10. Host 通过 guest server 执行动作
11. 保存截图、轨迹、录像
12. `evaluate()` 调用 getter + metric 判分
13. 写入 `result.txt`
14. 汇总 success rate

配套流程图见：

- [OSWorld 虚拟机 Benchmark 运行流程图（SVG）](/Users/bytedance/PycharmProjects/test5/osworld/docs/diagrams/osworld-vm-runtime-flow.svg)

---

## 12. 真实执行到的“命令”和“操作”总结

### 12.1 Host 侧 VMware 命令

真实会执行：

```bash
vmrun -T ws list
vmrun -T ws start "<vmx_path>" [nogui]
vmrun -T ws getGuestIPAddress "<vmx_path>" -wait
vmrun -T ws snapshot "<vmx_path>" init_state
vmrun -T ws revertToSnapshot "<vmx_path>" init_state
vmrun -T ws stop "<vmx_path>"
```

macOS host 上则是：

```bash
vmrun -T fusion ...
```

### 12.2 Host 到 guest 的 HTTP 调用

真实会打：

```http
GET  /terminal
GET  /screenshot
GET  /accessibility
POST /execute
POST /execute_with_verification
POST /setup/launch
POST /setup/upload
POST /setup/open_file
POST /run_python
POST /run_bash_script
```

### 12.3 Guest 内实际执行的动作

真实会做：

- 启动应用
- 运行 shell 命令
- 打开文件
- 上传 benchmark 附件
- 修改桌面 / 系统状态
- 截图
- 抽取 accessibility tree
- 执行 `pyautogui` 动作

---

## 13. 最后一句话总结

OSWorld 使用虚拟机，不是为了“显得高级”，而是因为 **benchmark 需要隔离、恢复、复现和自动评估可信度**。

在这个项目里，虚拟机路线的本质机制是：

**provider 管理 guest 生命周期，snapshot 保证任务起点一致，guest server 提供观测与执行接口，DesktopEnv 把它们统一成一个可评测的桌面环境。**

如果你只是想开发期验证 agent，本地宿主机也许能凑合。  
但如果你要做**正式的、可复现的、可对比的 CUA benchmark**，虚拟机不是可选项，而是这套机制的核心部分。
