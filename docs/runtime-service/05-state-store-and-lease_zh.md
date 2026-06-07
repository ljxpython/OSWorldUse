# 状态存储与租约

## 先定结论

多服务器场景下，**DB 是真相源，Redis 只是可选加速层**。

别反过来。Redis 可以快，但它不适合承载唯一真相。租约、绑定、节点注册这些东西要能审计、能恢复、能追踪，DB 更稳。

补一句口径：

- 本地开发和测试可以用 SQLite，尤其是临时调试、单元测试和最小化验证。
- 正式服务和长期部署必须用 PostgreSQL。
- 这份文档里的主方案、约束和租约设计都按 PostgreSQL 主线写，不把 SQLite 当正式服务方案。

## 四类状态

### 1. 节点注册

记录执行节点当前状态。

关键字段：

- `runtime_instance_id`
- `runtime_profile_id`
- `runtime_type`
- `base_url`
- `health_url`
- `resource_profile_id`
- `labels`
- `status`
- `status_reason`
- `last_heartbeat_at`
- `heartbeat_ttl_seconds`
- `last_capacity_payload`
- `bootstrap_snapshot`
- `last_capacity_at`

这层回答的是“这台节点现在活着吗、地址是什么、还能接多少活”。

### 2. 任务影子记录

记录平台提交给 Runtime 的一次任务。

关键字段：

- `run_id`
- `runtime_profile_id`
- `runtime_type`
- `runtime_mode`
- `runtime_endpoint`
- `runtime_instance_id`
- `resource_profile_id`
- `runtime_run_id`
- `status`
- `status_reason`
- `attempt`
- `idempotency_key`
- `request_payload`
- `response_payload`
- `last_status_payload`
- `bootstrap_snapshot`
- `error_code`
- `error_message`
- `last_polled_at`
- `cancel_requested_at`

这层回答的是“平台这次调用 Runtime 的全过程到底走到了哪一步”。

### 3. 资源租约

记录某个 ECS / VM / runtime 资源当前被谁占着。

关键字段：

- `runtime_type`
- `runtime_profile_id`
- `resource_profile_id`
- `resource_ref`
- `runtime_task_id`
- `lease_owner`
- `runtime_run_id`
- `runtime_instance_id`
- `lease_status`
- `lease_reason`
- `bootstrap_snapshot`
- `lease_expires_at`
- `heartbeat_at`
- `renewed_at`
- `version`

这层回答的是“这台资源现在归谁，多久没续约了”。

### 4. Run 绑定

记录一次 run 最终绑定到了哪台执行节点。

关键字段：

- `runtime_task_id`
- `runtime_profile_id`
- `runtime_type`
- `runtime_run_id`
- `runtime_instance_id`
- `resource_profile_id`
- `lease_id`
- `base_url_snapshot`
- `bootstrap_snapshot`
- `binding_status`
- `binding_reason`
- `created_at`
- `released_at`

这层回答的是“这个 run 后续 status / cancel / artifacts 应该回哪台节点”。

## 口径补充

- `runtime_endpoint` 只表示这次提交用的 Runtime Manager 入口，不是绑定节点地址。
- `base_url_snapshot` 只做路由快照，不是长期身份。
- `bootstrap_snapshot` 记录这次 run/task/binding 实际拉取的 CUA bundle/config 对象快照，里面直接带 `bundle_ref` / `config_ref`。
- `lease_owner` 是租约持有者标识，通常由 Runtime Manager 生成并在续约、释放里复用，不是用户 ID。
- `resource_ref` 可以是 ECS id、VM id 或其他资源标识。
- `runtime_run_id` 和 `lease_id` 都是 late-bind 字段，可以先空后写。
- `last_capacity_payload` 至少要表达 `free`、`leased`、`orphan_leases`、`allow_create`、`lock_backend.type`、`lock_backend.shareable_across_instances`。
- `binding_status`、`lease_status` 的终态必须由收敛任务写入，并保留对应 `reason`。

## bootstrap_snapshot

统一结构如下：

```json
{
  "bootstrap_mode": "tos",
  "cua_distribution": {
    "bundle_ref": {
      "storage_type": "tos",
      "bucket": "xua-cua-release",
      "object_key": "cua/releases/cua-linux-x64-pkg-<git-sha>-<timestamp>.tar.gz",
      "tos_uri": "tos://xua-cua-release/cua/releases/cua-linux-x64-pkg-<git-sha>-<timestamp>.tar.gz",
      "version": "cua-linux-x64-pkg-<git-sha>-<timestamp>",
      "sha256": "sha256:..."
    },
    "config_ref": {
      "storage_type": "tos",
      "bucket": "xua-cua-config",
      "object_key": "cua/configs/blackbox-runtime-template-<version>.json",
      "tos_uri": "tos://xua-cua-config/cua/configs/blackbox-runtime-template-<version>.json",
      "version": "blackbox-runtime-template-<version>",
      "sha256": "sha256:..."
    }
  }
}
```

- `bundle_ref` 是本次实际拉取的 CUA 可执行包对象。
- `config_ref` 是本次实际拉取的配置模板对象；如果配置不走 TOS，可以为空，但 `bootstrap_mode` 仍要记录来源模式。
- `storage_type=tos` 时，`bundle_ref` / `config_ref` 必须显式带 `tos_uri`，格式为 `tos://bucket/object_key`；这只是可读定位串，不是下载凭证。
- `bootstrap_snapshot` 不记录 presigned URL、AK/SK 或本机路径。

