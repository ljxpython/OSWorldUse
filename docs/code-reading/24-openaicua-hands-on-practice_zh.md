# 24 OpenAICUAAgent 动手实践

这一篇接在 [23 OpenAICUAAgent 推理主循环解读](./23-openaicua-predict-loop_zh.md) 后面看最合适。

前面两篇你已经知道了两件事：

- 这条 special-case 链路怎么跑
- `predict(...)` / `step(...)` / `self.cua_messages` 在代码里各自做什么

这一篇不再继续讲抽象结构，而是直接带你做一轮最小实践。

目标只有三个：

1. 亲手跑通一个单任务 `OpenAICUAAgent` demo
2. 用 PyCharm 单步看清 `predict -> step -> env.step` 的真实链路
3. 跑完以后，知道去哪里看结果，知道后面该从哪里改自己的模型适配

## 一、这次实践建议只跑一个任务

先不要一上来就跑多任务。

当前最合适的练手目标，还是继续用仓库里已经准备好的：

- [docs/code-reading/examples/test_one_chrome.json](./examples/test_one_chrome.json)

它只包含一个 Chrome 任务：

- `chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4`

这样做的好处很直接：

- 任务固定
- 结果目录固定
- 你更容易把日志、截图、代码断点对上

## 二、动手前先确认 4 个前置条件

正式跑之前，先确认下面 4 件事。

### 1. 你已经有可用的 `.vmx`

如果你前面已经跑过 `quickstart.py` 并生成了本地 VMware 虚拟机，那么 `--path_to_vm` 就应该传：

- `.vmx` 文件路径

例如：

```text
/Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx
```

### 2. 虚拟机里已经有 `init_state` 快照

因为 `DesktopEnv.reset(...)` 会尝试回滚到：

- `init_state`

如果这个快照没有准备好，后面的任务 reset 会失败。

### 3. 根目录 `.env` 里已经有 OpenAI key

当前这条 demo 优先读取的是：

- `OPENAI_API_KEY_CUA`

或者回退读取：

- `OPENAI_API_KEY`

如果你当前根目录 `.env` 里放的是我们前面一直在用的兼容变量名，现在也支持继续直接复用：

- `DOUBAO_API_KEY`
- `DOUBAO_API_URL`

如果你走兼容服务，还可以配：

- `OPENAI_BASE_URL_CUA`

或者：

- `OPENAI_BASE_URL`

但这里要注意一件事：

- `OpenAICUAAgent` 走的是 OpenAI Responses API 的 `computer_use_preview`
- 所以你的兼容服务必须真的兼容这套协议

如果后端只支持普通：

- `chat/completions`

那就算 key 读取到了，后面请求也还是会失败。

### 4. 你先用 `max_steps=1`

第一次练手不要追求任务成功率。

先保证：

- 能启动环境
- 能出模型响应
- 能真正执行一步 GUI 动作

所以第一次建议固定：

- `--max_steps 1`

## 三、第一轮先在命令行里跑通

第一次建议直接在仓库根目录执行：

```bash
rtk uv run python scripts/python/run_openaicua_demo.py \
  --path_to_vm "/Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx" \
  --provider_name vmware \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model computer-use-preview \
  --max_steps 1 \
  --result_dir ./results/openaicua-demo-smoke
```

这条命令的重点只有 4 个参数：

- `--path_to_vm`
  指向 `.vmx`
- `--provider_name vmware`
  让 `DesktopEnv` 走 VMware provider
- `--test_all_meta_path`
  只跑一个固定 Chrome 任务
- `--max_steps 1`
  只验证最小闭环

## 四、你应该重点看哪些日志

第一次跑时，不要试图读完所有日志。

只要盯住下面 5 个阶段就够了。

### 1. 环境启动

你应该能看到类似：

- `Initializing...`
- `Starting VMware VM...`
- `VMware VM IP address: ...`

### 2. 任务开始

你应该能看到类似：

- `Running OpenAICUA demo task: chrome/...`
- `Resetting environment...`

### 3. 模型响应

