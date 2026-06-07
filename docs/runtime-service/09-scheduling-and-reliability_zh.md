# 资源调度与可靠性

更新时间：2026-06-07

## 先定结论

- 第一版由 XUA 平台做宏观排队，OSWorld Runtime Manager 做执行面准入和资源锁。
- Runtime Manager 不做长队列，拿不到资源就返回 `capacity_exceeded`，让平台稍后重试或继续排队。
- 调度粒度是一次 `runtime_task`，不是单个 case。
- `resource_profile_id` 是资源池边界，同一个 `resource_profile_id` 同一时刻只能采用一种拓扑。
- `resource_leases` 负责资源互斥，`runtime_run_bindings` 负责路由粘性，两个表不能互相替代。
- 任务一旦进入 `bound/running`，默认不自动换节点重试；需要重跑时创建新的 attempt。

## 调度边界

### XUA 平台负责

- 创建 `EvaluationRun`。
- 控制全局队列和并发。
- 根据 `resource_profile_id` 判断是否继续等待或提交。
- 按 `idempotency_key` 幂等提交。
- 根据 Runtime 返回的 `capacity_exceeded`、`runtime_lost`、`timeout` 收敛平台状态。

### Runtime Manager 负责

- 校验 `runtime_type`、`runtime_mode`、`resource_profile_id`。
- 读取节点健康和容量快照。
- 选择执行实例。
- 创建 `resource_leases`。
- 创建 `runtime_run_bindings`。
- 启动 OSWorld runner 进程。
- 处理心跳、超时、取消和产物归档。

### 执行节点负责

- 上报心跳和容量。
- 执行 blackbox 或 vm_native runner。
- 接收同一 run 的 `status / cancel / artifacts`。
- 上传 manifest 和 artifacts 到对象存储。

## 准入流程

Runtime Manager 收到 `start` 后按下面顺序处理：

1. 用 `idempotency_key` 查重。
2. 校验 `runtime_type=osworld`。
3. 校验 `runtime_mode` 是否支持 `blackbox / vm_native`。
4. 校验 `resource_profile_id` 是否启用。
5. 读取健康实例，只允许 `healthy` 节点接新单。
6. 计算资源池剩余容量。
7. 在事务内创建或确认 `runtime_tasks`。
8. 在事务内抢占 `resource_leases`。
9. 在事务内写入 `runtime_run_bindings`。
10. 事务提交后启动 runner。
11. runner 接受后回填 `runtime_run_id` 和状态。

如果第 6 步没有容量，直接返回 `capacity_exceeded`，不要把任务塞进 Runtime Manager 长队列里装作接单成功。

## 容量计算

容量判断只看 DB 真相源和最新心跳快照：

- `runtime_instances.status=healthy`
- `runtime_instances.last_heartbeat_at` 未超过 TTL
- `resource_profiles.max_concurrency`
- active `resource_leases` 数量
- 执行节点上报的 `last_capacity_payload`

推荐最小公式：

```text
available_slots = min(
  resource_profile.max_concurrency - active_leases,
  sum(healthy_instance.available_slots)
)
```

如果节点 capacity payload 缺失，第一版按 `available_slots=0` 处理，别猜。

## 节点选择策略

第一版用朴素策略，别tm一上来搞复杂调度：

1. 过滤 `healthy` 节点。
2. 过滤 `resource_profile_id` 不匹配的节点。
3. 过滤版本或 label 不匹配的节点。
4. 优先选择 `available_slots` 最大的节点。
5. 并列时选择最近接单时间更早的节点。

`degraded` 节点默认不接新单，只保留查询、取消、产物拉取能力。

## 写入顺序和事务边界

准入成功时，核心写入必须在一个事务里完成：

```text
begin
  lock resource_profile 或 advisory lock(resource_profile_id)
  check active leases
  insert/update runtime_tasks
  insert resource_leases
  insert runtime_run_bindings
commit
```

事务提交后再启动 runner。原因很简单：进程启动可能慢、可能挂，不能把数据库锁拿着等 subprocess。

如果事务提交后 runner 启动失败：

- `runtime_tasks.status=failed`
- `runtime_tasks.status_reason=start_failed`
- `runtime_run_bindings.binding_status=released` 或 `lost`
- `resource_leases.lease_status=released`

如果 runner 已经接受但 `runtime_run_id` 回填失败：

