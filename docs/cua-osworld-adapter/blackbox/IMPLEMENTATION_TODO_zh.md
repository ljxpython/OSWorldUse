# CUA Blackbox 实现任务清单

日期：2026-05-01
状态更新：2026-05-02

## 1. 目标

把方案 B 拆成一个能按顺序执行的实现清单，避免一开始就写成大而全的通用框架。

当前状态：

- Phase 0 到 Phase 2 的 MVP 主链路已经实现，并完成本地 smoke 与单个真实 VM benchmark 闭环。
- Phase 3 仍以稳定性和异常恢复为主，属于下一轮补强。
- Phase 4 已具备基本批量入口，仍缺 domain 级统计和结构化失败分类。
- Phase 5 继续保持第一阶段不做。

---

## 2. 实施顺序

建议严格按以下顺序做：

1. 环境和启动确认
2. bridge 最小闭环
3. blackbox runner 最小闭环
4. 结果目录和日志统一
5. 批量任务支持

---

## 3. Phase 0：前置确认

### 3.1 CUA 可用性

- [ ] `CUA` 可本地编译（本轮未重新编译，只确认可执行产物）
- [x] `CUA` 可打二进制
- [x] `CUA run --help` 正常
- [x] `CUA run --nodeid` 路径可执行
- [x] `CUA` 远程工具模式可在独立环境下工作

### 3.2 OSWorld 可用性

- [x] `DesktopEnv.reset()` 正常
- [x] `env._get_obs()` 可返回 screenshot
- [ ] `env.step("WAIT")` 正常（blackbox 当前不依赖，待单独确认）
- [ ] `env.step(pyautogui code)` 正常（blackbox 当前不依赖，待单独确认）
- [x] `env.evaluate()` 正常

### 3.3 约束确认

- [x] 第一阶段只做 Ubuntu
- [x] 第一阶段只做 screenshot 驱动
- [x] 第一阶段只做 GUI 动作，不碰 shell / office
- [x] 第一阶段只做单进程 smoke test

---

## 4. Phase 1：Bridge MVP

### 4.1 建目录

- [x] 新建 bridge 模块目录
- [x] 新建协议定义文件
- [x] 新建工具翻译文件
- [x] 新建执行器文件

### 4.2 最小工具

- [x] `screenshot`
- [x] `mouse_click`
- [x] `clipboard_type`
- [x] `key_press`
- [x] `hotkey`
- [x] `wait`

### 4.3 最小验收

- [x] `screenshot` 能返回当前屏幕
- [x] `mouse_click` 能点击指定位置
- [x] `clipboard_type` 能输入文本
- [x] `hotkey` 能触发快捷键
- [x] 错误能正确返回 JSON

### 4.4 调试产物

- [x] 每次请求写日志
- [x] 每次响应写日志
- [x] 每次 screenshot 可追踪

---

## 5. Phase 2：Blackbox Runner MVP

### 5.1 Runner 骨架

- [x] 新建 `run_multienv_cua_blackbox.py`
- [x] 新增单任务执行函数
- [x] 复用 OSWorld 的任务分发逻辑
- [x] 复用 OSWorld 的结果目录组织方式

### 5.2 子进程控制

- [x] 能启动 `cua` 二进制
- [x] 能传入 `instruction`
- [x] 能传入 `runId`
- [x] 能传入 `target-screen`
- [x] 能等待子进程退出
- [x] 能收集 stdout / stderr

### 5.3 结果落盘

- [x] 保存 `cua.stdout.log`
- [x] 保存 `cua.stderr.log`
- [x] 保存 `result.txt`
- [x] 保存 `recording.mp4`
- [x] 保存 OSWorld 侧 `runtime.log`

### 5.4 最小验收

- [x] 一个任务能从 reset 跑到 evaluate
- [x] `CUA` 不再操作宿主机
- [x] OSWorld VM 上的 GUI 变化可见

---

## 6. Phase 3：稳定性补强

### 6.1 常见失败处理

- [ ] screenshot 超时
- [ ] click 未生效
- [ ] 文本输入错位
- [ ] 子进程中断
- [x] runId mismatch 明确报错
- [ ] 远程桥 busy

### 6.2 可观测性

- [x] 统一请求 ID
- [x] 统一 run ID
- [x] 统一错误码
- [x] 统一结果目录结构

### 6.3 清理逻辑

- [ ] 任务结束后清理临时文件
- [ ] 异常退出时清理子进程
- [ ] 断点恢复不破坏已有结果

---

## 7. Phase 4：批量评测

### 7.1 多任务

- [x] 支持 `test_all.json`
- [x] 支持单 domain
- [x] 支持单 example id

### 7.2 多环境

- [x] 允许多个任务串行跑
- [x] 默认按 `num_envs=1` 做第一阶段验收
- [ ] 并行放到第二阶段再做（入口已有，真实并行稳定性待验收）

### 7.3 统计

- [x] 输出总分
- [ ] 输出 domain 分数
- [ ] 输出失败分类

---

## 8. Phase 5：后续可选项

以下内容不在第一阶段：

- [x] `app_open`
- [ ] `get_cursor_position`
- [ ] `wait_for_user`
- [ ] `shell_exec`
- [ ] `officecli`
- [ ] `records`
- [ ] `brain`

