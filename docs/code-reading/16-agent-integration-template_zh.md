# 16 新 Agent 最小接入模板

这一篇接在 [15 从 mm_agents 理解 Agent 接入接口](./15-mm_agents-agent-interface_zh.md) 后面看最合适。

前一篇你已经知道：

- benchmark 对 agent 的最小契约是什么
- `PromptAgent` 哪些是协议，哪些只是默认实现
- 为什么有的 agent 能走标准 runner，有的必须走特例 runner

这一篇再往前走一步，直接回答：

- 如果我要接一个自己的 agent，第一版代码到底该怎么落？

## 先给一句结论

第一版最稳的接法，不是从零发明一套新流程，而是：

1. 新增一个最小 `MyAgent`
2. 复制一份 [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)
3. 只改 import、agent 初始化和少量参数
4. 继续复用 [lib_run_single.py](../../lib_run_single.py) 里的 `run_single_example(...)`

也就是说，你第一版应该优先适配现有 benchmark，而不是改 benchmark 去适配你。

## 一、第一版先故意收窄范围

如果你一开始就想同时支持：

- 多模型
- 多观测类型
- 多动作协议
- 多 domain
- 多 provider

基本上很快就会把问题搅在一起。

第一版建议只做下面这个目标：

- OS：`Ubuntu`
- provider：你现在已经能稳定跑起来的那一个
- observation：`screenshot`
- action space：`pyautogui`
- domain：`chrome`
- 并发：`1`

这个收敛非常重要，因为它会让你先验证“接入链路是否通”，而不是先陷入能力扩展。

## 二、第一版成功标准是什么

接入这类工作最好一开始就把成功标准写死。

建议把第一版成功标准定义成：

1. `scripts/python/run_multienv_myagent.py` 能正常启动环境
2. `agent.reset(...)` 能被标准 runner 正常调用
3. `agent.predict(...)` 能收到 `instruction` 和 `obs`
4. `actions` 能被 `env.step(...)` 正常执行
5. 结果目录里能看到 `traj.jsonl`、`result.txt`、步骤截图和 `recording.mp4`

只要这 5 条成立，你的最小接入就算成功了。

## 三、你应该新增哪两个文件

推荐第一版只新增这两个文件：

1. `mm_agents/my_agent.py`
2. `scripts/python/run_multienv_myagent.py`

其他层尽量先不动：

- 不改 `DesktopEnv`
- 不改 evaluator
- 不改任务 JSON 结构
- 不改 `lib_run_single.run_single_example(...)`

这是最小、最稳、也最容易回退的路径。

## 四、`mm_agents/my_agent.py` 的最小骨架

第一版最推荐直接对齐 `pyautogui + screenshot`。

原因很简单：

- `obs["screenshot"]` 一定会有
- `pyautogui` 是当前最容易接的动作格式之一
- [mm_agents/agent.py](../../mm_agents/agent.py) 里已经有现成 parser 可复用

最小骨架可以长这样：

```python
import logging
from typing import Dict, List, Tuple

from mm_agents.agent import parse_code_from_string

logger = logging.getLogger("desktopenv.agent")


class MyAgent:
    def __init__(
        self,
        model: str,
        max_tokens: int = 1500,
        top_p: float = 0.9,
        temperature: float = 0.0,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.reset()

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        global logger
        logger = _logger if _logger is not None else logging.getLogger("desktopenv.agent")
        self.vm_ip = vm_ip
        self.observations = []
        self.responses = []
        self.actions = []

    def _call_model(self, instruction: str, obs: Dict) -> str:
        # 这里替换成你自己的模型调用逻辑
        # 第一版哪怕先固定返回 "WAIT"，也能先验证接入链路
        return "WAIT"

    def predict(self, instruction: str, obs: Dict) -> Tuple[str, List]:
        self.observations.append(
            {
                "screenshot": obs.get("screenshot"),
                "accessibility_tree": obs.get("accessibility_tree"),
            }
        )

        response = self._call_model(instruction, obs)
        actions = parse_code_from_string(response)

        self.responses.append(response)
        self.actions.append(actions)

        logger.info("MyAgent response: %s", response)
        logger.info("MyAgent actions: %s", actions)

        return response, actions
```

这份骨架里，真正关键的只有三点：

