# CUA OSWorld Adapter Docs

日期：2026-05-01

## 状态

这是 CUA 接入 OSWorld 的主线文档目录。

当前已经收敛并落地验证的实现路线是 blackbox bridge：

- `../cua-blackbox/`
- `osworld_cua_bridge/`
- `scripts/python/run_multienv_cua_blackbox.py`

已经废弃且不再维护的历史路径：

- `mm_agents/cua/`
- `scripts/python/run_multienv_cua.py`

这些历史代码只保留参考，不作为 fallback。

这个目录继续保留两类信息：

- CUA 接入 OSWorld 的总设计、版本策略、边界约束
- 历史 adapter 方案的设计记录，供后续查阅

## 当前文档

- [CUA 接入 OSWorld 详细接口设计](./CUA_OSWORLD_ADAPTER_INTERFACE_DESIGN_zh.md)
- [CUAAdapterAgent 伪代码与接口草案](./CUA_ADAPTER_PSEUDOCODE_zh.md)
- [CUA 版本兼容与评测策略](./CUA_EVAL_VERSIONING_POLICY_zh.md)
- [CUA 冻结字段表](./CUA_FROZEN_FIELDS_zh.md)
- [CUA Smoke Test 用例表](./CUA_SMOKE_TEST_MATRIX_zh.md)
- [CUA 方案 A 实现路线图](./IMPLEMENTATION_ROADMAP_zh.md)
- [CUA 方案 A 实现任务拆分](./IMPLEMENTATION_TASKS_zh.md)

## 本地校验命令

```bash
python3 scripts/python/cua_smoke_test.py --result_dir ./results_cua_smoke
```

这个校验命令现在对应当前 blackbox bridge 主线，不再依赖 `mm_agents/cua`。

## 约定

- 冻结字段表定义评测边界内哪些配置不能随意变。
- Smoke test 用例表定义每次 `CUA` 或 adapter 升级前必须跑的最小检查。
- 后续的计划清单、自测点、实现任务也放在这个目录里。

如果这里的总设计描述和 `../cua-blackbox/` 的实现细节有冲突，以当前 blackbox 代码实现为准。