如果第一阶段跑通，再决定是否逐个恢复。

---

## 9. 建议的代码落点

建议后续代码先落这些位置：

- `scripts/python/run_multienv_cua_blackbox.py`
- `lib_run_single.py`
- `osworld_cua_bridge/`

如果后面要扩展，再考虑：

- `mm_agents/cua_blackbox/`
- `desktop_env/` 中的轻量辅助函数

---

## 10. 退出标准

当以下条件都满足时，可以认为方案 B 第一阶段完成：

1. `CUA` 能通过 blackbox runner 跑一个 OSWorld task
2. `CUA` 的动作真正作用在 OSWorld VM
3. OSWorld 能完成评测打分
4. 结果和日志可以回溯
5. 不需要修改 `CUA` 核心运行逻辑

当前 MVP 代码链路已满足以上 5 条；正式阶段验收仍需要补齐 Phase 3 的稳定性验收和 Phase 4 的统计输出。

---

## 11. 下一阶段整体规划

详细规划和测试点见：

- [下一阶段整体规划与测试点](./NEXT_PHASE_PLAN_AND_TEST_POINTS_zh.md)

建议按以下顺序继续开发：

1. `P1` 真实 VM 工具功能验收。
2. `P2` 异常分类与清理补强。
3. `P3` 批量评测汇总。
4. `P4` 真实 CUA 小规模回归。
5. `P5` 并行与长期稳定性。
6. `P6` Case 扩展与 CUA 版本兼容。

---

## 12. 下一阶段开发清单

### 12.1 P1：真实 VM 工具功能验收

- [x] 新增 `scripts/python/cua_bridge_vm_functional_test.py`
- [x] 复用 `DesktopEnv` 创建真实 Ubuntu VM 环境
- [x] 复用 `CuaBridgeExecutor` 和 `BridgeServer`
- [x] 支持直接发送 bridge tool request
- [x] 保存每步前后截图
- [x] 保存 `functional_steps.jsonl`
- [x] 保存 `functional_report.json`
- [x] 覆盖 `screenshot` / `get_screen_size`
- [x] 覆盖 click / double click / right click
- [x] 覆盖 drag / scroll
- [x] 覆盖 clipboard / keyboard / key / hotkey
- [x] 覆盖 wait / done

### 12.2 P2：异常分类与清理补强

- [x] 定义统一 `failure_type`
- [x] CUA 启动失败写入结构化失败原因
- [x] CUA timeout 写入结构化失败原因
- [x] bridge 错误写入结构化失败原因
- [x] controller 执行失败写入结构化失败原因
- [x] evaluate 失败写入结构化失败原因
- [x] 强制中断后清理 CUA 子进程
- [x] 强制中断后关闭 bridge server
- [x] 强制中断后保留已完成结果

### 12.3 P3：批量评测汇总

- [x] 生成 `summary.json`
- [x] 生成 `summary.csv`
- [x] 生成 `domain_summary.json`
- [x] 生成 `failure_summary.json`
- [x] 支持从已有 `result_dir` 重建 summary
- [x] 跳过已完成任务时不重复计分

### 12.4 P4：真实 CUA 小规模回归

- [x] 固定 3 到 5 个 Ubuntu benchmark task
- [x] 每个任务完整生成标准结果目录
- [x] 每个任务完整写入 `result.txt`
- [x] 每个任务保留 `recording.mp4`
- [x] 每个任务保留 CUA stdout / stderr
- [x] 每个失败任务有 `failure_type`
- [x] 小批量运行后生成 summary

验证记录：

- 2026-05-02 执行 `evaluation_examples/test_cua_regression.json`，5 个任务全部跑到 `env.evaluate()`。
- 结果目录：`results_cua_regression/pyautogui/screenshot/cua-blackbox-regression/`
- summary：`total=5`，`scored=5`，`failed=0`，`pending=0`，`average_score=0.5995482928125415`。
- 发现 1 条非阻断 bridge failure metadata：`bridge_unsupported_tool`，原因是 CUA 调用了当时尚未支持的 `app_open`；后续已按 CUA Linux 策略补齐 `app_open`。

### 12.5 P5：并行与长期稳定性

- [x] 串行连续 5 到 10 个任务不崩
- [ ] 验证 `num_envs > 1` 不串 runId
- [ ] 验证 `num_envs > 1` 不串 nodeId
- [ ] 验证 bridge port 不冲突
- [ ] 验证失败任务不影响后续任务

### 12.6 P6：Case 扩展与 CUA 版本兼容

- [ ] 明确复用 OSWorld 原生 case 和 evaluator 的边界
- [ ] 明确新增标准 benchmark case 的流程
- [ ] 明确新增 CUA 回归 case 的流程
- [x] 建立或约定 `evaluation_examples/test_cua_regression.json`
- [ ] 明确 CUA 外部 CLI 契约
- [ ] 明确 CUA tool schema 兼容边界
- [ ] CUA 升级时记录 `cua_version`
- [ ] CUA 升级时记录 `cua_bin` 和 `cua_config_path`
- [ ] 后续补强 CUA binary hash 和 config hash
- [ ] CUA 升级后执行 smoke、functional、小批量回归
