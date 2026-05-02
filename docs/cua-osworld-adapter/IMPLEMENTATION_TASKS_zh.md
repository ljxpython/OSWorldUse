# CUA 方案 A 实现任务拆分

日期：2026-05-01

> 状态说明：这份文档描述的是历史 `mm_agents/cua` adapter 路线。
> 该路线已经废弃，不再维护，也不作为 fallback。当前支持的实现路线是 `osworld_cua_bridge/` blackbox bridge。

## 1. 目标

这份文档把路线图拆成可执行任务。

目标不是先写代码，而是先把：

- 文件边界
- 任务顺序
- 依赖关系
- 完成标准

定死。

---

## 2. 任务总原则

1. `OSWorld` 侧只改适配层，不改 benchmark 核心逻辑。
2. `CUA` 侧只保留最小稳定面，不把 OSWorld 逻辑塞回去。
3. 先做单步闭环，再做批量评测。
4. 先冻结协议，再写实现。
5. 每次升级都要能通过 smoke test。

---

## 3. 任务总表

| 阶段 | 任务 | 主要文件 | 依赖 | 完成标准 |
|---|---|---|---|---|
| T0 | 冻结评测面 | `docs/cua-osworld-adapter/*` | 无 | `eval_profile`、版本字段、结果目录都已定义。 |
| T1 | 建 `mm_agents/cua` 包骨架 | `mm_agents/cua/__init__.py` | T0 | 包结构存在，可被 import。 |
| T2 | 定义数据类型 | `mm_agents/cua/types.py` | T1 | 动作、调试信息、状态结构明确。 |
| T3 | 定义动作翻译器 | `mm_agents/cua/translator.py` | T2 | 结构化动作能稳定翻成 OSWorld 动作。 |
| T4 | 定义 adapter agent | `mm_agents/cua/agent.py` | T2, T3 | `reset()`、`predict()`、history 管理可用。 |
| T5 | 新增专用 runner | `scripts/python/run_multienv_cua.py` | T4 | 能创建环境、实例化 agent、驱动 task。 |
| T6 | 新增单任务执行函数 | `lib_run_single.py` | T4, T5 | 能跑一条完整 episode，落盘轨迹和分数。 |
| T7 | 写版本元数据 | runner / helper | T5, T6 | 结果目录里能看到 `cua_version` 等字段。 |
| T8 | 跑 smoke test | `docs/cua-osworld-adapter/CUA_SMOKE_TEST_MATRIX_zh.md` | T5, T6, T7 | hard gate 用例全部通过。 |
| T9 | 做回归比较 | results / docs | T8 | 旧版本结果不被覆盖，可横向比较。 |

---

## 4. T1: 包骨架

### 要做什么

- 新增 `mm_agents/cua/`
- 新增 `__init__.py`
- 预留后续模块导出位置

### 不做什么

- 不实现模型调用
- 不实现 runner
- 不改 `DesktopEnv`

### 完成标准

- `import mm_agents.cua` 正常
- 子模块可逐步补齐

---

## 5. T2: 数据类型

### 要做什么

在 `mm_agents/cua/types.py` 里定义最小类型：

- `CUAAction`
- `CUAPredictInfo`
- `CUARuntimeState`

### 建议字段

- `CUAAction.kind`
- `CUAAction.args`
- `CUAAction.raw_text`
- `CUAAction.natural_language`
- `CUAPredictInfo.raw_response`
- `CUAPredictInfo.parsed_action`
- `CUAPredictInfo.debug`

### 完成标准

- 结构足够表达第一阶段动作
- 不依赖 OSWorld 特例对象
- 不强耦合具体模型 SDK

---

## 6. T3: 动作翻译器

### 要做什么

在 `mm_agents/cua/translator.py` 里实现：

- 动作校验
- 动作归一化
- `CUAAction -> OSWorld action` 翻译

### 第一阶段支持

