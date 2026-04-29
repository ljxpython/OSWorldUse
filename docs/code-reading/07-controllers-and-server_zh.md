# 07 Controllers 与 Guest Server 解读

这一篇接在 [06 Evaluator 与 Metrics 解读](./06-evaluators-and-metrics_zh.md) 后面最自然。

因为到这一步你已经知道：

- 环境如何返回 observation
- Agent 如何生成 action
- runner 如何串起主循环
- evaluator 如何打分

接下来最自然的问题就是：

- `DesktopEnv` 里那些 observation 和 action，实际上是怎么穿过网络边界到 guest 里的？
- `PythonController` 和 `SetupController` 为什么存在？
- guest 内部的 Flask server 到底提供了哪些能力？

这篇就专门讲这一层。

## 先记住最关键的结构

这一层的核心结构可以先记成：

`DesktopEnv -> Controller -> HTTP -> guest server -> guest OS`

也就是说：

1. `DesktopEnv` 不直接操纵 guest
2. 它通过 controller 发 HTTP 请求
3. guest 内部有一个 server 接这些请求
4. server 再调用本机的截图、命令执行、窗口控制、可访问性树抓取等能力

这是一种“宿主机控制远端桌面服务”的架构，而不是“宿主机直接本地调用 pyautogui”。

## 一、为什么要分成两个 controller

在环境初始化时，`DesktopEnv` 会创建两个控制器：

