# 21 SeedAgent 推理主循环解读

这一篇接在 [20 SeedAgent 最小实践与可运行 Demo](./20-seed-agent-demo-practice_zh.md) 后面看最合适。

如果说上一篇解决的是：

- `SeedAgent` 怎么真正跑起来
- 缺什么依赖
- 最小 demo 命令怎么写

那这一篇解决的是：

- `SeedAgent.predict(...)` 具体在干什么
- 它怎么组织消息
- Ark 返回之后怎么变成动作
- 它和 `PromptAgent` 的核心差异到底在哪里

为了降低复杂度，这一篇只聚焦主文件：

- [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)

## 先记住 `SeedAgent` 侧主线

围绕 `SeedAgent`，最应该先记住的是这条链：

`SeedAgent(...) -> reset() -> predict(instruction, obs) -> inference_with_thinking_ark(messages) -> parse_xml_action_v3(response) -> parsing_response_to_pyautogui_code(...)`

和环境主线拼在一起，就是：

`env.reset(...) -> obs -> agent.predict(...) -> actions -> env.step(...)`

也就是说，`SeedAgent` 的职责也仍然只有两件事：

1. 把 observation 组织成模型能理解的多轮消息
2. 把模型返回的 Seed 风格 tool-call 翻译回环境能执行的动作

## 一、先看文件结构

建议你第一次读 [seed_agent.py](../../mm_agents/seed_agent.py) 时，不要直接从 `class SeedAgent` 往下读，而是先看文件前半部分。

这个文件大致可以分成四层：

1. 常量和 tool schema
2. 消息微调函数
3. `SeedAgent` 主体
4. 推理与动作解析主循环

### 1. 顶部常量

最值得先记住的是这些：

- `FINISH_WORD = "finished"`
- `WAIT_WORD = "wait"`
- `CALL_USER = "call_user"`
- `INFEASIBLE = "infeasible"`

这些常量的意义不是 prompt 展示，而是模型输出解析后的控制分支。

也就是说，`SeedAgent` 后面会根据这些动作类型判断：

- 是继续执行动作
- 还是提前结束
- 还是直接失败

### 2. `GUI_TOOL_SCHEMAS`

对应代码就在文件前半部分。

它的作用不是直接执行动作，而是：

- 告诉模型当前允许调用哪些工具
- 给解析器一个“预期参数结构”

这里定义的常见动作包括：

- `click`
- `left_double`
- `right_single`
- `drag`
- `scroll`
- `move_to`
- `mouse_down`
- `mouse_up`
- `type`
- `hotkey`
- `press`
- `release`
- `finished`
- `call_user`
- `wait`
- `infeasible`

### 3. `modify_conversations(...)`

这个函数很小，但作用明确：

- 如果消息里带的是图片
- 就把 `image_url.detail` 强制改成 `high`

所以它的角色不是业务逻辑，而是：

- 在真正发给模型前做一次消息格式微调

## 二、`SeedAgent.__init__` 做了什么

对应代码：

