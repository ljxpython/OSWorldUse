# 规划、里程碑和待确认问题

## 规划

### 阶段 1：单节点 PoC

- 跑通 `blackbox`。
- 跑通 `vm_native`。
- 统一 `result_dir`、summary、artifact manifest。
- 先把 `validate / start / status / cancel / artifacts` 这套语义钉住。

### 阶段 2：多节点接入

- 引入节点登记和 capacity。
- 引入 run 绑定。
- 引入共享 artifact 存储。
- 引入 lease 和 heartbeat。
- 明确 Manager 入口和执行节点地址模型，优先支持 `ip:port`，域名作为可选别名。
- 落地 DB 真相源的状态存储和租约表。
- 把 `validate / start / status / cancel / artifacts` 的请求响应和最小时序钉死。
- 把 Runtime Manager 的状态机和故障收敛边界钉死。

### 阶段 3：故障恢复和扩容

- 节点异常时可以判定 run 状态。
- 孤儿 lease 可以回收。
- 产物可以从对象存储恢复。
- 执行节点可以横向增加，而不改控制面契约。

## 验收口径

- 一次 run 只能对应一个执行节点。
- `cancel` 不会打到错误节点。
- run 结束后能找到完整 summary、录屏和日志。
- 多节点部署后不会出现重复 lease。
- 同一份输入在不同节点上行为一致。

## 已确认结论

- lease 的真相源是 DB，Redis 只做可选加速层。
- 执行节点第一版可以直接用 `ip:port`，节点级域名只是地址别名。
- blackbox 和 vm_native 统一进同一个 Runtime Service，用 `runtime_mode` 区分执行路径。
- 节点异常后，由 Runtime Manager 收敛 `runtime_tasks`、`runtime_run_bindings` 和 `resource_leases`，平台侧再收敛 `EvaluationRun`。
- artifact 默认上传共享对象存储，平台只 ingest manifest，不扫本机目录。

## 待确认问题

1. 多节点是共享一批 ECS，还是每个节点自己维护独立池。
