# CUA 接入 OSWorld 详细接口设计

日期：2026-04-27

## 1. 文档目的

这份文档给出一个基于 **官方 OSWorld 代码架构** 的、可落地的 `CUA` 接入方案。

目标不是继续讨论抽象方向，而是回答下面这些工程问题：

1. `OSWorld` 现在的代码架构到底是什么样
2. `OSWorld` 已经是如何接入不同 agent 的
3. `CUA` 接进来时，适配层应该放在哪一边
4. 需要新增哪些模块、接口和运行脚本
5. 第一阶段应该支持哪些能力，哪些能力延后

本方案默认：

- 第一阶段以 **官方 OSWorld** 为准
- 第一阶段只做 `Ubuntu + screenshot + pyautogui`
- 第一阶段尽量**不改 CUA 核心智能逻辑**
- 适配层优先放在 **OSWorld 侧**

---

## 2. OSWorld 的真实代码架构

为了避免“空口说方案”，这里先用代码结构来固定讨论边界。

## 2.1 OSWorld 的五层结构

从代码上看，官方 OSWorld 至少可以分成五层：

### 第一层：Runner 层

负责：

- 读取任务列表
- 创建环境
- 创建 agent
- 驱动整个 benchmark 执行

核心文件：

- `run.py`
- `scripts/python/run_multienv.py`
- `scripts/python/run_multienv_*.py`

说明：

- `run.py` 更偏单环境、基础运行方式
- `run_multienv.py` 和 `run_multienv_*.py` 是官方更常用的批量评测入口

### 第二层：Episode 执行层

负责单任务执行流程：

- `env.reset()`
- `agent.reset()`
- 循环 `predict()`
- 调用 `env.step(...)` 或 agent 自带 `step(...)`
- 调用 `env.evaluate()`
- 保存 `traj.jsonl`、截图、录屏、`result.txt`

核心文件：

- `lib_run_single.py`

关键点：

官方 `OSWorld` 并不是只支持一种统一 agent 形态。  
它已经存在多个专用的 `run_single_example_xxx()` 分支。

### 第三层：Environment 层

负责 benchmark 环境本体：

- VM provider 管理
- task setup
- observation 采集
- action 执行
- evaluator 调用

核心文件：

- `desktop_env/desktop_env.py`

这是 benchmark 的核心，不是 `mm_agents`。

### 第四层：VM RPC 控制层

OSWorld 不是直接在宿主机本地操作 GUI，而是：

- 宿主机上有 `PythonController`
- `PythonController` 通过 HTTP 请求控制 guest VM 内 server

核心文件：

- `desktop_env/controllers/python.py`
- `desktop_env/controllers/setup.py`
- `desktop_env/server/main.py`

这一层已经天然提供了“宿主机 agent 控制 VM”的执行模式。

### 第五层：Task / Evaluator 层

负责 benchmark 任务定义与评分：

- task json
- setup config
- evaluator config
- result getter
- metric

核心位置：

- `evaluation_examples/`
- `desktop_env/evaluators/`

---

## 2.2 OSWorld 的 observation contract

官方 `OSWorld` 在环境层提供的 observation 结构是统一的。

典型 observation 包含：

- `screenshot`
- `accessibility_tree`
- `terminal`
- `instruction`

这意味着所有 agent 接入最终都要面对这一层 contract，而不是绕开它。

---

## 2.3 OSWorld 的 action contract

官方 OSWorld 的环境执行层主要接受两类动作：

1. `pyautogui` 字符串
2. 特殊终止信号
   - `WAIT`
   - `DONE`
   - `FAIL`

这对 `CUA` 的接入非常关键，因为最终无论中间怎么设计，第一阶段最稳妥的方式还是把动作落成 OSWorld 能执行的动作格式。

---

## 3. OSWorld 已经如何接入不同 agent

这是整个方案中最关键的一部分。

如果官方 OSWorld 已经证明了某些接入模式可行，就不应该再凭空设计另一套完全不同的机制。

## 3.1 普通 PromptAgent 路线

最基础的接法是：

- agent 实现 `reset()`
- agent 实现 `predict(instruction, obs)`
- `predict()` 返回 `response, actions`
- runner 把 `actions` 直接喂给 `env.step()`