- `click`
- `double_click`
- `move`
- `drag`
- `scroll`
- `type`
- `hotkey`
- `wait`
- `done`
- `fail`

### 关键约束

- 翻译结果只能是 `WAIT / DONE / FAIL / pyautogui`
- 文本必须安全转义
- 坐标缺失要返回可读错误

### 完成标准

- 输入同一动作，输出稳定一致
- 非法动作不会静默失败
- 所有错误都能被上层记录

---

## 7. T4: Adapter Agent

### 要做什么

在 `mm_agents/cua/agent.py` 里实现：

- `reset()`
- `predict()`
- 历史管理
- 调用模型
- 调用 translator

### 关键接口

```python
reset(_logger=None, **kwargs)
predict(instruction: str, obs: dict, **kwargs)
```

### 行为约束

- 不直接调用 `env.step()`
- 不把 `env` 存进 agent 核心状态
- 不依赖宿主机工具
- 只消费 OSWorld 提供的 `obs["screenshot"]`

### 完成标准

- 能被标准 runner 调用
- 能返回 `response, actions, info`
- 能记录 debug 信息

---

## 8. T5: 专用 Runner

### 要做什么

新增 `scripts/python/run_multienv_cua.py`，复用 OSWorld 现有多环境入口风格。

### 主要职责

- 解析参数
- 创建 `DesktopEnv`
- 创建 `CUAAdapterAgent`
- 调用专用单任务执行函数

### 完成标准

- 能从命令行启动
- 能跑单个 domain
- 能输出结果目录

---

## 9. T6: 单任务执行函数

### 要做什么

在 `lib_run_single.py` 中新增 `run_single_example_cua()`。

### 设计原则

- 尽量贴近 `run_single_example_opencua()` 的组织方式
- 但不要继承 `agent.step()` 那条 special-case 路径
- 由 OSWorld 统一负责 `env.step()`

### 完成标准

- 一条 episode 可完整走通
- `traj.jsonl` 能落盘
- `result.txt` 能落盘
- `recording.mp4` 能落盘

---

## 10. T7: 版本元数据

### 要做什么

把下面字段写进结果目录：

- `osworld_version`
- `cua_version`
- `adapter_version`
- `bridge_protocol_version`
- `eval_profile`

### 建议落点

- `args.json`
- `run_meta.json`
- `traj.jsonl` 首条记录

### 完成标准

- 每次跑分都能追到版本
- 新旧结果不会混淆
- 后续比较时不需要猜配置

---

## 11. T8: Smoke Test

### 要做什么

按 `CUA_SMOKE_TEST_MATRIX_zh.md` 跑 hard gate。

### 必跑项

- 启动检查
- 协议健康检查
- screenshot 回路
- mouse click
- text input
- hotkey
- 终止语义
- 错误输入
- 单任务闭环

### 完成标准

- hard gate 全过
- soft gate 结果有记录
- 失败能明确归类

---

## 12. T9: 回归比较

### 要做什么

对新旧版本结果做比较，但只在同一版本族内比。

### 比较规则

- 同一 `adapter_version` 比 `cua_version`
- 同一 `cua_version` 比 `adapter_version`
- 不同 `eval_profile` 不直接比

### 完成标准

- 旧结果保留
- 新结果单独落盘
- 分数变化可解释

---

## 13. 明确不碰的文件

第一阶段建议不要动这些：

- `evaluation_examples/*`
- `desktop_env/desktop_env.py`
- `desktop_env/evaluators/*`
- `task json` 结构

如果后面真要动，也必须先升级版本，再跑 smoke test。

---

## 14. 推荐执行顺序

1. 先做 `T1-T4`
2. 再做 `T5-T6`
3. 然后做 `T7`
4. 再跑 `T8`
5. 最后做 `T9`

这条顺序的目的只有一个：

> 先把单步协议跑通，再考虑批量评测和版本比较。
