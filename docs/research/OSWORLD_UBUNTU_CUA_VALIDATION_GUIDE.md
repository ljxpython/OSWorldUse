# OSWorld Ubuntu 环境下验证 CUA 指南

## 1. 目标

你当前已经有一个本地部署好的 Ubuntu 环境。  
本指南的目标是说明：

1. 如何检查当前 OSWorld 运行环境是否齐全
2. 如何使用 OSWorld 来验证你的项目 `CUA`
3. OSWorld 的用例集在哪里
4. 它是如何评估任务完成情况的
5. 评估指标有哪些

本指南默认你当前工作目录是：

`/Users/bytedance/PycharmProjects/test5/osworld`

## 2. 先明确：OSWorld 验证 CUA 的基本方式

OSWorld 的基本运行逻辑不是“直接拿 CUA 工程整仓跑”，而是：

1. OSWorld 提供任务集
2. OSWorld 提供环境控制与 reset / step / evaluate
3. 你把 CUA 包装成一个符合 OSWorld 接口的 agent
4. OSWorld 用 benchmark 任务去驱动这个 agent
5. OSWorld 保存轨迹、截图、录像并计算结果

从当前仓库来看，这条链已经存在：

- 环境抽象：`desktop_env/desktop_env.py`
- 单任务执行：`lib_run_single.py`
- 串行 runner：`run.py`
- 并行 runner：`scripts/python/run_multienv.py`
- CUA 适配示例：
  - `mm_agents/openai_cua_agent.py`
  - `mm_agents/opencua/opencua_agent.py`

## 3. 本地 Ubuntu 环境要检查什么

### 3.1 Python 侧

至少检查：

- Python 版本
- 依赖是否安装完整
- OpenAI / 其他模型 API Key 是否已配置

建议检查：

```bash
python --version
pip show pyautogui
pip show requests
pip show gymnasium
pip show openai
```

如果你用当前仓库环境，优先参考：

- `requirements.txt`
- `README.md`

### 3.2 宿主机 provider 侧

如果你本地 Ubuntu 环境跑在 `VMware` 中，要检查：

- `vmrun` 可用
- `.vmx` 路径可访问
- VM 能正常启动和恢复 snapshot

如果你走的是其他 provider，也要保证对应 provider 的环境可用。

### 3.3 guest Ubuntu 内部环境

OSWorld 真正依赖的是 guest 里的桌面环境和 server。

至少要确认：

- 图形桌面正常
- OSWorld server 已正确安装 / 可启动
- guest 内可被 host 通过 HTTP 接口访问
- 截图、执行命令、accessibility tree 接口可用

当前项目的控制逻辑依赖 guest server 提供这些接口：

- `/screenshot`
- `/accessibility`
- `/terminal`
- `/execute`
- `/setup/*`

对应控制器见：

- `desktop_env/controllers/python.py`
- `desktop_env/controllers/setup.py`

server 端实现见：

- `desktop_env/server/main.py`

### 3.4 Ubuntu guest 中的应用和任务依赖

很多 benchmark 任务不是纯桌面空环境，它们依赖：

- Chrome / Chromium
- LibreOffice
- VS Code
- GIMP
- VLC
- Thunderbird
- socat
- 以及部分账号、代理、Google 配置

这部分配置主要参考：

- `desktop_env/server/README.md`
- `desktop_env/evaluators/README.md`
- `SETUP_GUIDELINE.md`

## 4. 如何快速检查 OSWorld 环境是否可跑

### 4.1 第一关：最小 smoke test

先跑：

```bash
python quickstart.py --provider_name vmware --path_to_vm /path/to/your/vm.vmx
```

`quickstart.py` 做的事情很简单：

1. 构造一个最小任务
2. 创建 `DesktopEnv`
3. `reset(task_config=example)`
4. 执行一个 `pyautogui.rightClick()`
5. 关闭环境

如果这个都跑不通，说明你先别碰 benchmark，更别碰 CUA 适配。

### 4.2 第二关：正式 benchmark 最小子集

建议不要一上来跑全量任务。  
先选少量任务，例如单个 domain 的几个任务。

最小串行验证可以参考：

