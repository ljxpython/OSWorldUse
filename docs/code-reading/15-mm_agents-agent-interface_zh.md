# 15 从 mm_agents 理解 Agent 接入接口

这一篇接在 [14 新 Agent 接入清单与改动说明](./14-agent-integration-checklist_zh.md) 后面看最合适。

如果你现在真正想研究“一个新 agent 怎么接进 OSWorld”，那答案基本就是：

- 是的，下一步应该系统看 `mm_agents/`
- 但不要一头扎进所有 agent 实现
- 应该先分清“benchmark 真正要求的接口”与“某个 agent 自己的实现细节”

这一篇就专门解决这个问题。

## 先给一句结论

从接入视角看，`mm_agents/` 里最重要的不是“哪个 prompt 写得更复杂”，而是下面这条协议：

1. runner 调 `agent.reset(...)`
2. runner 把 `instruction` 和 `obs` 传给 `agent.predict(...)`
3. agent 返回 `response, actions`
4. runner 把 `actions` 逐个送进 `env.step(...)`

只要你的 agent 能稳定满足这条协议，它就能走 OSWorld 的标准接法。

## 一、为什么现在应该看 `mm_agents/`

前面几篇你已经把环境主链路走过了：

`task json -> env.reset -> agent.predict -> env.step -> env.evaluate`

看到这里，其实还剩最后一个关键问题：

- `agent.predict(...)` 到底应该长什么样？
- `obs` 里给 agent 的数据到底是什么？
- agent 输出的 `actions` 为什么能直接被环境执行？

这些问题，主要都在下面几处回答：