这类接法是最通用的基础模式。

## 3.2 OpenCUA 路线

官方仓库已经提供了 `OpenCUA` 接入。

它的特点是：

- 有自己专用的 runner
- 有自己专用的 `OpenCUAAgent`
- `predict()` 返回 `pyautogui_actions`
- 最终仍然把动作交给 `env.step()`

这个接法对我们非常重要，因为它说明：

- OSWorld 是愿意为 agent 单独写接入脚本的
- 外部 CUA 型 agent 完全可以通过**适配层**接进来
- “不是零适配”，但“不是重写 benchmark”

## 3.3 OpenAI CUA 路线

官方仓库还提供了 `OpenAICUAAgent` 这类接法。

这个接法进一步说明：

- 有些 agent 不止有 `predict()`
- 它们还会带 `step()` 和额外状态
- OSWorld 已经通过专用的 `run_single_example_xxx()` 来兼容这种差异

这意味着：

> OSWorld 不是只允许一种 agent 接口，而是允许通过 runner/adapter 做兼容。

---

## 4. 对 CUA 接入的核心判断

## 4.1 我们不应该坚持“零适配”

原因不是 CUA 不够通用，而是：

- OSWorld 统一的是 benchmark contract
- agent 自身内部协议本来就各不相同

所以“OSWorld 可以评各种 agent”不等于“完全不需要胶水层”。

更准确的理解应该是：

> OSWorld 通过 benchmark contract + 专用 runner + 专用 adapter 来接入不同 agent。

## 4.2 我们也不应该一开始就重改 CUA 核心逻辑

更合理的原则是：

- 尽量不动 `CUA` 的核心智能逻辑
- 优先在 OSWorld 侧增加 `adapter`
- 如果必须改 `CUA`，也尽量只改工具接缝和运行后端，而不是核心决策逻辑

---

## 5. 最终目标形态

我们已经明确，最终效果应该是：

- `CUA` 看到的是 benchmark VM 的截图
- `CUA` 发出的点击、拖拽、输入、命令作用在 benchmark VM
- 宿主机不应该被误操作

重要的是：

这并不要求把 `CUA` 整体安装进 VM 里。

更推荐的目标形态是：

```text
CUA runtime (host)
  -> adapter / backend
    -> OSWorld controller
      -> OSWorld VM server
        -> benchmark VM
```

这也是为什么本方案优先强调“OSWorld 侧适配”和“工具后端代理到 VM”。

---

## 6. 总体接入策略

## 6.1 第一阶段策略

第一阶段不追求保留 `CUA` 当前全部 runtime 特性。

第一阶段优先做：

- 把 `CUA` 适配成一个 OSWorld 能驱动的 agent
- 先让它在官方 benchmark 上跑通
- 先验证它的 benchmark 能力，而不是先保留它所有工具系统

### 第一阶段原则

- 优先复用 `predict -> env.step()` 模式
- 不直接运行 `CUA` 现有完整 `run()` 主循环
- 不先接 `shell_exec`
- 不先接 `wait_for_user`
- 不先接 records / brain / doneGate

## 6.2 第二阶段策略

第二阶段再逐步回收 `CUA` 自己的 runtime 能力：

- 保留 `CUA runtime`
- 但替换 `CUA` 的工具后端
- 让它们调用 OSWorld controller / VM server

也就是说：

- 第一阶段先做能力评测
- 第二阶段再做高保真 runtime 对接

---

## 7. 推荐方案：优先 OSWorld 侧适配

## 7.1 总体思路

优先在 OSWorld 仓库里新增：

1. `CUAAdapterAgent`
2. `run_multienv_cua.py`
3. `run_single_example_cua()`
4. 后续再加 `OSWorldToolAdapter`

### 为什么先这样做

因为这最符合官方已有模式：

- OpenCUA 就是专用 runner + 专用 agent
- OpenAI CUA 也是专用 runner + 专用 episode 分支

所以我们的路线不应该是“设计一套全新的 benchmark 接法”，而应该是：

> 沿着官方已经在用的接入模式，为 `CUA` 增加自己的适配器。

---

## 8. 需要新增的模块

以下建议全部放在官方 OSWorld 仓库内。

