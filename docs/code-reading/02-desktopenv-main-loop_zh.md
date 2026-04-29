# 02 DesktopEnv 主循环解读

这一篇专门讲 `DesktopEnv` 的主循环。

如果说 [01 Quickstart 运行与 PyCharm 上手](./01-quickstart-run-and-pycharm_zh.md) 解决的是“怎么跑起来”，那这一篇解决的是：

- `DesktopEnv` 到底做了什么
- 为什么它看起来像一个 Gym 环境，但实际上包了很多外部系统逻辑
- 一个任务是如何从 `task_config` 变成实际桌面操作和最终评分的

## 先记住一条运行主线

围绕 `DesktopEnv`，你最应该先记住的是这条链：

`DesktopEnv(...) -> reset(task_config) -> _get_obs() -> step(action) -> evaluate() -> close()`

对照 [quickstart.py](../../quickstart.py)，这条链对应的是：

1. 构造 `DesktopEnv`
2. `env.reset(task_config=example)`
3. `env.step("pyautogui.rightClick()")`
4. `env.close()`

注意一个很关键的点：

`DesktopEnv(...)` 本身就有副作用，它不是“纯构造对象”。

它在构造阶段就可能：

- 自动找 VM
- 自动下载镜像
- 启动虚拟机
- 等待 guest IP
- 创建控制器

这也是为什么你之前会看到“脚本一运行就卡住”，但还没走到 `print("Starting OSWorld environment...")`。

## 从 quickstart 看入口

建议先把 [quickstart.py](../../quickstart.py) 和本篇一起看。

`quickstart.py` 的环境入口在：

