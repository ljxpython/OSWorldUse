# 13. Suite / Case Catalog 开发任务清单

更新时间：2026-06-08

> 说明：这是 OSWorld 仓库视角的开发清单。第一版 catalog API 的 HTTP 实现位于 XUA-Eval 的 `runtimes/osworld/`，通过 `OSWORLD_HOME` 读取本仓库的 `evaluation_examples`。本仓库不写平台 DB、不写 XUA 前端、不承载平台控制面。平台侧主清单见 `/Users/bytedance/PycharmProjects/work/xua-eval/docs/xua-platform/26-suite-case-catalog-implementation-checklist.md`。

## 总目标

让 OSWorld 作为稳定的评测元数据来源：

```text
evaluation_examples/*.json
evaluation_examples/examples/{domain}/{case_id}.json
  -> Runtime catalog scanner
  -> /v1/catalog/*
  -> XUA-Eval runtime_catalog importer
```

## 本仓库边界

OSWorld 仓库负责：

- 保持 `evaluation_examples` suite/index 和 case JSON 可被稳定扫描。
- 保持 case JSON 中 `id/instruction/config/evaluator/related_apps` 等字段语义稳定。
- 必要时补充只读元数据辅助函数或测试 fixture。
- 验证原有 runner、provider、evaluator 不被破坏。

OSWorld 仓库不负责：

- 不写平台数据库。
- 不实现 XUA-Eval 控制面 API。
- 不维护 suite/case 多对多表。
- 不生成平台 run case snapshot。
- 不让 OSWorld 原 runner 依赖平台服务。

## 阶段 0：基线保护

- [x] O00-01 记录 OSWorld git 状态。
  - 验证：`rtk git status --short`。
  - 通过标准：明确已有 docs/scripts 改动，不误删用户文件。

- [x] O00-02 跑 OSWorld 单测基线。
  - 验证：`rtk uv run python -m unittest discover -s tests`。
  - 通过标准：记录当前通过/失败情况。

- [x] O00-03 验证原 runner CLI。
  - 验证：
    - `rtk uv run python scripts/python/run_multienv_cua_blackbox.py --help`
    - `rtk uv run python scripts/python/run_multienv_cua_vm_native.py --help`
  - 通过标准：原 CLI 仍可直接运行。

阶段 0 验证记录：

- `rtk git status --short`：OSWorld 仓库存在既有 docs/scripts 未提交改动，本轮没有改 OSWorld 原 runner。
- `rtk uv run python -m unittest discover -s tests`：113 tests OK。
- `rtk uv run python scripts/python/run_multienv_cua_blackbox.py --help`：通过。
- `rtk uv run python scripts/python/run_multienv_cua_vm_native.py --help`：通过。

## 阶段 1：Catalog 元数据来源梳理

- [x] O01-01 确认 suite/index 扫描范围。
  - 默认范围：
    - `evaluation_examples/*.json`
    - 明确白名单的 `evaluation_examples/**/suites/*.json`
  - 验证：列出第一版暴露的 suite 文件清单。

- [x] O01-02 确认 `suite_key` 稳定规则。
  - 规则：
    - 根目录 suite 使用文件名去掉 `.json`。
    - 子目录 suite 使用相对路径去掉 `.json` 后把 `/` 替换为 `:`。
  - 验证：`test_small`、`test_nogdrive`、`cua_blackbox:suites:windows_office_core` 等 key 稳定。

- [x] O01-03 确认 case 文件存在性。
  - 内容：suite/index 中引用的每个 `(domain, case_id)` 优先定位到 `evaluation_examples/examples/{domain}/{case_id}.json`；Windows 和 CUA 自定义 case 会继续查 `examples_windows`、`cua_blackbox/cases` 等候选根。找不到时 catalog 返回 `runnable_status=missing_source`。
  - 验证：新增或使用 catalog scanner 测试，输出缺失 case 列表。

- [x] O01-04 确认 case 字段映射。
  - 字段：
    - `id` -> `external_id`
    - index 顶层 key -> `domain`
    - `instruction` -> `prompt`
    - `config` -> `setup_config`
    - `evaluator.func` -> `grading_type`
    - `evaluator` -> `grading_criteria`
    - `related_apps` -> `tags`
  - 验证：抽样检查 `chrome` case 的 catalog 响应和原 JSON 对齐。

阶段 1 验证记录：

- XUA-Eval Runtime catalog scanner 已实现 suite/index 扫描范围：
  - `evaluation_examples/*.json`
  - `evaluation_examples/**/suites/*.json`
- `suite_key` 验证：
  - `evaluation_examples/test_small.json` -> `test_small`
  - `evaluation_examples/cua_blackbox/suites/demo_custom_case.json` -> `cua_blackbox:suites:demo_custom_case`
