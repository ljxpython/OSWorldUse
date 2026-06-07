# Artifact Manifest 与结果归档

更新时间：2026-06-07

## 先定结论

- OSWorld Runtime 必须把原始 `result_dir` 转换成标准 artifact manifest。
- XUA 平台 ingest 的唯一入口是 `GET /v1/runs/{runtime_run_id}/artifacts`。
- 生产环境默认由 Runtime 上传对象存储，manifest 只返回 `tos://bucket/key` 和元数据。
- 标准 manifest 顶层也会带 `bootstrap_snapshot`，记录这次 run 实际拉取的 CUA bundle/config 对象快照。
- `artifact_storage_mode=local_path` 只用于本地调试 / 单机 smoke，不做 TOS 上传，也不进入平台 ingest。
- 默认上传粒度是 case 级异步上传，case 结束后就入队上传，run 结束时只补 summary、failure summary 和最终 manifest。
- 平台不能扫 OSWorld 本地目录，也不能依赖 `result_dir` 私有结构。
- `completed` 的最低标准是 manifest 可读且核心结果完整。
- `failed` / `canceled` 也可以返回部分 artifact，但必须明确标记缺失和失败原因。

## OSWorld 本地产物

当前 blackbox / vm_native runner 的结果目录通常会包含：

```text
<result_root>/
  args.json
  failure_summary.json
  summary/
    summary.json
    summary.csv
  <domain>/
    <case_id>/
      result.txt
      run_meta.json
      cua_meta.json
      steps.json
      recording.mp4
      bridge_requests.jsonl
```

不同 runner、参数和历史版本可能会有差异，所以 Runtime 只能把这个目录当输入源，不能让平台直接消费它。

## 标准 Manifest 结构

Runtime 对外返回统一结构：

```json
{
  "runtime_run_id": "osw_abc",
  "platform_run_id": "run_123",
  "runtime_type": "osworld",
  "status": "completed",
  "bootstrap_snapshot": {
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
  },
  "storage": {
    "type": "tos",
    "bucket": "xua-eval-artifacts",
    "base_uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc"
  },
  "summary": {
    "summary_json": {
      "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/summary/summary.json",
      "content_type": "application/json"
    },
    "summary_csv": {
      "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/summary/summary.csv",
      "content_type": "text/csv"
    },
    "failure_summary_json": {
      "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/failure_summary.json",
      "content_type": "application/json"
    }
  },
  "cases": [
    {
      "external_id": "osworld_case_001",
      "domain": "chrome",
      "status": "scored",
      "score": 1.0,
      "passed": true,
      "failure_type": null,
      "failure_reason": null,
      "artifacts": {
        "result_txt": {
          "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/cases/chrome/osworld_case_001/result.txt",
          "content_type": "text/plain",
          "previewable": true
        },
        "run_meta_json": {
          "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/cases/chrome/osworld_case_001/run_meta.json",
          "content_type": "application/json",
          "previewable": true
        },
        "recording_mp4": {
          "uri": "tos://xua-eval-artifacts/xua/osworld/run_123/osw_abc/cases/chrome/osworld_case_001/recording.mp4",
          "content_type": "video/mp4",
          "size_bytes": 73400320,
          "previewable": true
        }
      },
      "raw": {}
    }
  ],
  "missing_artifacts": [],
  "errors": []
}
```

`storage.type` 的取值：

- `tos`：生产默认，`storage` 使用 `bucket` 和 `base_uri`。
- `local_path`：本地调试模式，`storage` 使用本地路径摘要，不上传对象存储，也不走平台 ingest。

`bootstrap_snapshot` 内的 `bundle_ref` / `config_ref` 也必须显式带 `tos_uri`，让排障和审计能直接看出拉的是哪份 TOS 对象。

## Artifact 类型

第一版固定这些类型：

| 类型 | 来源 | 说明 |
| --- | --- | --- |
| `summary_json` | `summary/summary.json` | 全局 summary |
| `summary_csv` | `summary/summary.csv` | 表格 summary |
| `failure_summary_json` | `failure_summary.json` | 失败汇总 |
| `result_txt` | case `result.txt` | 单 case 分数 |
| `run_meta_json` | case `run_meta.json` | 运行元信息 |
| `cua_meta_json` | case `cua_meta.json` | CUA 元信息 |
| `steps_json` | case `steps.json` | 步骤轨迹 |
| `bridge_requests_jsonl` | case `bridge_requests.jsonl` | bridge 请求日志 |
| `recording_mp4` | case `recording.mp4` | 录屏 |
| `runtime_log` | Runtime 日志 | 执行日志 |

