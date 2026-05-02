# CUA Blackbox 测试输入与报告展示规划

日期：2026-05-02

## 1. 目标

本规划解决两个问题：

1. CUA blackbox 相关测试输入放在哪里，怎么命名，怎么复用 OSWorld 现有用例。
2. 测试报告如何从“给机器看的 JSON/CSV”升级成“给人看的验收报告”。

当前原则是不重构主链路，不改变 OSWorld 原生 evaluator，不修改 `CUA` 源码。

---

## 2. 测试输入目录规范

### 2.1 现有用例继续复用

现有 OSWorld benchmark 用例继续复用：

- `evaluation_examples/examples/<domain>/<case_id>.json`
- `evaluation_examples/test_all.json`
- `evaluation_examples/test_small.json`
- 现有自定义 meta 文件

CUA blackbox runner 仍然通过 `--test_all_meta_path`、`--domain`、`--example_id` 读取这些用例。

不要为了 CUA 复制一份已有 case。复制会造成 evaluator、snapshot、config 漂移，后续维护会很恶心。

### 2.2 新增 CUA 专用输入目录

如果未来新增的是 CUA blackbox 专用回归集合、验收集合、临时实验集合或 CUA 专用 case，统一放到：

```text
evaluation_examples/cua_blackbox/
```

建议结构：

```text
evaluation_examples/cua_blackbox/
  README.md
  suites/
    regression.json
    smoke.json
    upgrade.json
  cases/
    <domain>/
      <case_id>.json
  profiles/
    single_env_vmware.example.json
```

说明：

- `suites/` 放 meta 文件，只引用已有 `evaluation_examples/examples/<domain>/<case_id>.json`。
- `profiles/` 放运行参数模板，不放密钥，不放本机私有路径。
- 已有 OSWorld case 不复制到 `evaluation_examples/cua_blackbox/`。
- 新增通用 benchmark case 仍放到 `evaluation_examples/examples/<domain>/`。
- 新增 CUA blackbox 专用 case 可以放到 `evaluation_examples/cua_blackbox/cases/<domain>/<case_id>.json`。
- runner 和 validation 会优先读取 `evaluation_examples/examples/`，找不到时再读取 `evaluation_examples/cua_blackbox/cases/`。

### 2.3 兼容策略

当前已有：

```text
evaluation_examples/test_cua_regression.json
```

后续建议新增：

```text
evaluation_examples/cua_blackbox/suites/regression.json
```

短期保留旧路径兼容，脚本默认可以逐步迁移到新路径。迁移时必须满足：

- 旧路径命令仍能运行。
- 新路径命令能通过 `validate_cua_regression_cases.py`。
- 文档示例统一使用新路径。
- 如果两个文件短期共存，内容必须一致或明确说明差异。

---

## 3. 统一报告生成器

### 3.1 目标

新增统一报告生成器：

```text
scripts/python/build_cua_blackbox_report.py
```

它不替代现有 JSON/CSV，而是在现有产物之上生成更适合人阅读的报告。

输入包括：

- `summary/summary.json`
- `summary/domain_summary.json`
- `summary/failure_summary.json`
- `cua_smoke_report.json`
- `functional_report.json`
- `compatibility_report.json`
- `case_acceptance_report.json`
- `run_meta.json`
- `cua_meta.json`

输出建议：

```text
report/
  index.html
  report.md
  report.json
```

### 3.2 报告内容

报告至少包含：

- 总览：通过/失败、总任务数、得分任务数、失败任务数、pending 数、平均分。
- 环境：CUA version、adapter version、bridge protocol、eval profile、provider、screen size。
- 测试矩阵：SMK / TP 覆盖和通过情况。
- Domain 汇总：每个 domain 的 total/scored/failed/pending/average。
- 失败分类：按 `failure_type` 聚合，列出代表性 task。
- Case 验收：静态检查、环境 reset、初始 evaluate、blackbox 单跑结果。
- 兼容性：CUA CLI、config、openclaw、hash 元数据。
- Artifacts：重要文件和目录链接，例如录屏、日志、截图、summary。
- 验收结论：是否可以进入下一阶段；如果不通过，列出阻塞项。

### 3.3 输出格式

第一阶段优先输出：

- `report.json`：统一聚合数据，给后续 Web 展示复用。
- `report.md`：适合贴到 PR、飞书、文档。
- `index.html`：单文件静态 HTML，方便直接发给别人看。

HTML 第一版不引入前端框架，不依赖外部 CDN，避免离线环境打不开。样式可以内嵌 CSS，重点是结构清楚、表格可读、失败项醒目。

---

## 4. 未来 Web 展示

统一报告生成器落地后，再考虑 Web 展示脚本：

```text
scripts/python/serve_cua_blackbox_report.py
```

目标：

- 本地启动一个只读 HTTP server。
- 自动定位一个或多个 result root。
- 用 Web 页面展示报告、summary、日志和 artifacts。
- 支持按任务、domain、failure type 过滤。

建议不要第一版就做复杂 Web 服务。先把 `report.json` 的结构做稳定，再基于它做 Web 展示，否则前端页面会跟底层报告结构互相拖后腿。

---

## 5. 任务清单

### 5.1 测试输入规范

- [x] 新建 `evaluation_examples/cua_blackbox/README.md`
- [x] 新建 `evaluation_examples/cua_blackbox/suites/`
- [x] 新建 `evaluation_examples/cua_blackbox/cases/`
- [x] 新建 `evaluation_examples/cua_blackbox/profiles/`
- [x] 新建 `evaluation_examples/cua_blackbox/suites/regression.json`
- [x] 保留 `evaluation_examples/test_cua_regression.json` 兼容入口
- [x] 更新脚本默认路径或支持新旧路径自动兼容
- [x] 更新所有文档示例为新目录优先

### 5.2 统一报告生成器

- [x] 新增 `scripts/python/build_cua_blackbox_report.py`
- [x] 支持从 blackbox result root 读取 summary
- [x] 支持读取 smoke / functional / compatibility / case acceptance report
- [x] 输出 `report/report.json`
- [x] 输出 `report/report.md`
- [x] 输出 `report/index.html`
- [x] 报告中展示总体结论、domain 汇总、失败分类和 artifacts 链接
- [x] 在 `build_cua_blackbox_summary.py` 或 blackbox runner 结束后可选触发报告生成

### 5.3 Web 展示

- [x] 等 `report.json` 稳定后，再设计 `serve_cua_blackbox_report.py`
- [x] 支持本地浏览器查看报告
- [x] 支持多个 result root 切换
- [x] 支持按 domain / task / failure type 过滤
- [x] 保持只读，不修改评测结果目录

---

## 6. 验收点

测试输入规范通过标准：

- 新目录存在且 README 说明清楚。
- 新旧 regression suite 都能被 case validation 脚本识别。
- 现有回归任务不被复制，不产生 evaluator 分叉。

统一报告生成器通过标准：

- 给一个已有 result root，可以生成 `report.json`、`report.md`、`index.html`。
- `report.md` 能直接阅读，不需要看原始 JSON。
- `index.html` 能离线打开，核心表格可读。
- 失败任务能从报告跳转或定位到对应日志、录屏、截图目录。

Web 展示通过标准：

- 启动脚本后能在浏览器查看报告。
- 不依赖外部服务。
- 不修改原始结果文件。
