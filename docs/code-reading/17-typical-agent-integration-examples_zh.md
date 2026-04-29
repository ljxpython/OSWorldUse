# 17 三个典型 Agent 接入例子与实际运行

这一篇接在 [16 新 Agent 最小接入模板](./16-agent-integration-template_zh.md) 后面看最合适。

你现在已经知道“新 agent 应该怎么接”。下一步最好的学习方式，不是继续抽象讨论，而是挑几个仓库里已经存在的典型例子，对着代码和启动命令看：

- 它们分别走哪条接入路径
- 整个运行链路长什么样
- 真正需要哪些配置
- 第一次试跑应该用什么命令

这一篇就专门做这件事。

## 先给一句结论

如果你想一边看代码、一边实际跑起来，推荐按这个顺序：

1. `PromptAgent`
2. `SeedAgent`
3. `OpenAICUAAgent`

原因很简单：

- `PromptAgent` 最标准
- `SeedAgent` 和它接口兼容，但内部实现明显不同
- `OpenAICUAAgent` 则是典型 special-case runner

把这三条线都走一遍，你对 OSWorld 的 agent 接入方式基本就有完整感觉了。

## 一、先准备一个单任务试跑文件

为了避免一上来跑完整个 `chrome` domain，这里先准备一个单任务 meta 文件：

- [docs/code-reading/examples/test_one_chrome.json](./examples/test_one_chrome.json)

它只包含一个任务：

- `bb5e4c0d-f964-439c-97b6-bdb9747de3f4`

也就是前面 [12 Chrome 任务端到端走读](./12-chrome-task-end-to-end_zh.md) 里已经看过的那个例子。

这个任务的目标是：

- 把 Chrome 的默认搜索引擎切换成 Bing

它很适合做首次接入验证，因为：

- 只涉及 `chrome`
- 环境预置比较简单
- 评测逻辑也比较直观

## 二、先记住一个统一主链路

虽然下面会讲 3 个 agent，但你要先记住，绝大多数路径都围绕这条链：

```text
run_multienv_xxx.py
  -> DesktopEnv(...)
  -> agent = XxxAgent(...)
  -> lib_run_single.run_single_example(...) 或 run_single_example_xxx(...)
  -> env.reset(task_config=example)
  -> agent.reset(...)
  -> obs = env._get_obs()
  -> response, actions = agent.predict(instruction, obs)
  -> env.step(action) 或 agent.step(action)
  -> env.evaluate()
```

真正的差异主要出在两处：

- `agent.predict(...)` 内部怎么做
- rollout 是直接 `env.step(...)`，还是要走 agent 自己的 `step(...)`

## 三、例子 1：`PromptAgent`

这是最标准、也最推荐你第一个实际跑起来的例子。

### 1. 该看哪些文件

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)
- [lib_run_single.py](../../lib_run_single.py)

### 2. 它属于哪类接入

它属于：

- 标准 agent
- 标准 runner
- 标准 rollout

也就是：

- `agent.predict(...)` 返回 `(response, actions)`
- `lib_run_single.run_single_example(...)` 直接调用 `env.step(action, ...)`

### 3. 它的运行链路是什么

可以直接把它想成：

```text
run_multienv.py
  -> PromptAgent
  -> run_single_example(...)
  -> agent.predict(...)
  -> env.step(...)
```

### 4. 你需要什么配置

如果你用 `gpt*` 模型，最小配置是 repo 根目录下有 `.env`：

```env
OPENAI_API_KEY=your_key_here
```

可选项：

```env
OPENAI_BASE_URL=https://your-proxy-or-compatible-endpoint/v1
```

如果你改用别的模型族，当前代码里还支持：

- `claude*`：需要 `ANTHROPIC_API_KEY`
- `gemini*`：需要 `GENAI_API_KEY`

但第一次试跑，建议先用 `gpt*` 这条最短路径。

### 5. 第一次怎么跑

直接跑单任务最合适：

```bash
uv run python scripts/python/run_multienv.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model gpt-4o \
  --num_envs 1 \
  --result_dir ./results/promptagent-one-task
```