- [desktop_env/desktop_env.py:212](../../desktop_env/desktop_env.py#L212)
- [desktop_env/desktop_env.py:213](../../desktop_env/desktop_env.py#L213)

分别是：

- `PythonController`
- `SetupController`

### 1. `PythonController`

对应文件：

- [desktop_env/controllers/python.py](../../desktop_env/controllers/python.py)

它偏向“运行时交互”。

它主要负责：

- 拿 screenshot
- 拿 accessibility tree
- 拿 terminal 输出
- 从 VM 下载文件
- 执行 Python / bash / 结构化 action

你可以把它理解成：

- Agent 与环境主循环用的实时控制通道

### 2. `SetupController`

对应文件：

- [desktop_env/controllers/setup.py](../../desktop_env/controllers/setup.py)

它偏向“任务前后准备”。

它主要负责：

- 下载文件到 VM
- 上传本地文件到 VM
- 启动应用
- 打开文件
- 激活窗口
- 执行初始化命令
- 处理 postconfig

你可以把它理解成：

- benchmark 任务 scaffolding 通道

## 二、`PythonController` 这一层到底做了什么

第一次阅读建议重点看这些方法：

- [python.py:42](../../desktop_env/controllers/python.py#L42) `get_screenshot()`
- [python.py:70](../../desktop_env/controllers/python.py#L70) `get_accessibility_tree()`
- [python.py:92](../../desktop_env/controllers/python.py#L92) `get_terminal_output()`
- [python.py:114](../../desktop_env/controllers/python.py#L114) `get_file()`
- [python.py:136](../../desktop_env/controllers/python.py#L136) `execute_python_command()`
- [python.py:241](../../desktop_env/controllers/python.py#L241) `execute_action()`

### 1. 它本质上是一个 HTTP 客户端

例如：

- `/screenshot`
- `/accessibility`
- `/terminal`
- `/file`
- `/execute`

这些都不是本地函数调用，而是 HTTP 请求。

举个最直接的例子：

- [python.py:49](../../desktop_env/controllers/python.py#L49)

这里是：

```python
requests.get(self.http_server + "/screenshot")
```

这说明 `get_screenshot()` 真正做的事是：

- 去 guest 里的 server 拿当前屏幕图像

### 2. 为什么 `execute_python_command()` 很重要

对应：

- [python.py:136](../../desktop_env/controllers/python.py#L136)

这个函数是 `pyautogui` action space 落地的关键。

它会把一段 Python 命令包装成：

```python
["python", "-c", "..."]
```

然后 POST 到：

- `/execute`

所以在 `pyautogui` 模式下，环境并不是在宿主机执行鼠标点击，而是在 guest 内部执行。

### 3. `execute_action()` 和 `execute_python_command()` 的关系

如果 action 是：

- 结构化动作字典

那会走：

- [python.py:241](../../desktop_env/controllers/python.py#L241) `execute_action()`

它会把诸如：

- `CLICK`
- `MOVE_TO`
- `DOUBLE_CLICK`
- `DRAG_TO`

这些高层动作翻译成真正的 `pyautogui` Python 命令，再交给 `execute_python_command()`。

所以：

- `execute_action()` 是动作翻译器
- `execute_python_command()` 是命令发送器

## 三、`SetupController` 这一层到底做了什么

第一次阅读建议先看：

- [setup.py:57](../../desktop_env/controllers/setup.py#L57) `setup(...)`

这是整个 setup 层的入口。

### 1. `setup(config)` 的核心模型

`config` 是一个列表，每个元素长这样：

```python
{
    "type": "...",
    "parameters": {...}
}
```

`SetupController.setup(...)` 会把它转换成：

```python
_<type>_setup(**parameters)
```

对应逻辑：

- [setup.py:86](../../desktop_env/controllers/setup.py#L86)
- [setup.py:92](../../desktop_env/controllers/setup.py#L92)

这意味着任务 JSON 里的：

- `download`
- `launch`
- `open`
- `sleep`
- `execute`
- `activate_window`

本质上都会映射成某个 `_xxx_setup()` 方法。

### 2. 最常见的几个 setup 方法

最值得先记住这些：

- [setup.py:108](../../desktop_env/controllers/setup.py#L108) `_download_setup`
- [setup.py:187](../../desktop_env/controllers/setup.py#L187) `_upload_file_setup`
- [setup.py:280](../../desktop_env/controllers/setup.py#L280) `_open_setup`
- [setup.py:300](../../desktop_env/controllers/setup.py#L300) `_launch_setup`
- [setup.py:324](../../desktop_env/controllers/setup.py#L324) `_execute_setup`
- [setup.py:457](../../desktop_env/controllers/setup.py#L457) `_sleep_setup`
- [setup.py:473](../../desktop_env/controllers/setup.py#L473) `_activate_window_setup`
- [setup.py:492](../../desktop_env/controllers/setup.py#L492) `_close_window_setup`

这几个基本覆盖了绝大多数 benchmark 任务的初始化和收尾动作。

### 3. 为什么 `SetupController` 要先探活 `/terminal`

在 `setup(...)` 一开始，它会先反复请求：

- [setup.py:71](../../desktop_env/controllers/setup.py#L71)

也就是：

```python
requests.get(self.http_server + "/terminal")
```

这不是为了拿 terminal 内容，而是为了确认：

- guest 内部 server 已经起来了
- HTTP 通道是通的

所以 `/terminal` 在这里兼任了“探活接口”。

## 四、guest 里到底跑了什么 server

对应文件：

- [desktop_env/server/main.py](../../desktop_env/server/main.py)

这个文件本质上是 guest 内部的 Flask 服务端。

你可以把它理解成：

- 控制器的对端

Controller 发什么请求，这个 server 就接什么请求。

## 五、先看 server 暴露了哪些关键路由

最值得优先记住的接口有：

### 运行时交互相关

- [server/main.py:76](../../desktop_env/server/main.py#L76) `/execute`
- [server/main.py:263](../../desktop_env/server/main.py#L263) `/screenshot`
- [server/main.py:347](../../desktop_env/server/main.py#L347) `/terminal`
- [server/main.py:902](../../desktop_env/server/main.py#L902) `/accessibility`
- [server/main.py:1129](../../desktop_env/server/main.py#L1129) `/file`
- [server/main.py:1494](../../desktop_env/server/main.py#L1494) `/start_recording`
- [server/main.py:1536](../../desktop_env/server/main.py#L1536) `/end_recording`
- [server/main.py:1571](../../desktop_env/server/main.py#L1571) `/run_python`
- [server/main.py:1666](../../desktop_env/server/main.py#L1666) `/run_bash_script`

### setup 相关

- [server/main.py:239](../../desktop_env/server/main.py#L239) `/setup/launch`
- [server/main.py:1155](../../desktop_env/server/main.py#L1155) `/setup/upload`
- [server/main.py:1198](../../desktop_env/server/main.py#L1198) `/setup/change_wallpaper`
- [server/main.py:1228](../../desktop_env/server/main.py#L1228) `/setup/download_file`
- [server/main.py:1285](../../desktop_env/server/main.py#L1285) `/setup/open_file`
- [server/main.py:1379](../../desktop_env/server/main.py#L1379) `/setup/activate_window`
- [server/main.py:1448](../../desktop_env/server/main.py#L1448) `/setup/close_window`

## 六、几个最关键的 server 路由怎么理解

### 1. `/execute`

对应：

- [server/main.py:76](../../desktop_env/server/main.py#L76)

它的职责非常直接：

- 在 guest 内执行一条命令
- 返回 stdout / stderr / returncode

所以：

- `PythonController.execute_python_command()`
- `get_vm_command_line()`

这类逻辑最终都会走到这里。

### 2. `/screenshot`

对应：

- [server/main.py:263](../../desktop_env/server/main.py#L263)

它负责在 guest 内截当前屏幕，并返回 PNG。

这个接口是 observation 的核心来源之一。

你在不同平台上会看到不同实现：

- Windows
- Linux
- macOS

但对上层 controller 来说，它们都统一表现成：

- 一个图片接口

### 3. `/terminal`

对应：

- [server/main.py:347](../../desktop_env/server/main.py#L347)

它目前更偏 Linux / GNOME 场景。

实现思路不是读取 shell 历史，而是：

- 通过 accessibility tree 找当前活跃的 terminal widget
- 再拿出文本内容

这解释了为什么 terminal 输出也能被当作 observation 或探活信号。

### 4. `/accessibility`

对应：

- [server/main.py:902](../../desktop_env/server/main.py#L902)

这是另一个 observation 核心来源。

它会在 guest 内采集 accessibility tree，并返回 XML/文本结构。

为什么这个实现这么重？

因为它要兼容：

- Linux AT-SPI
- Windows pywinauto
- macOS Accessibility API

所以你会在这个文件里看到非常长的平台分支和 tree 构造代码。

### 5. `/file`

对应：

- [server/main.py:1129](../../desktop_env/server/main.py#L1129)

它负责把 guest 内某个路径下的文件读出来，发回宿主机。

这就是：

- `get_vm_file(...)`
- `PythonController.get_file(...)`

能工作的根基。

## 七、为什么 accessibility 逻辑这么重

`server/main.py` 里最大的一段复杂度，不是命令执行，不是截图，而是 accessibility tree 构造。

例如：

- [server/main.py:423](../../desktop_env/server/main.py#L423) `_create_atspi_node`
- [server/main.py:579](../../desktop_env/server/main.py#L579) `_create_pywinauto_node`
- [server/main.py:744](../../desktop_env/server/main.py#L744) `_create_axui_node`

它的核心目标是：

- 把平台原生 accessibility 对象树
- 统一映射成结构相近的 XML 树

这样上层 Agent 和 evaluator 才能用统一逻辑消费它。

这也是为什么：

- accessibility tree 是这个项目里最“平台适配味”最重的部分之一

## 八、`SetupController` 和 `/setup/*` 是怎样一一对应的

这层映射关系特别值得记住。

例如：

- `_launch_setup()` -> `/setup/launch`
- `_open_setup()` -> `/setup/open_file`
- `_activate_window_setup()` -> `/setup/activate_window`
- `_close_window_setup()` -> `/setup/close_window`
- `_download_setup()` / `_upload_file_setup()` -> `/setup/upload`

所以你可以把 `SetupController` 理解成：

- 一个把任务 JSON setup 语义翻译成 HTTP 路由调用的适配层

## 九、把一次动作和一次 setup 分开看

这是理解这一层最重要的边界。

### 运行时 action

例如：

```python
pyautogui.click(...)
```

典型路径是：

1. Agent 生成动作
2. `env.step(action)`
3. `PythonController.execute_python_command(...)`
4. `/execute`
5. guest 内执行 Python 命令

### setup 动作

例如：

```json
{"type": "launch", "parameters": {...}}
```

典型路径是：

1. `env.reset(task_config)`
2. `SetupController.setup(config)`
3. `_launch_setup(...)`
4. `/setup/launch`
5. guest 内启动应用

这两条链看起来都在“控制 guest”，但它们的语义完全不同：

- action 是 Agent 主动决策的一部分
- setup 是 benchmark scaffolding

## 十、为什么 `DesktopEnv` 不直接 import server 函数

这是一个很值得理解的架构点。

`DesktopEnv`、controller 和 guest server 分离，意味着：

- 宿主机和 guest 是明确隔开的
- guest 逻辑可以独立运行
- provider 可以切换 VM / Docker / cloud

如果 `DesktopEnv` 直接 import server 里的函数，这个边界就会被打破。

所以虽然 HTTP 看起来有些笨，但它保住了架构上的清晰隔离。

## 十一、这一层最值得你自己动手看的 4 个点

### 实验 1：把 controller 当纯 HTTP 客户端读

先只读：

- [python.py](../../desktop_env/controllers/python.py)

不要想 benchmark，不要想 Agent，只把它当作：

- “一个请求封装器”

你会突然发现代码容易很多。

### 实验 2：从一个 setup 类型倒推到 server

例如拿：

- `launch`

顺着看：

1. JSON config
2. `_launch_setup()`
3. `/setup/launch`
4. guest 端 `subprocess.Popen(...)`

这样你会对“配置驱动初始化”理解更扎实。

### 实验 3：追一次 screenshot 链

从：

- `env._get_obs()`

一路追到：

- `PythonController.get_screenshot()`
- `/screenshot`

你会对 observation 来源非常清楚。

### 实验 4：追一次 file getter 链

从：

- `get_vm_file(...)`

一路追到：

- `PythonController.get_file()`
- `/file`

你会对 evaluator 为何能读取 guest 文件更清楚。

## 十二、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，说明这一层已经过关：

1. 为什么要把 controller 分成 `PythonController` 和 `SetupController`？
2. `/execute` 和 `/setup/launch` 的语义区别是什么？
3. screenshot、accessibility tree、terminal 输出分别从哪里来？
4. 为什么 accessibility tree 的 server 端实现特别复杂？
5. 为什么 `SetupController.setup()` 可以通过字符串 `type` 动态调 `_xxx_setup()`？
6. 为什么这个项目选择用 HTTP 而不是直接本地调用 guest 逻辑？

## 十三、下一步该读什么

如果继续沿“非 agent 深入”的方向走，接下来最自然的是：

1. `providers`
   去看 VMware / Docker / AWS / Azure 这些运行底座的差异
2. `evaluation_examples`
   去看 benchmark 任务设计是如何组织的

如果你问我现在更推荐哪个：

我建议先看 `providers`。

因为到这一步，你已经知道 guest 里服务怎么工作了，再往外一层就是：

- 这台 guest 是怎么被启动、回滚、拿 IP、管理生命周期的