## 8.1 第一阶段新增模块

### 模块 A：`mm_agents/cua/agent.py`

职责：

- 作为 `CUAAdapterAgent`
- 包装外部 `CUA`
- 对外暴露 OSWorld 可调用的接口

最小接口：

- `reset(_logger=None, **kwargs)`
- `predict(instruction: str, obs: Dict, **kwargs)`

第一阶段的定位：

- 只负责单步决策
- 不负责真正执行本机工具

### 模块 B：`scripts/python/run_multienv_cua.py`

职责：

- 作为 `CUA` 的官方多环境评测入口
- 按照现有 `run_multienv_opencua.py` 风格组织环境和任务队列

它的责任不是实现 CUA 智能，而是：

- 初始化环境
- 初始化 `CUAAdapterAgent`
- 调用 `lib_run_single.run_single_example_cua()`

### 模块 C：`lib_run_single.py` 新增 `run_single_example_cua()`

职责：

- 复用官方单任务执行模式
- 如果 `CUA` 需要专用 episode 逻辑，则在这里落地

第一阶段建议：

- 先尽量贴近 `run_single_example_opencua()`
- 不引入 agent 自带 `step()`
- 保持 `env.step()` 仍由 OSWorld 执行

---

## 8.2 第二阶段新增模块

### 模块 D：`mm_agents/cua/osworld_tool_adapter.py`

职责：

- 将 `CUA` 的 screenshot/mouse/keyboard/shell 需求转成 OSWorld controller 能理解的调用

### 模块 E：`mm_agents/cua/backends/`

建议拆成多个 backend：

- `screenshot_backend.py`
- `mouse_backend.py`
- `keyboard_backend.py`
- `shell_backend.py`

这样可以逐个替换，而不是一次性重写整套工具链。

---

## 9. 第一阶段接口设计

## 9.1 `CUAAdapterAgent` 接口

建议接口如下：

```python
class CUAAdapterAgent:
    def __init__(self, ...):
        ...

    def reset(self, _logger=None, **kwargs):
        ...

    def predict(self, instruction: str, obs: dict, **kwargs):
        ...
```

### `reset()`

职责：

- 重置内部历史
- 绑定 logger
- 初始化 `CUA` 的单步决策上下文

不做：

- 不截图
- 不执行 GUI 动作
- 不调用 benchmark env

### `predict()`

输入：

- `instruction`
- `obs`
- 可选 `step_idx`

输出建议保持 OSWorld 现有约定：

```python
response, actions, info_dict
```

其中：

- `response`：原始模型输出或调试文本
- `actions`：OSWorld 可直接执行的 action 列表
- `info_dict`：自然语言动作摘要、解析中间结果、调试信息

---

## 9.2 第一阶段动作输出协议

第一阶段建议把 `CUA` 的动作统一编译成：

- `WAIT`
- `DONE`
- `FAIL`
- `pyautogui` 字符串

不要在第一阶段输出一个全新的结构化 action schema。

原因：

- OSWorld 环境层原生就支持这些
- 可最大限度减少 benchmark 侧改动
- 冒烟验证最快

---

## 9.3 第一阶段 observation 协议

第一阶段只使用：

- `obs["screenshot"]`

不依赖：

- `accessibility_tree`
- `terminal`

原因：

- 当前 `CUA` 最自然的工作方式就是基于 screenshot
- 先减少接入变量

---

## 10. 第一阶段能力边界

## 10.1 先支持的能力

建议第一阶段只支持：

- screenshot
- mouse_click
- mouse_double_click
- mouse_move
- mouse_drag
- type
- hotkey
- scroll
- wait
- done
- fail

## 10.2 先不支持的能力

建议第一阶段暂不支持：

- `shell_exec`
- `wait_for_user`
- `records`
- `brain`
- `doneGate`
- `officecli`
- 本机文件系统副作用能力

原因：

- 这些能力一旦处理不好，很容易把副作用打到宿主机
- 它们对“先验证 benchmark 接入是否正确”不是必需项

---

## 11. 第二阶段接口设计

当第一阶段稳定后，进入第二阶段。

## 11.1 第二阶段核心变化

