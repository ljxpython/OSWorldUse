# CUA Blackbox 实现任务清单

日期：2026-05-01

## 1. 目标

把方案 B 拆成一个能按顺序执行的实现清单，避免一开始就写成大而全的通用框架。

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

- [ ] `CUA` 可本地编译
- [ ] `CUA` 可打二进制
- [ ] `CUA run --help` 正常
- [ ] `CUA run --nodeid` 路径可执行
- [ ] `CUA` 远程工具模式可在独立环境下工作

### 3.2 OSWorld 可用性

- [ ] `DesktopEnv.reset()` 正常
- [ ] `env._get_obs()` 可返回 screenshot
- [ ] `env.step("WAIT")` 正常
- [ ] `env.step(pyautogui code)` 正常
- [ ] `env.evaluate()` 正常

### 3.3 约束确认

- [ ] 第一阶段只做 Ubuntu
- [ ] 第一阶段只做 screenshot 驱动
- [ ] 第一阶段只做 GUI 动作，不碰 shell / office
- [ ] 第一阶段只做单进程 smoke test

---

## 4. Phase 1：Bridge MVP

### 4.1 建目录

- [ ] 新建 bridge 模块目录
- [ ] 新建协议定义文件
- [ ] 新建工具翻译文件
- [ ] 新建执行器文件

### 4.2 最小工具

- [ ] `screenshot`
- [ ] `mouse_click`
- [ ] `clipboard_type`
- [ ] `key_press`
- [ ] `hotkey`
- [ ] `wait`

### 4.3 最小验收

- [ ] `screenshot` 能返回当前屏幕
- [ ] `mouse_click` 能点击指定位置
- [ ] `clipboard_type` 能输入文本
- [ ] `hotkey` 能触发快捷键
- [ ] 错误能正确返回 JSON

### 4.4 调试产物

- [ ] 每次请求写日志
- [ ] 每次响应写日志
- [ ] 每次 screenshot 可追踪

---

## 5. Phase 2：Blackbox Runner MVP

### 5.1 Runner 骨架

- [ ] 新建 `run_multienv_cua_blackbox.py`
- [ ] 新增单任务执行函数
- [ ] 复用 OSWorld 的任务分发逻辑
- [ ] 复用 OSWorld 的结果目录组织方式

### 5.2 子进程控制

- [ ] 能启动 `cua` 二进制
- [ ] 能传入 `instruction`
- [ ] 能传入 `runId`
- [ ] 能传入 `target-screen`
- [ ] 能等待子进程退出
- [ ] 能收集 stdout / stderr

### 5.3 结果落盘

- [ ] 保存 `cua.stdout.log`
- [ ] 保存 `cua.stderr.log`
- [ ] 保存 `result.txt`
- [ ] 保存 `recording.mp4`
- [ ] 保存 OSWorld 侧 `runtime.log`

### 5.4 最小验收

- [ ] 一个任务能从 reset 跑到 evaluate
- [ ] `CUA` 不再操作宿主机
- [ ] OSWorld VM 上的 GUI 变化可见

---

## 6. Phase 3：稳定性补强

### 6.1 常见失败处理

- [ ] screenshot 超时
- [ ] click 未生效
- [ ] 文本输入错位
- [ ] 子进程中断
- [ ] runId 混乱
- [ ] 远程桥 busy

### 6.2 可观测性

- [ ] 统一请求 ID
- [ ] 统一 run ID
- [ ] 统一错误码
- [ ] 统一结果目录结构

### 6.3 清理逻辑

- [ ] 任务结束后清理临时文件
- [ ] 异常退出时清理子进程
- [ ] 断点恢复不破坏已有结果

---

## 7. Phase 4：批量评测

### 7.1 多任务

- [ ] 支持 `test_all.json`
- [ ] 支持单 domain
- [ ] 支持单 example id

### 7.2 多环境

- [ ] 允许多个任务串行跑
- [ ] 暂不并行
- [ ] 并行放到第二阶段再做

### 7.3 统计

- [ ] 输出总分
- [ ] 输出 domain 分数
- [ ] 输出失败分类

---

## 8. Phase 5：后续可选项

以下内容不在第一阶段：

- [ ] `app_open`
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
