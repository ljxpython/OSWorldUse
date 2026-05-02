# OSWorld CUA Bridge 使用指南

`osworld_cua_bridge` 是 OSWorld 侧的 CUA blackbox 接入层。它把 CUA 当成外部运行时或二进制进程使用，不要求修改 CUA 源码。

如果需要理解完整评测入口、调用链、时序和扩展点，先读：

```text
docs/cua-osworld-adapter/blackbox/DEVELOPER_GUIDE_zh.md
```

## 1. 目录职责

- `launcher.py`：启动 CUA 进程，拼装 `cua run` 参数，处理超时和退出码。
- `server.py`：启动本地 HTTP bridge server，接收 CUA 侧 openclaw 请求。
- `executor.py`：把 CUA tool 请求映射到 OSWorld `DesktopEnv` / controller 操作。
- `tool_translator.py`：把 CUA tool 参数转换成 `pyautogui` 执行动作。
- `protocol.py`：定义 bridge protocol 版本和请求响应结构。
- `failures.py`：记录标准失败类型，生成 `failure_summary.json` 的输入。
- `reporting.py`：生成 blackbox summary，包括 `summary.json`、`summary.csv`、domain 汇总和失败汇总。
- `bin/openclaw`：给 CUA 调用的 openclaw shim，负责把 tool call 转发给 OSWorld bridge。

边界约束：

- 不修改 CUA 源码。
- 不替换 OSWorld 原生 evaluator。
- 不在 bridge 中写 agent 逻辑，只负责工具执行、记录、失败分类和报告输入。

## 2. 配置方式

推荐在仓库根目录 `.env` 中配置 CUA 参数，CLI 参数优先级高于 `.env`。

常用环境变量：

```bash
OSWORLD_CUA_BIN=/path/to/cua/dist/cli/bin.js
OSWORLD_CUA_CONFIG_PATH=/path/to/cua/config/local.json
OSWORLD_CUA_REPO_ROOT=/path/to/cua
OSWORLD_OPENCLAW_BIN=/path/to/osworld/osworld_cua_bridge/bin/openclaw
OSWORLD_CUA_VERSION=cua-local
OSWORLD_CUA_RUNS_DIR=/tmp/osworld-cua-runs
OSWORLD_CUA_MAX_DURATION_MS=420000
OSWORLD_CUA_MAX_STEP_DURATION_MS=120000
OSWORLD_CUA_TIMEOUT_GRACE_SECONDS=60
```

最少必须满足：

- `OSWORLD_CUA_CONFIG_PATH` 指向可用的 CUA 配置文件。
- `OSWORLD_CUA_BIN` 可以解析到 CUA CLI，或系统 `PATH` 中存在 `cua`。
- `OSWORLD_OPENCLAW_BIN` 指向本目录的 `bin/openclaw`，不配置时脚本会使用仓库内默认路径。

## 3. 本地 smoke 验证

不启动 VM，只验证 bridge 协议、tool 翻译、failure 分类、summary、报告生成和 Web server 辅助逻辑：

```bash
uv run python scripts/python/cua_smoke_test.py \
  --result_dir ./results_cua_smoke
```

通过标准：

- `SMK-001` 到当前最新 SMK 项全部 `PASS`。
- 输出 `cua_smoke_report.json`。

## 4. 真实 VM 工具功能验证

用于验证 bridge tool 是否能在真实 VM 中执行：

```bash
uv run python scripts/python/cua_bridge_vm_functional_test.py \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --screen_width 1920 \
  --screen_height 1080 \
  --result_dir ./results_cua_bridge_functional
```

只验证部分工具时：

```bash
uv run python scripts/python/cua_bridge_vm_functional_test.py \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --tools screenshot,get_screen_size,get_cursor_position
```

## 5. CUA Blackbox 评测

推荐使用新的 CUA blackbox suite：

```bash
evaluation_examples/cua_blackbox/suites/regression.json
```

旧入口仍兼容：

```bash
evaluation_examples/test_cua_regression.json
```

单环境评测示例：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --model cua-blackbox-regression \
  --num_envs 1 \
  --max_steps 20 \
  --result_dir ./results_cua_regression \
  --screen_width 1920 \
  --screen_height 1080 \
  --build_report
```

当前本地 Mac 阶段建议 `num_envs=1`。如果要做 `num_envs>1`，需要多个独立 VM，不能让多个 worker 竞争同一个 `.vmx`。

## 6. 结果目录

blackbox 结果根目录格式：

```text
<result_dir>/<action_space>/<observation_type>/<model>/
  args.json
  <domain>/<task_id>/
    result.txt
    runtime.log
    cua_meta.json
    failure_summary.json
    recording.mp4
  summary/
    summary.json
    summary.csv
    domain_summary.json
    failure_summary.json
  report/
    report.json
    report.md
    index.html
