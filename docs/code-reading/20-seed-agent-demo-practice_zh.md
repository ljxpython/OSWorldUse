# 20 SeedAgent 最小实践与可运行 Demo

这一篇接在 [19 PromptAgent 最小实践与自定义模型适配](./19-prompt-agent-demo-practice_zh.md) 后面看最合适。

前一篇你已经完成了一条很重要的练手路径：

- 用最小 runner 跑通一个标准 agent
- 确认 VM/provider 侧问题和 agent/model 侧问题要分开排查
- 知道结果目录里该看什么

这一篇继续做 `SeedAgent`，但它和 `PromptAgent` 练手有一个关键区别：

- 这次不需要新写一个 `SeedAgentDemo(SeedAgent)` 子类
- 但需要补齐 `SeedAgent` 依赖的本地解析模块

也就是说，这次实践的重点不是“再包一个 agent 子类”，而是：

- 直接复用原始 `SeedAgent`
- 给它补一个当前仓库里缺失的 `ui_tars` 解析依赖
- 再用单任务 runner 把它真正跑起来

## 一、这次新增了哪几个文件

这次实践新增了三个文件：

1. [scripts/python/run_seed_agent_demo.py](../../scripts/python/run_seed_agent_demo.py)
2. [ui_tars/action_parser.py](../../ui_tars/action_parser.py)
3. [ui_tars/__init__.py](../../ui_tars/__init__.py)

它们的职责分工是：

- `run_seed_agent_demo.py`
  提供单任务、单进程、最小可运行的 `SeedAgent` 入口
- `ui_tars/action_parser.py`
  补齐 `SeedAgent` 当前实际依赖的 XML tool-call 解析与 `pyautogui` 代码转换
- `ui_tars/__init__.py`
  只是为了让 `ui_tars` 变成一个可导入包

注意这里没有去改：

