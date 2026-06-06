# OSWorld Runtime Service 方案讨论

这个目录用于讨论 OSWorld 作为内部 Runtime Service 时的执行侧设计、部署规划和多服务器一致性问题。

当前前提很明确：

- 只面向内部平台，不做多租户。
- 不讨论公网网关和鉴权。
- OSWorld 只负责执行面，不承担平台控制面。
- blackbox 和 vm_native 都算执行模式，但都必须有统一的 run 绑定和 artifact 归档口径。

## 文档

- [01 背景、目标和边界](./01-overview_zh.md)
- [02 多服务器部署与一致性](./02-multi-server_zh.md)
- [03 规划、里程碑和待确认问题](./03-roadmap_zh.md)
- [04 路由与地址约定](./04-routing-and-addressing_zh.md)
- [05 状态存储与租约](./05-state-store-and-lease_zh.md)
- [06 接口契约与最小时序](./06-runtime-api-contract-and-sequence_zh.md)

## 当前结论

1. 单机本地目录式跑法只能用于开发验证，不适合作为多服务器服务的最终形态。
2. 多服务器部署时，run 不能靠随机负载均衡去“碰运气”。
3. `runtime_run_id -> instance` 必须有明确绑定，status / cancel / artifacts 要按绑定路由。
4. 结果、录屏、summary、manifest 最终要落到共享存储，不能只留在本机临时目录。
