# 12. Suite / Case Catalog、快照与临时 test_all_meta_path 契约

## 结论

OSWorld Runtime 不管理平台评测集生命周期，也不写平台数据库。第一版采用更简单的分工：

- OSWorld 侧提供只读 catalog API，把 `evaluation_examples` 中的 suite / case 元数据标准化暴露出来。
- XUA-Eval 平台调用 catalog API，把 OSWorld 官方和常用 suite / case 同步进平台数据库。
- 平台负责自定义 suite、多对多关系、选择 case、创建 run 和冻结 run case snapshot。
- OSWorld Runtime 执行时只负责校验并运行平台传入的 OSWorld case snapshot。

运行 OSWorld 自定义评测集时，Runtime 根据平台传入的 `case_snapshot` 生成临时 JSON：

```json
{
  "chrome": ["bb5e4c0d-f964-439c-8b..."],
  "gimp": ["7a4deb26-d57d-4ea9-9a73-630f66a7b568"]
}
```

然后继续调用 OSWorld 原生脚本参数：

```bash
--test_all_meta_path "<runtime-task-dir>/generated_suite.json"
```

这保证官方 suite、自定义 OSWorld suite、失败回归 suite 都复用同一条 OSWorld 执行路径。

## 边界

OSWorld Runtime 做：

- 暴露只读 catalog API，扫描本地 OSWorld checkout 的 `evaluation_examples`。
- 返回标准化 suite / case 元数据和 catalog 版本。
- 接收平台传入的 `case_snapshot`。
- 校验 `framework_key=osworld`。
- 校验每个 case 有 `domain` 和 `external_id`。
- 可选校验 `evaluation_examples/examples/{domain}/{external_id}.json` 是否存在。
- 生成临时 `generated_suite.json`。
- 把 `generated_suite.json` 写入 runtime task 目录。
- 执行 OSWorld 原生 runner。
- 在 artifact manifest 或 runtime metadata 中暴露本次实际使用的 generated suite。
- 续跑时复用同一个 `generated_suite.json` 和 `result_dir`。

OSWorld Runtime 不做：

- 不创建平台 suite。
- 不同步平台 case。
- 不写 XUA-Eval 数据库。
- 不跨框架组合 case。
- 不从平台数据库读取 case。
- 不把 WebVoyager / AndroidWorld / 自建框架 case 塞进 OSWorld runner。

## Catalog API

Catalog API 是只读接口，供平台同步 OSWorld suite / case 元数据。它不启动 VM，不执行 agent，不生成 run，也不写平台数据库。

开发任务、验证命令和打勾记录见 [13 Suite / Case Catalog 开发任务清单](./13-suite-case-catalog-implementation-checklist_zh.md)。本文只定义契约。

第一版 catalog 来源：

- suite/index 文件：`evaluation_examples/*.json` 以及明确纳入白名单的 `evaluation_examples/**/suites/*.json`。
- case 本体优先来自 `evaluation_examples/examples/{domain}/{case_id}.json`。Windows 和 CUA 自定义 case 可来自 `evaluation_examples/examples_windows/{domain}/{case_id}.json`、`evaluation_examples/cua_blackbox/cases/{domain}/{case_id}.json` 等受控候选根。

`suite_key` 生成规则：

- 根目录 suite 使用文件名去掉 `.json`，例如 `evaluation_examples/test_small.json` -> `test_small`。
- 子目录 suite 使用相对路径去掉 `.json` 后把 `/` 替换为 `:`，例如 `evaluation_examples/cua_blackbox/suites/windows_office_core.json` -> `cua_blackbox:suites:windows_office_core`。
- `suite_key` 必须稳定，不跟随部署机器绝对路径变化。

### Get Catalog Info

```text
GET /v1/catalog/info
```

响应：

```json
{
  "framework_key": "osworld",
  "runtime_type": "osworld",
  "catalog_version": "osworld:<git_sha>:<evaluation_examples_hash>",
  "osworld_revision": "<git_sha>",
  "suite_roots": ["evaluation_examples"],
  "case_roots": [
    "evaluation_examples/examples",
    "evaluation_examples/examples_windows",
    "evaluation_examples/cua_blackbox/cases"
  ],
  "generated_at": "2026-06-08T00:00:00Z",
  "supports": ["suites", "cases"]
}
```

