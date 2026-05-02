# CUA Blackbox 下一阶段整体规划与测试点

日期：2026-05-02

## 1. 目标

当前 blackbox MVP 已经完成：

- `CUA` 以黑盒二进制方式由 OSWorld runner 拉起。
- `CUA` 通过 `openclaw` shim 调用 OSWorld 侧 bridge。
- bridge 将 CUA 工具请求转成 VM 内 GUI 操作。
- 单个真实 VM benchmark 闭环已经跑通。

下一阶段目标不是重构主链路，而是把这条链路做成可验收、可定位、可小规模批量评测的状态。

---

## 2. 总体原则

- 不修改 `CUA` 源码。
- 优先在 OSWorld 侧补工具验收、错误分类、日志和汇总。
- 先验证 bridge 工具层，再验证真实 CUA 决策层。
- 每个开发任务必须有对应测试点和可落盘结果。
- 第一阶段仍只覆盖 Ubuntu、screenshot、GUI 工具。
- 新增 case 和 CUA 版本升级必须复用 OSWorld evaluator，不把指标逻辑写进 CUA adapter。

---

## 3. 推荐开发顺序

## 3.1 P1：真实 VM 工具功能验收

目的：

- 验证 bridge 工具映射在真实 VM 上是否稳定。
- 把“工具层问题”和“CUA 模型决策问题”分开。

建议实现：

- 新增 `scripts/python/cua_bridge_vm_functional_test.py`。
- 复用 `DesktopEnv`、`CuaBridgeExecutor`、`BridgeServer`。
- 不启动真实 CUA 模型，直接向 bridge 发送工具请求。
- 每个工具执行前后保存截图和结构化结果。

覆盖工具：

- `screenshot`
- `get_screen_size`
- `mouse_click`
- `mouse_double_click`
- `mouse_right_click`
- `mouse_drag`
- `mouse_scroll`
- `clipboard_type`
- `keyboard_type`
- `key_press`
- `hotkey`
- `wait`
- `done`

输出产物：

- `functional_report.json`
- `functional_steps.jsonl`
- `bridge_requests.jsonl`
- `bridge_screenshots/`
- `runtime.log`

通过标准：

- 每个工具请求返回 `ok=true` 或明确可解释的失败类型。
- 关键 GUI 工具在 VM 截图中能观察到状态变化。
- 失败时可以定位到协议层、翻译层、controller 层或 VM 状态层。

---

## 3.2 P2：异常分类与清理补强

目的：

- 让失败结果可汇总，而不是只散落在 stdout/stderr。
- 避免 timeout、中断、bridge 失败后留下不可控状态。

建议实现：

- 定义统一失败分类。
- 在 blackbox runner 和 bridge launcher 中写入结构化失败原因。
- 在 CUA 子进程 timeout、启动失败、evaluate 失败时写入统一 metadata。
- 验证 signal/timeout 后 bridge server 和环境进程能收尾。

建议失败分类：

- `cua_start_failed`
- `cua_timeout`
- `cua_nonzero_exit`
- `bridge_bad_request`
- `bridge_unsupported_tool`
- `bridge_exec_failed`
- `tool_translation_failed`
- `controller_exec_failed`
- `evaluate_failed`
- `recording_failed`
- `unknown_error`

输出产物：

- `failure.json`
- `cua_meta.json` 中的 `failure_type`
- `traj.jsonl` 中的错误事件
- `runtime.log` 中的关键状态转移

通过标准：

- 每个失败任务至少有一个稳定的 `failure_type`。
- CUA 启动失败不会阻塞后续任务。
- timeout 后不会长期占用 bridge server。
- 中断后可以通过日志确认清理路径。

---

## 3.3 P3：批量评测汇总

目的：

- 让多任务评测结果可以直接用于判断是否进入下一阶段。
- 输出 domain 维度和失败维度的统计。

建议实现：

