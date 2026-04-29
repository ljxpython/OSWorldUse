# 14 新 Agent 接入清单与改动说明

这一篇接在 [13 Calc 任务端到端走读](./13-calc-task-end-to-end_zh.md) 后面看最合适。

前面你已经知道这个项目在做什么，也知道主链路是：

`task json -> env.reset -> agent.predict -> env.step -> env.evaluate`

那如果你现在手里有一个新的 agent，想把它接进这个 benchmark，最现实的问题就是：

- 到底要改哪些文件？
- 最小接入需要满足什么接口？
- 哪些层通常不用碰？
- 什么情况下要加专用 runner？

这一篇就只回答这些问题。

## 先给一句结论

如果你的 agent 已经能根据桌面观测输出：

- `pyautogui` 动作代码

或者：

- `computer_13` 结构化动作

那它接入 OSWorld 的最小改动通常只有两层：

1. 新增一个 agent 类
2. 新增或修改一个 runner 脚本

绝大多数情况下：

- 不需要改任务 JSON
- 不需要改 evaluator
- 不需要改 `DesktopEnv`

只有当你的 agent 使用了：

- 新的动作协议
- 新的观测协议
- 特殊的返回签名

时，才需要继续往环境层和 rollout 层改。

## 一、先分清两种接法

从仓库现状看，接新 agent 基本分成两种。

### 1. 标准接法

适合这种 agent：

- `predict(instruction, obs)` 就能工作
- 返回 `(response, actions)`
- `actions` 可以直接送进 `env.step()`

这类 agent 可以直接走：

- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example(...)`

典型参考：

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)
- [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)

### 2. 特例接法

适合这种 agent：

- 返回值不是 `(response, actions)`
- 需要额外上下文
- 自己内部有特殊 step 语义
- 动作不是标准 `pyautogui` / `computer_13`

这类 agent 通常需要：

1. 新增专用 runner
2. 在 [lib_run_single.py](../../lib_run_single.py) 里新增专用 `run_single_example_xxx(...)`

典型参考：

- [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)
- [scripts/python/run_multienv_hosted_gbox.py](../../scripts/python/run_multienv_hosted_gbox.py)
- [lib_run_single.py](../../lib_run_single.py)
  里的：
  - `run_single_example_openaicua`
  - `run_single_example_opencua`
  - `run_single_example_mano`
  - `run_single_example_vlaa_gui`

你可以把这两类理解成：

- 标准接法：适配 agent 到现有 benchmark 协议
- 特例接法：适配 benchmark 到 agent 的特殊协议

原则上，优先选第一种。

## 二、最小接入前，先确认 6 件事

在真正改代码前，先把下面 6 个问题确定。

### 1. 你的 agent 吃什么观测

当前主流观测协议是：

- `screenshot`
- `a11y_tree`
- `screenshot_a11y_tree`
- `som`

可以参考：

- [mm_agents/README.md](../../mm_agents/README.md)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

如果你的 agent 至少能吃：

- `screenshot`

就已经能接第一版。

### 2. 你的 agent 输出什么动作

当前环境主支持：

- `pyautogui`
- `computer_13`

环境侧允许的 action space 见：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

动作 schema 见：

- [desktop_env/actions.py](../../desktop_env/actions.py)

如果你的 agent 不是输出这两类之一，先考虑：

- 在 agent 内部增加一个输出转换层

不要第一反应就去改环境协议。

### 3. 你的 agent 的 `predict()` 返回什么

标准 rollout 期望的是：

- `response, actions = agent.predict(instruction, obs)`

可以直接看：

- [lib_run_single.py](../../lib_run_single.py)

如果你的返回值不是这两个，就要决定：

- 改 agent 适配 benchmark
还是
- 改 rollout 适配 agent

通常建议前者。

### 4. 你的 agent 的 `reset()` 需要什么

标准 rollout 会在 `env.reset(task_config=example)` 之后调用：

- `agent.reset(runtime_logger, vm_ip=env.vm_ip)`

见：

- [lib_run_single.py](../../lib_run_single.py)

所以你的 agent 最好支持：

- logger 注入
- `vm_ip` 注入

即使暂时不用，也建议把参数吃掉。

### 5. 你准备跑哪套任务

当前默认主 benchmark 是：

- [evaluation_examples/test_all.json](../../evaluation_examples/test_all.json)

默认是 Ubuntu 主任务集，共：

- `10` 个 domain
- `369` 个任务

包括：

- `chrome`
- `gimp`
- `libreoffice_calc`
- `libreoffice_impress`
- `libreoffice_writer`
- `multi_apps`
- `os`
- `thunderbird`
- `vlc`
- `vs_code`

另外仓库里还有 Windows 任务集：

- [evaluation_examples/examples_windows](../../evaluation_examples/examples_windows)

共：

- `4` 个 domain
- `49` 个任务

如果你第一版只是想验证 agent 能否接通，建议先跑：

- Ubuntu 默认任务集里的单一 domain

### 6. 你用什么 provider 跑

当前 provider 工厂支持：

- `vmware`
- `virtualbox`
- `docker`
- `aws`
- `azure`
- `aliyun`
- `volcengine`

见：

- [desktop_env/providers/__init__.py](../../desktop_env/providers/__init__.py)

第一版最重要的不是 provider 多高级，而是：

- 环境稳定
- 结果能复现

## 三、标准接法的最小清单

如果你的 agent 能适配标准协议，建议按下面顺序做。

### 1. 新增一个 agent 文件

例如：

- `mm_agents/my_agent.py`

最小建议实现：

```python
class MyAgent:
    def __init__(...):
        ...

    def reset(self, runtime_logger=None, vm_ip=None, **kwargs):
        ...

    def predict(self, instruction: str, obs: dict):
        return response, actions
