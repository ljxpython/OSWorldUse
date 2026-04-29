# CUAAdapterAgent 伪代码与接口草案

日期：2026-04-27

## 1. 文档目的

这份文档是上一份方案文档的继续，目标是把 `CUA` 接入官方 `OSWorld` 的第一阶段方案，进一步细化成：

- 具体文件布局建议
- `CUAAdapterAgent` 的类接口草案
- `run_multienv_cua.py` 的 runner 草案
- `lib_run_single.run_single_example_cua()` 的执行草案
- `CUA action -> OSWorld action` 的翻译草案

这份文档不直接改代码，但会尽量贴近当前 `OSWorld` 仓库已有实现风格。

---

## 2. 第一阶段实现目标

第一阶段只解决一个问题：

> 让 `CUA` 在**官方 OSWorld** 上，以最小接入成本，作为一个可评测 agent 跑起来。

第一阶段不追求：

- 完整保留 `CUA runtime.run()`
- 保留 `CUA` 所有本机工具能力
- 支持 `shell_exec`
- 支持 `wait_for_user`
- 支持 Windows/macOS

第一阶段只追求：

- screenshot 驱动
- 单步决策
- `pyautogui` 动作输出
- 被 `OSWorld env.step()` 正确执行

---

## 3. 推荐新增文件

建议全部放在官方 `OSWorld` 仓库内。

```text
osworld/
  mm_agents/
    cua/
      __init__.py
      agent.py
      translator.py
      types.py
      prompts.py              # 如有需要
  scripts/
    python/
      run_multienv_cua.py
```

如果希望更保守，也可以先只加两个文件：

```text
mm_agents/cua/agent.py
scripts/python/run_multienv_cua.py
```

并把转换逻辑先内联在 `agent.py` 中。

但从可维护性看，推荐至少拆出：

- `agent.py`
- `translator.py`
- `types.py`

---

## 4. 第一阶段的分层设计

第一阶段建议分成三层。

## 4.1 CUA 推理层

职责：

- 接收 `instruction`
- 接收当前 `obs["screenshot"]`
- 拼装提示词和历史
- 调用 CUA 模型
- 返回“中间动作表示”

这一层尽量不感知 OSWorld。

## 4.2 Action 翻译层

职责：

- 将 CUA 中间动作表示翻译成 OSWorld 可执行动作
- 输出 `WAIT / DONE / FAIL / pyautogui字符串`

这一层是第一阶段最关键的适配层。

## 4.3 OSWorld Agent 包装层

职责：

- 暴露 `reset()`
- 暴露 `predict(instruction, obs, **kwargs)`
- 管理历史
- 调用推理层
- 调用翻译层

这一层对外表现得像 OSWorld 里的其他 agent。

---

## 5. 类型定义建议

建议在 `mm_agents/cua/types.py` 中先定义几个最小类型。

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

ActionKind = Literal[
    "click",
    "double_click",
    "move",
    "drag",
    "scroll",
    "type",
    "hotkey",
    "wait",
    "done",
    "fail",
]

@dataclass
class CUAAction:
    kind: ActionKind
    args: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    natural_language: str = ""

@dataclass
class CUAPredictInfo:
    raw_response: str
    natural_language_action: str
    parsed_action: Optional[CUAAction]
    debug: Dict[str, Any] = field(default_factory=dict)
```

这层不要过度设计。

第一阶段只需要保证：

- 能表示中间动作
- 能把调试信息留出来

---

## 6. `translator.py` 设计

## 6.1 目标

翻译层只做一件事：

> 把 `CUAAction` 翻译成 OSWorld 能执行的动作格式

第一阶段输出格式统一为：

- `WAIT`
- `DONE`
- `FAIL`
- `pyautogui` Python 字符串

## 6.2 建议接口

```python
class CUAActionTranslator:
    def __init__(self, platform: str = "ubuntu"):
        self.platform = platform

    def to_osworld_action(self, action: CUAAction) -> str:
        ...
```

如有需要，也可以拆成一组函数：

```python
def translate_action(action: CUAAction, platform: str = "ubuntu") -> str:
    ...
