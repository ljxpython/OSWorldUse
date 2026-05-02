# CUA blackbox 自定义任务集 Case 清单
来源目录：`evaluation_examples/cua_blackbox/cases/`。本文件列出 1 个 case。

每条记录格式：`id`、源 JSON、任务、相关应用、前置动作、评测函数。任务字段保留原始 `instruction`，这是最不容易胡说八道的做法。

## chrome（1 个）
- `cua-demo-open-downloads` ([JSON](../../evaluation_examples/cua_blackbox/cases/chrome/cua-demo-open-downloads.json))：任务：Open Chrome's downloads page. Navigate to chrome://downloads and stop there.；应用：chrome；前置：launch -> launch；评测：is_expected_active_tab_approximate；环境变化风险：low.
