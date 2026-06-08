# 背景、目标和边界

## 背景

OSWorld 现在已经具备黑盒 bridge 和 vm_native 两条执行链路，但它们本质上仍是脚本式 runner，不是一个稳定的内部服务。

未来接入 `xua-eval` 时，OSWorld 侧要解决的不是“再写一个更大的脚本”，而是把执行行为收敛成稳定的 Runtime 服务能力。

## 目标

- 以 ECS 作为执行宿主。
- 支持 `blackbox` 和 `vm_native` 两种模式。
- 对外提供统一的 `validate / start / status / cancel / artifacts` 语义。
- 允许多台执行节点横向扩容。
- 所有 run 都能回收结果和排障证据。
- 接收平台冻结后的 OSWorld case snapshot，生成临时 `generated_suite.json` 并传给原生 `--test_all_meta_path`。

## 非目标

- 不做多租户。
- 不做公开网关。
- 不做独立鉴权体系。
- 不把平台数据库、调度逻辑、报表逻辑写进 OSWorld。
- 不管理平台 suite / case 生命周期，不负责导入或同步平台评测集。
- 不要求所有节点共享本地工作目录。

## 边界

- OSWorld repo 负责 provider、脚本、运行证据和评测产物。
- Runtime Service 负责任务入口、节点绑定、进度查询和取消。
- Runtime Service 可以校验和消费 OSWorld case snapshot，但不能替平台创建 suite 或 case。
- xua-eval 负责控制面、状态机、结果查询和业务侧报表。

## 术语

- `runtime_run_id`：一次运行的全局标识。
- `instance`：实际承载该 run 的执行节点。
- `lease`：节点或 ECS 的临时占用关系。
- `artifact manifest`：结果文件的标准清单。