如果模型请求走通，后面会进入：

- `agent.predict(...)`

这时常见的关键日志是：

- `Response: ...`
- `Actions: [...]`

### 4. 动作执行

如果模型返回了一个可执行 `computer_call`，后面你会看到类似：

- `Step 1: {...}`
- `Executing action: pyautogui - ...`

### 5. 收尾与评测

跑完后通常会看到类似：

- `Result: ...`
- `Finished. Scores: [...]`

如果你只是第一次练手，哪怕 `result` 不是 `1.0` 也没关系。

第一次最关键的是：

- 这一轮动作有没有真的从模型走到环境里执行

## 五、跑完以后，先去看结果目录

结果目录大致会在：

- `results/openaicua-demo-smoke/pyautogui/screenshot/{model}/chrome/{example_id}/`

最值得先看的几个文件是：

- `traj.jsonl`
- `result.txt`
- `recording.mp4`
- `step_*.png`

如果你想回顾这些文件的含义，可以对照：

- [11 Monitor 与运行结果解读](./11-monitor-and-results_zh.md)

### 1. `traj.jsonl`

这是最重要的执行轨迹文件。

你应该重点看：

- `action`
- `reward`
- `done`
- `info`
- `screenshot_file`

对 `OpenAICUAAgent` 来说，最值得确认的是：

- 本轮到底执行了什么 `pyautogui` 代码

### 2. `step_*.png`

这个文件能帮你做一件很重要的事：

- 把“日志里的动作”与“屏幕实际变化”对起来

### 3. `recording.mp4`

如果你想快速回放整轮行为，这是最省时间的入口。

### 4. `result.txt`

它表示这次 evaluator 的最终分数。

记住：

- `result.txt` 是任务成败
- 不是模型链路是否打通

## 六、第二轮用 PyCharm 单步看代码

命令行跑通以后，下一步就不要再盲跑了。

你应该切到 PyCharm，用 debugger 真的把链路看一遍。

## 七、PyCharm 运行配置怎么填

### 1. Script path

填：

- [scripts/python/run_openaicua_demo.py](/Users/bytedance/PycharmProjects/test5/osworld/scripts/python/run_openaicua_demo.py)

### 2. Parameters

填：

```text
--path_to_vm /Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx --provider_name vmware --action_space pyautogui --observation_type screenshot --test_all_meta_path docs/code-reading/examples/test_one_chrome.json --model computer-use-preview --max_steps 1 --result_dir ./results/openaicua-demo-pycharm
```

### 3. Working directory

填仓库根目录：

- `/Users/bytedance/PycharmProjects/test5/osworld`

### 4. Python interpreter

选项目虚拟环境里的解释器：

- `/Users/bytedance/PycharmProjects/test5/osworld/.venv/bin/python`

### 5. Environment variables

如果你的 `.env` 已经放在仓库根目录，这个 runner 会自动 `load_dotenv(".env")`。

所以大多数情况下：

- 不需要在 PyCharm 里手工再抄一遍 key

## 八、第一轮调试时，断点打在哪里

第一次不要打太多断点。

最推荐的是下面 4 个位置。

### 1. 入口层

在 [run_openaicua_demo.py:203](/Users/bytedance/PycharmProjects/test5/osworld/scripts/python/run_openaicua_demo.py:203) 这一行附近打断点：

- `lib_run_single.run_single_example_openaicua(...)`

你要确认的是：

- env 已经构建好了
- agent 已经构建好了
- `example["instruction"]` 就是你当前要跑的任务

### 2. rollout 主循环

在 [lib_run_single.py:238](/Users/bytedance/PycharmProjects/test5/osworld/lib_run_single.py:238) 这一行附近打断点：

- `response, actions = agent.predict(...)`

你要重点看：

- `obs["screenshot"]` 是否拿到了图片
- `instruction` 是什么

### 3. agent 推理入口

在 [openai_cua_agent.py:656](/Users/bytedance/PycharmProjects/test5/osworld/mm_agents/openai_cua_agent.py:656) 附近打断点：

