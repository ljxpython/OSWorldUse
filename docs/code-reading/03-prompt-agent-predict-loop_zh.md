# 03 PromptAgent 推理主循环解读

这一篇开始进入 Agent 侧主线。

如果说前一篇 [02 DesktopEnv 主循环解读](./02-desktopenv-main-loop_zh.md) 解决的是“环境如何提供 observation 并执行 action”，那这一篇解决的是：

- `PromptAgent` 如何消费 observation
- 它如何把当前状态组织成 prompt
- 模型回复之后如何被解析成 action
- 不同 observation / action 组合会怎样改变行为

为了降低复杂度，这一篇只聚焦仓库里的基础实现：

- [mm_agents/agent.py](../../mm_agents/agent.py)

不扩展到其他更重的 agent 分支，比如：

- `vlaa_gui`
- `os_symphony`
- `uipath`

## 先记住 Agent 侧主线

围绕 `PromptAgent`，最应该先记住的是这条链：

`PromptAgent(...) -> reset() -> predict(instruction, obs) -> call_llm(payload) -> parse_actions(response)`

它和环境主线拼在一起，就是：

`env.reset(...) -> obs -> agent.predict(...) -> actions -> env.step(...)`

也就是说，`PromptAgent` 的核心职责其实只有两件事：

1. 把环境 observation 翻译成模型能理解的 prompt
2. 把模型输出翻译回环境能执行的 action

## 一、先看文件结构

建议你第一次读 [mm_agents/agent.py](../../mm_agents/agent.py) 时，不要从 `PromptAgent` 直接往下读，而是先看它前面的辅助函数。

这个文件大致可以分成四层：

1. 图像与 accessibility tree 辅助函数
2. 输出解析函数
3. `PromptAgent` 主体
4. `call_llm()` 里针对不同模型后端的分发逻辑

### 1. 图像和 accessibility tree 辅助函数

这几组函数主要负责 observation 预处理：

- `encode_image`
- `encoded_img_to_pil_img`
- `save_to_tmp_img_file`
- `linearize_accessibility_tree`
- `tag_screenshot`
- `trim_accessibility_tree`

其中最重要的是：

