# 22 OpenAICUAAgent 最小实践与可运行 Demo

这一篇接在 [21 SeedAgent 推理主循环解读](./21-seed-agent-predict-loop_zh.md) 后面看最合适。

前面你已经练过两条标准路径：

- `PromptAgent`
- `SeedAgent`

它们的共同点是：

- runner 创建 env
- runner 调 `agent.predict(...)`
- runner 直接调 `env.step(...)`

而 `OpenAICUAAgent` 不一样。

这一篇最重要的目标，就是把这个“special-case agent”真的落成一个最小 demo，并把它和前两条标准路径的差异讲清楚。

## 一、这次新增和修改了哪些文件

这次实践新增了一个文件，修改了一个文件：

1. [scripts/python/run_openaicua_demo.py](../../scripts/python/run_openaicua_demo.py)
2. [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)

它们的职责分工是：

- `run_openaicua_demo.py`
  提供单任务、单进程、最小可运行的 `OpenAICUAAgent` 入口
- `openai_cua_agent.py`
  继续负责 special-case 的 `predict(...)` 和 `step(...)`

这次没有新建 `OpenAICUADemo(OpenAICUAAgent)` 子类。

原因很简单：

- 这条线的问题不在“模型适配层不够”
- 而在它本来就是一个 special-case agent

## 二、为什么这条线必须专用 runner

这一点你前面在 [17](./17-typical-agent-integration-examples_zh.md) 和 [18](./18-agent-chain-diagrams_zh.md) 里已经见过，但这次要真正把它落到实践里。

### 1. 它在构造时直接拿 `env`

[OpenAICUAAgent](../../mm_agents/openai_cua_agent.py) 构造函数里直接接收：

- `env`

这意味着它不是一个纯“只负责决策”的 agent。

### 2. 它自己实现了 `step(...)`

当前这条链路不是：

```text
agent.predict(...) -> env.step(...)
```

而是：

```text
agent.predict(...) -> agent.step(action) -> env.step(...)
```

所以它不能直接复用标准：

- `run_single_example(...)`

而必须走：

- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example_openaicua(...)`

### 3. 这就是 demo runner 的核心差异

这次新增的 [run_openaicua_demo.py](../../scripts/python/run_openaicua_demo.py) 没有调用标准 rollout，而是显式调用：

- `run_single_example_openaicua(...)`

所以你应该把这条线理解成：

- 标准 env
- 特例 agent
- 特例 rollout

## 三、这次顺手修了哪几个兼容性问题

这次不是只加 runner，还顺手修了几处会影响实际试跑的细节。

### 1. API key 读取现在支持两种环境变量

之前 [openai_cua_agent.py](../../mm_agents/openai_cua_agent.py) 只读：

- `OPENAI_API_KEY_CUA`

这次改成了：

- 优先读 `OPENAI_API_KEY_CUA`
- 如果没有，再回退读 `OPENAI_API_KEY`

也就是说，现在你可以继续沿用仓库原本的专用变量名，也可以直接复用普通 OpenAI key 环境变量。

### 2. 增加了 `OPENAI_BASE_URL_CUA` / `OPENAI_BASE_URL` 的兼容

如果你后面要走代理网关或兼容服务，现在也可以通过：

- `OPENAI_BASE_URL_CUA`
- 或 `OPENAI_BASE_URL`

去覆盖默认 OpenAI base URL。

### 3. Responses API 的 `reasoning` 参数改成了当前更稳的写法

原来代码里用的是：

```python
reasoning={"generate_summary": "concise"}
```

这次改成了：

```python
reasoning={"summary": "concise"}
```

这是为了和当前 OpenAI Responses API 的 computer use 文档写法保持一致。

### 4. `max_tokens` 现在真正传进 API 了

之前 `OpenAICUAAgent.__init__` 明明接收了：

- `max_tokens`

但 `_create_response(...)` 实际没有把它传给 `client.responses.create(...)`。

这次已经补成：

- `max_output_tokens=self.max_tokens`

### 5. 还顺手收了一个小空指针风险

在 `predict(...)` 里，原来对 `message` 项会直接对 `parsed_item.lower()` 操作。

如果 `parsed_item` 不是字符串，就可能抛异常。

这次已经加上了 `isinstance(parsed_item, str)` 的保护。

## 四、最小 demo runner 做了什么

[scripts/python/run_openaicua_demo.py](../../scripts/python/run_openaicua_demo.py) 的结构和前面的 `PromptAgent` / `SeedAgent` demo runner 基本一致，但有两点特殊。

### 1. 启动前先校验 OpenAI key

它会在真正启动 VM 之前先检查：

- `OPENAI_API_KEY_CUA`
- `OPENAI_API_KEY`

如果两个都没有，就直接报错退出。

这样做的目的很直接：

- 避免你在 key 都没配的情况下，先把 VM 拉起来白等几分钟

### 2. 继续复用专用 rollout

它最终调用的是：

- `run_single_example_openaicua(...)`

而不是标准 `run_single_example(...)`

这是这条 demo 和前两个 demo 最大的结构差异。

## 五、这条线的真实调用链是什么

这次最值得你记住的是这条链：

```text
run_openaicua_demo.py
  -> OpenAICUAAgent(env=env)
  -> run_single_example_openaicua(...)
  -> agent.predict(...)
  -> agent.step(action)
  -> env.step(...)