- [seed_agent.py:366](../../mm_agents/seed_agent.py#L366)

第一次读时，可以把 `__init__` 理解成 4 件事：

1. 保存模型和采样参数
2. 初始化轨迹缓存
3. 设定系统 prompt
4. 固定推理入口

### 1. 真正会影响当前主路径的参数

当前最值得记住的是这些：

- `model`
- `top_p`
- `temperature`
- `max_tokens`
- `history_n`
- `resize_image`
- `resized_image_width`
- `resized_image_height`

其中最影响当前行为的，是：

- `history_n`
- `resize_image`
- `model`

### 2. 当前主路径里“名字存在，但暂时没真正生效”的参数

这一点很重要，因为很容易看参数名就误解行为。

当前代码里：

- `max_trajectory_length`
  会保存到 `self.max_trajectory_length`，但当前 `predict(...)` 主路径没有真正使用它裁剪上下文
- `use_thinking`
  会保存到 `self.use_thinking`，但当前主路径仍然固定调用 `inference_with_thinking_ark(...)`
- `model_type`
  会保存到 `self.model_type`，但当前最小 demo 主路径里没有再用它切换推理分支

所以你现在更准确的理解应该是：

- 这些字段更像“保留位”
- 当前最小可运行路径的真实行为，主要由 `self.inference_func = self.inference_with_thinking_ark` 决定

### 3. 内部缓存是什么

`SeedAgent` 内部维护了五组状态：

- `self.thoughts`
- `self.actions`
- `self.observations`
- `self.history_images`
- `self.history_responses`

它们的意义可以理解成：

- `history_images`
  最近喂给模型看的截图历史
- `history_responses`
  模型历史回复原文
- `observations / thoughts / actions`
  当前 agent 自己维护的并行轨迹

## 三、`reset(...)` 做了什么

对应代码：

- [seed_agent.py:432](../../mm_agents/seed_agent.py#L432)

这个方法很短，但不能跳过。

它做了两件关键事情：

### 1. 接住运行期 logger 和最新的 VM IP

runner 在每个任务开始前会调用：

- `agent.reset(runtime_logger, vm_ip=env.vm_ip)`

所以这里不是简单清空状态，还顺手把：

- 最新 logger
- 最新 guest IP

同步进 agent。

### 2. 清空历史缓存

它会把下面几组缓存全部清空：

- `thoughts`
- `actions`
- `observations`
- `history_images`
- `history_responses`

所以 `SeedAgent` 每次新任务开始时，内部历史都是干净的。

## 四、`predict(...)` 才是真正核心

对应代码：

- [seed_agent.py:580](../../mm_agents/seed_agent.py#L580)

如果你只想吃透 `SeedAgent`，这个方法最值得反复读。

可以把它拆成 8 步。

## 五、步骤 1：补任务指令和 sudo 密码

开头先做：

```python
self.task_instruction = task_instruction + f"\nThe sudo password is osworld-public-evaluation"
```

这说明 `SeedAgent` 和 `PromptAgent` 一样，也会把任务目标直接扩进输入里。

但它不是写进 system prompt 模板，而是直接拼在 task instruction 后面。

## 六、步骤 2：校验三组并行轨迹长度

接着会做一个断言：

```python
assert len(self.observations) == len(self.actions) and len(self.actions) == len(self.thoughts)
```

这一步的目的很直接：

- 防止历史 observation、历史 thought、历史 action 不同步

因为后面消息回放时，这三组历史默认应该是一一对应的。

## 七、步骤 3：处理当前 screenshot

这一段做了三件事。

### 1. 把二进制截图转成 base64

如果 `obs["screenshot"]` 是 bytes，就先做 base64 编码。

这一步是为了后面能塞进：

- `data:image/png;base64,...`

这种 image_url 消息。

### 2. 读取当前截图宽高

代码会把截图重新读成 `PIL.Image`，拿到：

- `width`
- `height`

后面把 `<point>x y</point>` 转成 `pyautogui` 坐标时，会用到这两个值。

### 3. 可选 resize

如果 `self.resize_image` 为真，就会把当前图片 resize 后再编码。

这意味着当前 `SeedAgent` 内部缓存的截图，不一定是环境返回的原始分辨率截图，而可能是它自己缩放过的版本。

## 八、步骤 4：更新本地历史

这一步会先把当前截图放入：

- `self.history_images`

然后把当前 observation 以内部格式保存到：

- `self.observations`

保存形式是：

```python
{"screenshot": screenshot, "accessibility_tree": None}
```

这里有一个很关键的认知：

- `SeedAgent` 当前主路径只真正使用 screenshot
- 它没有像 `PromptAgent` 那样去消费 `a11y_tree`

### `history_n` 才是当前真正的历史裁剪参数

接着它会做：

```python
if len(self.history_images) > self.history_n:
    self.history_images = self.history_images[-self.history_n:]
```

这说明当前真正起裁剪作用的是：

- `history_n`

而不是 `max_trajectory_length`。

## 九、步骤 5：构造 messages 起始骨架

这一步先放进去 3 条消息：

1. 第一条 `system`
   就是 `self.system_prompt`
2. 第二条 `system`
   是超长的 function definition 和输出格式说明
3. 第三条 `user`
   是当前任务 instruction

这就是 `SeedAgent` 和 `PromptAgent` 很不一样的地方。

### 1. 它把工具定义直接塞进第二条 `system` 消息

也就是说，工具规范不是一个独立 schema 通过 API 传给模型，而是直接放进 prompt 文本中。

### 2. 它明确要求模型输出特殊 XML 结构

第二条 `system` 里已经告诉模型必须按这种格式输出：

```text
<think_never_used_...>...</think_never_used_...>
<seed:tool_call_never_used_...>
  <function_never_used_...=click>
    <parameter_never_used_...=point><point>x y</point></parameter_never_used_...>
  </function_never_used_...>
</seed:tool_call_never_used_...>
```

所以后面的解析器本质上是在解析它自己前面定义过的输出协议。

## 十、步骤 6：把历史 response 和截图回放进 messages

这一段是 `SeedAgent.predict(...)` 最值得慢慢对照的一段。

逻辑上分两种情况：

### 1. 没有历史 response

如果这是当前任务的第一步，就只追加一条：

- `role = "tool"`
- 内容是当前截图

### 2. 已经有历史 response

如果已经不是第一步，它会：

1. 逐条回放历史 response
2. 在需要的位置补历史截图
3. 最后再补当前截图

具体消息形态是：

- 历史截图用 `tool` 消息
- 历史回复用 `assistant` 消息

而且 `assistant` 消息会被拆成两块：

- `content`
  放 `</think...>` 之后的工具调用内容
- `reasoning_content`
  放 `<think...>` 里的推理内容

这说明 `SeedAgent` 的历史回放不是纯文本拼接，而是：

- 有意识地把“思考”和“动作调用”拆开保留

## 十一、步骤 7：调用 Ark 推理

在真正请求模型之前，会先经过：

- `modify_conversations(messages)`

它会把图片 detail 统一改成 `high`。

然后进入一个最多 3 次的重试循环：

```python
prediction = self.inference_func(messages)
```

而当前 `self.inference_func` 固定指向：

- `inference_with_thinking_ark(...)`

### `inference_with_thinking_ark(...)` 真正在做什么

对应代码：

- [seed_agent.py:505](../../mm_agents/seed_agent.py#L505)

它的核心逻辑可以概括成 4 步：

1. 从环境变量读取 `DOUBAO_API_KEY` 和 `DOUBAO_API_URL`
2. 创建 `Ark(base_url=api_url, api_key=api_key)`
3. 调 `vlm.chat.completions.create(...)`
4. 把流式返回的 `reasoning_content` 和 `content` 手工拼成一个最终字符串

这里最关键的一点是：

- 它不是直接返回 SDK 的结构化对象
- 而是自己拼出一个带 `<think_never_used_...>` 标签的字符串

这样后面的 `parse_xml_action_v3(...)` 才能继续按统一格式解析。

## 十二、步骤 8：解析模型输出并转成动作

拿到 `prediction` 之后，`SeedAgent` 会先把原始文本保存进：

- `self.history_responses`

然后进入解析阶段。

### 1. 先用 `parse_xml_action_v3(...)` 取出结构化动作

解析结果大致长这样：

```python
[
  {
    "function": "click",
    "parameters": {
      "point": "<point>988 117</point>"
    }
  }
]
```

### 2. 特殊控制动作先提前返回

如果解析出来的是这些动作：

- `finished`
- `wait`
- `error_env`
- `call_user`
- `infeasible`

就不会继续转成 `pyautogui` 点击，而是直接返回：

- `["DONE"]`
- `["WAIT"]`
- `["FAIL"]`

### 3. 普通 GUI 动作再转成 `pyautogui`

普通动作会先被整理成：

```python
{
  "action_type": "...",
  "action_inputs": {...}
}
```

然后交给：

- `parsing_response_to_pyautogui_code(...)`

最终得到能直接喂给 `env.step(...)` 的 Python 代码字符串。

## 十三、这次真实运行时看到的模型输出长什么样

这次 smoke test 的 [traj.jsonl](../../results/seed-agent-demo-smoke/pyautogui/screenshot/doubao-seed-2-0-pro-260215/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4/traj.jsonl) 里，第一步记录的是：

```text
<think_never_used_...>
Got it, let's see...
</think_never_used_...>
<seed:tool_call_never_used_...>
  <function_never_used_...=click>
    <parameter_never_used_...=point><point>988 117</point></parameter_never_used_...>
  </function_never_used_...>
</seed:tool_call_never_used_...>
```

随后被转成的实际动作是：

```python
import pyautogui
import time
pyautogui.click(988.0, 117.0, button='left')
```

这正好把 `SeedAgent` 的两层职责对应起来了：

1. 先产生 Seed 风格 tool-call
2. 再翻译成 OSWorld 可执行动作

## 十四、`SeedAgent` 和 `PromptAgent` 最核心的不同是什么

如果只抓最关键的差异，可以记这 4 条。

### 1. `PromptAgent` 更像 prompt 适配器

它更强调：

- 不同 observation_type
- 不同 action_space
- 不同模型后端

### 2. `SeedAgent` 更像“自带协议”的完整 agent

它不只是换个 prompt，而是自己定义了：

- 思考标签
- tool-call 标签
- 历史图片回放方式
- 工具调用解析协议

### 3. `PromptAgent` 输出更接近代码块或 JSON

而 `SeedAgent` 输出更接近：

- 自定义 XML 风格工具调用

### 4. `SeedAgent` 的内部自由度更高

但外部接口仍然保持标准兼容：

- `reset(...)`
- `predict(...) -> (response, actions)`

这也是它最值得你研究的地方。

## 十五、如果你要继续改 `SeedAgent`，优先应该改哪里

如果你后面要把 `SeedAgent` 继续往正式接入推进，最值得优先看的地方是这几处。

### 1. 先看 `predict(...)`

这是主循环核心。

如果你想改：

- 历史保留策略
- 消息组织方式
- 是否带更多上下文

优先看这里。

### 2. 再看 `inference_with_thinking_ark(...)`

如果你想改：

- 模型后端
- 是否流式
- reasoning 参数
- API 兼容方式

优先看这里。

### 3. 最后看 `ui_tars/action_parser.py`

如果你想改：

- 工具调用协议
- 新动作类型
- 坐标解析
- `pyautogui` 转换逻辑

优先看这里。

## 十六、这一篇之后，下一步最合适做什么

如果你继续往下学，最自然的方向有两个：

1. 直接对照 [seed_agent.py](../../mm_agents/seed_agent.py) 逐段看代码
   重点盯 `predict(...)` 和 `inference_with_thinking_ark(...)`
2. 开始思考你自己的 agent 更像哪条路线
   - 更像 `PromptAgent` 这种“换模型适配层”
   - 还是更像 `SeedAgent` 这种“内部协议自定义很重，但外部接口不变”

也就是说，这一篇的价值不是再教你“怎么运行”，而是帮你把 `SeedAgent` 的代码结构和运行时行为真正对上。
