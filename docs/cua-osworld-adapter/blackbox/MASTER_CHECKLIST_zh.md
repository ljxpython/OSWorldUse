# CUA Blackbox 总体任务清单

日期：2026-05-01
状态更新：2026-05-02

> 这是后续逐项打勾的总清单。  
> 完成一项就勾一项，直到全部结束。

---

## 当前状态快照

- 当前主线已经收敛到 `osworld_cua_bridge/` blackbox bridge，不再推进历史 `mm_agents/cua` adapter 路线。
- Bridge MVP、blackbox runner、本地 smoke test、单个真实 VM benchmark 闭环已经完成。
- 当前 Mac 本地阶段验收范围收敛为 `num_envs=1`，并行稳定性不再阻塞本阶段。
- 真实 VM 工具矩阵、连续多任务稳定性、失败分类、小批量真实 CUA 回归和 P6 兼容性检查入口已经完成。
- CUA 本机路径、配置、版本和 timeout 默认值已收敛到仓库根目录 `.env`，代码不保留本机硬编码 CUA 路径。
- `env.step()` 的 `WAIT` 和 `pyautogui` GUI 动作已通过真实 VM 独立验证。
- `get_cursor_position` 已补充为低风险 CUA bridge tool，并通过本地 smoke 与真实 VM 单工具功能验证。
- 本清单中 `[x]` 表示代码已落地且至少经过本地 smoke 或真实单任务闭环验证；`[ ]` 表示仍待专项验证或实现补强。

---

## 1. 文档与边界

- [x] 确认方案 B 是当前主推进路径
- [x] 确认第一阶段只做 Ubuntu
- [x] 确认第一阶段只做 screenshot + GUI
- [x] 确认第一阶段不做 shell / office / records / brain
- [x] 确认验收标准已冻结

---

## 2. CUA 可用性确认

- [x] `CUA` 二进制能构建或取得可执行产物
- [x] `CUA run` 能执行
- [x] `CUA run --nodeid` 能执行
- [x] `CUA` 可以用指定模型启动（CUA CLI 支持 `--model`，当前 runner 默认通过 config 驱动；OSWorld `--model` 只作结果目录标签）
- [x] `CUA` 可以返回截图

---

## 3. OSWorld 环境确认

- [x] `DesktopEnv` 可正常启动
- [x] `env.reset()` 可用
- [x] `env._get_obs()` 可拿到 screenshot
- [x] `env.step()` 可执行 GUI 动作
- [x] `env.evaluate()` 可运行

---

## 4. Bridge 协议

- [x] 确认请求字段
- [x] 确认响应字段
- [x] 确认错误码
- [x] 确认 runId / reqId 规范
- [x] 确认支持 screenshot
- [x] 确认支持 mouse_click
- [x] 确认支持 clipboard_type
- [x] 确认支持 hotkey
- [x] 确认支持 wait

---

## 5. Bridge 实现

- [x] 建立 bridge 目录
- [x] 建立协议定义
- [x] 建立工具翻译层
- [x] 建立执行层
- [x] 建立日志输出
- [x] 建立错误返回

---

## 6. Runner 实现

- [x] 建立 blackbox runner 脚本
- [x] 建立单任务执行函数
- [x] 建立子进程启动逻辑
- [x] 建立子进程等待逻辑
- [x] 建立结果收集逻辑
- [x] 建立录屏收尾逻辑
- [x] CUA 默认参数从 `.env` 读取，CLI 参数可覆盖

---

## 7. 结果与日志

- [x] 保存 `result.txt`
- [x] 保存 `runtime.log`
- [x] 保存 `recording.mp4`
- [x] 保存 `cua.stdout.log`
- [x] 保存 `cua.stderr.log`
- [x] 保存 `cua_meta.json`

---

## 8. Smoke Test

- [x] 单任务跑通
- [x] 单环境跑通
- [x] CUA 动作落到 VM
- [x] 结果可写回
- [x] 任务可结束

---

## 9. 功能测试

- [x] click 正常
- [x] double click 正常
- [x] right click 正常
- [x] drag 正常
- [x] scroll 正常
- [x] text input 正常
- [x] hotkey 正常

