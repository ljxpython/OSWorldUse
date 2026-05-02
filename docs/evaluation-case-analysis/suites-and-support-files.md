# 索引与配置文件说明
这里解释 `evaluation_examples/` 里不是单个 case、但会影响评测选择或运行环境的文件。艹，这些东西要是不分清，后面跑评测时就会把 suite 当任务、把账号配置当 case，纯属给自己挖坑。

## Suite / Index 文件
| 文件 | 作用 | 覆盖条目数 |
| --- | --- | ---: |
| [evaluation_examples/test_all.json](../../evaluation_examples/test_all.json) | Linux/Ubuntu 主任务全集索引。 | 369 |
| [evaluation_examples/test_cua_regression.json](../../evaluation_examples/test_cua_regression.json) | CUA 回归任务索引，当前结构和 `test_infeasible.json` 相同。 | 5 |
| [evaluation_examples/test_infeasible.json](../../evaluation_examples/test_infeasible.json) | 不可行任务集合索引。 | 28 |
| [evaluation_examples/test_nogdrive.json](../../evaluation_examples/test_nogdrive.json) | 排除 Google Drive 相关任务后的索引。 | 361 |
| [evaluation_examples/test_small.json](../../evaluation_examples/test_small.json) | 小规模 smoke/regression 任务索引。 | 39 |
| [evaluation_examples/cua_blackbox/suites/demo_custom_case.json](../../evaluation_examples/cua_blackbox/suites/demo_custom_case.json) | CUA blackbox suite 配置。 | 1 |
| [evaluation_examples/cua_blackbox/suites/regression.json](../../evaluation_examples/cua_blackbox/suites/regression.json) | CUA blackbox suite 配置。 | 5 |

## Settings / Profiles
| 路径 | 作用 |
| --- | --- |
| [evaluation_examples/settings/google/settings.json.template](../../evaluation_examples/settings/google/settings.json.template) | Google 账号配置模板，给需要登录态的浏览器任务使用。 |
| [evaluation_examples/settings/googledrive/settings.yml](../../evaluation_examples/settings/googledrive/settings.yml) | Google Drive/OAuth 相关配置。 |
| [evaluation_examples/settings/thunderbird/settings.json](../../evaluation_examples/settings/thunderbird/settings.json) | Thunderbird 邮件客户端配置。 |
| [evaluation_examples/cua_blackbox/profiles/single_env_vmware.example.json](../../evaluation_examples/cua_blackbox/profiles/single_env_vmware.example.json) | CUA blackbox 单环境 VMware profile 示例。 |

## 和 case 本体的关系
- suite/index 文件只决定“跑哪些 id”，不会定义任务目标、前置动作或评测逻辑。
- settings/profile 文件给运行环境提供账号、代理、虚拟机等外部条件，也不是 case。
- 单个 case 的真实行为仍然以对应 JSON 中的 `instruction`、`config`、`evaluator` 为准。