- [agent.py:71](../../mm_agents/agent.py#L71) `linearize_accessibility_tree(...)`
- [agent.py:120](../../mm_agents/agent.py#L120) `tag_screenshot(...)`
- [agent.py:217](../../mm_agents/agent.py#L217) `trim_accessibility_tree(...)`

### 2. 输出解析函数

这几组函数负责把模型回复解析回动作：

- [agent.py:128](../../mm_agents/agent.py#L128) `parse_actions_from_string(...)`
- [agent.py:162](../../mm_agents/agent.py#L162) `parse_code_from_string(...)`
- [agent.py:197](../../mm_agents/agent.py#L197) `parse_code_from_som_string(...)`

如果你想知道“模型输出为什么能变成 `pyautogui.rightClick()` 或 JSON action”，这一层就是关键。

### 3. Prompt 模板来源

`PromptAgent` 自己不把系统提示词硬编码在类里。

它从这里导入模板：

- [mm_agents/prompts.py](../../mm_agents/prompts.py)

也就是这些变量：

- `SYS_PROMPT_IN_SCREENSHOT_OUT_CODE`
- `SYS_PROMPT_IN_SCREENSHOT_OUT_ACTION`
- `SYS_PROMPT_IN_A11Y_OUT_CODE`
- `SYS_PROMPT_IN_A11Y_OUT_ACTION`
- `SYS_PROMPT_IN_BOTH_OUT_CODE`
- `SYS_PROMPT_IN_BOTH_OUT_ACTION`
- `SYS_PROMPT_IN_SOM_OUT_TAG`

这点很重要，因为它说明：

- Agent 主体负责“怎么拼消息”
- Prompt 模板负责“告诉模型应该输出什么格式”

## 二、`PromptAgent.__init__` 做了什么

对应代码：

- [agent.py:226](../../mm_agents/agent.py#L226)

`__init__` 的职责可以概括成 4 件事：

1. 保存模型和运行参数
2. 初始化轨迹缓存
3. 根据 observation / action 组合选择系统 prompt
4. 把 `client_password` 注入系统 prompt

### 1. 参数层面

第一次阅读时，最值得先记住这些参数：

- `model`
- `action_space`
- `observation_type`
- `max_trajectory_length`
- `a11y_tree_max_tokens`
- `client_password`

这里真正决定 Agent 行为分叉的，是：

- `action_space`
- `observation_type`

### 2. observation 和 action 的组合关系

逻辑集中在：

- [agent.py:256](../../mm_agents/agent.py#L256)

这里不是简单的“一个模型一个 prompt”，而是：

- 不同 observation 类型，用不同提示词
- 不同 action space，也用不同提示词

例如：

- `screenshot + pyautogui`
  选 `SYS_PROMPT_IN_SCREENSHOT_OUT_CODE`
- `a11y_tree + computer_13`
  选 `SYS_PROMPT_IN_A11Y_OUT_ACTION`
- `screenshot_a11y_tree + pyautogui`
  选 `SYS_PROMPT_IN_BOTH_OUT_CODE`
- `som + pyautogui`
  选 `SYS_PROMPT_IN_SOM_OUT_TAG`

所以你应该把 `PromptAgent` 理解成一个“配置驱动的 prompt 适配器”。

### 3. 为什么要注入 `client_password`

最后一行：

- [agent.py:287](../../mm_agents/agent.py#L287)

会执行：

```python
self.system_message = self.system_message.format(CLIENT_PASSWORD=self.client_password)
```

这说明系统提示词模板里是留了密码占位符的。

它不是纯文本常量，而是运行时模板。

## 三、`predict()` 是真正的核心

对应代码：

- [agent.py:289](../../mm_agents/agent.py#L289)

如果你只想吃透 `PromptAgent`，`predict()` 是最值得反复读的方法。

它可以拆成 6 步：

1. 构造 system message
2. 读取并裁剪历史轨迹
3. 把历史 observation/action 组装进 messages
4. 把当前 observation 组装进 messages
5. 调用 `call_llm()`
6. 调用 `parse_actions()`

### 1. system message 的构造

开头会先做：

- [agent.py:293](../../mm_agents/agent.py#L293)

也就是把任务 instruction 直接拼到系统提示词后面。

这一点和很多框架不同：

- 有些框架把 instruction 放在 user message
- 这里则是把“当前任务目标”直接加到 system message 后面

这会让模型更强地把 instruction 当成全局目标。

### 2. 轨迹缓存是什么

`PromptAgent` 内部维护三组并行数组：

- `self.observations`
- `self.actions`
- `self.thoughts`

见：

- [agent.py:252](../../mm_agents/agent.py#L252)

这里的含义可以理解成：

- `observations`
  历史输入
- `thoughts`
  模型历史回复原文
- `actions`
  从回复里解析出来的动作

### 3. 为什么要裁剪历史轨迹

历史裁剪逻辑在：

- [agent.py:313](../../mm_agents/agent.py#L313)

这一步是为了控制上下文长度。

`max_trajectory_length` 的作用不是限制动作执行，而是限制“喂给模型看的最近历史”。

如果设为：

- `0`
  就只看当前 observation
- `3`
  就保留最近 3 步轨迹

### 4. 历史轨迹是怎么拼进 messages 的

这一段在：

- [agent.py:327](../../mm_agents/agent.py#L327)

它的方式很直接：

1. 先把历史 observation 以 user message 形式放进去
2. 再把历史 thought 以 assistant message 放进去

要注意的是：

- 历史里放的是 `thought`
- 不是已经解析好的 action

也就是说，模型看到的是“自己过去说过什么”，不是环境内部结构化动作。

### 5. 当前 observation 是怎么进入 prompt 的

这是 `predict()` 最值得你仔细对照的一段：

- [agent.py:415](../../mm_agents/agent.py#L415)

根据 `observation_type` 不同，处理方式不同。

#### `screenshot`

逻辑：

- 截图做 base64 编码
- 作为 image_url 塞进消息

#### `a11y_tree`

逻辑：

- XML accessibility tree 先被 `linearize_accessibility_tree(...)`
- 再按 token 长度裁剪
- 最终作为纯文本塞进消息

#### `screenshot_a11y_tree`

逻辑：

- 同时提供截图和线性化后的 accessibility tree

这是当前最典型的多模态组合。

#### `som`

逻辑：

- 先对截图做标注
- 把可交互节点打上 tag
- 再让模型基于 tag 输出动作

这就是 `set-of-mark` 风格输入。

### 6. 一个关键认知：Agent 自己存的是“转换后的 observation”

例如在 `screenshot` 路径下：

- [agent.py:426](../../mm_agents/agent.py#L426)

它会把 base64 后的图像、裁剪后的 accessibility tree 存进 `self.observations`。

所以 Agent 内部缓存的 observation，不是环境刚返回的原始对象，而是它自己处理过的版本。

## 四、`call_llm()` 是模型后端分发器

对应代码：

- [agent.py:571](../../mm_agents/agent.py#L571)

这个方法很长，但第一次读不需要把每个 provider 分支都看完。

你应该先抓住它的结构角色：

- 它不是推理策略核心
- 它是“把统一 payload 适配到不同模型 API” 的后端分发器

### 1. 统一输入，分支输出

在 `predict()` 里，传给 `call_llm()` 的 payload 结构基本统一：

```python
{
    "model": self.model,
    "messages": messages,
    "max_tokens": self.max_tokens,
    "top_p": self.top_p,
    "temperature": self.temperature
}
```

而 `call_llm()` 的任务就是根据模型名字判断：

- 该走 OpenAI
- 还是 Claude
- 还是 Gemini
- 还是 Qwen
- 还是本地或第三方兼容接口

### 2. 最值得先看的几个分支

第一次阅读建议先看这几个：

- [agent.py:621](../../mm_agents/agent.py#L621) `gpt`
- [agent.py:657](../../mm_agents/agent.py#L657) `claude`
- [agent.py:897](../../mm_agents/agent.py#L897) `gemini`
- [agent.py:1026](../../mm_agents/agent.py#L1026) `qwen`

重点不要放在 API 细节，而是放在：

- 不同厂商对消息格式要求不一样
- 图像输入格式不一样
- system message 处理方式不一样

例如：

- Claude 分支会把 system message 合并进第一个 user message
- Gemini 分支会把 image part 放进 `parts`
- OpenAI 分支则直接用兼容 chat completions 的格式

### 3. 为什么 `call_llm()` 这么长

原因不是逻辑复杂，而是兼容面太宽。

你可以把它理解成：

- `PromptAgent.predict()` 是语义主线
- `call_llm()` 是接入层

真正决定桌面决策行为的，不是这些 HTTP 分支，而是：

- 用什么 observation
- 用什么 prompt
- 怎么解析动作

## 五、模型输出是怎么变成 action 的

模型回复之后，会进入：

- [agent.py:535](../../mm_agents/agent.py#L535)

也就是：

```python
actions = self.parse_actions(response, masks)
```

这一步把自然语言或代码文本，变成环境后续能执行的动作列表。

## 六、`parse_actions()` 的角色

对应代码：

- [agent.py:1110](../../mm_agents/agent.py#L1110)

它的职责不是“理解任务”，而是“根据当前配置选择正确解析器”。

### 1. `computer_13`

走：

- [agent.py:1115](../../mm_agents/agent.py#L1115)

也就是 `parse_actions_from_string(response)`。

它期待模型输出 JSON 风格动作。

### 2. `pyautogui`

走：

- [agent.py:1117](../../mm_agents/agent.py#L1117)

也就是 `parse_code_from_string(response)`。

它期待模型输出 Python 代码片段。

### 3. `som + pyautogui`

走：

- [agent.py:1129](../../mm_agents/agent.py#L1129)

也就是 `parse_code_from_som_string(response, masks)`。

这一步会把模型输出里的 tag 变量补成屏幕坐标。

## 七、两个最关键的解析函数

### 1. `parse_code_from_string(...)`

对应：

- [agent.py:162](../../mm_agents/agent.py#L162)

它的核心策略是：

- 支持 `WAIT / DONE / FAIL`
- 支持从 Markdown 代码块里提取代码
- 支持多段代码块

这解释了为什么 prompt 模板通常要求模型输出 fenced code block。

### 2. `parse_actions_from_string(...)`

对应：

- [agent.py:128](../../mm_agents/agent.py#L128)

它会优先找：

- ```json ... ```
- 然后退化到普通代码块
- 再退化到整段直接 JSON

这让 `computer_13` 风格输出更稳定。

## 八、`reset()` 为什么很重要

对应代码：

- [agent.py:1137](../../mm_agents/agent.py#L1137)

`PromptAgent.reset()` 做的事情看起来简单，但非常关键：

1. 更新 logger
2. 保存 `vm_ip`
3. 清空 `thoughts`
4. 清空 `actions`
5. 清空 `observations`

这意味着：

- 每次切新任务时，Agent 的短期轨迹都会被清空
- 否则前一个任务的上下文会污染下一个任务

所以在任务主循环里，`agent.reset(...)` 不是可选项。

## 九、把 Agent 和环境拼起来看

现在把 `DesktopEnv` 和 `PromptAgent` 合在一起，一次典型回合大致是这样：

1. `env.reset(task_config)`
2. `obs = env._get_obs()`
3. `agent.predict(instruction, obs)`
4. `call_llm(...)`
5. `parse_actions(...)`
6. `env.step(action)`
7. `env._get_obs()`
8. 再交回 `agent.predict(...)`

这里最重要的边界是：

- 环境负责“世界状态”和“动作执行”
- Agent 负责“状态表述”和“动作生成”

## 十、第一次读 Agent 时最容易误解的几点

### 1. `PromptAgent` 不是完整多 Agent 系统

它是一个单体 prompt-based agent。

不要把它和仓库里其他复杂 agent 分支混在一起理解。

### 2. `PromptAgent` 不知道怎么执行动作

它只负责输出动作文本。

真正执行动作的是环境里的 controller。

### 3. `PromptAgent` 的“记忆”很短

它只有：

- `observations`
- `actions`
- `thoughts`

这是一种非常轻量的短期轨迹缓存，不是复杂 memory 系统。

### 4. `call_llm()` 很长，不代表推理策略复杂

那一大段大多是多厂商 API 兼容代码。

真正该优先理解的还是：

- prompt 选择
- observation 转换
- 输出解析

## 十一、现在最值得你做的 4 个小实验

### 实验 1：打印 `messages`

在 `predict()` 里临时把 `messages` 打出来。

目标：

- 看清楚当前 observation 是如何变成 prompt 的
- 看清楚历史轨迹是如何插入上下文的

### 实验 2：切换 observation_type

试着比较：

- `screenshot`
- `a11y_tree`
- `screenshot_a11y_tree`

目标：

- 理解同一个任务在不同 observation 方案下，prompt 长什么样

### 实验 3：手工喂一个 response 给解析函数

例如单独试：

- `parse_code_from_string(...)`
- `parse_actions_from_string(...)`

目标：

- 理解模型输出格式为什么必须被 prompt 约束得很严格

### 实验 4：观察 `max_trajectory_length`

把它设成：

- `0`
- `1`
- `3`

目标：

- 看清短期轨迹记忆如何影响输入上下文

## 十二、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，说明 Agent 主线的第一轮理解已经过关：

1. `PromptAgent` 是怎么根据 observation_type 选择 prompt 模板的？
2. accessibility tree 为什么要先线性化？
3. 当前 observation 是怎么进 `messages` 的？
4. 历史轨迹是怎么被裁剪并拼进上下文的？
5. `call_llm()` 和 `predict()` 的职责边界是什么？
6. 为什么 `pyautogui` 和 `computer_13` 需要不同解析器？
7. `reset()` 为什么必须在每个任务开始时调用？

## 十三、下一步该读什么

如果继续沿主线往下，最自然的下一步不是再看别的 agent，而是看：

- 任务主循环如何把 `env` 和 `agent` 串起来

也就是：

- [lib_run_single.py](../../lib_run_single.py)
- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

因为到这一步，你已经分别理解了：

- 环境如何工作
- Agent 如何工作

接下来最值得做的，就是把二者放回真实运行入口里重新看一遍。