---

## 10. 稳定性

- [x] 连续任务不崩
- [x] 异常可恢复
- [x] 子进程可清理
- [x] 日志可追踪
- [x] 失败原因可定位
- [ ] `num_envs > 1` 真实并行稳定性通过（当前本地单 VM 阻塞）
- [x] 当前阶段明确只以 `num_envs=1` 作为本地验收范围

---

## 11. 验收

- [x] 完成 smoke test 验收
- [x] 完成功能测试验收
- [x] 完成 `num_envs=1` 稳定性验收
- [x] 形成当前阶段验收结论
- [x] 决定进入 `num_envs=1` 小规模评测与 case/版本兼容维护阶段

---

## 12. 下一阶段开发与验证

- [x] 完成 P1：真实 VM 工具功能验收
- [x] 完成 P2：异常分类与清理补强
- [x] 完成 P3：批量评测汇总
- [x] 完成 P4：真实 CUA 小规模回归
- [x] 完成 P5：`num_envs=1` 串行与长期稳定性预验收
- [ ] 完成 P5 扩展：`num_envs>1` 并行稳定性预验收（Mac 单 VM 暂缓）
- [x] 完成 P6：Case 扩展与 CUA 版本兼容策略

---

## 13. 下一阶段测试点

- [x] `TP-001` 本地 smoke 测试通过
- [x] `TP-002` 到 `TP-014` 真实 VM 工具功能测试通过
- [x] `TP-015` 到 `TP-019` 异常与清理测试通过
- [x] `TP-020` 到 `TP-022` 汇总报表测试通过
- [x] `TP-023` 到 `TP-024` 真实 CUA 回归测试通过
- [x] `TP-025` 串行稳定性测试通过
- [ ] `TP-026` 并行稳定性测试通过（当前本地只有一个 `.vmx`，未进入 CUA / bridge 阶段）
- [x] `TP-027` 新增 case 静态检查入口通过
- [x] `TP-028` 到 `TP-030` 新增 case 环境/evaluator/blackbox 单跑检查入口已建立（实际新增 case 时执行）
- [x] `TP-031` 到 `TP-033` CUA CLI、配置、openclaw 兼容检查通过
- [ ] `TP-034` CUA 小批量升级回归通过（等待实际 CUA 升级时执行）

P5 并行验证记录：

- 2026-05-02 尝试 `num_envs=2`，两个 EnvProcess 同时竞争 `vmware_vm_data/Ubuntu0/Ubuntu0.vmx`，VMware provider 启动失败。
- 失败发生在 CUA / bridge 之前，因此不能作为 CUA 并发缺陷处理；完成 `TP-026` 需要准备多个独立 VM 或扩展 runner 支持 per-worker VM path。

P6 验证记录：

- 2026-05-02 `validate_cua_regression_cases.py` 静态检查 5 个回归 case 通过。
- 2026-05-02 `check_cua_case_acceptance.py` 默认静态模式检查 5 个回归 case 通过，并支持按 domain/example 过滤；`TP-028` 到 `TP-030` 的真实环境、evaluator、blackbox 单跑通过显式开关执行。
- 2026-05-02 `check_cua_blackbox_compatibility.py` 检查 CUA CLI、config、openclaw、回归 case 通过。
- 2026-05-02 `cua_smoke_test.py` 本地 smoke `SMK-001` 到 `SMK-015` 全部通过。
- 2026-05-02 `cua_smoke_test.py --result_dir ./results_cua_smoke_bridge_busy` 本地 smoke `SMK-001` 到 `SMK-016` 全部通过，其中 `SMK-016` 覆盖 bridge busy 错误码和 `bridge_busy` 失败分类。
- 2026-05-02 `cua_smoke_test.py --result_dir ./results_cua_smoke_cursor` 本地 smoke `SMK-001` 到 `SMK-017` 全部通过。
- 2026-05-02 `cua_bridge_vm_functional_test.py --tools get_cursor_position --result_dir ./results_cua_bridge_cursor_functional` 真实 VM 单工具功能测试通过。