规则：

- `catalog_version` 用于平台判断一次同步是否来自同一份 OSWorld 元数据。
- 响应不返回机器绝对路径、AK/SK 或其他部署敏感信息。
- 如果 Runtime 实例无法读取 `evaluation_examples`，返回 `catalog_unavailable`。

### List Suites

```text
GET /v1/catalog/suites?page=1&page_size=50&keyword=test
```

响应 item：

```json
{
  "framework_key": "osworld",
  "suite_key": "test_small",
  "name": "test_small",
  "version": "osworld:<git_sha>:<evaluation_examples_hash>",
  "source_ref": "evaluation_examples/test_small.json",
  "source_hash": "sha256:...",
  "case_count": 34,
  "domains": ["chrome", "gimp"],
  "metadata": {}
}
```

### Get Catalog Snapshot

```text
GET /v1/catalog/snapshot
```

用途：给平台“一键同步评测资源”使用。该接口把 catalog info、suite 列表和每个 suite 下的 case 一次性返回，减少平台同步时的分页编排成本。

响应：

```json
{
  "info": {
    "framework_key": "osworld",
    "runtime_type": "osworld",
    "catalog_version": "osworld:<git_sha>:<evaluation_examples_hash>",
    "osworld_revision": "<git_sha>",
    "suite_roots": ["evaluation_examples"],
    "case_roots": ["evaluation_examples/examples"],
    "generated_at": "2026-06-08T00:00:00Z",
    "supports": ["suites", "cases", "snapshot"]
  },
  "suites": [
    {
      "framework_key": "osworld",
      "suite_key": "test_small",
      "name": "test_small",
      "version": "osworld:<git_sha>:<evaluation_examples_hash>",
      "source_ref": "evaluation_examples/test_small.json",
      "source_hash": "sha256:...",
      "case_count": 34,
      "domains": ["chrome", "gimp"],
      "metadata": {},
      "raw_index": null
    }
  ],
  "cases_by_suite": {
    "test_small": [
      {
        "framework_key": "osworld",
        "external_id": "bb5e4c0d-f964-439c-8b...",
        "domain": "chrome",
        "name": "bb5e4c0d-f964-439c-8b...",
        "prompt": "Open Chrome and ...",
        "source_ref": "evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-8b....json",
        "source_hash": "sha256:...",
        "runnable_status": "ready",
        "raw_metadata": {}
      }
    ]
  },
  "total_suites": 1,
  "total_cases": 34,
  "catalog_version": "osworld:<git_sha>:<evaluation_examples_hash>"
}
```

规则：

- `snapshot` 是只读接口，不启动 VM、不执行 agent、不写平台数据库。
- `suites[*].raw_index` 默认返回 `null`，避免把 suite index 细节暴露给普通同步流程；需要调试时仍可调用 `GET /v1/catalog/suites/{suite_key}`。
- `cases_by_suite` 的 key 必须等于 `suite_key`。
- `total_cases` 按 suite membership 计数，不做跨 suite 去重。
- 如果 Runtime 不支持该接口，平台可以回退到 `info/suites/suite cases` 分页接口。
- 如果 Runtime 支持该接口，`supports` 应包含 `snapshot`。

### Get Suite

```text
GET /v1/catalog/suites/{suite_key}
```

响应：

```json
{
  "framework_key": "osworld",
  "suite_key": "test_small",
  "name": "test_small",
  "version": "osworld:<git_sha>:<evaluation_examples_hash>",
  "source_ref": "evaluation_examples/test_small.json",
  "source_hash": "sha256:...",
  "case_count": 34,
  "domains": ["chrome", "gimp"],
  "raw_index": {
    "chrome": ["bb5e4c0d-f964-439c-8b..."]
  }
}
```

### List Suite Cases

```text
GET /v1/catalog/suites/{suite_key}/cases?page=1&page_size=100
```

响应 item：

