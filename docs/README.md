# Docs Index

这个目录目前分成 4 类内容：

- `code-reading/`
  面向 OSWorld 仓库源码阅读、运行链路、Agent 接入和实践文档。
- `research/`
  面向 CUA、Benchmark、成本核算、环境验证和方案设计的研究笔记。
- `cua-osworld-adapter/`
  这是 CUA 接入 OSWorld 的主线文档目录。当前支持的实现路线已经收敛到 blackbox bridge。
- `cua-blackbox/`
  这是 blackbox bridge 的实现补充文档，后续应逐步并入 `cua-osworld-adapter/` 主线目录。

## 当前主线

当前支持的实现和评测路线是 blackbox bridge。

对应代码入口：

- `osworld_cua_bridge/`
- `scripts/python/run_multienv_cua_blackbox.py`
- `lib_run_single.run_single_example_cua_blackbox()`

已废弃且不再维护的历史路径：

- `mm_agents/cua/`
- `scripts/python/run_multienv_cua.py`

这些历史代码只保留参考，不作为 fallback。

## Code Reading

- [代码解读总索引](./code-reading/README_zh.md)

## Research

- [研究文档索引](./research/README.md)

## CUA OSWorld Adapter

- [CUA OSWorld Adapter 目录索引（主线目录）](./cua-osworld-adapter/README.md)
- [CUA Adapter 伪代码](./cua-osworld-adapter/CUA_ADAPTER_PSEUDOCODE_zh.md)
- [CUA 与 OSWorld 适配接口设计](./cua-osworld-adapter/CUA_OSWORLD_ADAPTER_INTERFACE_DESIGN_zh.md)
- [CUA 版本兼容与评测策略](./cua-osworld-adapter/CUA_EVAL_VERSIONING_POLICY_zh.md)
- [CUA 冻结字段表](./cua-osworld-adapter/CUA_FROZEN_FIELDS_zh.md)
- [CUA Smoke Test 用例表](./cua-osworld-adapter/CUA_SMOKE_TEST_MATRIX_zh.md)
- [CUA 方案 A 实现路线图](./cua-osworld-adapter/IMPLEMENTATION_ROADMAP_zh.md)
- [CUA 方案 A 实现任务拆分](./cua-osworld-adapter/IMPLEMENTATION_TASKS_zh.md)

## CUA Blackbox

- [blackbox bridge 实现补充文档](./cua-blackbox/README.md)