- [quickstart.py:45](../../quickstart.py#L45)

这个调用会进入：

- [desktop_env/desktop_env.py:99](../../desktop_env/desktop_env.py#L99)

所以你在理解 `quickstart.py` 时，真正应该追进去看的不是脚本本身，而是 `DesktopEnv.__init__`。

## 一、`__init__` 做了什么

对应代码：

- [desktop_env/desktop_env.py:99](../../desktop_env/desktop_env.py#L99)

`__init__` 的职责可以概括成 5 件事：

1. 保存环境参数
2. 创建 provider 和 manager
3. 确定 VM 路径
4. 启动虚拟机并拿到 guest IP
5. 创建控制器

### 1. 参数层面

最值得先记住的参数有：

- `provider_name`
- `path_to_vm`
- `snapshot_name`
- `action_space`
- `headless`
- `require_a11y_tree`
- `require_terminal`
- `os_type`

这些参数里，最容易影响理解的是：

- `provider_name`
  决定环境跑在 VMware、Docker、AWS、Azure 等哪里。
- `path_to_vm`
  如果为空，环境会自己去找或下载 VM。
- `snapshot_name`
  默认是 `init_state`，后面 `reset()` 会依赖它做回滚。

### 2. provider 和 manager

创建 provider/manager 的入口在：

- [desktop_env/desktop_env.py:154](../../desktop_env/desktop_env.py#L154)

它调用的是：

- [desktop_env/providers/__init__.py:4](../../desktop_env/providers/__init__.py#L4)

这里要分清两个角色：

- `manager`
  更偏资源管理，负责“这台 VM 从哪里来、有没有空闲实例、要不要新建一个”。
- `provider`
  更偏运行操作，负责“启动 VM、停 VM、拿 IP、回滚快照”。

这是这个项目一个很重要的边界设计。

### 3. VM 路径是怎么确定的

如果你手动传了 `path_to_vm`：

- [desktop_env/desktop_env.py:169](../../desktop_env/desktop_env.py#L169)

它会直接用你给的路径。

如果你没有传：

- [desktop_env/desktop_env.py:173](../../desktop_env/desktop_env.py#L173)

它会调用 `self.manager.get_vm_path(...)`。

这也是第一次运行时会自动下载镜像的根源。

### 4. `_start_emulator()` 的职责

初始化尾段会调用：

- [desktop_env/desktop_env.py:183](../../desktop_env/desktop_env.py#L183)
- [desktop_env/desktop_env.py:198](../../desktop_env/desktop_env.py#L198)

`_start_emulator()` 主要干三件事：

1. `provider.start_emulator(...)`
2. `provider.get_ip_address(...)`
3. 创建 `PythonController` 和 `SetupController`

也就是说，`DesktopEnv` 一旦构造成功，默认就应该已经知道：

- guest 的 IP
- server 端口
- 怎么通过 HTTP 去拿 screenshot / accessibility tree / 执行动作

### 5. 两个控制器分别是什么

#### `PythonController`

对应代码：

- [desktop_env/controllers/python.py:14](../../desktop_env/controllers/python.py#L14)

它负责运行时交互，主要做这些事：

- `get_screenshot()`
- `get_accessibility_tree()`
- `get_terminal_output()`
- `execute_python_command()`
- `execute_action()`

它本质上是一个 HTTP 客户端，去请求 guest 内部的服务。

例如：

- 截图走 `/screenshot`
- 可访问性树走 `/accessibility`
- 执行 Python 命令走 `/execute`

这些可以直接在 [python.py:42](../../desktop_env/controllers/python.py#L42)、[python.py:70](../../desktop_env/controllers/python.py#L70)、[python.py:136](../../desktop_env/controllers/python.py#L136) 看出来。

#### `SetupController`

对应代码：

- [desktop_env/controllers/setup.py:40](../../desktop_env/controllers/setup.py#L40)

它负责任务开始前和评测前的“环境准备”。

比如：

- 下载文件进 VM
- 上传本地文件到 VM
- 启动应用
- 处理某些任务的预置状态

它最重要的方法是：

- [setup.py:57](../../desktop_env/controllers/setup.py#L57)

也就是 `setup(config, use_proxy=False)`。

## 二、`reset(task_config)` 做了什么

对应代码：

- [desktop_env/desktop_env.py:242](../../desktop_env/desktop_env.py#L242)

`reset()` 才是“切换到一个具体任务”的入口。

它的职责可以概括成：

1. 重置环境内部计数器
2. 决定要不要回滚快照
3. 读取任务配置
4. 调用 `SetupController` 执行任务预置
5. 返回第一帧 observation

### 1. 计数器重置

这部分在：

- [desktop_env/desktop_env.py:248](../../desktop_env/desktop_env.py#L248)

它会更新：

- `self._traj_no`
- `self._step_no`
- `self.action_history`

所以一次 `reset()` 就代表开始一个新的轨迹。

### 2. 为什么有时会回滚快照，有时不会

核心判断在：

- [desktop_env/desktop_env.py:267](../../desktop_env/desktop_env.py#L267)

如果 `self.is_environment_used` 为真，就会：

1. `revert_to_snapshot`
2. 再次 `_start_emulator()`

如果环境被认为还是“干净的”，就跳过快照回滚。

这个优化尤其是为了云 provider。

### 3. 任务信息是怎么装进环境的

这部分通过：

- [desktop_env/desktop_env.py:282](../../desktop_env/desktop_env.py#L282)
- [desktop_env/desktop_env.py:328](../../desktop_env/desktop_env.py#L328)

完成。

`_set_task_info()` 会把任务 JSON 里的内容拆进环境对象：

- `task_id`
- `cache_dir`
- `instruction`
- `config`
- `evaluator`

这里最重要的理解是：

环境不是硬编码每个 benchmark 任务，而是运行时把 JSON 任务配置“装载”进来。

### 4. `SetupController.setup(...)` 为什么重要

对应位置：

- [desktop_env/desktop_env.py:285](../../desktop_env/desktop_env.py#L285)
- [desktop_env/controllers/setup.py:57](../../desktop_env/controllers/setup.py#L57)

这一步会把任务里的 `config` 列表真正执行掉。

也就是：

- JSON 里写的 `launch`
- `download`
- `upload_file`
- 其他 setup 动作

会被解析成 `_launch_setup`、`_download_setup` 这类方法调用。

如果你想知道“任务 JSON 的 `config` 到底是怎么落地的”，这里就是主入口。

### 5. `reset()` 最后的返回值是什么

最后一段在：

- [desktop_env/desktop_env.py:303](../../desktop_env/desktop_env.py#L303)

它调用 `_get_obs()` 并直接返回 observation。

所以你可以把 `reset()` 理解成：

“把环境切到指定任务，并返回任务起始观测”

## 三、`_get_obs()` 返回什么

对应代码：

- [desktop_env/desktop_env.py:306](../../desktop_env/desktop_env.py#L306)

返回结构非常简单：

```python
{
    "screenshot": ...,
    "accessibility_tree": ...,
    "terminal": ...,
    "instruction": ...
}
```

实际字段是否有值，取决于环境初始化时的两个开关：

- `require_a11y_tree`
- `require_terminal`

### 每个字段从哪里来

- `screenshot`
  来自 `self.controller.get_screenshot()`
- `accessibility_tree`
  来自 `self.controller.get_accessibility_tree()`
- `terminal`
  来自 `self.controller.get_terminal_output()`
- `instruction`
  来自当前任务文本

这一步本质上是把 guest 内部 HTTP 服务包装成统一 observation。

## 四、`step(action)` 是怎么执行动作的

对应代码：

- [desktop_env/desktop_env.py:385](../../desktop_env/desktop_env.py#L385)

`step()` 做的事比标准 Gym 更简单一些：

- 它不真正计算 reward
- 它主要负责执行动作、返回最新 observation

### 1. 先更新内部状态

一进来就会：

- 步数加一
- 记录 `action_history`
- 把 `is_environment_used` 置为 `True`

这意味着后续再 `reset()` 时，环境会认为这台 VM 已经被污染过。

### 2. 特殊动作

这几个动作是内建控制信号：

- `WAIT`
- `FAIL`
- `DONE`

逻辑在：

- [desktop_env/desktop_env.py:397](../../desktop_env/desktop_env.py#L397)

它们的含义大致是：

- `WAIT`
  只等待，不做别的
- `FAIL`
  直接结束，并标记失败
- `DONE`
  直接结束，并标记完成

### 3. 两类 action space

当前最值得关注的是两种：

- `computer_13`
- `pyautogui`

对应逻辑在：

- [desktop_env/desktop_env.py:407](../../desktop_env/desktop_env.py#L407)

#### `computer_13`

这类动作会走：

- `self.controller.execute_action(action)`

也就是更结构化的动作表示。

#### `pyautogui`

这类动作通常是字符串形式的 Python 代码，例如：

```python
pyautogui.rightClick()
```

然后会走：

- [desktop_env/desktop_env.py:415](../../desktop_env/desktop_env.py#L415)
- [desktop_env/controllers/python.py:136](../../desktop_env/controllers/python.py#L136)

也就是把命令封装成：

```python
python -c "import pyautogui; import time; ..."
```

再通过 guest 内部 `/execute` 接口执行。

### 4. 为什么 `step()` 之后又会 `sleep`

对应：

- [desktop_env/desktop_env.py:424](../../desktop_env/desktop_env.py#L424)

这里的 `pause` 是很实用的设计。

因为很多桌面动作不是立即稳定的：

- 窗口切换
- 菜单展开
- 应用启动
- 页面跳转

如果不等一下，下一帧 observation 很可能还没反映刚才动作的结果。

### 5. 返回值长什么样

`step()` 返回：

```python
observation, reward, done, info
```

但这里要注意：

- `reward` 现在基本固定为 `0`
- `done` 很多时候只受 `WAIT/FAIL/DONE` 这类控制信号影响
- 真正的任务成败，不是靠 `step()` 判，而是靠 `evaluate()`

这是这个项目和强化学习环境最不一样的地方之一。

## 五、`evaluate()` 怎么判成功

对应代码：

- [desktop_env/desktop_env.py:429](../../desktop_env/desktop_env.py#L429)

这是 `DesktopEnv` 的另一个核心。

你可以把它理解成：

“把任务 JSON 里的 `evaluator` 解释成具体 getter + metric 调用”

### 1. 先执行 `postconfig`

一开始会先读：

- [desktop_env/desktop_env.py:434](../../desktop_env/desktop_env.py#L434)

也就是任务里的 `postconfig`。

这是评测前的额外准备动作。

例如：

- 关闭应用
- 重开应用
- 等待几秒

这样做通常是为了把 UI 状态整理成更适合读取评测结果的形式。

### 2. `FAIL` 的特殊处理

如果最后一个动作是 `FAIL`，很多任务会直接返回 0。

逻辑在：

- [desktop_env/desktop_env.py:440](../../desktop_env/desktop_env.py#L440)

这个判断很重要，因为它把 Agent 的“主动承认失败”映射到了评测结果里。

### 3. 单指标和多指标

`evaluate()` 支持两种模式：

- 单 metric
- 多 metric

对应逻辑分别在：

- [desktop_env/desktop_env.py:452](../../desktop_env/desktop_env.py#L452)
- [desktop_env/desktop_env.py:481](../../desktop_env/desktop_env.py#L481)

### 4. getter 和 metric 的关系

在 `_set_evaluator_info()` 里，环境已经把 evaluator 配置翻译成了这些对象：

- `self.result_getter`
- `self.expected_getter`
- `self.metric`

见：

- [desktop_env/desktop_env.py:338](../../desktop_env/desktop_env.py#L338)

所以评测时的逻辑其实就是：

1. 用 getter 取实际结果
2. 用 getter 取预期结果
3. 把两者喂给 metric

这就是为什么 JSON 任务里的 `evaluator` 能非常灵活。

## 六、把一整个任务串起来看

如果你把 `quickstart.py`、任务 JSON、`DesktopEnv` 放在一起看，一次任务大致是这样流动的：

1. 脚本构造 `DesktopEnv`
2. 环境选择 provider、找到 VM、启动 VM、拿到控制器
3. `reset(task_config)` 装载任务
4. `SetupController` 执行任务预置
5. `_get_obs()` 返回起始观测
6. `step(action)` 执行动作
7. `_get_obs()` 返回动作后的观测
8. `evaluate()` 用 getter + metric 判结果
9. `close()` 释放环境

如果你能把这 9 步在脑子里串起来，后面再读 Agent 代码就会轻松很多。

## 七、现在最值得你做的 4 个小实验

### 实验 1：打印 observation 结构

在 [quickstart.py](../../quickstart.py) 里临时加：

```python
print(obs.keys())
print(type(obs["screenshot"]), len(obs["screenshot"]))
```

目标是确认 `_get_obs()` 真正返回了什么。

### 实验 2：替换一个动作

把：

```python
env.step("pyautogui.rightClick()")
```

改成别的简单动作，例如点击或按键。

目标是理解 `pyautogui` 字符串是怎么流到 guest 里的。

### 实验 3：对照一个任务 JSON 看 `config`

拿一个真实任务 JSON，逐项对照 `reset()` 里如何调用 `SetupController.setup(...)`。

目标是理解 benchmark 任务不是死写在 Python 里的。

### 实验 4：单独看 `evaluate()`

选一个简单 evaluator，看看：

- `result` 的 getter 是什么
- `expected` 的 getter 是什么
- `metric` 是什么

目标是理解“成功”是怎么被算出来的。

## 八、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，说明 `DesktopEnv` 的第一轮理解已经过关：

1. 为什么构造 `DesktopEnv` 本身就可能很慢？
2. `reset()` 和 `_get_obs()` 的分工是什么？
3. 一个任务 JSON 是怎么被装进环境的？
4. `pyautogui` 动作是通过什么机制在 guest 内执行的？
5. 为什么 `step()` 不真正承担任务评分职责？
6. `evaluate()` 是怎么把 getter 和 metric 组合起来的？

## 九、下一步该读什么

如果你已经吃透这篇，建议下一篇去读 Agent 主线。

最自然的下一步是：

- `PromptAgent.__init__`
- `PromptAgent.predict`

也就是：

- [mm_agents/agent.py](../../mm_agents/agent.py)

因为到这一步，你已经知道环境如何提供 observation，接下来就该看 Agent 如何消费这些 observation 并产出 action。
