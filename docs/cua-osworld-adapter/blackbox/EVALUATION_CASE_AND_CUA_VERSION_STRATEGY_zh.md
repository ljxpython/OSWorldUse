# 评测 Case 扩展与 CUA 版本兼容策略

日期：2026-05-02

## 1. 结论

当前 blackbox 路线可以复用 OSWorld 原有评测内容和指标体系。

原因是 blackbox runner 仍然沿用 OSWorld 原生评测入口：

- 从 `evaluation_examples/test_all.json` 或自定义 meta 文件读取任务集合。
- 从 `evaluation_examples/examples/<domain>/<example_id>.json` 读取 task 配置。
- 通过 `DesktopEnv.reset(task_config=example)` 初始化环境。
- 在 CUA 执行结束后调用 `env.evaluate()` 打分。
- 将分数写入标准 `result.txt`。

CUA 在这里替换的是“执行任务的主体”，不是 OSWorld 的 case、环境初始化、evaluator 或 metric。

---

## 2. 可以复用的内容

## 2.1 Case 组织方式

可以继续复用：

- `evaluation_examples/test_all.json`
- `evaluation_examples/test_small.json`
- 自定义 `test_xxx.json`
- `evaluation_examples/examples/<domain>/<example_id>.json`
- `--domain`
- `--example_id`
- `--test_all_meta_path`

当前 blackbox runner 已经支持这些入口。

## 2.2 指标体系

可以继续复用：

- task JSON 里的 `evaluator.func`
- task JSON 里的 `evaluator.result`
- task JSON 里的 `evaluator.expected`
- task JSON 里的 `evaluator.options`
- `desktop_env/evaluators/metrics/`
- `desktop_env/evaluators/getters/`
- `DesktopEnv.evaluate()`

因此 CUA 的最终成功率、平均分、domain 分数应该和 OSWorld 原有 agent 使用同一套 evaluator 语义。

## 2.3 环境初始化

可以继续复用：

- task JSON 里的 `snapshot`
- task JSON 里的 `config`
- task JSON 里的 `evaluator.postconfig`
- OSWorld provider、VM reset、controller 和 setup 逻辑

只要 case 能被 OSWorld 原生 runner 跑，理论上就能被 CUA blackbox runner 使用。

---

## 3. 不能直接等价复用的内容

以下内容不能自动认为和其他 OSWorld agent 完全等价：

- 原 agent 的逐步 action 轨迹格式。
- 原 agent 的 response/action 统计。
- 基于 OSWorld `env.step()` action history 的细粒度行为分析。
- CUA 内部 reasoning、tool call、截图上下文的原生结构。

blackbox 路线的过程可观测性主要来自：

- `recording.mp4`
- `runtime.log`
- `traj.jsonl`
- `bridge_requests.jsonl`
- `bridge_screenshots/`
- `cua.stdout.log`
- `cua.stderr.log`
- `cua_meta.json`
- `run_meta.json`

如果后续要做跨 agent 的细粒度行为对比，需要额外把 CUA bridge 请求归一化成 OSWorld 可比较的 step summary。

---

## 4. 新增评测 Case 的流程

## 4.1 优先使用 OSWorld 原生 case schema

新增 case 时优先按 OSWorld 原有方式做，不修改 CUA adapter。

最小流程：

1. 选择或新增 domain。
2. 新建 `evaluation_examples/examples/<domain>/<new_id>.json`。
3. 在 JSON 中定义 `id`、`snapshot`、`instruction`、`config`、`related_apps`、`evaluator`。
4. 优先复用现有 getter 和 metric。
5. 如果现有 evaluator 不够，再新增 getter 或 metric。
6. 把 `<new_id>` 加入 `evaluation_examples/test_all.json` 或自定义 meta 文件。
7. 用 `--domain` 和 `--example_id` 单独跑通。
8. 再加入小批量回归集合。

## 4.2 建议的 case 分类

建议把新增 case 分成两类。

标准 benchmark case：

- 目标是所有 agent 都可评测。
- 放入 `evaluation_examples/examples/<domain>/`。
- 可以加入标准 `test_all.json` 或标准子集。
- evaluator 必须尽量 agent 无关。

CUA 接入回归 case：