第二阶段不再满足于“把动作编译成 pyautogui 字符串”，而是逐步恢复 `CUA` 自己的工具系统。

但这些工具不再直连宿主机，而是接入 OSWorld 的 VM 控制接口。

## 11.2 `OSWorldToolAdapter` 建议接口

```python
class OSWorldToolAdapter:
    def __init__(self, env):
        self.env = env
        self.controller = env.controller

    def get_screenshot(self) -> bytes:
        ...

    def mouse_click(self, x, y, button="left"):
        ...

    def mouse_double_click(self, x, y):
        ...

    def mouse_move(self, x, y):
        ...

    def mouse_drag(self, from_x, from_y, to_x, to_y):
        ...

    def key_press(self, keys):
        ...

    def type_text(self, text):
        ...

    def run_bash(self, script, timeout=30):
        ...
```

---

## 11.3 每类能力如何映射

### screenshot

优先来源：

- `env.controller.get_screenshot()`

### GUI 动作

通过：

- `env.controller.execute_python_command(...)`

把动作翻译成 VM 内 `pyautogui` 命令。

### shell

通过：

- `env.controller.run_bash_script(...)`

在 VM 内运行命令，而不是宿主机 `spawn`。

### 终止信号

仍然映射为：

- `DONE`
- `FAIL`
- `WAIT`

---

## 12. 实现阶段划分

## 阶段 A：Benchmark 接入验证

目标：

- 跑通官方 OSWorld
- 不改 CUA 核心逻辑
- 不保留完整 CUA tool runtime

交付物：

- `mm_agents/cua/agent.py`
- `scripts/python/run_multienv_cua.py`
- `lib_run_single.py` 中的 `run_single_example_cua()`

## 阶段 B：Tool backend 代理到 VM

目标：

- 保留 `CUA runtime`
- 工具调用全部走 VM
- 宿主机不再承受副作用

交付物：

- `osworld_tool_adapter.py`
- 各 backend 文件

## 阶段 C：恢复更多 CUA 原生能力

目标：

- `shell_exec`
- 更复杂的历史管理
- 更复杂的中间状态
- 可能的 office/workflow 特化能力

---

## 13. 我建议的实际落地顺序

1. 在 OSWorld 仓库里创建 `mm_agents/cua/`
2. 新建 `CUAAdapterAgent`
3. 新建 `run_multienv_cua.py`
4. 在 `lib_run_single.py` 增加 `run_single_example_cua()`
5. 第一版只让 `predict()` 输出 `pyautogui` 字符串
6. 先跑 3 个 smoke tasks
7. 再做 `OSWorldToolAdapter`
8. 再逐步把 `CUA` 的 tool backend 接到 VM

---

## 14. 风险与规避

## 风险 1：误以为完全不需要适配

规避：

- 文档层明确承认需要 adapter
- 但 adapter 优先放在 OSWorld 侧，而不是改 CUA 核心

## 风险 2：shell 打到宿主机

规避：

- 第一阶段完全禁用 shell
- 第二阶段只允许通过 `controller.run_bash_script()` 执行

## 风险 3：截图来源错误

规避：

- 第一阶段 screenshot 只来自 `obs["screenshot"]`
- 第二阶段 screenshot 只来自 `controller.get_screenshot()`

## 风险 4：把阶段目标做混

规避：

- 第一阶段只做 benchmark 接入验证
- 第二阶段再保留 CUA 原生 runtime 能力

---

## 15. 最终结论

基于官方 OSWorld 现有代码架构，最合理的接入路线不是：

- 期待 OSWorld 零适配吞下任意 agent

也不是：

- 一开始就重改 CUA 核心逻辑

而是：

1. 承认 benchmark 接入需要 adapter
2. 优先沿用 OSWorld 官方已经在使用的“专用 runner + 专用 agent 包装”模式
3. 第一阶段先做 `CUAAdapterAgent`
4. 第二阶段再做 `OSWorldToolAdapter`
5. 最终实现 `CUA` 直接操作 benchmark VM，而不是操作宿主机

这条路线最符合：

- 官方 OSWorld 的代码结构
- 已有 `OpenCUA` / `OpenAI CUA` 接入方式
- 你对最终“直接操作 VM”效果的要求
