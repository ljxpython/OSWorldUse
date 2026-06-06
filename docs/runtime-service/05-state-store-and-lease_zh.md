# 状态存储与租约

## 先定结论

多服务器场景下，**DB 是真相源，Redis 只是可选加速层**。

别反过来。Redis 可以快，但它不适合承载唯一真相。租约、绑定、节点注册这些东西要能审计、能恢复、能追踪，DB 更稳。

## 三类状态

### 1. 节点注册

记录执行节点当前状态。

关键字段：

- `runtime_instance_id`
- `base_url`
- `health_url`
- `capacity`
- `heartbeat_at`
- `status`
- `metadata`

这层回答的是“这台节点现在活着吗、地址是什么、还能接多少活”。

### 2. 资源租约

记录某个 ECS / VM / runtime 资源当前被谁占着。

关键字段：

- `lease_id`
- `resource_ref`
- `runtime_instance_id`
- `runtime_run_id`
- `lease_status`
- `leased_at`
- `lease_expires_at`
- `renewed_at`
- `released_at`
- `version`

这层回答的是“这台资源现在归谁，多久没续约了”。

### 3. Run 绑定

记录一次 run 最终绑定到了哪台执行节点。

关键字段：

- `runtime_run_id`
- `runtime_instance_id`
- `base_url_snapshot`
- `lease_id`
- `binding_status`
- `created_at`
- `released_at`

这层回答的是“这个 run 后续 status / cancel / artifacts 应该回哪台节点”。

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
