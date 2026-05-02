# CUA Blackbox Evaluation Inputs

这个目录只放 CUA blackbox 接入评测专用输入，不复制 OSWorld 已有 case。

## 目录约定

- `suites/`：CUA 专用 meta 文件，优先引用 `evaluation_examples/examples/<domain>/<case_id>.json` 中的现有 case。
- `cases/`：只放 CUA blackbox 专用 case。通用 benchmark case 仍应放到 `evaluation_examples/examples/<domain>/`。
- `profiles/`：运行参数模板，不放密钥，不放本机私有路径。

## 当前入口

- 推荐回归 suite：`suites/regression.json`
- 兼容旧入口：`../test_cua_regression.json`

短期内 `suites/regression.json` 和 `../test_cua_regression.json` 应保持内容一致。
