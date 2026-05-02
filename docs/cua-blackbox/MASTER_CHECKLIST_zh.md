# CUA Blackbox 总体任务清单

日期：2026-05-01

> 这是后续逐项打勾的总清单。  
> 完成一项就勾一项，直到全部结束。

---

## 1. 文档与边界

- [ ] 确认方案 B 是当前主推进路径
- [ ] 确认第一阶段只做 Ubuntu
- [ ] 确认第一阶段只做 screenshot + GUI
- [ ] 确认第一阶段不做 shell / office / records / brain
- [ ] 确认验收标准已冻结

---

## 2. CUA 可用性确认

- [ ] `CUA` 二进制能构建
- [ ] `CUA run` 能执行
- [ ] `CUA run --nodeid` 能执行
- [ ] `CUA` 可以用指定模型启动
- [ ] `CUA` 可以返回截图

---

## 3. OSWorld 环境确认

- [ ] `DesktopEnv` 可正常启动
- [ ] `env.reset()` 可用
- [ ] `env._get_obs()` 可拿到 screenshot
- [ ] `env.step()` 可执行 GUI 动作
- [ ] `env.evaluate()` 可运行

---

## 4. Bridge 协议

- [ ] 确认请求字段
- [ ] 确认响应字段
- [ ] 确认错误码
- [ ] 确认 runId / reqId 规范
- [ ] 确认支持 screenshot
- [ ] 确认支持 mouse_click
- [ ] 确认支持 clipboard_type
- [ ] 确认支持 hotkey
- [ ] 确认支持 wait

---

## 5. Bridge 实现

- [ ] 建立 bridge 目录
- [ ] 建立协议定义
- [ ] 建立工具翻译层
- [ ] 建立执行层
- [ ] 建立日志输出
- [ ] 建立错误返回

---

## 6. Runner 实现

- [ ] 建立 blackbox runner 脚本
- [ ] 建立单任务执行函数
- [ ] 建立子进程启动逻辑
- [ ] 建立子进程等待逻辑
- [ ] 建立结果收集逻辑
- [ ] 建立录屏收尾逻辑

---

## 7. 结果与日志

- [ ] 保存 `result.txt`
- [ ] 保存 `runtime.log`
- [ ] 保存 `recording.mp4`
- [ ] 保存 `cua.stdout.log`
- [ ] 保存 `cua.stderr.log`
- [ ] 保存 `cua_meta.json`

---

## 8. Smoke Test

- [ ] 单任务跑通
- [ ] 单环境跑通
- [ ] CUA 动作落到 VM
- [ ] 结果可写回
- [ ] 任务可结束

---

## 9. 功能测试

- [ ] click 正常
- [ ] double click 正常
- [ ] right click 正常
- [ ] drag 正常
- [ ] scroll 正常
- [ ] text input 正常
- [ ] hotkey 正常

---

## 10. 稳定性

- [ ] 连续任务不崩
- [ ] 异常可恢复
- [ ] 子进程可清理
- [ ] 日志可追踪
- [ ] 失败原因可定位

---

## 11. 验收

- [ ] 完成 smoke test 验收
- [ ] 完成功能测试验收
- [ ] 完成稳定性验收
- [ ] 形成验收结论
- [ ] 决定是否进入下一阶段