- 目标是验证 CUA blackbox 链路、GUI 工具和稳定性。
- 可以复用 `evaluation_examples/examples/<domain>/`，但先放入单独 meta 文件。
- 新的 suite/profile/case 统一放到 `evaluation_examples/cua_blackbox/`。
- `evaluation_examples/test_cua_regression.json` 作为历史兼容入口保留。
- 新增通用 benchmark case 仍放到 `evaluation_examples/examples/<domain>/`。
- 新增 CUA blackbox 专用 case 可以放到 `evaluation_examples/cua_blackbox/cases/<domain>/<case_id>.json`。
- 不应污染正式 benchmark 统计，除非 case 已被确认是通用任务。

当前推荐的回归 meta 路径：

- 新路径：`evaluation_examples/cua_blackbox/suites/regression.json`
- 兼容路径：`evaluation_examples/test_cua_regression.json`

短期内两个路径应保持内容一致，直到脚本默认路径全部迁移完成。

当前已固定的小批量回归集合：

- `chrome/030eeff7-b492-4218-b312-701ec99ee0cc`
  启用 Chrome `Do Not Track`
- `chrome/2ad9387a-65d8-4e33-ad5b-7580065a27ca`
  创建书签栏文件夹 `Favorites`
- `chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4`
  把默认搜索引擎改成 Bing
- `chrome/12086550-11c0-466b-b367-1d9e75b3910e`
  导航到密码管理页面
- `libreoffice_writer/4bcb1253-a636-4df4-8cb0-a35c04dfef31`
  导出当前文档为 PDF

## 4.3 Case JSON 最小骨架

```json
{
  "id": "new-uuid",
  "snapshot": "chrome",
  "instruction": "Do something observable in the VM.",
  "source": "internal",
  "config": [],
  "related_apps": ["chrome"],
  "evaluator": {
    "func": "match_in_list",
    "result": {
      "type": "default_search_engine"
    },
    "expected": {
      "type": "rule",
      "rules": {
        "expected": ["Bing"]
      }
    }
  },
  "proxy": false,
  "fixed_ip": false,
  "possibility_of_env_change": "low"
}
```

实际新增 case 时必须根据任务选择正确 `snapshot`、`config`、getter 和 metric。

---

## 5. 新增 Case 的验收点

新增 case 不能只看 CUA 是否能跑，还要先验收 case 本身。

## 5.1 Case 静态检查

检查项：

- JSON 可解析。
- `id` 和文件名一致。
- 所属 domain 已加入 meta 文件。
- `snapshot` 在当前 provider 下可用。
- `instruction` 明确、可操作、无歧义。
- `evaluator.func` 在 `desktop_env/evaluators/metrics/` 中存在。
- `evaluator.result.type` 和 `evaluator.expected.type` 对应 getter 存在。

当前可执行入口：

```bash
uv run python scripts/python/validate_cua_regression_cases.py \
  --meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --report_path ./results_cua_case_validation/report.json
```

也可以使用统一 case 验收入口的默认静态模式：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --result_dir ./results_cua_case_acceptance_static
```

## 5.2 Case 环境检查

检查项：

- `env.reset(task_config=example)` 正常。
- `config` 能完成初始状态准备。
- `env._get_obs()` 能返回 screenshot。
- `evaluator.postconfig` 不破坏任务结果。

执行：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --domain <domain> \
  --example_id <case-id> \
  --provider_name vmware \
  --path_to_vm <path-to-vm> \
  --headless \
  --check_env_reset \
  --result_dir ./results_cua_case_acceptance_env
```

## 5.3 Case 评测检查

检查项：

- 未执行任务时，`env.evaluate()` 应该返回低分或 0。
- 人工或脚本完成任务后，`env.evaluate()` 应该返回高分或 1。
- 同一个 case 重复运行结果稳定。
- evaluator 不依赖宿主机状态。

当前脚本支持 `--check_initial_evaluate` 记录 reset 后初始分数；人工或脚本完成后的高分检查仍需要 case 作者提供可复现完成步骤，或者用 blackbox 单跑结果辅助判断。

## 5.4 CUA 接入检查

检查项：

