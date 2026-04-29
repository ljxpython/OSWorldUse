# 19 PromptAgent 最小实践与自定义模型适配

这一篇接在 [18 Agent 详细链路图](./18-agent-chain-diagrams_zh.md) 后面看最合适。

前面你已经知道：

- benchmark 主链路是什么
- `PromptAgent` 在标准 runner 里怎么工作
- 新 agent 第一版为什么应该优先走标准路径

这一篇开始做第一次真正的 agent 实践，但目标仍然故意收窄：

- 不改 benchmark 主流程
- 不改 `DesktopEnv`
- 不直接改原始 `PromptAgent`
- 只新增一个基于 `PromptAgent` 的 demo 适配层
- 只跑一个最小单任务

这样做的目的很简单：先验证“你的自定义模型能不能挂到 OSWorld 的标准 agent 链路上”。

## 一、这次新增了哪两个文件

这次实践新增了两个文件：

1. [mm_agents/prompt_agent_demo.py](../../mm_agents/prompt_agent_demo.py)
2. [scripts/python/run_prompt_agent_demo.py](../../scripts/python/run_prompt_agent_demo.py)

它们的职责分工是：

- `mm_agents/prompt_agent_demo.py`
  只负责“把自定义 OpenAI 兼容接口适配到 `PromptAgent`”
- `scripts/python/run_prompt_agent_demo.py`
  只负责“用最小 runner 把这个 demo agent 真正跑起来”

注意这里没有去改：

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [lib_run_single.py](../../lib_run_single.py)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

这说明我们这次做的是“增量接入”，不是“改 benchmark 内核”。

## 二、为什么不直接改 `mm_agents/agent.py`

第一版实践不建议直接改 [mm_agents/agent.py](../../mm_agents/agent.py)，原因有三条。

### 1. 原始 `PromptAgent` 是基线实现

它本身已经承担了：

- prompt 拼装
- 历史轨迹维护
- 模型回复解析
- `pyautogui` / `computer_13` 动作提取

如果你一开始就改这里，很快会把“我的自定义模型适配问题”和“仓库原始 agent 行为问题”搅在一起。

### 2. 子类化更容易验证问题边界

如果我们只写一个 `PromptAgentDemo(PromptAgent)`，那么：

- prompt 逻辑继续复用原实现
- action parser 继续复用原实现
- `reset(...)` / `predict(...)` 契约继续复用原实现

这样一旦运行有问题，就能更快判断问题到底在：

- 模型接口适配层
- benchmark runner
- provider / VM 启动

### 3. 更方便后面继续做 SeedAgent 实践

这一版用“子类 + 独立 runner”的方式跑通后，后面继续做 `SeedAgent` 实践时，你会更容易比较：

- `PromptAgent` 路线是在复用什么
- `SeedAgent` 路线又额外定制了什么

## 三、`PromptAgentDemo` 改了什么

[mm_agents/prompt_agent_demo.py](../../mm_agents/prompt_agent_demo.py) 的核心思路只有一句话：

继续复用 `PromptAgent` 的大部分行为，只替换“模型请求发到哪里、怎么取回文本”。

### 1. 继续继承 `PromptAgent`

这个类不是从零实现一个新 agent，而是：

```python
class PromptAgentDemo(PromptAgent):
```

这意味着下面这些能力默认继续沿用原版：

- prompt 构造
- 多模态消息拼装
- `predict(...)`
- `parse_actions(...)`
- `reset(...)`

也就是说，这个 demo 不是重新发明 agent，而是在复用现成 agent 的基础上替换传输层。

### 2. 模型名优先从参数或 `.env` 读取

它在初始化时会优先读取：

- `--model`

如果你没有显式传 `--model`，就会回退到：

- `DOUBAO_API_MODEL`

这部分逻辑的意义是：

- 命令行可以临时覆盖模型
- 平时默认还是走根目录 `.env`

### 3. 新增 `_post_chat_completions(...)`

这个方法负责真正发 HTTP 请求。

它会从环境变量读取：