1. `reset(...)` 签名兼容标准 runner
2. `predict(...)` 返回 `(response, actions)`
3. `actions` 是环境能执行的 `pyautogui` 格式

## 五、如果你想走 `computer_13`

如果你的模型更适合输出结构化动作，而不是 `pyautogui` 代码，那就把 parser 换成：

```python
from mm_agents.agent import parse_actions_from_string
```

然后把：

```python
actions = parse_code_from_string(response)
```

换成：

```python
actions = parse_actions_from_string(response)
```

这时候你输出的内容就要符合 [desktop_env/actions.py](../../desktop_env/actions.py) 里定义的动作 schema。

如果你只是想先把链路接通，还是建议优先从 `pyautogui` 开始。

## 六、`scripts/python/run_multienv_myagent.py` 不要从零写

第一版最实用的做法，是：

- 直接复制 [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)
- 命名为 `scripts/python/run_multienv_myagent.py`

然后只改少数几处。

### 1. 改 import

把：

```python
from mm_agents.agent import PromptAgent
```

换成：

```python
from mm_agents.my_agent import MyAgent
```

### 2. 改 agent 初始化

把：

```python
agent = PromptAgent(
    model=args.model,
    max_tokens=args.max_tokens,
    top_p=args.top_p,
    temperature=args.temperature,
    action_space=args.action_space,
    observation_type=args.observation_type,
    max_trajectory_length=args.max_trajectory_length,
    client_password=args.client_password
)
```

改成类似：

```python
agent = MyAgent(
    model=args.model,
    max_tokens=args.max_tokens,
    top_p=args.top_p,
    temperature=args.temperature,
)
```

第一版这里最好别把 `PromptAgent` 的所有初始化参数都照抄过去。

你只保留自己 agent 真正需要的参数就够了。

### 3. 保留标准 rollout

下面这段不要动：

```python
lib_run_single.run_single_example(
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

它正是你第一版想复用的标准主循环。

### 4. 环境构造也尽量别动

下面这类参数，第一版建议继续保持：

```python
env = DesktopEnv(
    path_to_vm=args.path_to_vm,
    action_space=args.action_space,
    provider_name=args.provider_name,
    screen_size=screen_size,
    headless=args.headless,
    os_type="Ubuntu",
    require_a11y_tree=args.observation_type in [
        "a11y_tree",
        "screenshot_a11y_tree",
        "som",
    ],
    enable_proxy=True,
    client_password=args.client_password,
)
```

因为这部分一旦一起改，问题会变成：

- 是 agent 接入错了
还是
- 是环境初始化就变了

第一版不要把两类问题混在一起。

## 七、参数层面，第一版最好只保留哪些

如果你自己写 `run_multienv_myagent.py`，建议第一版至少保留这些参数：

- `--path_to_vm`
- `--headless`
- `--provider_name`
- `--action_space`
- `--observation_type`
- `--model`
- `--temperature`
- `--top_p`
- `--max_tokens`
- `--domain`
- `--test_all_meta_path`
- `--result_dir`
- `--num_envs`
- `--screen_width`
- `--screen_height`
- `--client_password`

其中最关键的是这 4 个：

- `--provider_name`
- `--path_to_vm`
- `--action_space`
- `--observation_type`

因为它们直接决定环境怎么启动，以及 agent 输出和环境执行是否匹配。

## 八、第一版如何做 smoke test

最推荐的 smoke test，不是一下子跑完所有任务，而是先缩成一个 domain，甚至一个任务。

### 方案 1：先跑一个 domain

直接沿用总 meta 文件，但只跑 `chrome`：

```bash
uv run python scripts/python/run_multienv_myagent.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --domain chrome \
  --num_envs 1 \
  --model your-model-name \
  --result_dir ./results/myagent-smoke
```

这会跑 `chrome` 下的全部任务。

### 方案 2：先跑一个任务

如果你只想验证接入，不想一上来跑完整个 domain，可以准备一个临时 meta 文件，例如：

```json
{
  "chrome": [
    "bb5e4c0d-f964-439c-97b6-bdb9747de3f4"
  ]
}
```

然后执行：

```bash
uv run python scripts/python/run_multienv_myagent.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path evaluation_examples/test_one_chrome.json \
  --num_envs 1 \
  --model your-model-name \
  --result_dir ./results/myagent-one-task
