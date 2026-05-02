# CUA Blackbox 单环境阶段验收结论

日期：2026-05-02

## 1. 验收范围

当前 Mac 本地磁盘空间有限，阶段验收范围明确收敛为：

- `provider_name=vmware`
- `num_envs=1`
- Ubuntu
- screenshot observation
- GUI 工具链路
- 不修改 `CUA` 源码

`num_envs>1` 并行稳定性暂缓，不作为当前阶段进入小规模评测的阻塞项。

## 2. 通过项

- 本地 bridge smoke 通过。
- 真实 VM 工具功能测试通过。
- 异常分类与清理补强通过。
- 批量 summary、domain summary、failure summary 通过。
- 真实 CUA 5 任务小规模回归通过。
- `num_envs=1` 串行连续任务稳定性通过。
- P6 case 静态检查、CUA CLI 契约检查、config/openclaw/hash 元数据检查通过。

## 3. 关键验证记录

- `results_cua_regression/pyautogui/screenshot/cua-blackbox-regression/`
  5 个任务全部跑到 `env.evaluate()`，`failed=0`，`pending=0`。
- `results_cua_compatibility/compatibility_report.json`
  CUA CLI、config、openclaw、回归 case 静态检查通过。
- `results_cua_smoke_p6/cua_smoke_report.json`
  `SMK-001` 到 `SMK-015` 全部通过。
- `results_cua_smoke_bridge_busy/cua_smoke_report.json`
  `SMK-001` 到 `SMK-016` 全部通过，其中 `SMK-016` 覆盖 bridge busy 错误码和 `bridge_busy` 失败分类。

## 4. 当前不通过或暂缓项

- `TP-026 num_envs>1` 并行稳定性暂缓。
- 暂缓原因是本地只有一个 `vmware_vm_data/Ubuntu0/Ubuntu0.vmx`，两个 worker 会竞争同一个 VM。
- 这不是 CUA blackbox bridge 并发缺陷，后续需要多个独立 VM 或 per-worker VM path 支持再验收。

## 5. 结论

当前方案在 `num_envs=1` 范围内验收通过，可以进入单环境小规模评测和持续 case/版本兼容维护。

后续如果要进入并行评测，需要先解决独立环境供给问题，再恢复 `TP-026`。
