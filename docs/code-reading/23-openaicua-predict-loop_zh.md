# 23 OpenAICUAAgent 推理主循环解读

这一篇接在 [22 OpenAICUAAgent 最小实践与可运行 Demo](./22-openaicua-demo-practice_zh.md) 后面看最合适。

上一篇解决的是：

- 这条 special-case 链路怎么跑起来
- demo runner 为什么必须单独写
- 需要哪些环境变量和启动参数

这一篇解决的是：

- `OpenAICUAAgent.predict(...)` 到底在做什么
- 为什么它要自己维护 `self.cua_messages`
- `computer_call` / `computer_call_output` 是怎么配对起来的
- `state_correct`、`messages`、`actions` 各自代表什么
- 它和 `PromptAgent` / `SeedAgent` 的核心差异到底在哪里

为了降低复杂度，这一篇只聚焦三处代码：

- [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
- [lib_run_single.py](../../lib_run_single.py)
- [scripts/python/run_openaicua_demo.py](../../scripts/python/run_openaicua_demo.py)

## 先记住 `OpenAICUAAgent` 侧主线

围绕 `OpenAICUAAgent`，最应该先记住的是这条链：

`OpenAICUAAgent(env=env) -> reset() -> predict(instruction, obs) -> _create_response() -> _handle_item(...) -> step(action) -> env.step(...)`

和前面两个 agent 最大的不同是：

- `PromptAgent` / `SeedAgent`
  主要负责“生成动作”
- `OpenAICUAAgent`
  既负责“生成动作”，也负责“把 OpenAI computer use 协议继续推进一轮”

所以拼到运行器侧以后，真实链路是：

`run_openaicua_demo.py -> run_single_example_openaicua(...) -> agent.predict(...) -> agent.step(...) -> env.step(...)`

而不是标准的：

`runner -> agent.predict(...) -> env.step(...)`

## 一、这个类为什么天然是 special-case

第一次读 [openai_cua_agent.py](../../mm_agents/openai_cua_agent.py) 时，最容易忽略的点有两个。

### 1. 构造函数直接拿了 `env`

对应代码：

- [openai_cua_agent.py:203](../../mm_agents/openai_cua_agent.py#L203)

这说明它不是纯推理层，而是：

- 一边持有模型会话状态
- 一边持有环境执行句柄

### 2. 它维护的是“协议会话”，不只是普通历史

这个类里最关键的状态其实不是：

- `self.thoughts`
- `self.actions`
- `self.observations`

而是：

- `self.cua_messages`

因为真正发给 OpenAI Responses API 的输入不是一段临时 prompt，而是：

- 一整段持续增长的多轮协议消息

你可以把 `self.cua_messages` 理解成：

- 当前这个 computer use 会话的上下文日志

## 二、先看构造函数里真正重要的状态

对应代码：

- [openai_cua_agent.py:203](../../mm_agents/openai_cua_agent.py#L203)

第一次阅读时，可以把 `__init__` 理解成 4 件事。

### 1. 保存环境和模型参数

最值得先记住的是这些字段：

- `self.env`
- `self.model`
- `self.max_tokens`
- `self.action_space`
- `self.observation_type`
- `self.screen_width`
- `self.screen_height`

这里和前两个 agent 最大的不同还是：

- `self.env` 直接保存在 agent 内部

### 2. 组装 OpenAI computer use tool 描述

对应代码里的：

```python
self.tools = [{
    "type": "computer_use_preview",
    "display_width": self.screen_width,
    "display_height": self.screen_height,
    "environment": "linux" if platform == "ubuntu" else "windows"
}]
```

这不是 OSWorld 的 action schema，而是：

- 发给 OpenAI Responses API 的 tool 声明

也就是说，这个 agent 会先让 OpenAI 产出：

- `computer_call`

然后再由本地代码把它翻译成 OSWorld 可执行动作。

### 3. 处理客户端密码

这里会根据 provider 推导默认密码：

- `aws` 默认 `osworld-public-evaluation`
- 其他 provider 默认 `password`

后面 `predict(...)` 会把这个密码拼进 `OPERATOR_PROMPT`。

### 4. 选择系统提示词

虽然这份文件里根据 `observation_type` 和 `action_space` 也会设置：

- `self.system_message`

但当前 `OpenAICUAAgent` 的主路径里，真正直接喂给 OpenAI Responses API 的核心输入，还是：

- `self.cua_messages`
- `OPERATOR_PROMPT`

所以你现在更应该优先关注消息会话结构，而不是先钻系统 prompt 细节。

## 三、`self.cua_messages` 是这条线最重要的状态

这一节是整篇最关键的部分。

`OpenAICUAAgent` 的会话历史主要会出现 3 类消息。

### 1. 首轮 `user` 消息

对应代码：

- [openai_cua_agent.py:663](../../mm_agents/openai_cua_agent.py#L663)

第一次 `predict(...)` 时，如果 `self.cua_messages` 还是空的，就会塞入：

```python
{
    "role": "user",
    "content": [
        {
            "type": "input_image",
            "image_url": "data:image/png;base64,..."
        },
        {
            "type": "input_text",
            "text": instruction + prompt
        }
    ]
}
```

这条消息表达的是：

- 当前屏幕长什么样
- 当前任务目标是什么
- 操作约束和密码提示是什么

注意这里和 `PromptAgent` / `SeedAgent` 不一样：

- 它不是每轮都重新拼一个“大 prompt”
- 而是只在首轮建立一次会话入口

### 2. 模型返回的 `response.output`

对应代码：

- [openai_cua_agent.py:680](../../mm_agents/openai_cua_agent.py#L680)

每次 `_create_response()` 成功后，都会做：

```python
self.cua_messages += response.output
```

也就是说，模型返回的这些 item 会直接并入会话历史。

这些 item 里可能包含：

- `reasoning`
- `message`
- `computer_call`

后面 `predict(...)` 会再逐项解析它们。

### 3. 本地执行后的 `computer_call_output`

对应代码：

- [openai_cua_agent.py:777](../../mm_agents/openai_cua_agent.py#L777)

`agent.step(action)` 执行完 OSWorld 动作以后，会往 `self.cua_messages` 末尾追加：

```python
{
    "type": "computer_call_output",
    "call_id": action["call_id"],
    "acknowledged_safety_checks": action["pending_checks"],
    "output": {
        "type": "input_image",
        "image_url": "data:image/png;base64,..."
    }
}
```

这条消息的作用不是给 OSWorld 用，而是告诉 OpenAI：

- 你刚才发出的那次 `computer_call` 已经执行完了
- 这是执行后的最新屏幕

所以这条线的协议节奏其实是：

`user screenshot -> model computer_call -> local env.step -> computer_call_output with new screenshot -> model next computer_call`

## 四、`_resolve_openai_client()` 和 `_create_response()` 负责发起下一轮协议

对应代码：

- [openai_cua_agent.py:286](../../mm_agents/openai_cua_agent.py#L286)
- [openai_cua_agent.py:298](../../mm_agents/openai_cua_agent.py#L298)

### 1. `_resolve_openai_client()` 做了什么

它做的事情很直接：

- 读取 `OPENAI_API_KEY_CUA`
- 如果没有，再回退读 `OPENAI_API_KEY`
- 如有需要，再读取 `OPENAI_BASE_URL_CUA` 或 `OPENAI_BASE_URL`

所以它解决的是：

- 当前这次调用要连哪个 OpenAI 兼容端点

### 2. `_create_response()` 真正发的是什么

这一步最关键的代码是：

```python
response = client.responses.create(
    model=self.model,
    input=self.cua_messages,
    tools=self.tools,
    reasoning={"summary": "concise"},
    truncation="auto",
    max_output_tokens=self.max_tokens,
)
```

这里最值得记住的是：

- `input` 不是本轮临时消息，而是 `self.cua_messages`
- `tools` 是 `computer_use_preview`
- `response` 不是单纯文本，而是一组结构化 output item

### 3. 为什么这里有重试和截图更新

`_create_response()` 的异常分支里会：

1. 重新从环境抓一次截图
2. 更新 `self.cua_messages` 最后一条消息里的图片
3. 等待 5 秒后重试

这说明它默认假设：

- 请求失败时，屏幕状态可能已经变化
- 下一次继续请求前，至少应该让会话里的最后一张图保持最新

如果最后一条消息是：

- `user`

它就更新 `content` 里的 `input_image`。

如果最后一条消息是：

- `computer_call_output`

它就更新 `output.image_url`。

这也是为什么 `self.cua_messages` 必须是结构化消息，而不能只是字符串历史。

## 五、`_handle_item(...)` 负责把响应 item 分流

对应代码：

- [openai_cua_agent.py:353](../../mm_agents/openai_cua_agent.py#L353)

这一步可以理解成一个小型分发器。

### 1. 遇到 `message`

如果 `item.type == "message"`，它会尝试取出：

- `output_text`

然后返回普通字符串。

这类内容主要用于：

- 给日志看
- 拼成最后的 `predict_info["response"]`

### 2. 遇到 `reasoning`

如果 `item.type == "reasoning"`，它会取出：

- `summary_text`

然后也返回普通字符串。

所以当前主路径里，`reasoning` 不是拿来执行的，而是：

- 作为模型中间解释文本被保留下来

### 3. 遇到 `function_call`

当前直接忽略，返回 `None`。

也就是说，当前这个 agent 的最小可运行路径并没有额外处理：

- 一般函数工具调用

### 4. 遇到 `computer_call`

这是最重要的分支。

它会做 3 件事：

1. 读出 `item.action.type`
2. 把 action 对象上的字段收集进 `action_args`
3. 调 `_convert_cua_action_to_pyautogui_action(...)`

如果转换成功，就返回一个 action dict：

```python
{
    "action_space": "pyautogui",
    "action": "...python code...",
    "pending_checks": item.pending_safety_checks,
    "call_id": item.call_id
}
```

你可以把它理解成：

- OpenAI 协议动作
  被翻译成了
- OSWorld 可执行动作

## 六、`_convert_cua_action_to_pyautogui_action(...)` 是协议翻译层

对应代码：

- [openai_cua_agent.py:411](../../mm_agents/openai_cua_agent.py#L411)

这是 `OpenAICUAAgent` 和 `PromptAgent` / `SeedAgent` 最不一样的一层。

前两个 agent 的典型路径是：

- 模型直接输出代码或动作描述

而这里是：

- 模型先输出 `computer_call`
- 本地再把它翻译成 `pyautogui` 代码

### 1. 当前已经支持的典型动作

这层已经覆盖了常见 GUI 基元：

- `click`
- `double_click`
- `type`
- `keypress`
- `scroll`
- `move`
- `drag`
- `wait`
- `screenshot`

### 2. 转换后的结果长什么样

例如 `click(x=42, y=24)` 会被翻成：

```python
import pyautogui
pyautogui.moveTo(42, 24)
pyautogui.click(button='left')
```

这也是前面 mock 验证时真正跑通的一段最小动作。

### 3. 为什么这个转换层很关键

如果你未来要把这条链接到自定义模型或自定义协议，最容易动的地方其实不是 runner，而是这里。

因为你真正需要回答的是：

- 模型输出的结构化动作，如何落成 OSWorld 当前 action space 能执行的代码

这一步答对了，后面 `env.step(...)` 才能继续跑。

## 七、`predict(...)` 是整个 agent 的核心

对应代码：

- [openai_cua_agent.py:656](../../mm_agents/openai_cua_agent.py#L656)

如果你只反复读一个方法，就读这里。

可以把它拆成 8 步。

### 1. 先补操作提示词

开头先做：

```python
prompt = OPERATOR_PROMPT.format(CLIENT_PASSWORD=self.client_password)
```

也就是说，每轮真正带进去的任务上下文里，都会包含：

- 客户端密码
- 浏览器偏好
- 不要反复确认
- 可以声明 infeasible

### 2. 把当前截图转成 base64

对应代码里的：

```python
base64_image = encode_image(obs["screenshot"])
```

因为 OpenAI computer use 输入图片时，需要的是：

- `data:image/png;base64,...`

### 3. 仅在首轮创建用户入口消息

这一步非常关键。

只有当：

- `self.cua_messages == []`

时，才会创建首轮 `user` 消息。

所以第二轮开始，`predict(...)` 并不会重新塞一条新的 `user screenshot + instruction`。

它默认依赖的是：

- 上一轮保存在 `self.cua_messages` 里的完整协议上下文

### 4. 调 `_create_response()` 取本轮模型输出

这里会记录一次 `model_timer`，最后写进：

- `predict_info["model_usage"]`

这对后面看结果目录、排查耗时很有用。

### 5. 把 `response.output` 并入历史

这一步就是：

```python
self.cua_messages += response.output
```

注意顺序：

- 先拿到返回
- 再把返回写回历史
- 再逐项解析

也就是说，`predict_info["messages"]` 里拿到的是：

- 当前轮已经包含模型输出后的完整会话

### 6. 逐项解析 `response.output`

这一段循环会同时维护：

- `actions`
- `responses`
- `action_exit`
- `thought_exit`
- `message_exit`
- `infeasible_message`

这里最值得注意的是两个分支。

第一，如果模型文本里包含：

- `infeasible`
- `unfeasible`
- `impossible`
- `not feasible`
- `cannot be done`

就会直接压入一个：

- `FAIL`

动作，并把 episode 视为不可继续。

第二，如果 `_handle_item(...)` 解析出的是 action dict，就会加入：

- `actions`

否则就进入：

- `responses`

### 7. 计算 `state_correct`

这是很多人第一次读这条线最容易混淆的字段。

当前代码里的核心规则很简单：

```python
if action_exit and not infeasible_message:
    state_correct = True
```

也就是说，现在的 `state_correct` 主要表达的是：

- 本轮模型是否成功给出了至少一个可执行 `computer_call`
- 并且没有明确宣告 infeasible

它不是：

- 任务是否完成
- evaluator 是否判分成功
- 当前动作是否一定执行正确

### 8. 组装 `predict_info`

最后返回的是：

```python
predict_info = {
    "model_usage": {...},
    "messages": self.cua_messages,
    "response": "...",
    "state_correct": state_correct,
}
```

再加上：

- `actions`

所以 `predict(...)` 的返回值本质上是：

- 一份本轮推理诊断信息
- 一组准备执行的动作

## 八、`state_correct` 到底控制了什么

这一点要结合 [lib_run_single.py](../../lib_run_single.py) 一起看。

对应代码：

- [lib_run_single.py:226](../../lib_run_single.py#L226)

在 `run_single_example_openaicua(...)` 里，拿到返回后会立刻做：

```python
done = not response.get('state_correct', False)
```

这意味着：

- 如果这一轮没有产出有效动作
- 或者模型直接说 infeasible

runner 会把 episode 停下来。

所以你可以把 `state_correct` 理解成：

- “这个 special-case 协议当前还能不能继续下一轮”

而不是传统意义上的：

- “当前状态是否正确”

## 九、`step(...)` 才是这条线和标准 agent 彻底分叉的地方

对应代码：

- [openai_cua_agent.py:748](../../mm_agents/openai_cua_agent.py#L748)

这一步可以拆成 4 件事。

### 1. 把 action dict 包成 `Action`

当前传进来的 `action` 一般长这样：

```python
{
    "action_space": "pyautogui",
    "action": "...python code...",
    "pending_checks": [...],
    "call_id": "..."
}
```

然后它会做：

```python
step_action = Action(action.get("action", ""), self.action_space)
```

### 2. 真正调用环境执行

随后执行：

```python
obs, reward, terminated, info = self.env.step(step_action.get_action())
```

这里才真正进入：

- OSWorld controller
- guest server
- 虚拟机桌面动作执行

### 3. 把执行后的 screenshot 回灌进协议历史

这一步是 `OpenAICUAAgent` 最特殊的能力：

```python
self.cua_messages.append({
    "type": "computer_call_output",
    "call_id": action["call_id"],
    "acknowledged_safety_checks": action["pending_checks"],
    "output": {
        "type": "input_image",
        "image_url": f"data:image/png;base64,{screenshot_base64}",
    },
})
```

这说明 `step(...)` 不是单纯执行动作，而是在执行完动作后，顺手把：

- 最新屏幕
- 对应的 `call_id`
- 已确认的 safety checks

继续写回 OpenAI 协议上下文。

### 4. 返回环境观测和 step 信息

最终它返回：

- `obs`
- `reward`
- `terminated`
- `info`
- `step_info`

其中 `step_info` 里还额外记了：

- `step_time`
- `action`

## 十、为什么 `computer_call_output` 这么关键

如果只看一轮代码，很容易低估这条消息的重要性。

但从协议角度看，它其实相当于：

- 本地执行结果回执

没有它，下一轮 OpenAI model 只知道：

- 自己发过一个 `computer_call`

却不知道：

- 这个动作有没有真的执行
- 执行后屏幕变成了什么样

所以这条链的闭环不是：

`predict -> env.step`

而是：

`predict -> computer_call -> env.step -> computer_call_output -> next predict`

这就是为什么它必须自己维护 `messages`，也必须自己实现 `step(...)`。

## 十一、和 `PromptAgent` / `SeedAgent` 的差异，应该怎么抓

这一节你可以当成复习总表。

### 1. 输入组织方式不同

- `PromptAgent` / `SeedAgent`
  更像“每轮按模板拼 prompt”
- `OpenAICUAAgent`
  更像“维护一个持续增长的协议会话”

### 2. 模型输出形态不同

- `PromptAgent`
  常见是代码块或动作文本
- `SeedAgent`
  常见是 XML / tool-call 风格片段
- `OpenAICUAAgent`
  是 Responses API 的结构化 output item

### 3. 动作执行责任不同

- `PromptAgent` / `SeedAgent`
  runner 拿到动作后直接 `env.step(...)`
- `OpenAICUAAgent`
  先 `agent.step(...)`，再由 agent 内部转调 `env.step(...)`

### 4. 会话状态保存位置不同

- `PromptAgent` / `SeedAgent`
  主要保存轨迹、截图历史、文本历史
- `OpenAICUAAgent`
  额外必须保存协议消息 `self.cua_messages`

## 十二、这次 mock 验证到底证明了什么

因为当前本地环境里没有可直接使用的 OpenAI key，这条线没有做 live 的 OpenAI 实网冒烟。

但已经做过一次 mock 验证，至少证明了下面这条最核心的链是通的：

`predict(...) -> _handle_item(...) -> _convert_cua_action_to_pyautogui_action(...) -> agent.step(...) -> env.step(...)`

当 mock 返回一个：

- `click(x=42, y=24)`

时，最终被翻成了：

```python
import pyautogui
pyautogui.moveTo(42, 24)
pyautogui.click(button='left')
```

并且验证到了这些关键结果：

- `state_correct = True`
- `action_count = 1`
- `messages_len = 5`

所以当前更准确的结论不是：

- 这条线完整 live 跑通过了

而是：

- 这条线的 special-case 主循环和协议闭环已经被本地验证通了
- 只差真实 OpenAI key 就能继续做 live 冒烟

## 十三、如果你未来要接自定义模型，最先改哪

如果你的目标是“不是用 OpenAI 官方 computer use，而是接自己的兼容模型”，最该先看的是这三层。

### 1. 客户端接入层

先看：

- `_resolve_openai_client()`
- `_create_response()`

这里决定：

- key 从哪读
- base URL 指向哪里
- 请求参数怎么发

### 2. 响应解析层

再看：

- `_handle_item(...)`

这里决定：

- 你的兼容模型返回的数据结构，要怎么拆成 message / reasoning / action

### 3. 协议转动作层

最后看：

- `_convert_cua_action_to_pyautogui_action(...)`

这里决定：

- 你的结构化动作，如何真正落成 OSWorld 可执行动作

如果这三层都能对齐，那么这条线通常不需要大改：

- `run_openaicua_demo.py`
- `run_single_example_openaicua(...)`

## 十四、这一篇读完后，你应该能回答的问题

如果下面这些问题你都能回答，说明你已经抓住了 `OpenAICUAAgent` 的主干。

1. 为什么 `OpenAICUAAgent` 必须走专用 runner？
2. `self.cua_messages` 里最关键的三类消息分别是什么？
3. `computer_call` 和 `computer_call_output` 是怎么形成闭环的？
4. `state_correct` 控制的到底是什么？
5. `predict(...)` 返回的 `messages`、`response`、`actions` 各自代表什么？
6. 如果要接兼容模型，应该优先改哪三层？

## 一句话建议

理解 `OpenAICUAAgent` 时，不要把它当成“另一个 prompt agent”。

更准确的理解应该是：

- 它是一个“持有 env 的协议桥接器”
- 一头连 OpenAI computer use output item
- 一头连 OSWorld 的 `pyautogui` 执行链