- 用 `idempotency_key` 向同一实例查询。
- 查得到就回填。
- 查不到就收敛为 `failed`，不要创建第二个运行。

## 幂等规则

`idempotency_key` 是提交幂等边界。

- 同一个 `runtime_type + idempotency_key` 只能对应一个 `runtime_task`。
- 已经创建 `runtime_run_id` 时，重复提交必须返回同一个 `runtime_run_id`。
- 已经绑定实例时，重复提交必须返回同一个 `runtime_instance_id`。
- 重复提交不能再次抢 lease。
- 如果原任务已终态，重复提交返回终态结果，不重新执行。

重跑必须创建新的 attempt 和新的 `idempotency_key`，不能拿旧任务硬改。

## 取消可靠性

取消流程只认绑定：

1. 查 `runtime_run_bindings`。
2. 如果 `binding_status=bound/releasing`，按 `base_url_snapshot` 调同一节点。
3. 如果节点可达，Runtime Manager 把任务推进 `canceling`。
4. 如果节点不可达，任务进入 `failed`，原因是 `runtime_lost` 或 `cancel_unreachable`。
5. 释放或回收 `resource_leases`。

取消不能走随机负载均衡，也不能换节点补 cancel。

## 超时规则

建议拆三类超时：

| 超时 | 触发阶段 | 收敛原因 |
| --- | --- | --- |
| `start_timeout` | runner 长时间未接受 | `start_timeout` |
| `run_timeout` | 执行超过任务期限 | `timeout` |
| `cancel_timeout` | cancel 后超过 grace | `cancel_timeout` |

`run_timeout` 可以先向绑定节点发 cancel；超过 grace 后仍未终态，就收敛到 `failed`，同时释放或回收 lease。

## 重试规则

允许重试的场景：

- Runtime Manager 还没接受任务，HTTP 请求失败。
- `capacity_exceeded`，平台继续排队后重新提交。
- `validate` 失败修正参数后重新提交。

不自动重试的场景：

- 已经创建 `runtime_run_id`。
- 已经写入 `runtime_run_bindings.bound`。
- 已经启动 OSWorld runner。
- 节点执行中失联。
- artifact 上传失败但本地状态不可确认。

这些场景要么收敛失败，要么由平台创建新的 attempt。别在同一个任务上偷偷换节点重跑，乖乖，那个 bug 能把后面统计全干碎。

## 后台收敛任务

Runtime Manager 至少需要这些后台任务：

### 心跳扫描

- 扫描 `runtime_instances.last_heartbeat_at`。
- 超过 TTL 后标记 `unreachable`。
- 对绑定到失联节点的运行做故障收敛。

### 租约扫描

- 扫描 `resource_leases.lease_expires_at`。
- 超时后进入 `expired`。
- 回收完成后进入 `reclaimed`。

### 任务扫描

- 扫描长时间卡在 `submitted / accepted / running / canceling` 的任务。
- 根据超时类型推进到 `failed` 或 `canceled`。

### 产物扫描

- 扫描已完成但缺失 manifest 的任务。
- manifest 不可读时标记 `artifact_missing` 或 `upload_error`。

## 故障代码口径

建议第一版至少统一这些 `status_reason` / `error_code`：

- `capacity_exceeded`
- `validation_error`
- `start_failed`
- `start_timeout`
- `runtime_lost`
- `timeout`
- `cancel_unreachable`
- `cancel_timeout`
- `upload_error`
- `artifact_missing`
- `internal_error`

错误信息可以详细，但错误码必须稳定，否则平台侧统计就是一坨稀泥。

## 关键不变量

- active `resource_leases` 对同一个 `resource_profile_id + resource_ref` 只能有一条。
- 一个 `runtime_task_id` 只能有一个 `runtime_run_bindings`。
- 一个非空 `runtime_run_id` 只能绑定一个 `runtime_instance_id`。
- `bound` 后不漂移。
- `completed` 必须有可读 manifest。
- `failed/canceled/completed` 都是终态，不允许再回到 running。

## 结论

第一版不要把调度做成大而全的资源系统。够用的做法是：

1. 平台控制大队列。
2. Runtime Manager 做准入和资源锁。
3. DB 做真相源。
4. 失败按状态机收敛。
5. 重跑用新 attempt，别在旧任务上鬼鬼祟祟漂移。