```

## 6.3 第一阶段翻译规则

### click

输入：

```python
CUAAction(kind="click", args={"x": 100, "y": 200, "button": "left"})
```

输出：

```python
import pyautogui
pyautogui.moveTo(100, 200)
pyautogui.click(button='left')
```

### double_click

输出：

```python
import pyautogui
pyautogui.moveTo(x, y)
pyautogui.doubleClick()
```

### move

输出：

```python
import pyautogui
pyautogui.moveTo(x, y)
```

### drag

输出：

```python
import pyautogui
pyautogui.moveTo(from_x, from_y)
pyautogui.dragTo(to_x, to_y, duration=0.5, button='left')
```

### scroll

输出：

```python
import pyautogui
pyautogui.scroll(amount)
```

### type

第一阶段建议直接用：

```python
import pyautogui
pyautogui.typewrite("text")
```

注意：

- 文本内容必须经过 `repr()` 或等价转义
- 第一阶段尽量优先跑英文/ASCII 任务

### hotkey

输出：

```python
import pyautogui
pyautogui.hotkey('ctrl', 'l')
```

### wait

输出：

- 直接返回 `WAIT`
- 或者返回 `import time; time.sleep(x)`

建议第一阶段统一返回 `WAIT`，保持和 OSWorld 的终止型动作语义一致。

### done / fail

直接翻译成：

- `DONE`
- `FAIL`

---

## 7. `agent.py` 设计

## 7.1 角色

`CUAAdapterAgent` 是第一阶段真正对接 OSWorld 的类。

它不应该：

- 直接执行宿主机工具
- 直接启动完整 `CUA runtime.run()`

它应该：

- 维护 CUA 所需历史
- 基于 screenshot 做单步决策
- 产出 OSWorld 可执行动作

## 7.2 建议类接口

```python
class CUAAdapterAgent:
    def __init__(
        self,
        model: str,
        max_tokens: int = 1500,
        top_p: float = 0.9,
        temperature: float = 0.0,
        action_space: str = "pyautogui",
        observation_type: str = "screenshot",
        max_trajectory_length: int = 3,
        screen_size: tuple[int, int] = (1920, 1080),
        client_password: str = "password",
        **kwargs,
    ):
        ...

    def reset(self, _logger=None, **kwargs):
        ...

    def predict(self, instruction: str, obs: dict, **kwargs):
        ...
```

## 7.3 内部状态建议

```python
self.logger
self.model
self.max_tokens
self.top_p
self.temperature
self.screen_size
self.client_password

self.observations = []
self.actions = []
self.raw_responses = []
self.debug_infos = []
```

不要一开始把状态做得太复杂。

第一阶段只保留：

- 最近几步 screenshot
- 最近几步动作
- 最近几步原始模型输出

---

## 7.4 `reset()` 伪代码

```python
def reset(self, _logger=None, **kwargs):
    if _logger is not None:
        self.logger = _logger
    else:
        self.logger = logging.getLogger("desktopenv.agent")

    self.observations = []
    self.actions = []
    self.raw_responses = []
    self.debug_infos = []
```

第一阶段不需要在 `reset()` 中做：

- VM 绑定
- screenshot 获取
- shell 初始化

这些都由 OSWorld 管。

---

## 7.5 `predict()` 伪代码

```python
def predict(self, instruction: str, obs: dict, **kwargs):
    screenshot = obs["screenshot"]

    # 1. 构造当前 step 的消息
    messages = self._build_messages(
        instruction=instruction,
        screenshot=screenshot,
        history_actions=self.actions,
        history_observations=self.observations,
        history_responses=self.raw_responses,
    )

    # 2. 调用 CUA 模型或 CUA 的单步决策接口
    raw_response = self._call_cua(messages)

    # 3. 解析成中间动作表示
    cua_action, natural_language, debug_info = self._parse_cua_response(raw_response)

    # 4. 翻译成 OSWorld action
    osworld_action = self.translator.to_osworld_action(cua_action)

    # 5. 写历史
    self.observations.append(obs)
    self.actions.append(natural_language)
    self.raw_responses.append(raw_response)
    self.debug_infos.append(debug_info)

    # 6. 组织返回值
    response = raw_response
    actions = [osworld_action]
    info_dict = {
        "action": natural_language,
        "parsed_action": cua_action.kind if cua_action else None,
        "debug": debug_info,
    }
    return response, actions, info_dict
```

---

## 8. `run_multienv_cua.py` 设计

## 8.1 角色

它的角色不是做智能逻辑，而是：

- 读取参数
- 初始化 env
- 初始化 `CUAAdapterAgent`
- 任务分发
- 调用 `lib_run_single.run_single_example_cua()`

## 8.2 最简单策略

建议直接复制 `run_multienv_opencua.py` 的骨架，再做最小修改。

不建议从零新写。

## 8.3 核心差异点

和 `run_multienv_opencua.py` 相比，第一阶段的 `run_multienv_cua.py` 有两个差异：

1. 不需要 `agent.env = env`
2. 不需要 agent 自带 `step()`

它更接近：

- runner 管环境
- runner 调 `predict()`
- OSWorld 执行 `env.step()`

---

## 8.4 `run_env_tasks()` 伪代码

```python
def run_env_tasks(task_queue, args, shared_scores):
    env = DesktopEnv(...)
    agent = CUAAdapterAgent(
        model=args.model,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        temperature=args.temperature,
        action_space=args.action_space,
        observation_type=args.observation_type,
        max_trajectory_length=args.max_trajectory_length,
        client_password=args.client_password,
        screen_size=(args.screen_width, args.screen_height),
    )

    while True:
        item = task_queue.get(...)
        domain, example_id = item
        example = load_example(...)
        example_result_dir = ...
        lib_run_single.run_single_example_cua(
            agent,
            env,
            example,
            args.max_steps,
            example["instruction"],
            args,
            example_result_dir,
            shared_scores,
        )
