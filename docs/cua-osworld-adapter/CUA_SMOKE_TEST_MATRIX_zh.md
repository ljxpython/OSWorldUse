# CUA Smoke Test 用例表

日期：2026-05-01

## 1. 目的

这份表定义：

> 每次 `CUA` 或 adapter 升级后，最少要跑哪些测试，才能确认评测链路没坏。

Smoke test 的目标不是追求高分，而是确认：

- 启动正常
- 协议正常
- 动作能落到 OSWorld VM
- 结果能落盘
- 失败能定位

---

## 2. 测试分层

### 2.1 Hard Gate

必须通过，否则不允许进入正式 benchmark。

### 2.2 Soft Gate

建议通过，不通过也不一定阻断正式跑分，但必须记录风险。

---

## 3. Smoke Test 用例表

| ID | 层级 | 场景 | 前置条件 | 检查点 | 期望结果 |
|---|---|---|---|---|---|
| `SMK-001` | Hard | 启动检查 | `CUA` binary / runner 可用 | `CUA` 能启动，OSWorld 能 reset | 无启动错误，能进入任务循环。 |
| `SMK-002` | Hard | 协议健康检查 | bridge 已启动 | 请求 `health` / `version` | 返回可解析 JSON，版本信息完整。 |
| `SMK-003` | Hard | 截图回路 | VM 已进入桌面 | 请求一次 screenshot | 返回有效 PNG/JPEG，尺寸正确。 |
| `SMK-004` | Hard | 鼠标点击 | 已知目标按钮 | 执行 `mouse_click` | UI 有可见变化，且点位正确。 |
| `SMK-005` | Hard | 文本输入 | 已知输入框 | 执行 `clipboard_type` / `type` | 文本正确输入到 VM 内。 |
| `SMK-006` | Hard | 快捷键 | 已知快捷键动作 | 执行 `hotkey` / `key_press` | 组合键生效。 |
| `SMK-007` | Hard | 终止语义 | 任意空任务 | 分别执行 `WAIT / DONE / FAIL` | OSWorld 对三种终止信号处理一致。 |
| `SMK-008` | Hard | 错误输入 | 缺字段 / 未知工具 | 发送非法请求 | 返回结构化错误，不崩溃。 |
| `SMK-009` | Hard | 单任务闭环 | 一个最小 benchmark task | `reset -> predict -> step -> evaluate` | 能完成一条完整评测链路并生成结果。 |
| `SMK-010` | Soft | 版本回归 | 新旧版本各一套结果 | 对比相同 task 的结果目录 | 旧版本结果保持可复现，新版本结果单独落盘。 |
| `SMK-011` | Soft | 录屏与轨迹 | 开启录屏 / traj | 检查产物目录 | `traj.jsonl`、`result.txt`、`recording.mp4` 都存在。 |
| `SMK-012` | Hard | 汇总统计 | 合成成功、失败、pending 结果 | 生成 summary | 总数、得分、失败数、pending 数正确。 |
| `SMK-013` | Hard | domain 和 CSV 汇总 | 多 domain 合成结果 | 生成 domain summary 和 CSV | domain 分数和 CSV 行数正确。 |
| `SMK-014` | Hard | summary 重建 | 已有 result_dir | 重新生成 summary | failure summary 可重建。 |
| `SMK-015` | Hard | `app_open` Linux 策略 | 假 controller | 生成 app 打开命令 | 按 CUA Linux 策略尝试 gtk/gio/xdg/可执行文件。 |
| `SMK-016` | Hard | bridge busy | 并发 bridge 请求 | 第二个请求命中 busy | 返回 `BUSY` 且记录 `bridge_busy`。 |

---

## 4. 最小通过标准

以下用例必须通过才能算 smoke test 合格：

- `SMK-001`
- `SMK-002`
- `SMK-003`
- `SMK-004`
- `SMK-005`
- `SMK-006`
- `SMK-007`
- `SMK-008`
- `SMK-009`
- `SMK-012`
- `SMK-013`
- `SMK-014`
- `SMK-015`
- `SMK-016`

`SMK-010` 和 `SMK-011` 建议通过。

---

## 5. 本地自动化入口

当前已提供一个不依赖真实 VM 的本地 smoke test，用来先验证 adapter / bridge 的协议、动作翻译和 openclaw shim：

```bash
python3 scripts/python/cua_smoke_test.py --result_dir ./results_cua_smoke
```

覆盖范围：

- 覆盖 `SMK-001` 到 `SMK-008`、`SMK-012` 到 `SMK-016` 的本地协议、动作翻译、汇总、`app_open` 和 busy 错误链路。
- 不覆盖 `SMK-009` 的真实 benchmark 闭环；`SMK-009` 仍需要用 `run_multienv_cua.py` 或 `run_multienv_cua_blackbox.py` 在真实 VM 上跑一个最小 task。
- 报告落盘到 `results_cua_smoke/cua_smoke_report.json`。

真实 VM 单任务闭环建议命令模板：

```bash
python3 scripts/python/run_multienv_cua_blackbox.py \
  --provider_name vmware \
  --path_to_vm <path-to-vm> \
  --test_all_meta_path evaluation_examples/test_all.json \
  --domain chrome \
  --max_steps 5 \
  --num_envs 1
```

---

## 6. 每次测试要记录的字段

每个 smoke test 都应记录：

- `run_id`
- `cua_version`
- `adapter_version`
- `bridge_protocol_version`
- `eval_profile`
- `task_id`
- `result`
- `failure_reason`
- `artifact_paths`

---

## 7. 失败分类

建议统一分成这些失败类型：

- `startup_failure`
- `protocol_failure`
- `screenshot_failure`
- `action_failure`
- `environment_failure`
- `evaluation_failure`
- `artifact_failure`

这样后面看日志时，能快速判断是 `CUA`、adapter、bridge 还是 OSWorld 环境出问题。