- [mm_agents/README.md](../../mm_agents/README.md)
- [mm_agents/agent.py](../../mm_agents/agent.py)
- [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
- [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
- [lib_run_single.py](../../lib_run_single.py)

所以如果你是为了“接入新 agent”而读代码，`mm_agents/` 确实就是下一站。

## 二、先看 benchmark 真正要求的最小契约

最重要的不是先看 `PromptAgent`，而是先看标准 rollout 怎样调用 agent。

直接看：

- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example(...)`

这条标准调用链可以缩成下面几步：

```python
env.reset(task_config=example)
agent.reset(runtime_logger, vm_ip=env.vm_ip)
obs = env._get_obs()
response, actions = agent.predict(instruction, obs)
for action in actions:
    obs, reward, done, info = env.step(action, ...)
```

从这里你就能倒推出，OSWorld 对 agent 的最小要求其实很少。

### 1. 要有 `reset(...)`

标准 runner 会尝试这样调：

```python
agent.reset(runtime_logger, vm_ip=env.vm_ip)
```

所以新 agent 最好支持：

- `_logger`
- `vm_ip`
- `**kwargs`

即使你暂时不用 `vm_ip`，也建议把它吃进去，因为环境 reset 后虚拟机地址可能会变化。

### 2. 要有 `predict(instruction, obs)`

标准 runner 只关心这一件事：

- 给你任务指令
- 给你当前观测
- 你返回下一步动作

其中：

- `instruction` 是字符串
- `obs` 是字典

当前环境提供的基础观测可以直接看：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)
  里的 `_get_obs`

它至少会给出：

```python
{
    "screenshot": ...,
    "accessibility_tree": ...,
}
```

这里要特别注意：

- `screenshot` 是环境原始截图数据
- `accessibility_tree` 是否存在，取决于环境是否启用了 `require_a11y_tree`

也就是说，agent 拿到的是“环境原始观测”，怎么编码、怎么裁剪、怎么放进模型消息，都是 agent 自己的工作。

### 3. 要返回 `(response, actions)`

标准 runner 期望的是：

```python
response, actions = agent.predict(instruction, obs)
```

这里：

- `response` 通常是模型原始回复，主要用于日志和轨迹记录
- `actions` 才是环境真正执行的内容

只要 `actions` 里的每一项能被 `env.step(...)` 接受，runner 就能继续跑。

### 4. `actions` 必须和当前 action space 兼容

这一点要同时看两边：

- agent 侧如何产出动作
- 环境侧如何消费动作

相关文件：

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)
- [desktop_env/actions.py](../../desktop_env/actions.py)

当前默认最重要的两类动作是：

- `pyautogui`
- `computer_13`

你可以把它们理解成：

- `pyautogui`：输出 Python 风格的 GUI 操作代码
- `computer_13`：输出结构化枚举动作

如果你的 agent 不能直接产出这两类动作之一，最稳妥的做法通常不是改环境，而是先在 agent 内部加一层动作适配。

## 三、`PromptAgent` 里哪些是协议，哪些只是默认实现

这是研究 `mm_agents/agent.py` 时最重要的阅读原则。

### 1. 真正属于“协议层”的部分

从接入角度看，下面这些是你要学的：

- `__init__` 里 action space 和 observation type 的基本约束
- `predict(...)` 的输入输出形状
- `parse_actions(...)` 如何把模型输出转成环境可执行动作
- `reset(...)` 如何清空 agent 内部状态

这些部分决定了：

- runner 能不能调用你
- env 能不能执行你的动作

### 2. 属于“默认实现层”的部分

下面这些不是 benchmark 强制要求，而是 `PromptAgent` 自己的实现选择：

- 如何拼 system prompt
- 是否保留历史轨迹
- 历史保留多少步
- 是否线性化 accessibility tree
- 是否裁剪 accessibility tree token 长度
- 如何路由 OpenAI、Claude、Gemini、Qwen 等不同模型接口
- 如何在 `som` 模式下做 tag screenshot

这些都可以替换。

换句话说：

- 你不需要复制 `PromptAgent` 的 prompt 设计
- 你不需要复制它的大段 `call_llm(...)`
- 你也不需要复制它全部历史管理逻辑

你真正要保住的是：

- 输入契约
- 输出契约
- 动作兼容性

## 四、如何读 `PromptAgent`

如果你现在打开 [mm_agents/agent.py](../../mm_agents/agent.py)，建议按下面顺序读。

### 1. 先看 `__init__`

这一段最值得注意的是：

- `observation_type`
- `action_space`

`PromptAgent` 支持的观测类型有：

- `screenshot`
- `a11y_tree`
- `screenshot_a11y_tree`
- `som`

支持的动作空间有：

- `computer_13`
- `pyautogui`

这里的核心价值不是 prompt 本身，而是你要看懂：

- 不同观测类型会改变 agent 需要预处理的数据
- 不同动作空间会改变模型输出格式和解析方式

### 2. 再看 `predict(...)`

这是 `PromptAgent` 的主循环。

从接入视角看，可以把它拆成 5 件事：

1. 把任务 instruction 拼进 system message
2. 把历史 observation 和 action 组织成上下文
3. 把当前 `obs` 转成模型可吃的输入
4. 调模型
5. 把模型回复解析成 `actions`

你读这一段时，建议只回答下面几个问题：

- `obs["screenshot"]` 是在 agent 内部怎么编码的？
- `obs["accessibility_tree"]` 是在 agent 内部怎么整理的？
- 历史轨迹是怎么截断的？
- 最后返回给 runner 的东西到底是什么？

把这几个问题看明白，就够了。

### 3. 然后看 `parse_actions(...)`

这部分很关键，因为它直接决定“模型字符串”怎么变成“环境动作”。

`PromptAgent` 的逻辑很清楚：

- `computer_13` 走 `parse_actions_from_string(...)`
- `pyautogui` 走 `parse_code_from_string(...)`
- `som + pyautogui` 走 `parse_code_from_som_string(...)`

这给你一个很明确的接入思路：

- 如果你的模型输出格式和现有 parser 接近，可以直接复用 parser
- 如果你的模型输出格式不同，就在 agent 内部加自己的 parser

但目标不变：

- 最后产出的 `actions` 必须是环境能执行的格式

### 4. 最后看 `reset(...)`

`PromptAgent.reset(...)` 做的事情其实很朴素：

- 注入 logger
- 保存 `vm_ip`
- 清空 thoughts / actions / observations

这也再次说明，runner 真正依赖的不是复杂逻辑，而是：

- 每个任务开始前，agent 能回到干净状态

## 五、为什么 `SeedAgent` 很值得你看

如果你的目标是“学会怎么接一个新的模型 agent”，那 [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 很值得作为第二个样例。

原因是它很适合回答一个实际问题：

- 不复制 `PromptAgent` 的内部实现，能不能仍然接进 OSWorld？

答案是可以。

`SeedAgent` 和 `PromptAgent` 在内部实现上差异很大：

- 它自己的 system prompt 不一样
- 它自己的消息组织方式不一样
- 它自己的模型调用方式不一样
- 它还维护了自己的历史图片和响应历史

但它在“外部接口”上仍然保持了标准兼容：

- 有 `reset(_logger=None, vm_ip=None, **kwargs)`
- 有 `predict(task_instruction, obs)`
- 返回 `(response, actions)`
- runner 仍然可以直接复用 `run_single_example(...)`

对应入口：

- [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)

这就是你接新 agent 时最应该模仿的路径：

- 内部自由发挥
- 外部协议不变

## 六、为什么 `OpenAICUAAgent` 是“特殊接法”样例

如果你想知道“什么时候必须改 runner”，那就该看：

- [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
- [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)
- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example_openaicua(...)`

它和标准接法最大的不同有三点。

### 1. agent 在构造时直接拿 `env`

标准 `PromptAgent` / `SeedAgent` 是：

- runner 创建 env
- runner 创建 agent
- rollout 里由 runner 调 `env.step(...)`

但 `OpenAICUAAgent` 在构造时就接收了 `env`。

这说明它不是一个“只负责决策”的纯 agent，而是已经部分知道环境执行细节。

### 2. rollout 不再直接调用 `env.step(...)`

在 `run_single_example_openaicua(...)` 里，实际执行变成了：

```python
obs, reward, done, info, step_info = agent.step(action)
```

也就是说：

- 动作执行逻辑有一部分被吸进 agent 里了

这就是标准 runner 不能直接复用的直接原因。

### 3. `predict(...)` 返回的不只是普通文本响应

它返回的 `response` 里还会包含：

- `state_correct`
- `model_usage`
- `messages`

runner 会根据 `state_correct` 决定 episode 是否继续。

这已经超出了标准 `(response, actions)` 的“弱约束日志含义”，变成了“带控制语义的返回值”。

所以它必须走专用 rollout。

## 七、你接自己的 agent 时，应该优先复用什么

如果你的目标是尽快把 agent 接进 benchmark，建议优先复用这些层：

- 现有任务 JSON
- 现有 `DesktopEnv`
- 现有 evaluator
- 现有 provider 配置
- 现有标准 `run_single_example(...)`

能不动的尽量别动。

最推荐的第一版接法是：

1. 新增 `mm_agents/my_agent.py`
2. 让它支持 `reset(...)` 和 `predict(...)`
3. 让它输出兼容 `pyautogui` 或 `computer_13` 的 `actions`
4. 新增一个 `scripts/python/run_multienv_myagent.py`
5. 继续复用 `lib_run_single.run_single_example(...)`

这是最稳、最容易 debug、也最符合仓库现有组织方式的路径。

## 八、哪些内容不要盲目照抄

第一次读 `mm_agents/agent.py` 时，很容易把很多东西都当成“接入必需品”。

其实下面这些通常都不是第一版必须照抄的：

- 超长的多模型 API 路由
- 所有观测模式同时支持
- 所有 action space 同时支持
- 复杂的多轮历史管理
- `som` 的标注截图逻辑
- 所有 provider 的密码和 endpoint 兼容分支

更现实的做法是先收缩。

比如第一版只做：

- 平台：`Ubuntu`
- 观测：`screenshot`
- 动作：`pyautogui`
- domain：`chrome`

先把最小链路打通，再扩展。

## 九、建议的阅读顺序

如果你是按“接入 agent”这条主线往下读，推荐顺序如下：

1. [mm_agents/README.md](../../mm_agents/README.md)
   先确认当前支持的 observation space 和 action space。
2. [lib_run_single.py](../../lib_run_single.py)
   先看标准 runner 怎样调用 agent。
3. [mm_agents/agent.py](../../mm_agents/agent.py)
   重点读 `__init__`、`predict`、`parse_actions`、`reset`。
4. [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)
   看标准 `PromptAgent` 是怎么被实例化并塞进任务循环的。
5. [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
   看一个“内部实现不同，但外部协议兼容”的样例。
6. [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)
   看它如何继续复用标准 rollout。
7. [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
   看一个“需要专用 runner”的特例。
8. [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)
   看 special-case rollout 是怎么长出来的。

## 十、看完这一篇后，你脑子里应该留下什么

如果这一篇看明白了，你至少应该能稳定回答下面 5 个问题：

1. OSWorld 标准 runner 对 agent 的最小接口要求是什么？
2. `obs` 是谁提供的，原始形状是什么？
3. `PromptAgent` 里哪些是 benchmark 协议，哪些只是它自己的实现？
4. `SeedAgent` 为什么能复用标准 runner？
5. `OpenAICUAAgent` 为什么必须走专用 runner？

这 5 个问题答清楚后，你就已经具备自己接一个新 agent 的代码阅读基础了。

## 下一步建议

下一篇最自然的延续，是直接写一份“最小可接入模板”，把抽象阅读变成可落地骨架。

也就是：

- `mm_agents/my_agent.py` 至少要写什么
- `scripts/python/run_multienv_myagent.py` 至少要改什么
- 第一版应该如何限制范围，先把链路跑通

如果你愿意，下一步我们就可以继续把这篇模板文档补出来。