- 新增或补强结果汇总逻辑。
- runner 结束后生成总览文件。
- 支持从已有 `result_dir` 重建 summary。

输出产物：

- `summary.json`
- `summary.csv`
- `domain_summary.json`
- `failure_summary.json`

通过标准：

- 能统计总任务数、完成数、失败数、平均分。
- 能按 domain 统计任务数、平均分、失败数。
- 能按 `failure_type` 聚合失败数量。
- 已完成任务不会被重复计算。

---

## 3.4 P4：真实 CUA 小规模回归

目的：

- 验证真实 CUA 决策、bridge、VM、OSWorld evaluate 的完整链路。
- 判断接入后是否具备小规模 benchmark 评测价值。

建议范围：

- 先选 3 到 5 个 Ubuntu task。
- 优先选择 Chrome、LibreOffice、文件管理这类能观察 GUI 行为的任务。
- 每个任务限制合理的 `max_steps`、`cua_max_duration_ms`、`cua_max_step_duration_ms`。

输出产物：

- 每个 task 的标准 OSWorld 结果目录。
- 每个 task 的 `result.txt`、`runtime.log`、`recording.mp4`、`cua.stdout.log`、`cua.stderr.log`、`cua_meta.json`。
- 批量级 `summary.json` 和 `failure_summary.json`。

通过标准：

- 至少 3 个任务能完整跑到 `env.evaluate()`。
- 失败任务有明确失败分类。
- 成功任务可以通过录屏和 bridge 日志追踪关键行为。
- 不需要修改 `CUA` 源码。

---

## 3.5 P5：并行与长期稳定性

目的：

- 在单环境稳定后，验证是否可以进入更大规模评测。

建议范围：

- 先做串行连续 5 到 10 个任务。
- 再验证 `num_envs > 1` 的真实并行稳定性。
- 并行前先确认 CUA runsDir、nodeId、runId、bridge port、result_dir 均不会冲突。

通过标准：

- 串行连续任务不因上一个任务状态污染下一个任务。
- 并行任务不会互相串 runId 或 nodeId。
- 失败任务不会导致整批评测提前退出。

当前验证记录：

- 2026-05-02 已完成串行 5 任务真实 CUA 回归，`num_envs=1` 下未出现跨任务目录、runId 或结果汇总污染。
- 2026-05-02 已尝试 `num_envs=2` 并行预验收，但当前本地 VMware 目录只有一个 `vmware_vm_data/Ubuntu0/Ubuntu0.vmx`。
- 两个 EnvProcess 同时启动同一个 VM，失败发生在 provider 启动阶段，日志见 `logs/normal-20260502@135207.log`，结果目录仅生成 `args.json`。
- 因未进入 CUA / bridge 阶段，`TP-026` 暂不能打勾；后续必须先准备多个独立 VM，或扩展 runner 让不同 worker 绑定不同 `path_to_vm`。

---

## 3.6 P6：Case 扩展与 CUA 版本兼容

目的：

- 明确新增评测 case 的标准流程。
- 明确 CUA 版本升级时的最小成本接入边界。
- 确保新增 case 和 CUA 升级都能复用 OSWorld 原生 evaluator。

详细策略：

- [评测 Case 扩展与 CUA 版本兼容策略](./EVALUATION_CASE_AND_CUA_VERSION_STRATEGY_zh.md)

建议实现：

- 补充 case 静态检查或说明文档。
- 固定 `evaluation_examples/cua_blackbox/suites/regression.json` 作为 CUA 小批量回归集合，保留 `evaluation_examples/test_cua_regression.json` 兼容入口。
- 在 summary 中保留 `cua_version`、`adapter_version`、`bridge_protocol_version`、`eval_profile`。
- 后续补强 CUA binary hash、config hash、repo commit。

通过标准：