- `rtk uv run pytest -q tests/test_osworld_runtime_catalog.py`：5 passed，覆盖 suite discovery、case metadata、nested suite key、缺失 case、重复 external_id 冲突。
- 真实 OSWorld catalog smoke：
  - `/v1/catalog/suites?keyword=test_small` 返回 `test_small`。
  - `/v1/catalog/suites/test_small/cases?page_size=2` 返回 total=39，case 含 `domain/external_id/source_hash/source_ref`。

## 阶段 2：OSWorld 兼容性约束

- [x] O02-01 验证 catalog 扫描不执行 OSWorld runner。
  - 通过标准：调用 `/v1/catalog/*` 不启动 VM、不创建 provider 实例、不产生 result_dir。

- [x] O02-02 验证 catalog 响应不泄漏机器敏感信息。
  - 检查项：不返回本机绝对路径、AK/SK、presigned URL、ECS id。
  - 允许：返回 repo-relative `source_ref`。

- [ ] O02-03 验证原 `--test_all_meta_path` 语义不变。
  - 内容：Runtime 生成的 `generated_suite.json` 仍是 OSWorld 原生 `domain -> [case_id]` JSON。
  - 验证：用 `test_small` 子集生成 JSON 后，原 runner 能识别。

- [ ] O02-04 验证续跑语义不变。
  - 内容：已有 `result.txt` 的 case 不重复执行。
  - 验证：调用 blackbox / vm_native 脚本中的 `get_unfinished` 相关测试或 smoke。

阶段 2 验证记录：

- 当前 catalog API 只读扫描 JSON 文件，不调用 runner、provider、state lease 或 VM 创建逻辑。
- catalog 响应返回 repo-relative `source_ref`，例如 `evaluation_examples/examples/chrome/<case_id>.json`；不返回本机绝对路径、AK/SK、presigned URL 或 ECS id。

## 阶段 3：和 XUA-Eval 联调

- [x] O03-01 Runtime catalog info 联调。
  - 依赖：XUA-Eval Runtime 启动，`OSWORLD_HOME` 指向本仓库。
  - 验证：`GET /v1/catalog/info` 返回 `framework_key=osworld` 和 `catalog_version`。

- [x] O03-02 Runtime catalog suites 联调。
  - 验证：`GET /v1/catalog/suites` 能返回 `test_small`。

- [x] O03-03 Runtime catalog suite cases 联调。
  - 验证：`GET /v1/catalog/suites/test_small/cases` 能返回真实 case，并带 `domain/external_id/source_hash/source_ref`。

- [ ] O03-04 平台 importer 联调。
  - 验证：XUA-Eval 导入 `test_small` 后，平台 DB 有 suite、case、membership、import job。

- [ ] O03-05 Browser 页面联调。
  - 工具：Browser。
  - 验证：打开 `http://127.0.0.1:5173/suites` 和 `/cases`，能看到从 OSWorld catalog 同步的数据。

阶段 3 验证记录：

- 使用 XUA-Eval Runtime ASGI app，`OSWORLD_HOME=/Users/bytedance/PycharmProjects/test5/osworld`：
  - `/v1/catalog/info` 返回 `framework_key=osworld` 和 `catalog_version=osworld:c38104da628f:...`。
  - `/v1/catalog/suites?keyword=test_small` 返回 total=1，suite_key=`test_small`。
  - `/v1/catalog/suites/test_small/cases?page_size=2` 返回 total=39。

## 阶段 4：最终验收

- [ ] O04-01 OSWorld 全量单测。
  - 验证：`rtk uv run python -m unittest discover -s tests`。

- [ ] O04-02 原 runner help 验证。
  - 验证：
    - `rtk uv run python scripts/python/run_multienv_cua_blackbox.py --help`
    - `rtk uv run python scripts/python/run_multienv_cua_vm_native.py --help`

- [ ] O04-03 文档同步。
  - 文件：
    - [12-suite-case-runtime-contract_zh.md](./12-suite-case-runtime-contract_zh.md)
    - 本文件。
    - `/Users/bytedance/PycharmProjects/work/xua-eval/docs/xua-platform/25-suite-case-management-and-import-design.md`
    - `/Users/bytedance/PycharmProjects/work/xua-eval/docs/xua-platform/26-suite-case-catalog-implementation-checklist.md`
  - 验证：接口、字段、错误码、验证命令一致。

阶段 4 验证记录：

- 待补。

## 每轮收尾模板

```text
完成项：
- [x] Oxx-xx ...

验证：
- 命令：
- 结果：

影响判断：
- 是否影响原 runner：
- 是否影响 evaluation_examples：
- 是否需要平台侧同步修改：
```