```json
{
  "framework_key": "osworld",
  "external_id": "bb5e4c0d-f964-439c-8b...",
  "domain": "chrome",
  "name": "Open Chrome and ...",
  "prompt": "Open Chrome and ...",
  "source_ref": "evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-8b....json",
  "source_hash": "sha256:...",
  "raw_metadata": {}
}
```

### List Cases

```text
GET /v1/catalog/cases?domain=chrome&page=1&page_size=100
```

查询参数：

- `domain`：可选。
- `suite_key`：可选，只返回某个 suite 下的 case。
- `q`：可选，按 `external_id`、`name`、`prompt` 做轻量搜索。
- `page` / `page_size`：分页。

### Get Case

```text
GET /v1/catalog/cases/{external_id}
```

规则：

- OSWorld case id 理论上应在框架内全局唯一。
- 如果实现发现同一个 `external_id` 出现在多个 domain，必须返回冲突错误，要求调用方带 `domain` 查询参数重试。

响应：

```json
{
  "framework_key": "osworld",
  "external_id": "bb5e4c0d-f964-439c-8b...",
  "domain": "chrome",
  "name": "Open Chrome and ...",
  "prompt": "Open Chrome and ...",
  "setup_config": {},
  "grading_type": "rule",
  "grading_criteria": {},
  "source_ref": "evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-8b....json",
  "source_hash": "sha256:...",
  "raw_metadata": {}
}
```

### Catalog 部署约束

第一版平台应配置一个固定的 OSWorld catalog endpoint 或固定 RuntimeProfile 来做元数据同步，不要把 catalog 请求随机打到多个执行节点。

原因：

- 多台 OSWorld Runtime 节点可能 checkout 到不同 git revision。
- `evaluation_examples` 可能存在本地补丁或分支差异。
- 随机负载均衡会导致一次 suite 同步跨 catalog 版本，平台 DB 里混入不同来源的 case。

如果未来必须多节点提供 catalog，需要满足：

- 所有节点使用同一个 OSWorld 镜像或同一个 `osworld_revision`。
- `GET /v1/catalog/info` 返回一致的 `catalog_version`。
- 平台导入任务开始时锁定 `catalog_version`，后续分页请求发现版本变化必须中止并返回 `catalog_version_changed`。

## Runtime 请求字段

标准 Runtime request 在原有字段基础上增加 `case_snapshot`。

```json
{
  "platform_run_id": "uuid",
  "runtime_task_id": "uuid",
  "idempotency_key": "osworld:run:attempt:1",
  "runtime_type": "osworld",
  "runtime_mode": "blackbox",
  "resource_profile_id": "osworld-volcengine",
  "case_selection": {
    "mode": "explicit",
    "framework_key": "osworld",
    "suite_id": "uuid",
    "suite_key": "osworld-my-regression"
  },
  "case_snapshot": [
    {
      "case_id": "uuid",
      "external_id": "bb5e4c0d-f964-439c-8b...",
      "domain": "chrome",
      "framework_key": "osworld",
      "case_revision": 3,
      "source_ref": "evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-8b....json"
    }
  ],
  "run_options": {
    "num_envs": 1,
    "max_steps": 80,
    "artifact_storage_mode": "tos",
    "artifact_upload_policy": "per_case",
    "resume_policy": "fresh"
  }
}
```

兼容规则：

- 如果平台还没有发 `case_snapshot`，Runtime 可以继续兼容旧字段 `case_external_ids` / `case_selection.case_ids` / `case_selection.domain`。
- 新链路优先使用 `case_snapshot`，旧字段只作为过渡兼容。
- 如果同时提供 `case_snapshot` 和 `run_options.test_all_meta_path`，正式运行优先使用 `case_snapshot` 生成的临时 JSON；`run_options.test_all_meta_path` 只作为兼容或手工调试输入。
- `artifact_storage_mode=tos` 表示生成 TOS URI 并按上传策略处理；`artifact_storage_mode=local_path` 表示本地调试产物，manifest 中 artifact 使用绝对本地路径，平台可以入库 metadata 但不要求生成访问 URL；`local` 作为 `local_path` 兼容别名。