- 新增 case 不需要修改 CUA adapter。
- CUA 版本升级优先只替换 `--cua_bin`、`--cua_config_path` 和 `--cua_version`。
- CLI、openclaw、tool schema 发生破坏性变化时能明确定位到兼容性破坏。

当前验证记录：

- 2026-05-02 已新增 `scripts/python/check_cua_blackbox_compatibility.py`，覆盖 CUA CLI 契约、config/openclaw 存在性、hash 元数据和回归 case 静态检查。
- 2026-05-02 已增强 `scripts/python/validate_cua_regression_cases.py`，检查 evaluator metric 和 getter 是否存在，并可输出 JSON report。
- 2026-05-02 已执行 CUA 兼容性检查，`cua --help`、`cua run --help`、回归 case 静态检查均通过。
- 2026-05-02 已执行本地 smoke，`SMK-001` 到 `SMK-019` 全部通过，其中 `SMK-016` 覆盖 bridge busy，`SMK-017` 覆盖 `get_cursor_position`，`SMK-018` 覆盖统一报告生成器，`SMK-019` 覆盖只读 Web report server 辅助逻辑。
- 2026-05-02 已执行真实 VM 单工具 functional，`TP-003a get_cursor_position` 通过。

---

## 3.7 P7：测试输入规范与美观报告

目的：

- 统一 CUA blackbox 专用 suite/profile 的输入目录。
- 保留现有 OSWorld case 复用能力，不复制已有用例。
- 在机器可读 JSON/CSV 之外，生成适合对外阅读的 HTML/Markdown 报告。
- 为后续 Web 展示预留稳定的 `report.json` 数据结构。

详细策略：

- [测试输入与报告展示规划](./TEST_INPUTS_AND_REPORTING_PLAN_zh.md)

建议实现：

- 新建 `evaluation_examples/cua_blackbox/`。
- 新建 `evaluation_examples/cua_blackbox/suites/regression.json`，优先引用现有 OSWorld case。
- 后续新增 CUA 专用 case 放到 `evaluation_examples/cua_blackbox/cases/`，不要复制已有 OSWorld case。
- 保留 `evaluation_examples/test_cua_regression.json` 兼容入口。
- 新增 `scripts/python/build_cua_blackbox_report.py`。
- 输出 `report/report.json`、`report/report.md`、`report/index.html`。
- 新增只读 Web 展示脚本。

当前实现状态：

- 2026-05-02 已新增 `evaluation_examples/cua_blackbox/`，并保留旧路径兼容。
- 2026-05-02 已新增 `scripts/python/build_cua_blackbox_report.py`，支持生成 JSON、Markdown、HTML 三种报告。
- 2026-05-02 已支持 `run_multienv_cua_blackbox.py --build_report` 和 `build_cua_blackbox_summary.py --build_report` 可选生成报告。
- 2026-05-02 已新增 `scripts/python/serve_cua_blackbox_report.py`，支持只读 Web 查看、多个 result root、前端过滤和 artifact root 限制。

通过标准：

- 新旧 suite 都能通过 case validation。
- 给定一个已有 result root 能生成统一报告。
- HTML 报告可以离线打开，能看懂总体结论、domain 汇总、失败分类和 artifacts 链接。
- Web 展示只读，不修改原始评测结果。

---

## 4. 测试点矩阵