- `DOUBAO_API_KEY`
- `DOUBAO_API_URL`

然后把 `PromptAgent` 组好的 payload 发到你的 OpenAI 兼容接口。

这样你不需要改 `PromptAgent.predict(...)` 本身，只需要保证“输入 payload 能发出去，返回文本能拿回来”。

### 4. 新增 `_extract_message_content(...)`

不同兼容接口返回的 `message.content` 结构可能不完全一样。

这个方法做的事情是：

- 如果 `content` 是字符串，直接返回
- 如果 `content` 是列表，就把里面的文本片段拼起来

这一步是典型的适配层工作。

### 5. 重写 `call_llm(...)`

原始 `PromptAgent` 最关键的可替换点就是 `call_llm(...)`。

我们这次没有去改 `predict(...)`，而是只在这里接管：

- 记录日志
- 发请求
- 处理 `context_length_exceeded`
- 返回最终文本

所以你可以把这份 demo 理解成：

- `PromptAgent` 负责“思考链路和动作解析”
- `PromptAgentDemo` 负责“把请求送到你的模型服务上”

## 四、最小 runner 改了什么

[scripts/python/run_prompt_agent_demo.py](../../scripts/python/run_prompt_agent_demo.py) 不是完整的多进程 benchmark 入口，而是一个最小单任务实践脚本。

这么做是为了先压低复杂度。

### 1. 显式加载根目录 `.env`

这个脚本启动时会检查根目录 `.env` 是否存在，并执行：

```python
load_dotenv(".env")
```

这一步的意义是：

- 你在项目根目录里配好的模型密钥和 URL，可以直接被 demo runner 使用
- 不需要先把这些环境变量手工 `export`

### 2. 默认只跑一个单任务 meta

它默认使用：

- [docs/code-reading/examples/test_one_chrome.json](./examples/test_one_chrome.json)

这份 meta 文件只放了一个 `chrome` 任务，目的就是让你第一次实践时只验证最短链路。

### 3. 默认参数故意收敛

这个 runner 默认就是按最小实践来的：

- `action_space=pyautogui`
- `observation_type=screenshot`
- `max_steps=5`

第一次实践时，这三个组合是最稳的。

### 4. 继续复用标准单任务主循环

最关键的一点是，它没有自己另写 rollout，而是继续调用：

- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example(...)`

这意味着你这次练的是标准 OSWorld agent 接入路径，不是特殊路径。

## 五、`.env` 现在需要哪些变量

这次 `PromptAgent` demo 适配依赖根目录 `.env` 里的三项配置：

```env
DOUBAO_API_KEY=...
DOUBAO_API_URL=...
DOUBAO_API_MODEL=...
```

三者分别对应：

- `DOUBAO_API_KEY`
  你的模型服务鉴权密钥
- `DOUBAO_API_URL`
  OpenAI 兼容接口的基础地址或完整 `chat/completions` 地址
- `DOUBAO_API_MODEL`
  默认模型名

如果你在命令行里显式传了：

```bash
--model your-model-name
```

那么它会覆盖 `.env` 里的 `DOUBAO_API_MODEL`。

## 六、最小运行命令应该怎么写

第一次实践建议直接跑单任务。

命令形态如下：

```bash
uv run python scripts/python/run_prompt_agent_demo.py \
  --path_to_vm "/absolute/path/to/your-vm.vmx" \
  --provider_name vmware \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --max_steps 2 \
  --result_dir ./results/prompt-agent-demo-smoke