```bash
python run.py \
  --provider_name vmware \
  --path_to_vm /path/to/your/vm.vmx \
  --observation_type screenshot \
  --model gpt-4o \
  --max_steps 15 \
  --result_dir ./results_smoke
```

更接近正式实验的是并行 runner，但你当前阶段建议先 `num_envs=1`：

```bash
python scripts/python/run_multienv.py \
  --provider_name vmware \
  --path_to_vm /path/to/your/vm.vmx \
  --observation_type screenshot \
  --model gpt-4o \
  --num_envs 1 \
  --max_steps 15 \
  --result_dir ./results_smoke
```

## 5. 如何用 OSWorld 验证你的 CUA

### 5.1 路线一：复用已有 CUA 适配

当前仓库里已经有两类 CUA 适配：

1. `OpenAICUAAgent`
   - 文件：`mm_agents/openai_cua_agent.py`
   - runner：`scripts/python/run_multienv_openaicua.py`

2. `OpenCUAAgent`
   - 文件：`mm_agents/opencua/opencua_agent.py`
   - runner：`scripts/python/run_multienv_opencua.py`

如果你的 CUA 和它们风格接近，最省事的方式是：

- 按这两个示例写一个你自己的 `mm_agents/xxx_cua_agent.py`
- 再复制一份 runner，例如：
  - `scripts/python/run_multienv_mycua.py`

### 5.2 你要满足的最小 agent 接口

从当前 runner 和 `lib_run_single.py` 看，最小要满足：

- `reset(...)`
- `predict(instruction, obs, **kwargs)` 或近似接口

对于普通 `PromptAgent` 风格：

- `predict()` 返回 `response, actions`

对于 `OpenAICUAAgent` 风格：

- `predict()` 返回包含 `state_correct / messages / response / model_usage` 的结构，以及动作列表
- `step()` 可能交由 agent 自己进一步处理

所以如果你要接你自己的 CUA，最务实的做法不是完全重写 OSWorld，而是：

- 参考 `openai_cua_agent.py`
- 把你的 CUA 输出动作映射到 OSWorld 能执行的动作格式

### 5.3 动作最终要落到什么格式

最终 OSWorld 环境执行的核心还是：

- `pyautogui` 字符串代码
- 或 `computer_13` 结构化动作

当前仓库里绝大多数 CUA 路线最后都会把动作转成：

- `pyautogui.moveTo(...)`
- `pyautogui.click(...)`
- `pyautogui.typewrite(...)`
- `pyautogui.hotkey(...)`

也就是说：

**你自己的 CUA 不需要和 OSWorld 的内部完全一致，但最终必须能产出 OSWorld 能消费的动作。**

## 6. 用例集在哪里

### 6.1 总任务清单

总入口在：

- `evaluation_examples/test_all.json`

它的结构是：

- key = domain
- value = 该 domain 下的 task id 列表

例如：

- `chrome`
- `gimp`
- `libreoffice_calc`
- `libreoffice_impress`
- `libreoffice_writer`
- `multi_apps`
- `os`
- `thunderbird`
- `vlc`
- `vs_code`

### 6.2 具体任务文件

Ubuntu 任务文件主要在：

- `evaluation_examples/examples/<domain>/<example_id>.json`

Windows 任务文件主要在：

- `evaluation_examples/examples_windows/...`

### 6.3 一个任务文件长什么样

一个典型任务包含：

- `id`
- `instruction`
- `config`
- `evaluator`

例如 Chrome 任务：

- 先启动浏览器
- 设置远程调试端口
- 最后用 evaluator 检查默认搜索引擎是否变成 Bing

这说明：

- `instruction` 决定 agent 要做什么
- `config` 决定任务开始前环境怎样被布置
- `evaluator` 决定成功怎么判定

## 7. 它是如何评估的

### 7.1 评估入口

核心评估函数在：

- `DesktopEnv.evaluate()`

大逻辑是：

1. 执行 `postconfig`
2. 根据任务 `evaluator` 配置
3. 调用相应 getter 拿结果状态
4. 调用相应 metric 判定结果
5. 输出单任务分数

### 7.2 evaluator 的组成

一个任务的 evaluator 一般包含：

- `func`
- `result`
- `expected`
- `options`
- `postconfig`