| ID | 类型 | 测试点 | 触发方式 | 通过标准 |
| --- | --- | --- | --- | --- |
| TP-001 | 本地 smoke | bridge 协议、翻译、openclaw shim | `python3 scripts/python/cua_smoke_test.py` | 所有 SMK 项通过 |
| TP-002 | VM functional | screenshot 返回有效图片 | 直接 bridge 请求 | 图片有 mime、width、height、base64 |
| TP-003 | VM functional | screen size 返回真实 VM 尺寸 | 直接 bridge 请求 | width/height 与 runner 参数一致 |
| TP-003a | VM functional | cursor position 返回真实 VM 光标坐标 | 直接 bridge 请求 | output 包含整数 x/y |
| TP-004 | VM functional | click 生效 | 直接 bridge 请求 | 请求成功且截图可观察焦点变化 |
| TP-005 | VM functional | double click 生效 | 直接 bridge 请求 | 请求成功且目标产生双击行为 |
| TP-006 | VM functional | right click 生效 | 直接 bridge 请求 | 请求成功且上下文菜单或等效行为出现 |
| TP-007 | VM functional | drag 生效 | 直接 bridge 请求 | 请求成功且目标位置或选择区域变化 |
| TP-008 | VM functional | scroll 生效 | 直接 bridge 请求 | 请求成功且页面或列表滚动 |
| TP-009 | VM functional | clipboard_type 输入 | 直接 bridge 请求 | 文本出现在目标输入框 |
| TP-010 | VM functional | keyboard_type 输入 | 直接 bridge 请求 | 文本出现在目标输入框 |
| TP-011 | VM functional | key_press 生效 | 直接 bridge 请求 | Enter/Esc/Tab 等按键行为可观察 |
| TP-012 | VM functional | hotkey 生效 | 直接 bridge 请求 | Ctrl+L/Ctrl+A 等快捷键行为可观察 |
| TP-013 | VM functional | wait 不阻塞异常 | 直接 bridge 请求 | 等待后继续接受下一次请求 |
| TP-014 | VM functional | done 结束语义 | 直接 bridge 请求 | bridge 标记 done 且返回成功 |
| TP-015 | failure | runId mismatch | 构造错误 runId | 返回 `BAD_REQUEST` 且不执行工具 |
| TP-016 | failure | unsupported tool | 请求禁用工具 | 返回 `UNSUPPORTED_TOOL` |
| TP-017 | failure | CUA 启动失败 | 传入不存在的 `--cua_bin` | 写入 `failure_type=cua_start_failed` |
| TP-018 | failure | CUA timeout | 设置极短 timeout | 写入 `failure_type=cua_timeout` |
| TP-019 | failure | evaluate 失败 | 构造 evaluate 异常场景 | 写入 `failure_type=evaluate_failed` |
| TP-020 | reporting | 总分汇总 | 跑多个任务后汇总 | 输出总任务数、完成数、平均分 |
| TP-021 | reporting | domain 汇总 | 多 domain 结果目录 | 输出每个 domain 的平均分和失败数 |
| TP-022 | reporting | 失败分类汇总 | 混合成功失败任务 | 输出 failure type 分布 |
| TP-023 | regression | 真实 CUA 单任务 | blackbox runner | 完整生成 result 和日志 |
| TP-024 | regression | 真实 CUA 小批量 | 3 到 5 个 task | 可完成汇总且失败可定位 |
| TP-025 | stability | 串行连续任务 | `num_envs=1` 多任务 | 不崩溃、不串目录、不串 runId |
| TP-026 | stability | 并行任务预验收 | `num_envs>1`，且每个 worker 使用独立 VM 实例 | 不串 nodeId、runId、bridge port |
| TP-027 | case | 新增 case 静态检查 | `validate_cua_regression_cases.py` 或 `check_cua_case_acceptance.py` 默认模式 | id、snapshot、instruction、evaluator 均有效 |
| TP-028 | case | 新增 case 环境检查 | `check_cua_case_acceptance.py --check_env_reset` | reset/config/screenshot 正常 |
| TP-029 | case | 新增 case evaluator 检查 | `check_cua_case_acceptance.py --check_initial_evaluate` + 人工/脚本完成后 evaluate | 未完成低分，完成后高分 |
| TP-030 | case | 新增 case blackbox 单跑 | `check_cua_case_acceptance.py --run_blackbox` | 标准结果目录完整 |
| TP-031 | version | CUA CLI 兼容检查 | `cua --help` / `cua run --help` | 必需 flag 仍存在 |
| TP-032 | version | CUA 配置兼容检查 | `check_cua_blackbox_compatibility.py` | config 存在且 hash 可记录 |
| TP-033 | version | CUA openclaw 兼容检查 | `check_cua_blackbox_compatibility.py` + smoke | openclaw shim 请求格式兼容 |
| TP-034 | version | CUA 小批量升级回归 | `evaluation_examples/cua_blackbox/suites/regression.json`，兼容 `test_cua_regression.json` | 至少 3 个任务跑到 evaluate |

