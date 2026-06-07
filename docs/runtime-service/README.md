# OSWorld Runtime Service 方案讨论

这个目录用于讨论 OSWorld 作为内部 Runtime Service 时的执行侧设计、部署规划和多服务器一致性问题。

当前前提很明确：

- 只面向内部平台，不做多租户。
- 不讨论公网网关和鉴权。
- OSWorld 只负责执行面，不承担平台控制面。
- blackbox 和 vm_native 都算执行模式，但都必须有统一的 run 绑定和 artifact 归档口径。

## 文档怎么读

如果你要找“接口、功能、如何使用、传参、响应”，先看这张表。

| 你要找什么 | 先看哪份文档 | 说明 |
| --- | --- | --- |
| Runtime 对外接口主契约 | [06 接口契约与最小时序](./06-runtime-api-contract-and-sequence_zh.md) | validate / start / status / cancel / artifacts 的主文档 |
| 状态存储与字段口径 | [05 状态存储与租约](./05-state-store-and-lease_zh.md) | runtime_instance / task / binding / lease 字段 |
| 状态机与故障收敛 | [07 状态机与故障收敛](./07-state-machine-and-failure-convergence_zh.md) | 终态、漂移、失联、取消收口 |
| DDL 草案 | [08 DDL 草案](./08-ddl-draft_zh.md) | PostgreSQL 落表、约束、索引 |
| 调度与可靠性 | [09 资源调度与可靠性](./09-scheduling-and-reliability_zh.md) | 并发、背压、重试、取消语义 |
| 产物与归档 | [10 Artifact Manifest 与结果归档](./10-artifact-manifest-and-result-archive_zh.md) | manifest、TOS、访问方式 |

## 文档

- [01 背景、目标和边界](./01-overview_zh.md)
- [02 多服务器部署与一致性](./02-multi-server_zh.md)
- [03 规划、里程碑和待确认问题](./03-roadmap_zh.md)
- [04 路由与地址约定](./04-routing-and-addressing_zh.md)
- [05 状态存储与租约](./05-state-store-and-lease_zh.md)
- [06 接口契约与最小时序](./06-runtime-api-contract-and-sequence_zh.md)
- [07 状态机与故障收敛](./07-state-machine-and-failure-convergence_zh.md)
- [08 DDL 草案](./08-ddl-draft_zh.md)
- [09 资源调度与可靠性](./09-scheduling-and-reliability_zh.md)
- [10 Artifact Manifest 与结果归档](./10-artifact-manifest-and-result-archive_zh.md)

## 当前主线

1. `06` 是当前对外接口、参数、响应、时序的主契约。
2. `05 / 07 / 08 / 09 / 10` 分别负责字段、状态机、DDL、调度、产物。
3. `01 / 02 / 03 / 04` 更多是背景、路由、规划和讨论材料。

## 当前结论

1. 单机本地目录式跑法只能用于开发验证，不适合作为多服务器服务的最终形态。
2. 多服务器部署时，run 不能靠随机负载均衡去“碰运气”。
3. `runtime_run_id -> instance` 必须有明确绑定，status / cancel / artifacts 要按绑定路由。
4. 结果、录屏、summary、manifest 最终要落到共享存储，不能只留在本机临时目录。
5. Runtime Manager 负责执行面状态收敛，平台负责业务态收敛，别把两层状态机搅在一起。
6. 落表可以直接按 DDL 草案推进，不要再靠口头约定猜字段。
7. 第一版平台做宏观排队，Runtime Manager 做准入和资源锁；已绑定任务不自动换节点重试。
8. OSWorld 本地结果目录是私有实现，标准 artifact manifest 才是对外契约。
9. 默认兼容 OSWorld 既有执行路径和功能，不做无关重构；只有为 runtime 接口、资源调度或必要的执行参数透传时，才允许做增量改动。