```

说明：

- `result.txt`：OSWorld evaluator 分数。
- `runtime.log`：单任务运行日志。
- `cua_meta.json`：CUA 进程、bridge、openclaw 等运行元数据。
- `failure_summary.json`：标准失败分类。
- `recording.mp4`：VM 操作录屏，失败排查优先看这个。
- `summary/`：机器可读汇总。
- `report/`：对外展示用报告。

## 7. 报告生成

评测时加 `--build_report` 会自动生成报告。

也可以在已有结果目录上重建：

```bash
uv run python scripts/python/build_cua_blackbox_summary.py \
  --result_root <result-root> \
  --build_report
```

或只生成报告：

```bash
uv run python scripts/python/build_cua_blackbox_report.py \
  --result_root <result-root>
```

生成内容：

- `report/report.json`：统一聚合数据，给 Web 展示复用。
- `report/report.md`：适合贴到 PR、飞书或验收文档。
- `report/index.html`：离线可打开的静态 HTML 报告。

## 8. Web 只读展示

启动本地只读 Web viewer：

```bash
uv run python scripts/python/serve_cua_blackbox_report.py \
  --result_root <result-root> \
  --open_browser
```

多个结果目录：

```bash
uv run python scripts/python/serve_cua_blackbox_report.py \
  --result_root <result-root-a> \
  --result_root <result-root-b>
```

扫描目录：

```bash
uv run python scripts/python/serve_cua_blackbox_report.py \
  --results_dir ./results_cua_regression
```

安全边界：

- 只读，不修改原始评测结果。
- artifact 只允许访问 `result_root` 内的文件或目录。
- root 外路径会返回 `403`。

## 9. 新增 Case 方法

先判断新增 case 是否应进入通用 OSWorld benchmark：

- 通用 benchmark case：放到 `evaluation_examples/examples/<domain>/<case_id>.json`。
- CUA blackbox 专用 case：放到 `evaluation_examples/cua_blackbox/cases/<domain>/<case_id>.json`。

不要复制已有 OSWorld case。已有 case 只需要在 `suites/*.json` 中引用。

CUA 专用 case 示例：

```text
evaluation_examples/cua_blackbox/cases/chrome/cua-demo-open-downloads.json
evaluation_examples/cua_blackbox/suites/demo_custom_case.json
```

新增 CUA 专用 case 的步骤：

1. 在 `evaluation_examples/cua_blackbox/cases/<domain>/` 下创建 `<case_id>.json`。
2. 确保 JSON 中的 `id` 与文件名 `<case_id>` 一致。
3. 设置 `snapshot`、`instruction`、`config`、`related_apps` 和 `evaluator`。
4. 把 `<case_id>` 加入一个 suite，例如 `evaluation_examples/cua_blackbox/suites/demo_custom_case.json`。
5. 先跑静态校验，再跑 VM reset，再跑 blackbox 单任务。

静态校验：

```bash
uv run python scripts/python/validate_cua_regression_cases.py \
  --meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json
```

环境 reset 检查：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json \
  --domain chrome \
  --example_id cua-demo-open-downloads \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --check_env_reset \
  --result_dir ./results_cua_case_acceptance_demo
```

blackbox 单任务运行：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --test_all_meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json \
  --domain chrome \
  --example_id cua-demo-open-downloads \
  --model cua-blackbox-demo \
  --num_envs 1 \
  --result_dir ./results_cua_demo \
  --build_report
```

验收标准：

- 静态校验通过，无 missing getter / missing metric。
- `env.reset()` 能完成，reset 后有 screenshot。
- 未完成任务时 evaluator 不应误判高分。
- blackbox 运行能生成 `result.txt` 或标准 `failure_summary.json`。
- 报告能通过 `--build_report` 生成。

## 10. Case 验收

静态检查：

```bash
uv run python scripts/python/validate_cua_regression_cases.py
```

统一 case 验收：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --result_dir ./results_cua_case_acceptance
```

带 VM reset 检查：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --provider_name vmware \
  --path_to_vm /path/to/Ubuntu0.vmx \
  --headless \
  --check_env_reset \
  --result_dir ./results_cua_case_acceptance_env
```

## 11. 常见排障

CUA 无法启动：

- 检查 `OSWORLD_CUA_BIN` 是否存在。
- 检查 `OSWORLD_CUA_CONFIG_PATH` 是否存在且可读。
- 执行 `uv run python scripts/python/check_cua_blackbox_compatibility.py`。

openclaw 请求失败：

- 检查 `OSWORLD_OPENCLAW_BIN` 是否指向 `osworld_cua_bridge/bin/openclaw`。
- 看任务目录下 `bridge_requests.jsonl` 和 `runtime.log`。

任务失败但没有分数：

- 看任务目录下 `failure_summary.json`。
- 看 `summary/failure_summary.json` 的 failure type 聚合。
- 结合 `recording.mp4` 和 `runtime.log` 定位。

报告打不开：

- 先确认 `<result-root>/summary/summary.json` 存在。
- 重新执行 `build_cua_blackbox_report.py --result_root <result-root>`。
- Web 模式下确认传入的是 result root，不是 `report/` 子目录；脚本也支持直接传 `report/report.json`。