如果你不想先造自定义 meta，也可以直接跑整个 `chrome` domain：

```bash
uv run python scripts/python/run_multienv.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --domain chrome \
  --model gpt-4o \
  --num_envs 1 \
  --result_dir ./results/promptagent-chrome
```

### 6. 第一次跑完重点看什么

重点看结果目录里的：

- `traj.jsonl`
- `runtime.log`
- `recording.mp4`
- `result.txt`

你主要想确认 4 件事：

1. `agent.reset(...)` 有没有正常执行
2. `agent.predict(...)` 有没有返回动作
3. `env.step(...)` 有没有真的执行动作
4. `env.evaluate()` 最后有没有产出分数

## 四、例子 2：`SeedAgent`

这是最适合你研究“标准接口不变，但 agent 内部实现完全可以不同”的例子。

### 1. 该看哪些文件

- [mm_agents/seed_agent.py](../../mm_agents/seed_agent.py)
- [scripts/python/run_multienv_seedagent.py](../../scripts/python/run_multienv_seedagent.py)
- [lib_run_single.py](../../lib_run_single.py)

### 2. 它属于哪类接入

它也属于：

- 标准 agent
- 标准 runner
- 标准 rollout

也就是说，它虽然内部消息格式、模型调用方式、动作解析都和 `PromptAgent` 很不一样，但外部接口仍然兼容：

- `reset(...)`
- `predict(...) -> (response, actions)`
- 继续复用 `run_single_example(...)`

### 3. 它的运行链路是什么

链路和 `PromptAgent` 非常像：

```text
run_multienv_seedagent.py
  -> SeedAgent
  -> run_single_example(...)
  -> agent.predict(...)
  -> env.step(...)
```

真正不同的是：

- `SeedAgent` 自己维护历史图片
- 自己拼多轮消息
- 自己解析函数式输出
- 最后再转成 `pyautogui` 代码

### 4. 你需要什么配置

当前代码里，`SeedAgent` 的推理主路径直接读取：

```env
DOUBAO_API_KEY=your_key_here
DOUBAO_API_URL=your_api_url_here
```

这里要特别注意一个代码层面的事实：

- 当前 `SeedAgent.__init__` 里把 `self.inference_func` 固定指向了 `inference_with_thinking_ark`

也就是说，第一次试跑时，你应该按“需要 `DOUBAO_API_KEY` 和 `DOUBAO_API_URL`”来准备配置，而不是只看命令行参数里的 `--model_type`。

### 5. 第一次怎么跑

如果你已经有对应的豆包 / Ark 接口配置，可以这样跑：

```bash
uv run python scripts/python/run_multienv_seedagent.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model doubao-1-5-thinking-vision-pro-250428 \
  --model_type doubao \
  --num_envs 1 \
  --result_dir ./results/seedagent-one-task
```

如果你只是为了看链路，而不是马上调模型效果，这个例子最值得观察的是：

- 它如何保持标准 runner 不变
- 只在 agent 内部实现自己的推理协议

### 6. 它和 `PromptAgent` 的学习重点差别是什么

看 `PromptAgent`，你主要学的是：

- benchmark 最小契约

看 `SeedAgent`，你主要学的是：

- 只要外部接口稳定，内部逻辑可以非常不一样

这对你后面接自己的 agent 很重要。

## 五、例子 3：`OpenAICUAAgent`

这是最适合你研究“什么时候必须专门写 runner”的例子。

### 1. 该看哪些文件

- [mm_agents/openai_cua_agent.py](../../mm_agents/openai_cua_agent.py)
- [scripts/python/run_multienv_openaicua.py](../../scripts/python/run_multienv_openaicua.py)
- [lib_run_single.py](../../lib_run_single.py)
  里的 `run_single_example_openaicua(...)`

### 2. 它属于哪类接入

它属于：

- 特例 agent
- 特例 runner
- 特例 rollout

因为它不只是“根据观测产出动作”，它还额外做了两件事：