## 字段细化

### `runtime_instances`

- `runtime_instance_id`：节点身份，不能直接拿 IP 代替。
- `runtime_profile_id`：所属 RuntimeProfile，决定这台节点服务哪个 runtime_type。
- `runtime_type`：实例类型，第一阶段固定为 `osworld`。
- `base_url`：对外调用该实例的基础地址快照。
- `health_url`：健康检查地址，可与 `base_url` 不同。
- `resource_profile_id`：这台实例承载的资源池引用。
- `labels`：调度标签，例如 region、os、mode、pool。
- `status`：当前健康状态。
- `status_reason`：最近一次状态变更原因。
- `last_heartbeat_at`：最近一次心跳时间。
- `heartbeat_ttl_seconds`：判定失联的阈值快照。
- `last_capacity_payload`：最近一次 capacity 响应快照，至少保留 `free`、`leased`、`orphan_leases`、`allow_create`、`lock_backend.type`、`lock_backend.shareable_across_instances`。
- `last_capacity_at`：最近一次 capacity 拉取时间。

### `runtime_tasks`

- `run_id`：所属 EvaluationRun。
- `runtime_profile_id`：调用的 RuntimeProfile。
- `runtime_type`：Runtime 类型，例如 `osworld`。
- `runtime_mode`：执行模式，例如 `blackbox` / `vm_native`。
- `runtime_endpoint`：当次提交使用的 Runtime 入口快照。
- `runtime_instance_id`：最终绑定实例快照。
- `resource_profile_id`：当次任务使用的资源池引用。
- `runtime_run_id`：Runtime 侧生成的运行标识。
- `status`：平台侧任务状态。
- `status_reason`：状态变化原因。
- `attempt`：平台提交尝试号，从 1 开始递增。
- `idempotency_key`：提交幂等键。
- `request_payload`：发给 Runtime 的请求快照。
- `response_payload`：validate / start 的原始响应快照。
- `last_status_payload`：最近一次 status 响应快照。
- `error_code`：归一化错误码。
- `error_message`：脱敏后的错误信息。
- `last_polled_at`：最近一次轮询时间。
- `cancel_requested_at`：第一次发起取消的时间。

### `runtime_run_bindings`

- `runtime_profile_id`：绑定时使用的 RuntimeProfile。
- `runtime_type`：Runtime 类型。
- `runtime_run_id`：Runtime 侧运行标识。
- `runtime_instance_id`：绑定到的实例。
- `resource_profile_id`：绑定到的资源池引用。
- `lease_id`：关联的资源租约标识。
- `base_url_snapshot`：绑定时地址快照。
- `binding_status`：`pending` / `bound` / `releasing` / `released` / `lost`。
- `binding_reason`：绑定、重绑、释放、丢失原因。
- `created_at`：创建时间。
- `released_at`：释放时间。

### `resource_leases`

- `runtime_type`：资源所属 Runtime 类型。
- `runtime_profile_id`：资源对应的 RuntimeProfile。
- `resource_profile_id`：平台侧资源池引用。
- `resource_ref`：具体资源标识。
- `runtime_task_id`：触发该租约的 RuntimeTask。
- `lease_owner`：租约持有者标识。
- `runtime_run_id`：关联的 Runtime run。
- `runtime_instance_id`：承载该资源的 Runtime 实例。
- `lease_status`：`leased` / `renewing` / `released` / `expired` / `reclaimed`。
- `lease_reason`：状态变化原因。
- `lease_expires_at`：租约失效时间。
- `heartbeat_at`：最近一次续约或保活时间。
- `renewed_at`：最近一次成功续约时间。
- `version`：CAS 版本号。

## 推荐流程

### start

1. Manager 查健康节点和可用容量。
2. 选中一个节点。
3. 在事务里创建租约。
4. 写入 run 绑定。
5. 启动实际执行。

### status / cancel / artifacts

1. 先查 run 绑定。
2. 再查当前节点注册信息。
3. 用当前 `base_url` 访问绑定节点。
4. 如果节点不可达，返回 `runtime_lost` 或 `runtime_unreachable`。

### heartbeat

1. 节点定期刷新 `heartbeat_at`。
2. 超过 TTL 认为节点不健康。
3. 不健康节点上的租约进入回收流程。

### release

1. 正常结束时主动释放租约。
2. 异常结束时由回收任务兜底。
3. 释放动作必须幂等。

## 允许用 Redis 的地方

Redis 可以用来做：

- 节点心跳缓存
- 短期调度队列
- 热路径容量缓存

但不要用 Redis 代替 DB 做唯一真相。Redis 丢了，租约和绑定就会飘，后面 cancel 和审计都没法收。

## 不允许的做法

- 本地文件锁当分布式锁。
- `/tmp` registry 当共享状态源。
- 节点挂了以后自动把 run 漂移到另一台机器。
- 用一个共享域名把执行节点池随机分发给不同 run。

## 结论

这套系统里最重要的不是“快”，而是“不乱”。

所以：

1. DB 存真相。
2. Redis 只做加速。
3. 绑定不可漂移。
4. 租约要有 TTL 和回收。
