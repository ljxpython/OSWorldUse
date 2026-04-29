# 04 PromptAgent 最小练手例子

这篇不再讲大段架构，而是给你一个最小、可重复、可观察的练习。

目标只有一个：

先把 `PromptAgent` 单独玩明白。

这里故意不依赖 VM，不依赖 benchmark 全流程，也不要求你先配模型 API Key。

## 这个练习能帮你掌握什么

跑完这一个小例子，你应该能直观看到：

1. `PromptAgent` 接收的 `obs` 长什么样
2. `predict(instruction, obs)` 会组装出什么 `messages`
3. 模型回复为什么必须是代码块格式
4. `parse_code_from_string()` 是怎么把回复变成 `pyautogui` 动作的

这个练习不解决“Agent 是否真的会做桌面任务”，它只解决“Agent 这层代码到底怎么工作”。

## 我给你准备的最小脚本

新加的脚本在这里：

- [scripts/python/prompt_agent_minimal_demo.py](../../scripts/python/prompt_agent_minimal_demo.py)

它默认使用：

- `observation_type="screenshot"`
- `action_space="pyautogui"`
- `mock` 模式

也就是说：

- 你只需要提供一张截图
- 脚本会构造 `PromptAgent`
- 它会把 prompt payload 打印出来
- 然后用一段假模型回复走完整个解析流程

这样你不用先配 API key，也能把主线吃透。

## 一、准备一张截图

你可以用任意一张本地 PNG/JPG：

- 桌面截图
- 浏览器截图
- 系统设置截图
- 甚至随便一张 GUI 图片

这个例子的重点不是任务正确性，而是 Agent 的输入输出结构。

假设你的图片是：

```text
/Users/yourname/Desktop/demo.png
```

## 二、先用 mock 模式跑

命令：

```bash
uv run python scripts/python/prompt_agent_minimal_demo.py \
  --image /Users/yourname/Desktop/demo.png
```

这条命令会做三件事：

1. 读取图片字节
2. 构造 `PromptAgent`
3. 打印它发给 LLM 的 payload，并返回一个假的模型回复

默认假的模型回复是：

```python
pyautogui.click(320, 240)
pyautogui.write("OSWorld benchmark")
pyautogui.press("enter")
```

然后脚本会继续调用 `parse_actions()`，把它解析成动作列表。

## 三、你应该重点看什么输出

### 1. `Sanitized payload preview`

这里是最值得你认真看的部分。

它会展示：

- `model`
- `max_tokens`
- `top_p`
- `temperature`
- `messages`

尤其是 `messages`，你会看到：

1. 一个 `system` message
2. 一个 `user` message

其中：

- `system` message 来自 `PromptAgent.__init__` 选中的 prompt 模板
- `user` message 来自当前的 screenshot observation

图片内容不会原样打出来，而是被替换成：

```text
[base64 image omitted, N chars]
```

这样你能看结构，不会被超长 base64 干扰。

### 2. `Raw model response`

这一段让你直接看到“模型原始文本长什么样”。

这里最重要的认知是：

- 环境不直接吃自然语言
- `PromptAgent` 也不直接吃自然语言动作描述
- 它要么吃代码块，要么吃 JSON 风格动作

### 3. `Parsed actions`

这一段是 `PromptAgent.parse_actions()` 的结果。

在这个最小例子里，它应该会变成类似：

```json
[
  "pyautogui.click(320, 240)\npyautogui.write(\"OSWorld benchmark\")\npyautogui.press(\"enter\")"
]
```

这一步就是从“模型文本”到“可执行动作”的转换。

## 四、如果你想把 payload 保存成文件

可以加：

```bash
uv run python scripts/python/prompt_agent_minimal_demo.py \
  --image /Users/yourname/Desktop/demo.png \
  --dump-messages /tmp/prompt_agent_payload.json
```

然后你就可以单独打开这个 JSON 文件慢慢看。

这个方式特别适合你：