1. 在构造时直接拿 `env`
2. 在 agent 内部实现了 `step(...)`

这会让调用链发生明显变化。

### 3. 它的运行链路是什么

和前两个 agent 的最大区别是这里：

```text
run_multienv_openaicua.py
  -> OpenAICUAAgent(env=env)
  -> run_single_example_openaicua(...)
  -> agent.predict(...)
  -> agent.step(action)
  -> env.step(...)
```

也就是说：

- rollout 不再直接 `env.step(...)`
- 而是先走 `agent.step(...)`

所以它必须使用：

- `run_single_example_openaicua(...)`

而不能直接复用标准 `run_single_example(...)`

### 4. 你需要什么配置

当前代码里，OpenAI CUA 这条线使用的是：

```env
OPENAI_API_KEY_CUA=your_key_here
```

注意这里不是：

- `OPENAI_API_KEY`

而是专门单独读：

- `OPENAI_API_KEY_CUA`

另外，这条线第一次试跑时，建议你显式传 `--model`，不要完全依赖脚本默认值。

### 5. 第一次怎么跑

如果你有可用的 OpenAI CUA 权限，建议命令写得明确一点：

```bash
uv run python scripts/python/run_multienv_openaicua.py \
  --provider_name vmware \
  --path_to_vm "/path/to/your.vmx" \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model computer-use-preview \
  --num_envs 1 \
  --result_dir ./results/openaicua-one-task
```

这条命令的重点不是“分数一定高”，而是让你亲眼看到：

- `predict(...)` 产出的并不是普通 pyautogui 字符串
- agent 先把 CUA 风格动作转成 pyautogui
- rollout 再通过 `agent.step(...)` 去执行

### 6. 第一次跑这个例子最容易踩什么坑

最常见的是这 3 类：

- 没有 `OPENAI_API_KEY_CUA`
- `--model` 没显式指定，导致和你的账号能力不匹配
- 误以为它能直接复用标准 `run_single_example(...)`

所以这条线更适合在你已经看懂前两个例子之后再跑。

## 六、把三个例子放在一起比较

如果你只想快速抓住差别，可以记这 6 句话：

- `PromptAgent` 是最标准的 baseline。
- `SeedAgent` 是“内部实现不同，但外部协议不变”的典型例子。
- `OpenAICUAAgent` 是“外部协议都开始变化，所以必须专用 runner”的典型例子。
- `PromptAgent` 和 `SeedAgent` 都能继续复用标准 `run_single_example(...)`。
- `OpenAICUAAgent` 需要 `run_single_example_openaicua(...)`。
- 你自己接新 agent 时，第一版应尽量靠近 `PromptAgent` / `SeedAgent` 这条线，而不是直接走 `OpenAICUAAgent` 这种特例路径。

## 七、建议你的实际试跑顺序

最推荐的试跑顺序是：

1. 先跑 `PromptAgent`
2. 再跑 `SeedAgent`
3. 最后再跑 `OpenAICUAAgent`

每跑完一个，都去看：

- `traj.jsonl`
- `runtime.log`
- `recording.mp4`

你会很快建立一种直觉：

- 这个 agent 到底只是换了模型后端
还是
- 它已经改了整条 rollout 逻辑

## 八、如果你只打算先模仿一个例子，应该选谁

如果你接下来准备写自己的 agent，我的建议很明确：

- 先模仿 `PromptAgent`
或者
- 先模仿 `SeedAgent`

不要一开始就模仿 `OpenAICUAAgent`。

原因不是它不好，而是它已经不再是“最小接入模板”了。

它更像是：

- 特殊协议适配样例

而不是：

- 第一版新 agent 的最优起点

## 下一步建议

走到这里，最自然的下一步有两条：

1. 继续写文档，把 `SeedAgent` 按模板逐项拆开
2. 直接开始写一个 `mm_agents/my_agent.py`

如果你愿意，下一步我建议继续补一篇：

- `18-seed-agent-against-template_zh.md`

专门把 `SeedAgent` 按你刚看过的“最小接入模板”逐段对照拆解。
