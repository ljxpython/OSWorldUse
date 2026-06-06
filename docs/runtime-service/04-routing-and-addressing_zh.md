# 路由与地址约定

## 先回答问题

不是“完全不用域名”，而是**不要把域名当成 run 归属的依据**。

第一阶段建议这样分：

- **平台到 Runtime Manager**：可以是域名，也可以是 `ip:port`。
- **Runtime Manager 到执行节点**：可以是 `http://<ip>:<port>`，也可以是内部 DNS 名称。
- **run 的身份**：只认 `runtime_run_id`。
- **节点的身份**：只认 `runtime_instance_id`。

域名只是地址别名，不能替代绑定关系。

## 推荐口径

### 1. 平台只认 Manager

平台不直接访问执行节点，也不做节点级负载均衡。

平台只配置一个稳定入口：

```text
OSWORLD_RUNTIME_ENDPOINT=http://runtime-manager.internal:7001/v1
```

如果没有内部域名，也可以先用：

```text
OSWORLD_RUNTIME_ENDPOINT=http://10.0.0.12:7001/v1
```

这里的地址是 **Manager 的入口**，不是执行节点池地址。

### 2. Manager 保存节点地址

每个执行节点注册时，写入：

- `runtime_instance_id`
- `base_url`
- `health_url`
- `capacity`
- `updated_at`

`base_url` 第一阶段可以直接是：

```text
http://10.0.1.23:8080
```

或者：

```text
http://osworld-runtime-node-01.internal:8080
```

只要 Manager 能稳定访问就行。

### 2.1 如果执行节点使用域名

可以，但必须是**节点级域名**，不是“整个池子一个共享域名”。

推荐格式例如：

```text
osworld-runtime-node-01.internal
osworld-runtime-node-02.internal
```

要求：

- 一个域名只对应一台执行节点。
- 域名变化时，由 Manager 更新注册表。
- 如果节点是动态 IP，域名由服务发现或内网 DNS 自动更新。
- 域名只当地址别名，不当身份。

不要用这种模式：

```text
osworld-runtime-pool.internal
```

然后让 DNS / LB 自动随机分到不同节点，再把 `status / cancel / artifacts` 打过去。这个会把 run 绑定直接冲烂。

如果必须用共享入口，那它只能是 Manager 的入口，不是执行节点入口。

### 3. 绑定是核心

start 时先选节点，再写绑定：

```text
runtime_run_id -> runtime_instance_id -> base_url_snapshot
```

后续的 `status / cancel / artifacts` 都先查 binding，再转发到绑定节点。

### 4. 不做随机分发

这些请求不能被 LB 随机分到别的节点：

- `GET /runs/{runtime_run_id}`
- `POST /runs/{runtime_run_id}/cancel`
- `GET /runs/{runtime_run_id}/artifacts`

LB 只适合放在 Manager 前面，不适合放在执行节点级别做 round-robin。

### 5. 节点失联怎么处理

如果绑定节点不可达：

- 返回 `runtime_unreachable` 或 `runtime_lost`
- 不自动切到另一台节点继续查、继续 cancel、继续拉产物
- 由上层决定重试、失败或人工介入

原因很简单，状态机不能靠“换台机器试试”来收敛。

## 结论

第一阶段可以直接用 `ip:port`，尤其适合 ECS 内部网络。

但真正重要的不是地址形式，而是：

1. 管理入口稳定。
2. 节点地址可注册。
3. run 绑定不可漂移。
4. 产物最终外置到共享存储。
