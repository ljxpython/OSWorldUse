# CUA 方案 A 实现路线图

日期：2026-05-01

> 状态说明：这份文档描述的是历史 `mm_agents/cua` adapter 路线。
> 该路线已经废弃，不再维护，也不作为 fallback。当前支持的实现路线是 `osworld_cua_bridge/` blackbox bridge。

## 1. 目标

这份路线图把方案 A 变成可执行顺序：

> `OSWorld` 主控，`CUA` 作为可替换 adapter 接入，并且未来 `CUA` 升级时尽量不改评测主链路。

---

## 2. 总体顺序

建议按下面顺序做：

1. 冻结评测面
2. 冻结协议面
3. 做最小 adapter
4. 做专用 runner
5. 做 smoke test
6. 做版本化结果落盘
7. 再考虑后续扩展

---

## 3. Phase 0：边界冻结

### 3.1 要完成的事

- 确认 `eval_profile` 名称
- 确认 `adapter_version` 初始值
- 确认 `bridge_protocol_version`
- 确认 `cua_version` 的记录方式
- 确认结果目录结构
- 确认 hard gate smoke test

### 3.2 产物

- `[CUA_FROZEN_FIELDS_zh.md](./CUA_FROZEN_FIELDS_zh.md)`
- `[CUA_SMOKE_TEST_MATRIX_zh.md](./CUA_SMOKE_TEST_MATRIX_zh.md)`
- `[CUA_EVAL_VERSIONING_POLICY_zh.md](./CUA_EVAL_VERSIONING_POLICY_zh.md)`

---

## 4. Phase 1：最小 adapter

### 4.1 目标

做一个最小可运行的 `CUAAdapterAgent`，只覆盖第一阶段协议：

- 输入：`instruction + screenshot`
- 输出：`response + actions + debug`
- 动作：`WAIT / DONE / FAIL / pyautogui`

### 4.2 需要新增的文件

- `mm_agents/cua/__init__.py`
- `mm_agents/cua/agent.py`
- `mm_agents/cua/translator.py`
- `mm_agents/cua/types.py`
- `mm_agents/cua/prompts.py`（可选）

### 4.3 关键要求

- 不把 `env` 塞进 agent
- 不让 agent 直接调用 `env.step()`
- 不复用 `OpenAICUAAgent` 的 special-case loop
- 只保留能被 OSWorld 直接消费的输出

---

## 5. Phase 2：专用 runner

### 5.1 目标

做一个专门用于方案 A 的 runner，复用 OSWorld 的标准评测主干，但接入自己的 adapter。

### 5.2 需要新增的文件

- `scripts/python/run_multienv_cua.py`
- `lib_run_single.py` 里的 `run_single_example_cua()`

### 5.3 关键要求

- 复用 `DesktopEnv`
- 复用 `env.evaluate()`
- 复用结果目录约定
- 复用录屏和轨迹落盘方式
- 不改 task JSON
- 不改 evaluator

---

## 6. Phase 3：版本化日志与元数据

### 6.1 目标

让未来 `CUA` 升级后，结果仍然可比较、可复现。

### 6.2 要写入的字段

- `osworld_version`
- `cua_version`
- `adapter_version`
- `bridge_protocol_version`
- `eval_profile`

### 6.3 建议额外字段

- `prompt_version`
- `task_set`
- `screen_size`
- `run_id`
- `adapter_config_hash`

---

## 7. Phase 4：Smoke test

### 7.1 目标

每次 `CUA` / adapter 升级前，先证明链路没坏。

### 7.2 必跑项

- 启动检查
- 协议健康检查
- screenshot 回路
- mouse click
- text input
- hotkey
- 终止语义
- 错误输入
- 单任务闭环

### 7.3 参考文档

- `[CUA_SMOKE_TEST_MATRIX_zh.md](./CUA_SMOKE_TEST_MATRIX_zh.md)`

---

## 8. Phase 5：回归与比较

### 8.1 目标

让后续版本的 CUA 升级能和旧版本做公平比较。

### 8.2 规则

- 同一 `adapter_version` 内比较不同 `cua_version`
- 同一 `cua_version` 内比较不同 `adapter_version`
- 不同 `eval_profile` 不直接比较

---

## 9. Phase 6：后续扩展

这部分不进第一阶段：

- 多观测类型
- 多动作空间
- 多平台
- 复杂历史管理
- `shell_exec`
- `officecli`
- `wait_for_user`
- `records`
- `brain`

这些能力只在协议允许且 smoke test 通过后再加。

---

## 10. 任务拆分建议

建议后续代码任务按下面顺序拆：

1. `mm_agents/cua` 基础文件
2. `run_multienv_cua.py`
3. `run_single_example_cua()`
4. 版本元数据落盘
5. smoke test
6. 结果目录对齐

---

## 11. 最终完成标准

当以下条件成立时，方案 A 第一阶段可以认为完成：

- `CUAAdapterAgent` 可运行
- `run_multienv_cua.py` 可跑
- `env.evaluate()` 可工作
- 结果可落盘
- smoke test 全部 hard gate 通过
- 未来 `CUA` 升级时，能通过版本化结果继续评测