- `def predict(...)`

你要重点看：

- `self.cua_messages` 初始是不是空
- 首轮 `user` 消息是怎么组装的

### 4. 动作执行入口

在 [openai_cua_agent.py:748](/Users/bytedance/PycharmProjects/test5/osworld/mm_agents/openai_cua_agent.py:748) 附近打断点：

- `def step(...)`

你要重点看：

- `action["call_id"]`
- `action["pending_checks"]`
- `action["action"]`
- 执行后追加的 `computer_call_output`

## 九、单步时最值得看的变量

你第一次用 debugger 时，建议只盯下面几组变量。

### 1. `self.cua_messages`

这是整条链里最重要的变量。

你应该观察它如何从：

- 空列表

变成：

- 首轮 `user`
- 模型 `response.output`
- 本地 `computer_call_output`

### 2. `response.output`

你要确认：

- 返回里有没有 `computer_call`
- 有没有 `reasoning`
- 有没有 `message`

### 3. `actions`

你要确认：

- `_handle_item(...)` 最终有没有产出可执行 action dict

### 4. `state_correct`

你要确认：

- 为什么它是 `True`
- 或为什么它是 `False`

因为这个值会直接决定 rollout 是否继续下一轮。

## 十、这次实践最推荐的观察顺序

第一次别在代码里来回跳。

推荐顺序是：

1. 先在 `predict(...)` 里看首轮 `user` 消息怎么进 `self.cua_messages`
2. 再看 `_create_response()` 返回的 `response.output`
3. 再看 `_handle_item(...)` 怎么把 `computer_call` 变成 `actions`
4. 最后看 `step(...)` 怎么把执行后的截图写回 `computer_call_output`

如果你把这 4 步都看清了，`OpenAICUAAgent` 这条 special-case 链路就算真正吃透了。

## 十一、如果这轮跑不起来，优先排查什么

第一次实践时，最常见的问题就这几类。

### 1. 卡在虚拟机启动或重置

优先排查：

- `--path_to_vm` 是否真的是 `.vmx`
- VMware 虚拟机当前是否能正常启动
- `init_state` 快照是否存在

### 2. 启动后很久没进入模型调用

优先排查：

- guest server 是否正常启动
- VM IP 是否拿到了有效地址
- 环境 reset 是否已经完成

### 3. 直接报缺少 key

优先排查：

- 根目录 `.env` 是否存在
- `OPENAI_API_KEY_CUA` 或 `OPENAI_API_KEY` 是否真的已配置

### 4. 模型返回了文本，但没有动作

优先排查：

- `response.output` 里是否根本没有 `computer_call`
- `_handle_item(...)` 是否没能把返回结构转成 action dict
- `state_correct` 是否因此变成了 `False`

## 十二、如果你下一步要接自定义模型，实践重点放哪

你现在不要急着重写整个 agent。

更合理的实践顺序是：

1. 先用现有 demo 跑通一轮
2. 再把 `.env` 改成你自己的 `OPENAI_BASE_URL_CUA` 和模型名
3. 如果返回结构不兼容，再去改：
   - `_create_response()`
   - `_handle_item(...)`
   - `_convert_cua_action_to_pyautogui_action(...)`

也就是说，你现在真正要练的不是“从零造 agent”，而是：

- 在现有 `OpenAICUAAgent` 上做最小兼容适配

## 十三、这次实践做完后，你应该输出什么结论

你自己跑完一轮后，至少要能回答下面 5 个问题。

1. 这次 `response.output` 里到底包含了哪些 item 类型？
2. 这次模型最终生成了什么 `pyautogui` 动作？
3. `self.cua_messages` 在这一轮结束时，比开始时多了哪些消息？
4. `state_correct` 为什么是当前这个值？
5. 如果把底层模型换成你自己的兼容服务，你准备先改哪一层？

## 一句话建议

这次实践不要追求“任务一定成功”，而要追求：

- 你能亲眼看到一次 `computer_call -> pyautogui -> env.step -> computer_call_output` 的完整闭环