- 用 `run_multienv_cua_blackbox.py --domain <domain> --example_id <id>` 可单独运行。
- 标准结果目录完整。
- `result.txt`、`runtime.log`、`recording.mp4`、`cua_meta.json` 存在。
- 失败时有 `failure_type` 或可定位日志。

执行：

```bash
uv run python scripts/python/check_cua_case_acceptance.py \
  --meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --domain <domain> \
  --example_id <case-id> \
  --provider_name vmware \
  --path_to_vm <path-to-vm> \
  --headless \
  --run_blackbox \
  --blackbox_result_dir ./results_cua_case_acceptance_blackbox \
  --result_dir ./results_cua_case_acceptance_blackbox_report
```

---

## 6. CUA 版本兼容策略

## 6.1 最小成本接入边界

如果 CUA 保持以下外部契约稳定，升级 CUA 应该只需要换配置和二进制，不需要修改 OSWorld 侧核心代码：

- `cua run <task>` 可用。
- `--config` 可用。
- `--runs-dir` 可用。
- `--nodeid` 或 `--node-id` 可用。
- `--openclaw-bin` 可用。
- `--target-os linux` 可用。
- `--target-screen <WxH>` 可用。
- `--target-dpr 1` 可用。
- `--max-steps` 可用。
- `--max-duration-ms` 和 `--max-step-duration-ms` 可用。
- CUA 仍通过 openclaw 调用远程工具。
- openclaw 请求中仍能表达 `runId`、`reqId`、`tool`、`args`。

## 6.2 升级 CUA 时允许变化的内容

通常允许变化：

- CUA 二进制路径。
- CUA config 路径。
- CUA 模型名称。
- CUA 模型 provider、base url、api key。
- CUA 内部 prompt、reasoning、规划策略。
- CUA 内部日志格式。
- CUA runsDir 内部文件结构。

这些变化不应该影响 OSWorld 侧 evaluator。

## 6.3 会导致适配成本上升的变化

以下变化会破坏最小成本接入，需要修改 OSWorld 侧 bridge 或 launcher：

- `cua run` CLI flag 发生破坏性改名。
- `--nodeid` 远程工具模式被移除。
- `--openclaw-bin` 被移除或语义变化。
- openclaw CLI 调用格式变化。
- CUA tool 名称发生破坏性变化。
- CUA tool 参数 schema 发生破坏性变化。
- screenshot 返回格式发生破坏性变化。
- 坐标体系从 normalized/pixel 语义发生变化。
- CUA 不再支持关闭 shell、records、brain 或 knowledge。

对应修改位置通常是：

- `osworld_cua_bridge/launcher.py`
- `osworld_cua_bridge/bin/openclaw`
- `osworld_cua_bridge/protocol.py`
- `osworld_cua_bridge/tool_translator.py`

---

## 7. CUA 升级流程

每次升级 CUA 建议按固定流程执行。

## 7.1 记录版本信息

需要记录：

- `cua_version`
- `cua_bin`
- `cua_config_path`
- `adapter_version`
- `bridge_protocol_version`
- `eval_profile`
- `test_all_meta_path`
- `screen_width`
- `screen_height`

这些 CUA 相关参数既可以通过 CLI 传入，也可以通过环境变量作为默认值传入。CLI 参数优先级高于环境变量。

本仓库会在启动 CUA blackbox 相关入口时尝试加载仓库根目录 `.env`。`.env` 只保存本机路径、密钥和本地 timeout 默认值，不提交到仓库；代码中不保留 `/Users/.../cua` 这类本机硬编码 fallback。

| CLI 参数 | 环境变量 | 建议 |
| --- | --- | --- |
| `--cua_bin` | `OSWORLD_CUA_BIN` | 适合写入 env，用于切换 CUA 二进制 |
| `--cua_config_path` | `OSWORLD_CUA_CONFIG_PATH` | 适合写入 env，用于切换 CUA 配置 |
| `--cua_repo_root` | `OSWORLD_CUA_REPO_ROOT` | 适合写入 env，用于指定 CUA 工作目录 |
| `--cua_version` | `OSWORLD_CUA_VERSION` | 适合写入 env，用于结果标记 |
| `--openclaw_bin` | `OSWORLD_OPENCLAW_BIN` | 可写入 env，默认使用本仓库 shim |
| `--cua_runs_dir` | `OSWORLD_CUA_RUNS_DIR` | 谨慎写入 env，默认每个 task 独立目录更安全 |
| `--cua_node_id` | `OSWORLD_CUA_NODE_ID` | 单环境可写入 env，并发时不建议固定 |
| `--cua_max_duration_ms` | `OSWORLD_CUA_MAX_DURATION_MS` | 可写入 env |
| `--cua_max_step_duration_ms` | `OSWORLD_CUA_MAX_STEP_DURATION_MS` | 可写入 env |
| `--cua_timeout_grace_seconds` | `OSWORLD_CUA_TIMEOUT_GRACE_SECONDS` | 可写入 env |

