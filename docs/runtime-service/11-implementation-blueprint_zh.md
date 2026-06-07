# OSWorld Runtime Service 实现蓝图

更新时间：2026-06-07

> 说明：这是 OSWorld 仓库视角的实现落地说明。平台侧完整实现蓝图在 XUA-Eval 的 `docs/xua-platform/22-osworld-runtime-service-implementation-blueprint.md`。本文只说明 OSWorld 这一侧的边界和需要配合的点。

## 先定结论

- OSWorld 仓库不长期承载平台-facing FastAPI 服务。
- Runtime 包装代码优先放在 XUA-Eval 的 `runtimes/osworld/`，后续可独立为 `xua-osworld-runtime` 仓库。
- OSWorld 仓库继续提供评测脚本、case、provider、evaluator 和结果目录。
- Runtime 通过 `OSWORLD_HOME` 指向本仓库，然后 subprocess 调用现有脚本。
- 对 OSWorld 的改动尽量小，只做稳定 CLI 参数、result_dir、summary 输出、退出码和 artifact 必要字段。

## Runtime 包装目录

XUA-Eval 侧推荐目录：

```text
runtimes/osworld/
  pyproject.toml
  Dockerfile
  src/xua_osworld_runtime/
    main.py
    config.py
    api/
    service/
    runner/
    state/
    artifacts/
    bootstrap/
    resources/
    security/
```

OSWorld 侧保持原有入口：

```text
scripts/python/run_multienv_cua_blackbox.py
scripts/python/run_multienv_cua_vm_native.py
```

## OSWorld 需要保证的能力

### 1. 稳定 CLI

Runtime command builder 只把 allowlist 参数映射到 OSWorld 脚本。OSWorld 侧需要保持下面参数语义稳定：

```text
--os_type
--provider_name
--test_all_meta_path
--domain
--example_id
--model
--result_dir
--num_envs
--max_steps
--enable_recording
--build_report
--log_level
--disable_task_proxy
```

如果新增参数用于 TOS 上传、CUA config 或 result manifest，必须兼容旧命令，不破坏本地直接跑脚本。

### 2. `result_dir/result.txt` 续跑语义

继续沿用现有 `get_unfinished()` 逻辑：

- case 目录里已有 `result.txt`，视为已完成。
- 没有 `result.txt`，继续补跑。
- retry / rerun 不清空旧 `result_dir`。

Runtime 只负责把 `resume_policy=continue_from_result_txt` 映射到旧结果目录，不改变 OSWorld 原生判断方式。

### 3. 结果目录可被标准化读取

Runtime manifest builder 会从 OSWorld result_dir 读取：

```text
result.txt
steps.json
cua_meta.json
bridge_requests.jsonl
recording.mp4
runtime.log
summary.json / summary.csv
```

OSWorld 不需要直接写平台 DB，但应尽量保证这些文件路径和含义稳定。缺失文件时 Runtime 会写入 `missing_artifacts`，不会假造结果。

### 4. CUA bundle / config 由 Runtime 物化

CUA CLI 和 config 可以由 Runtime 从 TOS 下载并物化到本机。

OSWorld 脚本侧只需要通过受控环境变量或已有参数读取：

```text
OSWORLD_CUA_BIN
OSWORLD_CUA_CONFIG_PATH
```

OSWorld 不应该记录 TOS presigned URL、AK/SK 或 config 下载凭证。

### 5. Artifact 上传不由平台扫本地目录

正式链路：

```text
OSWorld result_dir
  -> Runtime manifest builder
  -> Runtime TOS uploader
  -> 平台 ingest manifest
```

平台不扫描 OSWorld 本地目录。OSWorld 只需要把原始证据写完整。

## Runtime 最小开发顺序

1. Runtime package 和 `/v1/health`：检查 `OSWORLD_HOME` 和两个脚本存在。
2. command builder：把 `runtime_mode` 映射为对应脚本和 allowlist CLI 参数。
3. subprocess runner：启动、查询、取消 OSWorld 脚本。
4. result reader：读取 result_dir，保留 `result.txt` 续跑语义。
5. manifest builder：生成标准 artifact manifest。
6. TOS uploader：按 case 上传 artifact，run 结束后生成 summary manifest。
7. CUA bootstrap：从 TOS 拉取 bundle/config，设置 `OSWORLD_CUA_BIN` 和 `OSWORLD_CUA_CONFIG_PATH`。

## 状态存储口径

- 本地调试可以使用 SQLite。
- 正式服务和多实例必须使用 PostgreSQL。
- 多实例共享同一个资源池时，lease / binding / runtime task 必须共享状态，不能靠本地文件锁碰运气。

## OSWorld 侧禁止改动方向

- 不在 OSWorld 仓库里写平台 DB 逻辑。
- 不在 OSWorld 仓库里写 XUA 前端或控制面 API。
- 不把 Runtime Manager 的调度、租约和绑定状态塞进 OSWorld runner 脚本。
- 不为了平台服务化重构 evaluator / provider 主逻辑。

如果 OSWorld 脚本确实缺少必要能力，只做小补丁，并保持本地命令行可直接运行。

## 验收口径

- 本地直接跑 OSWorld 原命令仍可用。
- Runtime 通过 `OSWORLD_HOME` 调脚本可用。
- `blackbox` 和 `vm_native` 都能生成 result_dir。
- 同一 result_dir 续跑时已完成 case 不重复执行。
- Runtime 能从 result_dir 生成标准 manifest。
- TOS 上传失败能暴露为 `upload_error` 或 `artifact_missing`，不污染 OSWorld 分数。

## 对应平台文档

- XUA-Eval Runtime 实现蓝图：`docs/xua-platform/22-osworld-runtime-service-implementation-blueprint.md`
- Runtime API 契约：`docs/xua-platform/16-osworld-runtime-service-contract-and-sequence.md`
- Artifact / manifest：`docs/xua-platform/20-osworld-runtime-service-result-ingest-and-artifacts.md`