理解方式：

- `result`：从环境里取什么
- `expected`：期望值是什么
- `func`：怎么比较

例如：

- `result.type = default_search_engine`
- `expected.rules.expected = ["Microsoft Bing", "Bing"]`
- `func = match_in_list`

### 7.3 getter 和 metric 在哪

getter 和 metric 主要分两块：

- getter：`desktop_env/evaluators/getters/`
- metric：`desktop_env/evaluators/metrics/`

metric 现在已经按领域拆得很细，比如：

- `chrome.py`
- `docs.py`
- `gimp.py`
- `slides.py`
- `table.py`
- `vlc.py`
- `vscode.py`
- `basic_os.py`
- `general.py`

这说明 OSWorld 不是只看一个大模型打分，而是大量使用程序化规则判断。

## 8. 评估指标有哪些

### 8.1 单任务层指标

单任务最终最核心的是：

- **task result / score**

这通常是：

- `0.0` = 失败
- `1.0` = 成功

但也可能是：

- 介于 `0` 和 `1` 之间的部分分

因为有些 evaluator 会返回平均分或组合分。

### 8.2 任务过程记录

单任务执行过程中会记录：

- 每步动作
- 每步响应
- 每步截图
- `traj.jsonl`
- `recording.mp4`
- `runtime.log`

所以它不只是给一个分，还保存了复盘材料。

### 8.3 汇总层指标

`show_result.py` 汇总时主要看：

- 每个 domain 的 success rate
- Office / Daily / Professional 三类 success rate
- Overall success rate
- 总得分 / 总任务数

更具体地说：

1. **Per-domain success rate**
2. **Category-level success rate**
   - Office
   - Daily
   - Professional
3. **Overall success rate**
4. **Detailed score**
   - 格式：`score/total`

### 8.4 当前项目的“指标”本质

当前 OSWorld 的评估本质上更接近：

- **任务完成率 benchmark**

而不是复杂的 RL 奖励体系。

虽然 `step()` 里也有 `reward` 变量，但当前主流程真正看的是：

- `evaluate()` 产出的最终任务分

## 9. 你现在最适合怎么验证自己的 CUA

### Phase 1：环境验证

先确认：

1. `quickstart.py` 跑通
2. guest server 能正常提供 screenshot / execute / setup 接口
3. 你本地 Ubuntu VM 的 snapshot / reset 可用

### Phase 2：基线验证

先用现成基线 agent 跑少量任务，确认 benchmark 自身无问题：

- `chrome`
- `os`
- `multi_apps`

各挑 1 到 3 个任务就够

### Phase 3：CUA 接口接入

从这两条里选一条：

1. 参考 `mm_agents/openai_cua_agent.py`
2. 参考 `mm_agents/opencua/opencua_agent.py`

把你自己的 CUA 包成一个 OSWorld agent。

### Phase 4：少量任务试跑

建议先跑：

- 1 个 domain
- 3 到 5 个 task
- `num_envs = 1`

先看：

- 能不能稳定出动作
- 环境有没有 reset 污染
- evaluator 是否能得到可解释结果

### Phase 5：正式小规模 benchmark

再逐步扩大到：

- 单个 domain 全量
- 多个 domain
- 最后才考虑大规模跑分

## 10. 建议你优先检查的内容

如果你现在就开始动手，我建议你按这个顺序检查：

1. Ubuntu VM 能否正常启动和回滚 snapshot
2. guest 中 OSWorld server 是否可访问
3. `quickstart.py` 是否成功
4. 现成基线 agent 能否跑一个任务
5. 你的 CUA 是否能映射成 OSWorld 动作
6. 单任务结果是否被正确写入 `result.txt`
7. `show_result.py` 是否能汇总

## 11. 一句话总结

你现在本地已经有 Ubuntu，下一步不是直接硬上全量 benchmark，而是：

**先把 OSWorld 环境跑通，再用现成 CUA 适配示例包你的 agent，最后从少量任务开始验证。**

当前最关键的三个事实是：

1. **用例集在** `evaluation_examples/`
2. **评估入口在** `DesktopEnv.evaluate()`
3. **核心指标是** 单任务得分 + domain / category / overall success rate