```

对于接入验证，这个方式更好。

因为你要先证明：

- 环境能起来
- agent 能收观测
- action 能执行

而不是先追求 benchmark 分数。

## 九、跑完以后你应该看哪些文件

第一版接通后，最值得检查的是结果目录。

标准 runner 会在类似下面的位置写结果：

```text
results/<action_space>/<observation_type>/<model>/<domain>/<example_id>/
```

重点看这些文件：

- `traj.jsonl`
- `result.txt`
- `runtime.log`
- `recording.mp4`
- `step_*.png`

它们分别回答的问题是：

- `traj.jsonl`：agent 每一步到底返回了什么
- `result.txt`：评测结果是多少
- `runtime.log`：agent 内部日志有没有异常
- `recording.mp4`：动作执行过程到底发生了什么
- `step_*.png`：每步之后屏幕长什么样

如果你发现 agent “看起来像是卡住”，第一检查对象通常不是模型日志，而是：

- `traj.jsonl`
- `recording.mp4`

## 十、第一版最常见的 6 个接入错误

### 1. `reset()` 签名不兼容

典型问题：

- 没有 `_logger`
- 没有 `vm_ip`
- 没有 `**kwargs`

这会在标准 runner 调 `agent.reset(runtime_logger, vm_ip=env.vm_ip)` 时直接炸掉。

### 2. `predict()` 返回值不对

标准 runner 期望的是：

```python
response, actions = agent.predict(instruction, obs)
```

如果你返回的是：

- 只有 `actions`
- 三元组
- 自定义对象

都会导致后续主循环不兼容。

### 3. `actions` 不是环境支持的格式

典型问题：

- 你返回了字符串，但不是合法 `pyautogui` 代码
- 你返回了 dict，但不符合 `computer_13` schema
- 你输出了 agent 自己内部工具格式，没有转成 benchmark 动作

这个问题最直接的证据，通常会出现在：

- `traj.jsonl`
- 运行日志

### 4. `observation_type` 和 agent 内部逻辑不匹配

例如：

- 你只会吃截图
- 却把 `--observation_type` 设成了 `a11y_tree`

或者：

- 你依赖 `accessibility_tree`
- 却把 `observation_type` 设成了 `screenshot`

第一版最简单的办法就是固定：

- `--observation_type screenshot`

### 5. 过早把 `DesktopEnv` 一起改了

一旦你同时改：

- `DesktopEnv`
- runner
- agent

后面一出问题，就很难判断根因在哪一层。

第一版尽量只改 agent 和 agent runner。

### 6. 一上来就跑全量 benchmark

接入验证和 benchmark 跑分是两回事。

第一版应该先追求：

- 能跑通一个任务

不是：

- 能一次性跑完 369 个任务

## 十一、你可以怎么逐步扩展

如果最小版本已经跑通，后续扩展建议按下面顺序来：

1. 先把 `chrome + screenshot + pyautogui` 跑稳
2. 再加历史轨迹
3. 再加 `a11y_tree` 或 `screenshot_a11y_tree`
4. 再考虑更多 domain
5. 最后再考虑是否要做 special-case runner

这个顺序的核心思想是：

- 先保住标准接法
- 再扩能力

不要反过来。

## 十二、看完这一篇后，你应该怎么动手

如果你现在准备自己接一个 agent，最推荐的落地顺序是：

1. 复制 `scripts/python/run_multienv.py` 为 `run_multienv_myagent.py`
2. 写一个最小 `mm_agents/my_agent.py`
3. 先让 `_call_model(...)` 固定返回 `WAIT`
4. 跑一个单任务 smoke test
5. 确认结果目录和轨迹日志正常
6. 再把真实模型调用接进去

这里第 3 步看起来很笨，但其实非常值。

因为它能先帮你证明：

- runner 是通的
- env 是通的
- agent 接口是通的

等这条链确认没问题，再接入真实模型，调试范围会小很多。

## 下一步建议

下一篇最自然的延续，是继续往“真实实现”走，而不是停留在模板：

- 选一个现成 agent，按这个模板反推它为什么能接上
- 或者直接开始写你自己的 `my_agent.py`

如果你愿意，下一步我们可以继续补一篇：

- `17-seed-agent-against-template_zh.md`

专门把 [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 按这一篇模板拆开，对照看它是怎么一步步接到 benchmark 里的。
