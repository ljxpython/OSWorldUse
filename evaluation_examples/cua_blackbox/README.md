# CUA Blackbox Evaluation Inputs

这个目录只放 CUA blackbox 接入评测专用输入，不复制 OSWorld 已有 case。

## 目录约定

- `suites/`：CUA 专用 meta 文件，优先引用 `evaluation_examples/examples/<domain>/<case_id>.json` 中的现有 case。
- `cases/`：只放 CUA blackbox 专用 case。通用 benchmark case 仍应放到 `evaluation_examples/examples/<domain>/`。
- `profiles/`：运行参数模板，不放密钥，不放本机私有路径。

## 当前入口

- 推荐回归 suite：`suites/regression.json`
- 兼容旧入口：`../test_cua_regression.json`
- CUA 专用 case 示例：`cases/chrome/cua-demo-open-downloads.json`
- CUA 专用 case 示例 suite：`suites/demo_custom_case.json`

短期内 `suites/regression.json` 和 `../test_cua_regression.json` 应保持内容一致。

## 新增 Case 方法

优先判断 case 类型：

- 通用 benchmark case：放到 `evaluation_examples/examples/<domain>/<case_id>.json`。
- CUA blackbox 专用 case：放到 `evaluation_examples/cua_blackbox/cases/<domain>/<case_id>.json`。

新增 CUA 专用 case 后，把 `<case_id>` 加入 `suites/*.json`。

示例：

```json
{
  "chrome": [
    "cua-demo-open-downloads"
  ]
}
```

验证：

```bash
uv run python scripts/python/validate_cua_regression_cases.py \
  --meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json
```

单任务运行：

```bash
uv run python scripts/python/run_multienv_cua_blackbox.py \
  --test_all_meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json \
  --domain chrome \
  --example_id cua-demo-open-downloads \
  --num_envs 1
```
