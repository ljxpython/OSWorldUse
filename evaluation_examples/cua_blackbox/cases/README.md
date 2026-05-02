# CUA Blackbox Cases

这个目录只放 CUA blackbox 专用 case。

已有 OSWorld case 不要复制到这里，直接在 `suites/*.json` 中引用 `evaluation_examples/examples/<domain>/<case_id>.json`。

如果新增 case 对所有 agent 都适用，应放到 `evaluation_examples/examples/<domain>/`。

当前示例：

- `chrome/cua-demo-open-downloads.json`

这个示例不在默认 regression suite 中，只用于说明 CUA 专用 case 的文件结构。需要执行时使用：

```bash
uv run python scripts/python/validate_cua_regression_cases.py \
  --meta_path evaluation_examples/cua_blackbox/suites/demo_custom_case.json
```
