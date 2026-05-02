# CUA Blackbox 总体任务清单

日期：2026-05-01
状态更新：2026-05-02

> 这是后续逐项打勾的总清单。  
> 完成一项就勾一项，直到全部结束。

---

## 当前状态快照

- 当前主线已经收敛到 `osworld_cua_bridge/` blackbox bridge，不再推进历史 `mm_agents/cua` adapter 路线。
- Bridge MVP、blackbox runner、本地 smoke test、单个真实 VM benchmark 闭环已经完成。
- 仍未完成的是真实 VM 工具矩阵、连续多任务稳定性、失败分类和最终验收结论。
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
- [ ] `env.step()` 可执行 GUI 动作（blackbox 当前直接走 controller，待单独确认）
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

- [ ] 连续任务不崩
- [x] 异常可恢复
- [x] 子进程可清理
- [x] 日志可追踪
- [x] 失败原因可定位

---

## 11. 验收

- [x] 完成 smoke test 验收
- [x] 完成功能测试验收
- [ ] 完成稳定性验收
- [ ] 形成验收结论
- [ ] 决定是否进入下一阶段

---

## 12. 下一阶段开发与验证

- [x] 完成 P1：真实 VM 工具功能验收
- [x] 完成 P2：异常分类与清理补强
- [x] 完成 P3：批量评测汇总
- [x] 完成 P4：真实 CUA 小规模回归
- [ ] 完成 P5：并行与长期稳定性预验收
- [ ] 完成 P6：Case 扩展与 CUA 版本兼容策略

---

## 13. 下一阶段测试点

- [x] `TP-001` 本地 smoke 测试通过
- [x] `TP-002` 到 `TP-014` 真实 VM 工具功能测试通过
- [x] `TP-015` 到 `TP-019` 异常与清理测试通过
- [x] `TP-020` 到 `TP-022` 汇总报表测试通过
- [x] `TP-023` 到 `TP-024` 真实 CUA 回归测试通过
- [ ] `TP-025` 到 `TP-026` 稳定性测试通过
- [ ] `TP-027` 到 `TP-034` Case 扩展与 CUA 版本兼容测试通过