- 对照 [mm_agents/agent.py](../../mm_agents/agent.py)
- 一边看 `predict()`
- 一边看它实际构造出来的 payload

## 五、接下来怎么做 3 个小改动

跑通默认脚本后，建议你立刻做这 3 个改动。

### 改动 1：换 instruction

把：

```text
Please open the browser and search for OSWorld benchmark.
```

换成你自己的任务，比如：

- `Please click the search box and type hello world.`
- `Please open system settings.`
- `Please focus on the left sidebar.`

目标：

看 instruction 是如何进入 system message 的。

### 改动 2：改 mock response

在脚本里找到：

- [default_mock_response](../../scripts/python/prompt_agent_minimal_demo.py)

改成：

```python
return """```python
pyautogui.moveTo(500, 300)
pyautogui.doubleClick()
```"""
```

目标：

看 `parse_actions()` 如何处理不同代码块。

### 改动 3：故意输出错误格式

把 mock response 改成：

```python
return "Click the search box and type hello."
```

目标：

观察解析失败时会发生什么。

这样你会立刻明白：

- prompt 为什么要严格约束输出格式
- 解析器为什么重要

## 六、如果你想真的调用模型

脚本也支持 live 模式，但我建议你先用 mock 模式练熟。

如果你确实想调真实模型，可以这样：

```bash
export OPENAI_API_KEY=your_key_here

uv run python scripts/python/prompt_agent_minimal_demo.py \
  --image /Users/yourname/Desktop/demo.png \
  --live \
  --model gpt-4o
```

这里要注意：

1. 这不是 benchmark 运行
2. 这不会执行动作，只会做 `predict()`
3. 它只是把截图 + instruction 丢给模型，然后看模型输出什么

所以它是一个很好的“Agent 推理层调试器”。

## 七、这和完整项目主线是什么关系

这个最小例子只覆盖了主线中的一小段：

`obs -> agent.predict() -> prompt -> model response -> parse_actions()`

它没有覆盖：

- `DesktopEnv.reset()`
- `env.step()`
- `env.evaluate()`

也正因为它刻意把环境层拿掉了，所以非常适合练手。

你可以先把 Agent 这层搞明白，再回头把它拼回完整链路。

## 八、建议你边跑边对照看的代码位置

最值得同时打开的几个位置：

- [mm_agents/agent.py:226](../../mm_agents/agent.py#L226)
- [mm_agents/agent.py:289](../../mm_agents/agent.py#L289)
- [mm_agents/agent.py:1110](../../mm_agents/agent.py#L1110)
- [mm_agents/agent.py:1137](../../mm_agents/agent.py#L1137)
- [scripts/python/prompt_agent_minimal_demo.py](../../scripts/python/prompt_agent_minimal_demo.py)

对照方法很简单：

1. 跑脚本
2. 看 payload
3. 找 `predict()`
4. 看 response
5. 找 `parse_actions()`

这样你会比直接死读代码快很多。

## 九、练完这个例子后你应该能回答的问题

如果你跑完并改过几次 mock response，下面这些问题应该都能回答：

1. `obs["screenshot"]` 为什么必须是字节，而不是文件路径？
2. `PromptAgent` 的 prompt 模板是在哪里选中的？
3. 当前 observation 是怎么变成 `messages` 的？
4. 为什么模型回复必须尽量是代码块？
5. `parse_actions()` 为什么能把代码文本解析成动作？
6. 为什么这个小例子不需要 VM 也能帮你学会 Agent 主线？

## 十、下一步怎么继续

如果你把这个小例子跑通了，下一步最自然的不是再加复杂度，而是做这两个选择之一：

1. 回到完整链路：
   `DesktopEnv + PromptAgent + lib_run_single`
2. 继续只在 Agent 层里深入：
   改 observation_type、改 prompt、改 response parser

如果你愿意，我下一步可以继续给你补：

- `05-runner-and-task-loop_zh.md`

专门把 `lib_run_single.py`、`run.py`、`run_multienv.py` 串起来。 