- [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
- [lib_run_single.py](../../lib_run_single.py)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

这说明这次仍然是“增量接入 + 最小练手”，没有去动 benchmark 主干。

## 二、为什么这次不再写 `SeedAgentDemo` 子类

和 [19](./19-prompt-agent-demo-practice_zh.md) 里 `PromptAgentDemo` 的路线不一样，这次直接复用原始 `SeedAgent` 更合适。

原因有三条。

### 1. `SeedAgent` 本身已经是完整 agent

[mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 本身已经实现了：

- `reset(...)`
- `predict(...)`
- 历史图片维护
- 多轮消息拼装
- 模型调用
- Tool-call 解析后的动作转换

也就是说，它并不缺一个外层 agent 壳。

### 2. 当前最直接的问题不是 agent 抽象不够，而是依赖缺口

这次真正卡住的第一件事不是模型参数、不是 runner、也不是 VM，而是：

```python
from ui_tars.action_parser import parse_xml_action, parsing_response_to_pyautogui_code, parse_xml_action_v3
```

当前仓库里并没有 `ui_tars` 这个包。

所以比起再写一层子类，更应该先把：

- 导入缺口
- Tool-call 解析缺口

补齐。

### 3. 这样更方便你直接对照原始 `SeedAgent`

这次实践最适合学习的，不是“怎么二次封装 `SeedAgent`”，而是：

- 原始 `SeedAgent` 自己怎么组织消息
- 它怎么把模型输出变成动作
- 它和 `PromptAgent` 的不同到底在哪里

直接复用原始类，会让你看代码时边界更清楚。

## 三、这次为什么必须补 `ui_tars/action_parser.py`

这次实践里，最先暴露出来的问题是：

```text
ModuleNotFoundError: No module named 'ui_tars'
```

这不是环境没装好，而是当前仓库本身就没有这个目录。

### 1. `SeedAgent` 依赖它做两件事

[mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 当前直接依赖这三个函数：

- `parse_xml_action(...)`
- `parse_xml_action_v3(...)`
- `parsing_response_to_pyautogui_code(...)`

其中真正关键的是后两个：

- `parse_xml_action_v3(...)`
  负责把模型返回的 Seed 风格 XML tool-call 解析成结构化动作
- `parsing_response_to_pyautogui_code(...)`
  负责把结构化动作转成 OSWorld 可以执行的 `pyautogui` 代码

### 2. 这次补的是“最小可运行实现”

这次新增的 [ui_tars/action_parser.py](../../ui_tars/action_parser.py) 不是完整还原某个外部 UI-TARS 包，而是只补了 `SeedAgent` 当前 smoke test 真正需要的最小能力：

- 解析 `<function_...=click>` 这种函数块
- 解析 `<parameter_...=point>` 这种参数块
- 把 `<point>x y</point>` 转成坐标
- 把常见动作转成 `pyautogui` 代码

支持的常见动作包括：

- `click`
- `left_double`
- `right_single`
- `drag`
- `move_to`
- `scroll`
- `type`
- `hotkey`
- `press`
- `release`
- `mouse_down`
- `mouse_up`

这已经足够支撑最小 demo。

## 四、最小 runner 做了什么

[scripts/python/run_seed_agent_demo.py](../../scripts/python/run_seed_agent_demo.py) 的目标和前一篇里的 `run_prompt_agent_demo.py` 一样：

- 只跑一个任务
- 只开一个环境
- 尽量少碰多进程和批量调度

### 1. 自动加载根目录 `.env`

它会在启动时自动执行：

```python
load_dotenv(".env")
```

所以你根目录里的：

- `DOUBAO_API_KEY`
- `DOUBAO_API_URL`
- `DOUBAO_API_MODEL`

都会直接生效。

### 2. 默认只跑单任务 meta

默认使用的还是：

- [docs/code-reading/examples/test_one_chrome.json](./examples/test_one_chrome.json)

这能保证第一次实践只验证最短链路。

### 3. 继续复用标准 rollout

它仍然调用：

- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example(...)`

所以它走的仍然是 OSWorld 标准 agent 路线，不是特殊路径。

## 五、这次 `SeedAgent` 的真实调用链是什么

这次练手最值得你盯住的是这条链：

```text
run_seed_agent_demo.py
  -> SeedAgent
  -> SeedAgent.predict(...)
  -> inference_with_thinking_ark(...)
  -> parse_xml_action_v3(...)
  -> parsing_response_to_pyautogui_code(...)
  -> env.step(...)
```

和 `PromptAgent` 相比，`SeedAgent` 的内部差异主要在这里：

### 1. 它自己维护历史图片

不是 runner 维护历史，而是 `SeedAgent` 自己维护：

- `self.history_images`
- `self.history_responses`

### 2. 它自己组织多轮消息

它不是直接复用 `PromptAgent` 的 prompt 结构，而是自己拼：

- system prompt
- function definition prompt
- 当前任务 instruction
- 历史截图
- 历史 response

### 3. 它要求模型输出 Seed 风格 tool-call

它期待模型输出的不是普通代码块，而是类似：

```text
<seed:tool_call...>
  <function...=click>
    <parameter...=point><point>988 117</point></parameter...>
  </function...>
</seed:tool_call...>
```

然后再转成 `pyautogui`。

## 六、`.env` 现在至少需要哪些变量

这次最小 demo 依赖这几项：

```env
DOUBAO_API_KEY=...
DOUBAO_API_URL=...
DOUBAO_API_MODEL=...
```

三者分别对应：

- `DOUBAO_API_KEY`
  Ark / Doubao 鉴权密钥
- `DOUBAO_API_URL`
  Ark/OpenAI 兼容服务基础地址
- `DOUBAO_API_MODEL`
  默认模型名

### 1. 当前最稳的理解方式

对这次 demo 来说，`DOUBAO_API_URL` 最稳的写法是基础地址，例如：

```env
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
```

原因是当前 [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 的主推理路径直接走：

- `Ark(base_url=api_url, api_key=api_key)`

而不是像前一篇里的 `PromptAgentDemo` 那样自己手工 `POST`。

### 2. 当前代码里的一个重要事实

虽然 runner 暴露了：

- `--model_type`
- `--use_thinking`

但当前 [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py) 里，`self.inference_func` 仍然固定指向：

- `inference_with_thinking_ark(...)`

所以这次 demo 实际走的是：

- Ark
- thinking 风格
- 流式 `chat.completions.create(...)`

你可以把这件事理解成：

- 这些参数目前更像“接口保留位”
- 当前最小 demo 的真实调用路径还是固定的

## 七、最小运行命令应该怎么写

第一次实践建议直接跑单任务、单步数：

```bash
uv run python scripts/python/run_seed_agent_demo.py \
  --path_to_vm "/Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx" \
  --provider_name vmware \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --max_steps 1 \
  --result_dir ./results/seed-agent-demo-smoke
```

这里最关键的几个参数是：

- `--path_to_vm`
  传 `.vmx` 路径
- `--provider_name vmware`
  使用 VMware provider
- `--test_all_meta_path`
  只跑一个最小任务
- `--max_steps 1`
  只验证“模型返回动作并执行”这条最短链路

如果你想换模型，也可以显式传：

```bash
--model your-model-name
```

否则会默认读取 `.env` 里的 `DOUBAO_API_MODEL`。

## 八、这次实际已经验证通过了什么

这次不是只做了导入检查，而是已经把整条最小链路真正跑通了。

当前已经确认通过的部分有：

### 1. `SeedAgent` 可以在当前仓库里正常导入

补完 `ui_tars` 包以后，`SeedAgent` 已经可以直接被 runner 导入和实例化。

### 2. VMware 重置链路正常

已经确认下面这条链路能通：

- 启动 VM
- 获取 guest IP
- `env.reset(...)`
- 回滚快照
- 回滚后再次启动 VM
- 再次获取 guest IP
- setup 环境
- 成功获取 screenshot

### 3. Ark 模型请求成功返回

实际日志里已经看到：

```text
HTTP Request: POST https://ark.cn-beijing.volces.com/api/v3/chat/completions "HTTP/1.1 200 OK"
```

这说明：

- API key 可用
- base URL 可用
- 当前模型可用

### 4. 模型返回动作被成功解析并执行

实际 smoke test 里，模型给出的首步动作被解析成了：

```python
import pyautogui
import time
pyautogui.click(988.0, 117.0, button='left')
```

随后 `env.step(...)` 也执行成功。

## 九、这次实际跑通到了什么程度

这次 smoke test 的结果目录是：

- `results/seed-agent-demo-smoke/pyautogui/screenshot/doubao-seed-2-0-pro-260215/...`

已经实际生成了：

- `args.json`
- `traj.jsonl`
- `runtime.log`
- `result.txt`
- `summary/results.json`

对应的汇总状态是：

- `status: success`
- `score: 0.0`

这里的 `0.0` 不是链路没跑通，而是因为：

- 这次只跑了 `max_steps=1`
- 目标是 smoke test，不是完整解题

也就是说，这次验证的重点是：

- 环境能不能起来
- 模型能不能返回 Seed 风格动作
- parser 能不能解析
- 动作能不能落到 VM 里执行

而不是“一步就完成整个任务”。

## 十、这次还暴露了什么非阻塞问题

这次运行结束时，还有一个和前面 `PromptAgent` demo 类似的小问题：

```text
Failed to stop recording. Status code: 500
Failed to stop recording. Status code: 400
```

这说明当前 guest 侧录屏停止逻辑仍然不稳定。

但这个问题目前不影响：

- agent 主链路
- 结果产出
- 结果汇总

所以可以先把它当作非阻塞问题。

## 十一、下次如果再失败，应该先怎么判断

后面你再跑这条命令时，可以按下面顺序快速分层。

### 1. 如果导入时报 `No module named 'ui_tars'`

优先检查：

- [ui_tars/__init__.py](../../ui_tars/__init__.py)
- [ui_tars/action_parser.py](../../ui_tars/action_parser.py)

也就是说，先看 parser 依赖，不要一上来就看模型。

### 2. 如果停在 `Starting VMware VM...`

优先怀疑：

- VMware/Fusion 启动慢
- 快照恢复慢
- guest 还没完全起来

这时先看 provider/VM 层。

### 3. 如果模型请求没有 `200 OK`

优先检查：

- `.env` 里的 `DOUBAO_API_KEY`
- `.env` 里的 `DOUBAO_API_URL`
- `.env` 里的 `DOUBAO_API_MODEL`

### 4. 如果模型返回后报 `Parsing action error`

优先检查：

- 模型输出有没有包含 Seed 风格 tool-call
- [ui_tars/action_parser.py](../../ui_tars/action_parser.py) 的函数块解析是否匹配当前输出格式

这时优先看 parser，不是优先看 VM。

## 十二、跑完后最值得先看哪些文件

结果目录里最值得先看的，仍然是这四类文件：

1. `traj.jsonl`
   看每一步 response、action、reward
2. `runtime.log`
   看运行期日志，定位卡在哪一层
3. `result.txt`
   看单任务得分
4. `summary/results.json`
   看最终汇总状态

如果这些文件都存在，并且 `traj.jsonl` 里能看到：

- 模型返回
- 解析后的动作
- action 执行结果

那就说明这条 `SeedAgent` demo 链路已经真正跑起来了。

## 十三、这一篇之后，下一步最适合看什么

现在你已经有了两条最小练手路径：

1. [19 PromptAgent 最小实践与自定义模型适配](./19-prompt-agent-demo-practice_zh.md)
2. 这一篇 `SeedAgent` 最小实践

这两条线最值得对照的不是“谁更强”，而是：

- `PromptAgent` 更像“换模型适配层”的最小样板
- `SeedAgent` 更像“内部实现完全不同，但仍然保持标准接口”的样板

如果你接下来要继续深入，最自然的方向有两个：

1. 回到 [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
   逐段对照它的 `predict(...)`、消息拼装、Tool-call 解析
2. 再继续做你自己的 agent 接入
   先决定你更像 `PromptAgent` 路线，还是更像 `SeedAgent` 路线

也就是说，这一篇现在可以作为你后面接自定义 GUI agent 的第二个对照模板。
