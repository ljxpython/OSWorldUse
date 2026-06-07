# 多服务器部署与一致性

## 会出现什么问题

1. run 状态散在不同机器，查询和取消会打错对象。
2. 同一台 ECS 或 VM 被多个 worker 抢占，产生重复执行。
3. 本机 `result_dir`、录屏和日志只存在于某一台节点，节点异常后结果丢失。
4. 多台服务器版本不一致，导致同一请求在不同节点行为不同。
5. 负载均衡把 `status`、`cancel`、`artifacts` 分发到不持有该 run 的节点。

## 推荐拓扑

### 方案 A：单节点

适合本地开发和 PoC。优点是简单，缺点是没有扩容能力，也不适合作为正式服务。

### 方案 B：多节点共享池

多个执行节点共享同一批 ECS 或 VM，适合横向扩容。

前提是必须补齐以下能力：

- 共享 lease 存储。
- 共享 run -> instance 绑定。
- 共享 artifact 存储。
- 节点 heartbeat 和 orphan 回收。

### 方案 C：多节点分池

每个节点或每组节点负责自己的池，控制面根据容量选择目标节点。

这是最容易落地的方式，适合第一阶段先把链路跑稳。

## 必须补的能力

- admission 时记录 `runtime_run_id -> instance/base_url`。
- `status / cancel / artifacts` 必须按绑定路由，不做随机分发。
- 对于共享池，lease 必须带 TTL，节点挂了以后能自动回收。
- artifact 要上传共享对象存储，节点本地只保留临时副本。
- 节点要暴露 health 和 capacity，控制面才能做容量感知。
- 状态真相源必须共享，不能写进本地文件或单机内存。

## 池模型

`resource_profile_id` 只定义资源池边界，不强行规定共享池还是独立池。

这套 Runtime Contract 同时兼容两种拓扑：

- 共享池：多个执行节点共享同一批 ECS / VM，lease 状态必须共享。
- 独立池：每个节点或节点组维护自己的资源池，lease 只在池内竞争。

统一约束不变：

- 同一个 `resource_profile_id` 在同一时刻只采用一种拓扑。
- `runtime_run_id -> runtime_instance_id` 的绑定规则不变。
- `status / cancel / artifacts` 的路由规则不变。
- 控制面只看 `resource_profile_id` 和 capacity，不需要感知底层池是共享还是独立。

## 地址模型

第一阶段不要求所有节点都挂固定域名。

推荐的最小口径是：

- 平台只配置一个 Manager 入口。
- Manager 维护执行节点 `base_url`。
- `base_url` 可以是 `ip:port`，也可以是内部 DNS 名称。
- 节点身份以 `runtime_instance_id` 为准，不以 IP 为准。
- `base_url_snapshot` 只作为本次绑定的快照，不作为长期身份。

因此，**可以先不用域名**，直接用内部网段的 `ip:port`；但这不是“不要地址管理”，而是“地址管理下沉到 Runtime Manager”。

## blackbox 特有约束

- 每个 run 的 `bridge port`、`nodeId`、`runId`、`runsDir` 不能复用。
- 同一个 CUA 运行上下文不能被多个任务并发共享。
- bridge server 只服务本 run，不要被别的 run 直接复用。

## vm_native 特有约束

- 每个任务必须绑定独立 ECS 或至少独立桌面环境。
- 同一 ECS 不要被多个 worker 同时竞争。
- reset、setup、录屏和 artifact 拉回必须跟着同一个执行节点走。

## 结论

多服务器不是不能做，问题是不能让状态漂移。

最稳的做法是：

1. 先固定 run 绑定到唯一执行节点。
2. 再把 lease、结果和产物外置。
3. 节点池可以是共享池，也可以是独立池，协议不变。
4. 最后再谈节点池扩容和故障恢复。