```

---

## 9. `run_single_example_cua()` 设计

## 9.1 角色

第一阶段建议新增一个和 `run_single_example_opencua()` 平行的函数：

```python
def run_single_example_cua(...):
    ...
```

虽然它和通用 `run_single_example()` 很像，但建议单独加出来，原因是：

- 便于后续第二阶段扩展
- 便于单独加调试信息
- 便于日后接入 `OSWorldToolAdapter`

## 9.2 建议实现

第一阶段尽量和通用版本保持一致。

```python
def run_single_example_cua(agent, env, example, max_steps, instruction, args, example_result_dir, scores):
    runtime_logger = setup_logger(example, example_result_dir)

    env.reset(task_config=example)
    agent.reset(runtime_logger)

    time.sleep(60)
    obs = env._get_obs()
    done = False
    step_idx = 0
    env.controller.start_recording()

    while not done and step_idx < max_steps:
        response, actions, info_dict = agent.predict(
            instruction,
            obs,
            step_idx=step_idx,
        )

        if not actions:
            break

        for action in actions:
            action_timestamp = ...
            obs, reward, done, info = env.step(action, args.sleep_after_execution)
            save_step_artifacts(...)
            if done:
                break
        step_idx += 1

    time.sleep(20)
    result = env.evaluate()
    write_result(...)
    env.controller.end_recording(...)
```

---

## 10. 第一阶段不建议直接使用 `agent.step()`

虽然 OSWorld 已经支持有些 agent 自带 `step()`，但我仍然不建议在第一阶段给 `CUA` 走这条路径。

原因：

1. 当前 `CUA` 本身就已经是完整 runtime
2. 如果太早让它接管 `step()`，很容易把 benchmark 责任边界打乱
3. 第一阶段的核心目标是 benchmark 接入验证，而不是完整保留 CUA 原生执行链

所以第一阶段优先做：

- `predict -> env.step`

第二阶段再考虑：

- `predict -> tool backend -> VM`

---

## 11. 第二阶段的接口扩展草案

当第一阶段跑稳之后，再引入第二阶段。

## 11.1 `OSWorldToolAdapter` 接口草案

```python
class OSWorldToolAdapter:
    def __init__(self, env):
        self.env = env
        self.controller = env.controller

    def get_screenshot(self) -> bytes:
        return self.controller.get_screenshot()

    def get_accessibility_tree(self) -> str | None:
        return self.controller.get_accessibility_tree()

    def execute_python(self, command: str):
        return self.controller.execute_python_command(command)

    def run_bash(self, script: str, timeout: int = 30):
        return self.controller.run_bash_script(script, timeout=timeout)
```

## 11.2 CUA 工具后端切换草案

建议让 `CUA` 的工具后端支持两个模式：

- `local`
- `osworld_vm`

伪代码：

```python
class ToolBackendMode(str, Enum):
    LOCAL = "local"
    OSWORLD_VM = "osworld_vm"
```

这样：

- 本地调试仍可用
- benchmark 模式下强制打到 VM

---

## 12. 第一阶段的能力验收标准

以下条件全部满足，才算第一阶段可交付：

1. 新增 `run_multienv_cua.py`
2. 新增 `CUAAdapterAgent`
3. 新增 `run_single_example_cua()`
4. 能在 Ubuntu OSWorld benchmark 上跑通至少 3 个 smoke tasks
5. 结果目录包含：
   - `traj.jsonl`
   - step screenshots
   - `result.txt`
   - `recording.mp4`
6. 评测过程中不调用宿主机 screenshot/mouse/shell

---

## 13. 我建议的下一步代码实现顺序

按代码落地时，建议严格按下面顺序做：

1. 新建 `mm_agents/cua/agent.py`
2. 在 `agent.py` 中只实现单步 `predict()`
3. 内联最小 translator，先不拆文件
4. 新建 `scripts/python/run_multienv_cua.py`
5. 在 `lib_run_single.py` 增加 `run_single_example_cua()`
6. 先跑 1 个 task
7. 再跑 3 个 smoke tasks
8. 稳定后再把 translator 独立成 `translator.py`
9. 最后才开始写 `OSWorldToolAdapter`

---

## 14. 最终结论

如果按照官方 OSWorld 现有架构来落地，最合理的第一阶段实现不是：

- 零适配直接吞下 `CUA`

而是：

- 在 OSWorld 侧新增 `CUAAdapterAgent`
- 沿用官方已有的“专用 runner + 专用 episode”模式
- 先用 `predict -> env.step` 跑通 benchmark
- 再在第二阶段恢复 `CUA` 的工具 runtime，并把后端切到 OSWorld VM

这条路线是当前最稳妥、证据最充分、工程上最容易收敛的方案。