```

这里的 `actions` 最好直接是：

- `List[str]`，用于 `pyautogui`

或者：

- `List[dict]`，用于 `computer_13`

### 2. 确保支持 3 个特殊动作

无论你走哪种动作协议，都建议显式支持：

- `WAIT`
- `DONE`
- `FAIL`

因为环境和 parser 都会识别它们。

参考：

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

### 3. 新增一个 runner 脚本

最常见做法是复制一个最接近的脚本，例如：

- [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)

然后改三处：

1. import 你的 agent
2. 构造 agent 的参数
3. 调用标准 `lib_run_single.run_single_example(...)`

如果你的 agent 能满足标准接口，这一步通常就够了。

### 4. 对齐默认参数

建议第一版先把下面参数固定下来：

- `action_space=pyautogui`
- `observation_type=screenshot`
- `os_type=Ubuntu`
- `provider_name=docker` 或 `vmware` 或你现有稳定环境

原因很简单：

- `screenshot + pyautogui` 是当前最容易接通的一条路径

### 5. 先只跑一个 domain

例如：

- `chrome`
或
- `libreoffice_calc`

不要第一版上来就跑全部 `369` 个任务。

## 四、标准接法下，通常不需要改哪些层

如果你走的是标准接法，下面这些通常不要动。

### 1. 不改任务 JSON

任务定义已经是 benchmark 本体的一部分。

### 2. 不改 evaluator

评测规则最好保持 benchmark 原样。

### 3. 不改 `DesktopEnv`

只要你输出的是现有动作协议，就不需要改环境层。

### 4. 不改 controller

只要动作最终落到：

- `pyautogui`
或
- `computer_13`

就不需要改控制层。

这四点很重要，因为它们决定了：

- 你是在“接入 benchmark”
还是在“改 benchmark”

尽量做前者。

## 五、什么情况下要加专用 `run_single_example_xxx`

当你的 agent 不满足标准 `(response, actions)` 协议时，就需要考虑特例 rollout。

常见触发条件有：

### 1. `predict()` 还返回额外信息

例如：

- `response, actions, info_dict`

### 2. 每一步不是简单动作列表

例如：

- agent 内部自己维护 planner / executor 多阶段状态

### 3. 需要访问 env 本体

例如：

- agent 构造时直接吃 `env`

参考：

- [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)

### 4. 你的动作不是直接给 `env.step()` 的

例如：

- agent 输出 tool calls
- 需要再转换一次

这种情况下，最稳妥的做法是：

1. 新增 `run_single_example_myagent(...)`
2. 新增 `run_multienv_myagent.py`

不要硬塞进通用 rollout，把逻辑改得很乱。

## 六、特例接法的改动清单

如果确定要走特例接法，建议按下面顺序做。

### 1. 先复制最相近的专用 runner

例如：

- OpenAI CUA 风格：
  [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)
- 外部服务风格：
  [scripts/python/run_multienv_hosted_gbox.py](../../scripts/python/run_multienv_hosted_gbox.py)

### 2. 在 `lib_run_single.py` 新增专用 rollout

例如：

- `run_single_example_myagent(...)`

要做的事情仍然还是这几步：

1. `env.reset(...)`
2. `agent.reset(...)`
3. 拿初始观测
4. 调 `predict(...)`
5. 执行动作
6. 记录截图和 `traj.jsonl`
7. `env.evaluate()`
8. 写 `result.txt`

主流程不要改，只改和你的 agent 协议强相关的部分。

### 3. 保持结果目录结构不变

结果目录仍然建议保持：

`results/{action_space}/{observation_type}/{model}/{domain}/{task_id}/`

因为：

- `show_result.py`
- `monitor/`

都是按这个结构读结果的。

## 七、什么时候才应该改环境协议

这个门槛要抬高。

只有下面几种情况，才建议改环境协议。

### 1. 你一定要引入新的 action space

这时要同时改：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)
- [desktop_env/actions.py](../../desktop_env/actions.py)
- controller 执行逻辑
- 可能还包括 agent parser / prompt

### 2. 你一定要引入新的 observation space

这时要改：

- `DesktopEnv._get_obs()`
- agent 侧输入处理
- 可能还有 runner 参数解析

### 3. 你要评测一个当前 benchmark 没覆盖的新 OS / 新 app 族

这时才会进一步碰：

- provider
- setup
- evaluator
- task data

如果只是接一个新 agent，绝大多数时候还没到这一步。

## 八、第一版最推荐的接入路径

如果你想最低成本验证 agent 能不能跑，我建议直接照下面这条路线。

### 推荐路线

1. 新建 `mm_agents/my_agent.py`
2. 让它支持：
   - `reset(runtime_logger=None, vm_ip=None, **kwargs)`
   - `predict(instruction, obs) -> (response, actions)`
3. 输出 `pyautogui` 动作
4. 复制 [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)
5. 改成 `run_multienv_myagent.py`
6. 先跑：
   - `observation_type=screenshot`
   - `action_space=pyautogui`
   - `domain=chrome`

这条路线几乎是当前仓库里阻力最小的接法。

## 九、你需要特别注意的 8 个兼容点

### 1. `predict()` 返回值必须稳定

不要一会儿返回 list，一会儿返回 tuple。

### 2. `actions` 必须可直接执行

最终要能直接送进：

- `env.step(action)`

### 3. `reset()` 最好吞掉多余参数

例如：

- `runtime_logger`
- `vm_ip`
- `**kwargs`

即使暂时不用，也别让它因为签名不兼容而炸掉。

### 4. 要能处理长轨迹

runner 会多轮调用 `predict()`，不是一次性完成。

### 5. 要接受 benchmark 给定的任务 instruction

不要把 agent 写成只能跑某个固定 prompt 模板。

### 6. 结果目录命名别改

否则：

- `show_result.py`
- `monitor`

都会跟不上。

### 7. 先别碰 evaluator

一旦你为了 agent 去改 evaluator，benchmark 可比性就变弱了。

### 8. 特例 rollout 也要保留标准产物

至少保留：

- `traj.jsonl`
- `runtime.log`
- `result.txt`
- 截图
- `recording.mp4`

## 十、一个最小改动示意

如果你的 agent 已经能输出 `pyautogui` 代码，最小改动通常就是：

### 改动 1

新增：

- `mm_agents/my_agent.py`

### 改动 2

新增：

- `scripts/python/run_multienv_myagent.py`

并在里面：

1. `from mm_agents.my_agent import MyAgent`
2. 构造 `agent = MyAgent(...)`
3. 调用：
   `lib_run_single.run_single_example(...)`

如果做到这里就能跑通，那已经是一个合格的 benchmark 接入版本。

## 十一、当前仓库里哪些例子最值得当模板

如果你自己接新 agent，我建议优先参考下面三个。

### 1. 最标准模板

- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

适合：

- 你想看“最通用 benchmark 跑法”

### 2. 标准接法模板

- [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)

适合：

- 你已经有自己的 agent，只是想换掉默认 `PromptAgent`

### 3. 特例接法模板

- [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)

适合：

- 你的 agent 协议和标准 rollout 有明显不同

## 十二、如果你问“第一版到底该改哪些文件”，我的建议是这个

### 必改

- `mm_agents/my_agent.py`
- `scripts/python/run_multienv_myagent.py`

### 视情况改

- [lib_run_single.py](../../lib_run_single.py)
  只在你需要专用 rollout 时改

### 尽量不改

- `desktop_env/`
- `evaluation_examples/`
- `desktop_env/evaluators/`

## 十三、最后给你一份最短 checklist

如果你只想拿一张最短可执行清单，就看这个。

1. 确认你的 agent 吃 `obs`，吐 `(response, actions)`。
2. 先把动作适配到 `pyautogui`。
3. 实现 `reset(runtime_logger=None, vm_ip=None, **kwargs)`。
4. 新增 `mm_agents/my_agent.py`。
5. 复制一个最接近的 `run_multienv_xxx.py`。
6. 把 agent import 和实例化替换掉。
7. 能复用 `run_single_example()` 就不要新写 rollout。
8. 先跑 Ubuntu + `screenshot` + `pyautogui` + 单一 domain。
9. 保持结果目录结构不变。
10. 跑通后再考虑 `a11y_tree`、结构化动作或 Windows。

## 十四、读完这一篇后，下一步最自然是什么

如果你接下来真的准备动手接一个 agent，最实用的下一步不是继续看更多理论，而是：

1. 选一个现有 runner 作为模板
2. 选 `chrome` 做第一批小规模验证
3. 先拿到能正常写出 `result.txt` 的第一版

如果你愿意，我下一步可以直接继续给你一份：

- `15-agent-integration-template_zh.md`

内容会更偏工程落地，直接给出：

- 推荐的新文件骨架
- `MyAgent` 最小类模板
- `run_multienv_myagent.py` 最小脚手架

这样你就可以照着改，不用再自己拼。 