```

这里最关键的几个参数是：

- `--path_to_vm`
  传你的 `.vmx` 路径，也就是 `vmrun` 列出来的那条路径
    macOS 上通常用 `vmrun -T fusion list`
    Linux/Windows 上通常用 `vmrun -T ws list`
    可以使用 `rg --files vmware_vm_data -g '*.vmx'` 来查找。vmx 文件一般在 `vmware_vm_data/` 目录下。
- `--provider_name vmware`
  表示当前通过 VMware provider 启动环境
- `--test_all_meta_path`
  明确只跑单任务 meta

如果你只是想先看脚本参数是否正确，也可以先执行：

```bash
uv run python scripts/python/run_prompt_agent_demo.py --help
```

## 七、这次实际排查后确认了什么

这次不是只做了“代码能导入”的静态验证，而是已经把最小链路真正跑了一遍。

当前已经确认通过的部分有：

### 1. 自定义模型适配层可以真正收到请求并返回动作

已经确认下面这条链路能通：

- `PromptAgentDemo.predict(...)`
- 调用重写后的 `call_llm(...)`
- 请求发到自定义 OpenAI 兼容接口
- 返回模型文本
- 继续复用原始 `PromptAgent` 的动作解析
- 得到可执行的 `pyautogui` 代码

### 2. VMware 环境可以完成完整的 reset 链路

已经确认下面这条链路能通：

- 启动 VM
- 获取 guest IP
- `env.reset(...)` 触发回滚快照
- 回滚后再次启动 VM
- 再次获取 guest IP
- 连接 guest 里的 `server/main.py`
- 执行 task setup
- 成功获取 screenshot

### 3. 最小单任务 runner 已经能完整出结果

已经实际生成了：

- `traj.jsonl`
- `runtime.log`
- `result.txt`
- `summary/results.json`

这说明当前最小实践已经不是“只能启动到一半”，而是已经能把 agent 跑起来并落盘结果。

## 八、这次失败的第一个根因：`http://unknown:5000`

你之前遇到的关键日志是这类：

```text
VMware VM IP address: unknown
try to connect http://unknown:5000
```

这个问题的根因不在 agent，而在 VMware provider。

### 1. `getGuestIPAddress` 可能返回 `unknown`

原始实现里，[desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py) 的 `get_ip_address(...)` 只要命令有输出，就直接把输出当 IP 返回。

但 VMware 在 guest 尚未完全准备好时，可能返回：

- `unknown`
- 空串
- 非 0 返回码

如果把 `unknown` 直接当 IP 使用，后面 setup 就会去访问：

```text
http://unknown:5000
```

于是后续的 screenshot、setup、controller 调用都会失败。

### 2. `revertToSnapshot` 之前是异步放出去的

另一个更隐蔽的问题是：[desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py) 原先的 `_execute_command(...)` 用的是 `subprocess.Popen(...)`，但对非返回输出的命令没有等待真正结束。

这会导致：

1. `revertToSnapshot` 还没真正完成
2. `reset()` 就已经继续调用 `_start_emulator()`
3. VMware 还在回滚，脚本却已经开始判断 VM 是否在运行
4. 后续状态很容易混乱

这正是之前“刚说 VM is running，后面却拿不到 IP”的根本原因。

### 3. 这次是怎么修的

这次在 [desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py) 里做了两个修正：

- `_execute_command(...)` 现在会等待命令真正结束
- `get_ip_address(...)` 现在只有拿到合法 IP 才返回

也就是说，下面这些情况都会继续重试，而不是直接往下走：

- 返回码不是 0
- 输出为空
- 输出为 `unknown`
- 输出不是合法 IP

所以现在再遇到 guest 还没完全起来的阶段，日志会表现为“继续等”，而不会再把 `unknown` 带进 HTTP 请求。

## 九、这次失败的第二个根因：模型接口返回 404

VM 问题修好以后，第二个暴露出来的问题是模型调用失败。

典型日志会像这样：

```text
Failed to call custom model, status=404
```

### 1. 根因不是 key 错了，而是 URL 用法不对

根目录 `.env` 里原先配置的是：

```env
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
```

这是基础地址，不是完整的 `chat/completions` 路径。

而最初版本的 [mm_agents/prompt_agent_demo.py](../../mm_agents/prompt_agent_demo.py) 是直接把这个地址拿去 `POST`，于是就会返回 `404`。

### 2. 现在的适配规则

这次已经在 [mm_agents/prompt_agent_demo.py](../../mm_agents/prompt_agent_demo.py) 里补了 URL 规范化逻辑。

现在它支持两种写法：

#### 写法 A：传基础地址

```env
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
```

