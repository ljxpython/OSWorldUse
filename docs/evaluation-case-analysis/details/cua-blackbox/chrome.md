# CUA blackbox 自定义任务集 / chrome 详细 case 分析
来源目录：`evaluation_examples/cua_blackbox/cases/chrome/`。本文件覆盖 1 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## cua-demo-open-downloads
- 源 JSON：[evaluation_examples/cua_blackbox/cases/chrome/cua-demo-open-downloads.json](../../../../evaluation_examples/cua_blackbox/cases/chrome/cua-demo-open-downloads.json)
- 平台/集合：CUA blackbox 自定义任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：cua_blackbox_demo_case
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab_approximate`

**Agent 要做什么**
Open Chrome's downloads page. Navigate to chrome://downloads and stop there.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_active_tab_approximate`。近似检查 Chrome 当前活动标签页/URL。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": ""}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "chrome://downloads/"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