## validate 行为

`POST /v1/runs/validate` 必须只读。

检查项：

- `runtime_type == osworld`。
- `runtime_mode in {blackbox, vm_native}`。
- `case_snapshot` 不为空。
- 所有 case 的 `framework_key == osworld`。
- 所有 case 有 `external_id`。
- 所有 case 有 `domain`。
- 生成后的 domain 分组不为空。
- 如果开启本地源码校验，检查 case JSON 文件存在。
- 生成 command preview 时展示临时 JSON 路径占位，而不是平台原始 suite path。

错误码建议：

| code | 场景 |
| --- | --- |
| `empty_case_snapshot` | 平台没有传 case |
| `framework_mismatch` | 混入非 OSWorld case |
| `case_domain_missing` | case 缺少 domain |
| `case_external_id_missing` | case 缺少 external_id |
| `case_source_missing` | 本地 OSWorld case JSON 不存在 |
| `generated_suite_empty` | 生成的临时 suite 没有任何 case |

## start 行为

`POST /v1/runs` 执行步骤：

1. 解析 request。
2. 按 `idempotency_key` 做幂等检查。
3. 创建 runtime task 目录。
4. 根据 `case_snapshot` 生成 `generated_suite.json`。
5. 保存 `case_snapshot.json` 和 `generated_suite.json`。
6. 构造 OSWorld runner 命令。
7. 命令里使用 `--test_all_meta_path <generated_suite.json>`。
8. 启动 subprocess 或 fake backend。
9. 记录 `generated_suite_path` 到 runtime state。
10. 在 artifact manifest 中返回 generated suite 信息。

## 生成规则

输入：

```json
[
  {"external_id": "case-1", "domain": "chrome"},
  {"external_id": "case-2", "domain": "chrome"},
  {"external_id": "case-3", "domain": "gimp"}
]
```

输出：

```json
{
  "chrome": ["case-1", "case-2"],
  "gimp": ["case-3"]
}
```

规则：

- domain 按字典序稳定输出。
- 同一 domain 下 case 按平台传入顺序输出。
- 重复 `(domain, external_id)` 去重，并记录 warning。
- 不改写 external_id。
- 不把 source_ref 写进 OSWorld suite JSON，source_ref 只进入 metadata。

## Artifact / Metadata

Runtime artifacts 响应建议增加：

```json
{
  "run_metadata": {
    "generated_suite": {
      "path": "runtime://runs/osw_xxx/generated_suite.json",
      "case_count": 3,
      "domains": ["chrome", "gimp"],
      "sha256": "sha256:..."
    }
  }
}
```

如果 TOS 上传开启，可以把文件作为 run-level artifact 上传：

```text
xua/osworld/<runtime_run_id>/metadata/generated_suite.json
xua/osworld/<runtime_run_id>/metadata/case_snapshot.json
```

## 续跑

`resume_policy=continue_from_result_txt` 时：

- 必须复用原 `result_dir`。
- 必须复用原 `generated_suite.json`。
- 不能因为平台 suite 后续编辑或同步而改变本次续跑 case 集。
- OSWorld 仍按已有 `result.txt` 判断已完成 case，并只补跑缺失 case。

如果平台要求追加新 case 到同一个 result_dir，需要显式生成新的 run attempt 或新的 runtime task，并在 metadata 中记录追加来源。第一版不建议开放“追加新 case 到旧 run”。

## 和平台导入同步的关系

平台侧负责：

- 调用 OSWorld catalog API 同步官方和常用 suite。
- 把 catalog 返回的 suite / case 元数据写入平台数据库。
- 维护 suite / case 多对多关系。
- 同步来源变化。
- 创建 run 时冻结 case snapshot。

OSWorld Runtime 侧负责：

- 暴露只读 catalog API。
- 消费冻结后的 snapshot。
- 生成临时 suite JSON。
- 执行和产出 manifest。

这条边界不能反过来。Runtime 可以校验本地 case 文件是否存在，也可以通过 catalog API 展示已有 OSWorld 元数据，但不能替平台补建 suite、补写 case 或维护平台多对多关系。