```

和 `PromptAgent` / `SeedAgent` 相比，真正不同的是：

- `predict(...)` 返回的是 special-case action dict
- rollout 不直接执行 action
- `agent.step(...)` 会把 CUA action 转成 `pyautogui` 再落到环境里

## 六、`.env` 现在至少需要哪些变量

这次 demo 至少依赖下面一项 key：

```env
OPENAI_API_KEY_CUA=...
```

或者：

```env
OPENAI_API_KEY=...
```

如果你需要自定义 base URL，还可以额外提供：

```env
OPENAI_BASE_URL_CUA=...
```

或者：

```env
OPENAI_BASE_URL=...
```

### 1. 当前最推荐的理解方式

如果你只是第一次试跑，最稳的还是：

- 配 `OPENAI_API_KEY_CUA`
- 不配 base URL
- 显式传 `--model computer-use-preview`

### 2. 当前最自然的模型参数

这次 demo runner 里默认使用的是：

- `model=computer-use-preview`
- `max_tokens=1024`

这和当前 OpenAI computer use 文档的典型用法是一致的。

## 七、最小运行命令应该怎么写

第一次实践建议继续只跑一个任务：

```bash
uv run python scripts/python/run_openaicua_demo.py \
  --path_to_vm "/Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx" \
  --provider_name vmware \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model computer-use-preview \
  --max_steps 1 \
  --result_dir ./results/openaicua-demo-smoke
```

这里最关键的几个参数是：

- `--path_to_vm`
  传 `.vmx` 路径
- `--provider_name vmware`
  使用 VMware provider
- `--model computer-use-preview`
  显式指定 CUA 模型
- `--max_steps 1`
  先只验证最短链路

## 八、这次我们实际验证到了什么程度

这次和前两个 agent 的状态不一样。

### 1. 当前环境里没有 OpenAI CUA key

这次本地检查结果是：

- `OPENAI_API_KEY_CUA` 缺失
- `OPENAI_API_KEY` 也缺失

所以这次没法像 `PromptAgent` / `SeedAgent` 那样做真实在线 smoke test。

### 2. 但 special-case 主链路已经做了 mock 验证

这次已经用 mock 方式验证了下面这条链：

- `OpenAICUAAgent.predict(...)`
- `_handle_item(...)`
- `_convert_cua_action_to_pyautogui_action(...)`
- `agent.step(...)`
- `env.step(...)`

mock 验证里，构造出的 CUA action 是：

```text
click(x=42, y=24, button='left')
```

最终转换成的 `pyautogui` 代码是：

```python
import pyautogui
pyautogui.moveTo(42, 24)
pyautogui.click(button='left')
```

并且已经成功走到了 fake env 的 `step(...)`。

### 3. 所以当前最准确的结论

当前已经确认：

- demo runner 可导入、可编译
- `OpenAICUAAgent` 的 special-case rollout 结构是通的
- CUA action 到 `pyautogui` 的翻译链是通的

当前还没有确认的是：

- 真实 OpenAI CUA 在线请求
- 真实 VM 里的完整单任务 rollout

缺口原因不是代码已知报错，而是：

- 当前本地没有可用 key

## 九、下次拿到 key 以后，应该先看什么

一旦你补上 key，第一次试跑时重点盯这几层：

### 1. 先看 `_create_response(...)` 是否返回成功

如果这里失败，优先检查：

- `OPENAI_API_KEY_CUA`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL_CUA`
- `OPENAI_BASE_URL`
- `--model`

### 2. 再看 `predict(...)` 里有没有拿到 `computer_call`

因为这条线真正往下执行，依赖的是 `response.output` 里存在：

- `computer_call`

如果没有这个 item，而只有文本消息，当前 rollout 很容易直接结束。

### 3. 再看 `agent.step(...)`

如果 `predict(...)` 已经拿到 action，但动作没落到环境里，就重点看：

- `_convert_cua_action_to_pyautogui_action(...)`
- `agent.step(...)`

## 十、跑完后最值得先看哪些文件

如果你后面补上 key 进行真实试跑，结果目录里最值得先看的仍然是：

1. `traj.jsonl`
   看每一步的 special-case action dict、reward、done
2. `runtime.log`
   看请求和 rollout 卡在哪一层
3. `result.txt`
   看最终得分
4. `recording.mp4`
   看 VM 里真实发生了什么

尤其是这条线，你更应该注意 `traj.jsonl` 里记录的不是简单字符串 action，而是像：

```json
{
  "action_space": "pyautogui",
  "action": "import pyautogui ...",
  "call_id": "...",
  "pending_checks": []
}
```

因为这是它 special-case 协议的一部分。

## 十一、这一篇之后，下一步最适合做什么

如果你接下来继续往下学，最自然的方向有两个：

1. 继续拆 [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
   重点看 `predict(...)`、`_handle_item(...)`、`_convert_cua_action_to_pyautogui_action(...)`、`step(...)`
2. 真正补上 OpenAI key 后，再做一次 live smoke test

也就是说，这一篇现在的作用和前两篇不完全一样：

- `PromptAgent` / `SeedAgent` 是“已经在线跑通”
- `OpenAICUAAgent` 这一篇是“代码和 mock 链路已通，live 试跑还差 key”

但这已经足够让你先把 special-case 结构学明白了。