---

## 5. 推荐执行命令

本地 smoke：

```bash
python3 scripts/python/cua_smoke_test.py --result_dir ./results_cua_smoke
```

CUA blackbox 兼容性检查：

```bash
uv run python scripts/python/check_cua_blackbox_compatibility.py \
  --result_dir ./results_cua_compatibility
```

该命令默认读取仓库根目录 `.env` 中的 `OSWORLD_CUA_CONFIG_PATH`、`OSWORLD_CUA_BIN`、`OSWORLD_CUA_REPO_ROOT` 等配置；需要临时切换 CUA 版本时再显式传 CLI 参数覆盖。

CUA 回归 case 静态检查：

```bash
uv run python scripts/python/validate_cua_regression_cases.py \
  --meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --report_path ./results_cua_case_validation/report.json
```

真实 VM blackbox 单任务：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  --provider_name vmware \
  --path_to_vm /Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx \
  --headless \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path docs/code-reading/examples/test_one_chrome.json \
  --model cua-blackbox-smoke \
  --max_steps 10 \
  --num_envs 1 \
  --result_dir ./results_cua_blackbox_verify \
  --screen_width 1920 \
  --screen_height 1080 \
  --env_ready_sleep 10 \
  --settle_sleep 5 \
  --cua_max_duration_ms 420000 \
  --cua_max_step_duration_ms 120000 \
  --log_level INFO
```

真实 VM functional test 的目标命令：

```bash
uv run python scripts/python/cua_bridge_vm_functional_test.py \
  --provider_name vmware \
  --path_to_vm /Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx \
  --headless \
  --screen_width 1920 \
  --screen_height 1080 \
  --result_dir ./results_cua_bridge_functional
```

说明：最后一个命令是下一阶段要新增的目标入口，当前文档先定义目标行为和验收点。

统一报告生成：

```bash
uv run python scripts/python/build_cua_blackbox_report.py \
  --result_root <result-root> \
  --smoke_report <path-to-cua_smoke_report.json> \
  --functional_report <path-to-functional_report.json> \
  --compatibility_report <path-to-compatibility_report.json> \
  --case_acceptance_report <path-to-case_acceptance_report.json>
```

只传 `--result_root` 时，脚本会从 `<result-root>/summary/` 读取 blackbox summary，并把报告写到 `<result-root>/report/`。

也可以在评测结束后自动生成：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  ... \
  --build_report
```

或在重建 summary 时同时生成：

```bash
uv run python scripts/python/build_cua_blackbox_summary.py \
  --result_root <result-root> \
  --build_report
```

只读 Web 展示：

```bash
uv run python scripts/python/serve_cua_blackbox_report.py \
  --result_root <result-root> \
  --open_browser
```

多个结果目录可以重复传 `--result_root`，或用 `--results_dir <dir>` 扫描目录下的 `report/report.json`。

---

## 6. 完成判定

可以进入更大规模 benchmark 前，需要满足：

- TP-001 到 TP-014 通过。
- TP-015 到 TP-019 至少覆盖并能稳定产出 failure type。
- TP-020 到 TP-022 通过。
- TP-023 和 TP-024 通过。
- TP-027 到 TP-034 用于新增 case 和 CUA 升级验收。
- `MASTER_CHECKLIST_zh.md` 中功能测试和稳定性验收项完成勾选。

如果任一 hard gate 不通过，不进入批量 benchmark，只先修对应层级问题。