不存在的文件不能硬凑，必须写进 `missing_artifacts` 或 `errors`。

## 上传规则

生产环境默认上传对象存储：

```text
xua/osworld/{platform_run_id}/{runtime_run_id}/manifest.json
xua/osworld/{platform_run_id}/{runtime_run_id}/summary/summary.json
xua/osworld/{platform_run_id}/{runtime_run_id}/summary/summary.csv
xua/osworld/{platform_run_id}/{runtime_run_id}/failure_summary.json
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/result.txt
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/run_meta.json
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/cua_meta.json
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/steps.json
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/bridge_requests.jsonl
xua/osworld/{platform_run_id}/{runtime_run_id}/cases/{domain}/{external_id}/recording.mp4
xua/osworld/{platform_run_id}/{runtime_run_id}/logs/runtime.log
```

规则：

- key 中必须包含 `platform_run_id` 和 `runtime_run_id`。
- `domain`、`external_id` 写入 key 前必须做安全转义。
- 不把 ECS id、IP、AK/SK、用户 token 写进 key。
- case 级上传默认异步执行，别等整场 run 完了才一起上传，尾巴太长。
- 上传完成后再生成最终 manifest。
- manifest 中不能暴露本机绝对路径。
- 大文件要记录 `size_bytes`，可选记录 checksum。
- `artifact_storage_mode=local_path` 时不上传 TOS，只保留本地路径 manifest。

## 状态和完整性

`completed` 必须满足：

- manifest 本身可读。
- 至少有 summary 或 case 结果。
- 每个已评分 case 有 `external_id`、`domain`、`status`、`score`、`passed`。
- 必需 artifact 缺失时，任务不能伪装成成功。

`failed` / `canceled` 可以满足：

- 返回部分已上传 artifact。
- `errors` 说明失败原因。
- `missing_artifacts` 说明缺失文件。
- 平台 ingest 后 run 终态仍按原始状态收敛，不因为有部分 artifact 变成 completed。

## Manifest 生成流程

```text
1. 某个 case 结束后，Runtime 把该 case 的 artifact 入队上传。
2. 上传 worker 以 case 为单位异步写入对象存储。
3. run 结束或被取消时，Runtime 解析 summary、case result 和元数据，并 flush 上传队列。
4. Runtime 生成或更新 manifest 草稿。
5. 所有必需 artifact 落定后，Runtime 生成最终 manifest。
6. Runtime 校验 manifest 可读性。
7. Runtime 返回 artifacts 响应。
```

如果第 4 步上传失败：

- 记录 `upload_error`。
- 已经上传的 artifact 仍然返回。
- 如果核心结果缺失，`runtime_tasks.status=failed`。

如果第 5 步 manifest 生成失败：

- `runtime_tasks.status=failed`
- `status_reason=artifact_missing` 或 `upload_error`
- 不返回伪完整结果。

## 接口行为

`GET /v1/runs/{runtime_run_id}/artifacts` 是只读接口：

- 必须先查 `runtime_run_bindings`。
- 必须路由到同一绑定实例或由 Runtime Manager 返回已归档 manifest。
- 不能重新执行 runner。
- 不能扫描未绑定节点目录。
- 可以触发一次幂等的补上传，但不能改变 run 身份。
- 如果 `artifact_storage_mode=local_path`，这个接口只返回本地路径摘要，不作为平台 ingest 输入。

## 脱敏要求

manifest 不能包含：

- AK/SK
- TOS 写凭证
- 云控制台 token
- 本机绝对路径
- 公网 IP
- 未脱敏 ECS id
- 用户输入里的敏感字段

需要排障的信息写 `metadata`，但只能写脱敏摘要，例如 path hash、文件大小、content type。

## 结论

Runtime 这一侧只需要守住一句话：本地结果目录是私有实现，标准 manifest 才是对外契约。谁让平台去猜目录，谁就是在给以后挖坑。