以下运行时环境变量由 OSWorld 自动注入或覆盖后传给 CUA 子进程，不建议绕过 runner 直接手写依赖；其中 `OSWORLD_CUA_NODE_ID` 如果手动设置，只应作为 runner 默认入参使用：

- `OSWORLD_CUA_BRIDGE_URL`
- `OSWORLD_CUA_RUN_ID`
- `OSWORLD_CUA_NODE_ID`
- `CUA_CONFIG_DIR`
- `CUA_OSWORLD_MODEL_API_KEY`

当前已补强 metadata：

- CUA binary hash。
- CUA config hash。
- runtime config hash。
- openclaw shim hash。
- meta file hash。

后续仍可继续补充：

- CUA repo commit。

## 7.2 兼容性检查

检查命令：

```bash
cua --help
cua run --help
```

检查项：

- 必需 CLI flag 仍存在。
- `--nodeid` 或 `--node-id` 仍存在。
- `--openclaw-bin` 仍存在。
- timeout、max steps、target screen 参数仍存在。

当前可执行入口：

```bash
uv run python scripts/python/check_cua_blackbox_compatibility.py \
  --result_dir ./results_cua_compatibility
```

如果未显式传 `--cua_config_path`，该命令从 `.env` 的 `OSWORLD_CUA_CONFIG_PATH` 读取。

输出：

- `compatibility_report.json`
- CUA CLI 契约检查结果
- CUA binary / config / openclaw / meta hash
- 回归 case 静态检查结果

## 7.3 本地 smoke

执行：

```bash
python3 scripts/python/cua_smoke_test.py --result_dir ./results_cua_smoke
```

通过标准：

- bridge protocol 正常。
- openclaw shim 正常。
- 工具翻译正常。
- disabled tool 仍被拒绝。

## 7.4 真实 VM functional test

执行下一阶段新增的 functional test。

通过标准：

- screenshot、click、text、hotkey 等基础工具在 VM 内可用。
- bridge request/response 可追踪。
- failure type 可用。

## 7.5 真实 CUA 小批量回归

执行：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  --provider_name vmware \
  --path_to_vm /Users/bytedance/PycharmProjects/test5/osworld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx \
  --headless \
  --action_space pyautogui \
  --observation_type screenshot \
  --test_all_meta_path evaluation_examples/cua_blackbox/suites/regression.json \
  --model <cua-version-label> \
  --num_envs 1 \
  --result_dir ./results_cua_regression \
  --screen_width 1920 \
  --screen_height 1080 \
  --log_level INFO
```

`--cua_bin` 和 `--cua_config_path` 可省略，默认从 `.env` 的 `OSWORLD_CUA_BIN` 与 `OSWORLD_CUA_CONFIG_PATH` 读取；升级验证时可以显式传参覆盖。

通过标准：

- 至少 3 个任务跑到 `env.evaluate()`。
- 成功任务有可追踪录屏和日志。
- 失败任务有明确失败原因。

---

## 8. 最终判定

新增 case 可以进入评测集合，需要满足：

- case 静态检查通过。
- case 环境检查通过。
- case 评测检查通过。
- CUA blackbox 单任务运行通过或失败可定位。

CUA 新版本可以替换旧版本，需要满足：

- CLI 兼容性检查通过。
- 本地 smoke 通过。
- 真实 VM functional test 通过。
- 真实 CUA 小批量回归通过。
- 不需要修改 CUA 源码。

如果 CUA 升级导致 OSWorld 侧必须修改 bridge 或 launcher，应记录为兼容性破坏，不视为最小成本升级。
