# DDL 草案

## 先定结论

- 这是 PostgreSQL 风格的落表草案，不是最终 migration。
- 本地测试可以用 SQLite，但这里只讨论正式服务主线，正式环境不切 SQLite。
- 只展开四张核心表：`runtime_instances`、`runtime_tasks`、`runtime_run_bindings`、`resource_leases`。
- `runtime_run_id` 和 `lease_id` 都是 late-bind 字段，允许先空后写。
- 容量历史快照保留为可选附录，不影响主链路。

## 通用约定

- 主键统一用 `uuid`。
- 时间统一用 `timestamptz`。
- 结构化快照统一用 `jsonb`，默认空对象。
- `runtime_type`、`runtime_mode`、`status`、`binding_status`、`lease_status` 用 `text` + 枚举约束。
- `metadata` 一律保留，方便后续排障和扩展。

## `runtime_instances`

用途：记录 Runtime Manager 可见的执行实例。

建议字段：

- `id uuid primary key`
- `runtime_profile_id uuid not null`
- `runtime_type text not null`
- `instance_key text not null`
- `base_url text not null`
- `health_url text not null`
- `resource_profile_id uuid not null`
- `labels jsonb not null default '{}'::jsonb`
- `status text not null default 'registering'`
- `status_reason text`
- `last_heartbeat_at timestamptz`
- `heartbeat_ttl_seconds integer not null default 60`
- `last_capacity_payload jsonb not null default '{}'::jsonb`
- `bootstrap_snapshot jsonb not null default '{}'::jsonb`
- `last_capacity_at timestamptz`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

需要考虑：

- `last_capacity_payload` 至少建议保存 `free`、`leased`、`orphan_leases`、`allow_create`、`lock_backend`。

建议状态：

- `registering`
- `healthy`
- `degraded`
- `unreachable`
- `retired`

建议约束：

- `unique (runtime_type, instance_key)`
- `check (heartbeat_ttl_seconds > 0)`

建议索引：

- `runtime_type`
- `resource_profile_id`
- `status`
- `last_heartbeat_at`

## `runtime_tasks`

用途：记录平台提交给 Runtime 的任务影子记录。

建议字段：

- `id uuid primary key`
- `run_id uuid not null`
- `runtime_profile_id uuid not null`
- `runtime_type text not null`
- `runtime_mode text not null`
- `runtime_endpoint text not null`
- `runtime_instance_id uuid`
- `resource_profile_id uuid not null`
- `runtime_run_id text`
- `status text not null default 'created'`
- `status_reason text`
- `attempt integer not null default 1`
- `idempotency_key text not null`
- `request_payload jsonb not null default '{}'::jsonb`
- `response_payload jsonb not null default '{}'::jsonb`
- `last_status_payload jsonb not null default '{}'::jsonb`
- `bootstrap_snapshot jsonb not null default '{}'::jsonb`
- `error_code text`
- `error_message text`
- `last_polled_at timestamptz`
- `cancel_requested_at timestamptz`
- `created_at timestamptz not null default now()`
- `submitted_at timestamptz`
- `accepted_at timestamptz`
- `started_at timestamptz`
- `finished_at timestamptz`
- `updated_at timestamptz not null default now()`

建议状态：

- `created`
- `submitted`
- `accepted`
- `queued`
- `running`
- `completed`
- `failed`
- `canceling`
- `canceled`

建议约束：

- `unique (runtime_type, idempotency_key)`
- `unique (runtime_type, runtime_run_id) where runtime_run_id is not null`
- `check (attempt > 0)`

建议索引：

- `run_id`
- `status`
- `runtime_run_id`

## `runtime_run_bindings`

用途：记录一次 RuntimeTask 实际绑定到哪个 Runtime 实例。

建议字段：

- `id uuid primary key`
- `runtime_task_id uuid not null`
- `runtime_type text not null`
- `runtime_profile_id uuid not null`
- `runtime_run_id text`
- `runtime_instance_id uuid not null`
- `resource_profile_id uuid not null`
- `lease_id uuid`
- `base_url_snapshot text not null`
- `bootstrap_snapshot jsonb not null default '{}'::jsonb`
- `binding_status text not null default 'pending'`
- `binding_reason text`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `released_at timestamptz`

建议状态：

- `pending`
- `bound`
- `releasing`
- `released`
- `lost`

建议约束：

- `unique (runtime_task_id)`
- `unique (runtime_type, runtime_run_id) where runtime_run_id is not null`

建议索引：

- `runtime_instance_id`
- `runtime_run_id`
- `binding_status`

## `resource_leases`

用途：记录资源占用、续约和回收。

建议字段：

- `id uuid primary key`
- `runtime_type text not null`
- `runtime_profile_id uuid not null`
- `resource_profile_id uuid not null`
- `resource_ref text not null`
- `runtime_task_id uuid not null`
- `lease_owner text not null`
- `runtime_run_id text`
- `runtime_instance_id uuid not null`
- `lease_status text not null default 'leased'`
- `lease_reason text`
- `bootstrap_snapshot jsonb not null default '{}'::jsonb`
- `lease_expires_at timestamptz not null`
- `heartbeat_at timestamptz`
- `renewed_at timestamptz`
- `created_at timestamptz not null default now()`
- `released_at timestamptz`
- `version bigint not null default 1`
- `metadata jsonb not null default '{}'::jsonb`

建议状态：

- `leased`
- `renewing`
- `released`
- `expired`
- `reclaimed`

建议约束：

- `check (version > 0)`
- `unique (resource_profile_id, resource_ref) where lease_status in ('leased', 'renewing')`

建议索引：

- `resource_profile_id`
- `runtime_run_id`
- `runtime_instance_id`
- `lease_status`
- `lease_expires_at`

## Late-bind 说明

- `runtime_tasks.runtime_run_id` 可以在 Runtime 接受后回填。
- `runtime_run_bindings.runtime_run_id` 可以在 Runtime 接受后回填。
- `runtime_run_bindings.lease_id` 可以在 lease 创建后回填。
- 如果 ORM 不支持同事务回填，建议把相关约束做成可延迟检查，或者先落 lease 再更新 binding。

## 可选附录：容量历史快照

如果后面要保留容量历史，可以另加：

- `runtime_capacity_snapshots(id, runtime_instance_id, runtime_type, resource_profile_id, available_slots, running_tasks, queued_tasks, bootstrap_snapshot, lock_backend_snapshot, capacity_payload, captured_at)`

这张表只做调度和排障，不替代 `runtime_instances.last_capacity_payload`。