程序会自动补成：

```text
https://ark.cn-beijing.volces.com/api/v3/chat/completions
```

#### 写法 B：直接传完整接口

```env
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
```

这种写法程序也能直接识别，不会重复拼接。

所以现在更推荐的理解方式是：

- `DOUBAO_API_URL` 可以填基础地址
- 也可以直接填完整 `chat/completions` 地址

## 十、这次实际已经跑通到了什么程度

这次实际回归时，使用的是下面这类命令：

```bash
uv run python scripts/python/run_prompt_agent_demo.py \
  --path_to_vm "/Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx" \
  --provider_name vmware \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --max_steps 1 \
  --result_dir ./results/prompt-agent-demo-smoke-fix3
```

执行过程里，已经看到过这些关键日志：

- `VMware VM IP address: 192.168.254.129`
- `Environment setup complete.`
- `Got screenshot successfully`
- `Generating content with custom PromptAgent demo model`
- `RESPONSE: <python action code>`
- `Command executed successfully`
- `Finished. Scores: [0.0]`

这里的 `0.0` 不是说链路没跑通，而是因为这次只是一个单步 smoke test。

也就是说，这次验证的重点是：

- VM 能不能起来
- setup 能不能完成
- agent 能不能请求模型
- 模型返回能不能被解析成动作
- 动作能不能真正执行

而不是“一个动作就把任务完整做完”。

## 十一、下次如果再失败，应该先怎么判断

后面你再跑这条命令时，可以先按日志把问题快速分层。

### 1. 如果停在 `Starting VMware VM...`

优先怀疑：

- VMware/Fusion 本身没有把 VM 拉起来
- 首次启动很慢
- 快照恢复很慢

这时先不要急着看 agent 代码。

### 2. 如果出现 `http://unknown:5000`

优先怀疑：

- guest IP 还没有准备好
- provider 拿到了无效 IP
- VM 在快照恢复后的状态还不稳定

先看 [desktop_env/providers/vmware/provider.py](../../desktop_env/providers/vmware/provider.py) 这一层。

### 3. 如果出现 `Failed to call custom model, status=404`

优先检查：

- `.env` 里的 `DOUBAO_API_URL`
- 你的服务到底要求填基础地址还是完整地址
- 当前模型服务是否真的是 OpenAI 兼容接口

这时先看 [mm_agents/prompt_agent_demo.py](../../mm_agents/prompt_agent_demo.py)。

### 4. 如果最后分数是 `0.0`

先不要立刻判断为“接入失败”。

先确认这几个问题：

- agent 有没有成功返回动作
- 动作有没有成功执行
- `traj.jsonl` 有没有记录 response 和 action
- 这次是不是本来就只跑了很少的步数

如果这些都正常，那么 `0.0` 很可能只是“任务没做完”，不是“链路没打通”。

## 十二、跑完后最值得先看哪些文件

结果目录里最值得先看的，仍然是这四类文件：

1. `traj.jsonl`
   看每一步 observation、model response、parsed action、reward
2. `runtime.log`
   看运行期日志，定位卡在哪一层
3. `result.txt`
   看单任务最终得分
4. `summary/results.json`
   看最终汇总状态

这次实际结果目录示例是：

- `results/prompt-agent-demo-smoke-fix3/pyautogui/screenshot/doubao-seed-2-0-pro-260215/...`

如果你在这几个文件里都能看到数据，就说明最小 runner 已经真正跑起来了。

## 十三、这一篇之后，下一步看什么最合适

现在这条 `PromptAgentDemo` 最小路径已经跑通，下一步就很适合继续做 `SeedAgent` 实践。

原因很简单：

1. 现在你已经有了一条“复用 `PromptAgent` 主体逻辑”的最小接入样板
2. 接下来再看 `SeedAgent`，你就能更清楚地区分：
   - 哪些是 benchmark 要求的统一接口
   - 哪些是某个具体 agent 自己增加的推理和动作逻辑

也就是说，这篇文档现在的作用已经从“第一次搭 demo”变成了“后面接更多 agent 的对照样板”。
