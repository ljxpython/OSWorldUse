# CUA Blackbox Integration Docs

这个子目录专门记录 **方案 B**：

> 尽量不改 `CUA` 源码，把 `CUA` 当成黑盒二进制 / 黑盒运行时接入 OSWorld 评测。

## 当前状态

这是当前支持的实现路线，隶属于上级 `cua-osworld-adapter/` 主线文档体系。

当前实现入口：

- `osworld_cua_bridge/`
- `scripts/python/run_multienv_cua_blackbox.py`
- `scripts/python/build_cua_blackbox_summary.py`
- `scripts/python/run_cua_blackbox_regression.py`
- `scripts/python/validate_cua_regression_cases.py`
- `scripts/python/check_osworld_env_step.py`
- `lib_run_single.run_single_example_cua_blackbox()`

当前固定回归集合：

- `evaluation_examples/test_cua_regression.json`

当前批量评测会在结果根目录自动生成：

- `summary/summary.json`
- `summary/summary.csv`
- `summary/domain_summary.json`
- `summary/failure_summary.json`

当前 Mac 本地阶段验收范围：

- `num_envs=1`
- VMware 单 VM
- 并行稳定性 `TP-026` 暂缓，不阻塞当前阶段单环境评测

当前 CUA 参数默认值：

- `OSWORLD_CUA_BIN`、`OSWORLD_CUA_CONFIG_PATH`、`OSWORLD_CUA_REPO_ROOT` 等默认从仓库根目录 `.env` 读取
- CLI 参数优先级高于 `.env`
- `.env` 不提交到仓库，代码中不保留本机 CUA 路径硬编码

当前文档包括：

- [方案总设计与实施清单](./PLAN_B_CUA_BLACKBOX_OSWORLD_INTEGRATION_zh.md)
- [技术架构图](./TECHNICAL_ARCHITECTURE_zh.md)
- [单环境阶段验收结论](./SINGLE_ENV_ACCEPTANCE_CONCLUSION_zh.md)
- [Bridge 协议设计](./BRIDGE_PROTOCOL_zh.md)
- [实现任务清单](./IMPLEMENTATION_TODO_zh.md)
- [下一阶段整体规划与测试点](./NEXT_PHASE_PLAN_AND_TEST_POINTS_zh.md)
- [评测 Case 扩展与 CUA 版本兼容策略](./EVALUATION_CASE_AND_CUA_VERSION_STRATEGY_zh.md)
- [伪代码实现草案](./PSEUDOCODE_IMPLEMENTATION_zh.md)
- [验收标准](./ACCEPTANCE_CRITERIA_zh.md)
- [总体任务清单](./MASTER_CHECKLIST_zh.md)

和根目录下原有文档的关系：

- `../CUA_OSWORLD_ADAPTER_INTERFACE_DESIGN_zh.md`
  主要描述“OSWorld 主控、CUA 适配成 agent”的方案 A。
- `./PLAN_B_CUA_BLACKBOX_OSWORLD_INTEGRATION_zh.md`
  主要描述“CUA 主控、OSWorld 提供远程执行环境与评测”的方案 B。

阅读建议：

1. 如果目标是尽量少改 `CUA`，优先快速验证 benchmark 接入，先看方案 B。
2. 如果目标是继续开发和验收当前 blackbox 路线，按“下一阶段整体规划与测试点”推进。
3. 如果目标是新增评测 case 或升级 CUA 版本，按“评测 Case 扩展与 CUA 版本兼容策略”推进。
4. 如果目标是长期做标准 `mm_agents` 接入，再看方案 A。

如果本目录和上级 `cua-osworld-adapter/` 的描述出现冲突，以当前 blackbox 代码实现为准。
