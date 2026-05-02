# Linux/Ubuntu 主任务集 / chrome 详细 case 分析
来源目录：`evaluation_examples/examples/chrome/`。本文件覆盖 46 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 030eeff7-b492-4218-b312-701ec99ee0cc
- 源 JSON：[evaluation_examples/examples/chrome/030eeff7-b492-4218-b312-701ec99ee0cc.json](../../../../evaluation_examples/examples/chrome/030eeff7-b492-4218-b312-701ec99ee0cc.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.surreycc.gov.uk/website/cookies/do-not-track
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`exact_match`

**Agent 要做什么**
Can you enable the 'Do Not Track' feature in Chrome to enhance my online privacy?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`enable_do_not_track` 状态 `{"type": "enable_do_not_track"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`exact_match`。实际值必须与规则中的期望值精确一致。
  - 实际结果 `enable_do_not_track`：读取 Chrome Do Not Track 设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "true"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 06fe7178-4491-4589-810f-2e2bc9502122
- 源 JSON：[evaluation_examples/examples/chrome/06fe7178-4491-4589-810f-2e2bc9502122.json](../../../../evaluation_examples/examples/chrome/06fe7178-4491-4589-810f-2e2bc9502122.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.wikihow.com/Switch-Tabs-in-Chrome
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_tabs`

**Agent 要做什么**
Can you make my computer bring back the last tab I shut down?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.lonelyplanet.com`, `https://www.airbnb.com`, `https://www.tripadvisor.com`
- 4. `chrome_close_tabs`：关闭指定 Chrome 标签页。 关闭标签页配置 `{"urls_to_close": ["https://www.tripadvisor.com"]}`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`open_tabs_info` 状态 `{"type": "open_tabs_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_tabs`。检查 Chrome 打开的标签页集合。
  - 实际结果 `open_tabs_info`：读取 Chrome 当前打开的标签页列表。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "urls": ["https://www.lonelyplanet.com", "https://www.airbnb.com", "https://www.tripadvisor.com"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 0d8b7de3-e8de-4d86-b9fd-dd2dce58a217
- 源 JSON：[evaluation_examples/examples/chrome/0d8b7de3-e8de-4d86-b9fd-dd2dce58a217.json](../../../../evaluation_examples/examples/chrome/0d8b7de3-e8de-4d86-b9fd-dd2dce58a217.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab + is_expected_active_tab`

**Agent 要做什么**
Browse the natural products database.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://drugs.com`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`；`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`or`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_active_tab`。检查 Chrome 当前活动标签页是否符合规则。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://www.drugs.com/npc/"}`。
  - 选项/规则：无额外 options。
- Metric 2：`is_expected_active_tab`。检查 Chrome 当前活动标签页是否符合规则。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://www.drugs.com/npp/"}`。
  - 选项/规则：无额外 options。
- 通过条件：任一 metric 通过即可整体通过。

## 12086550-11c0-466b-b367-1d9e75b3910e
- 源 JSON：[evaluation_examples/examples/chrome/12086550-11c0-466b-b367-1d9e75b3910e.json](../../../../evaluation_examples/examples/chrome/12086550-11c0-466b-b367-1d9e75b3910e.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.quora.com/What-are-the-cool-tricks-to-use-Google-Chrome
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab_approximate`

**Agent 要做什么**
Computer, please navigate to the area in my browser settings where my passwords are stored. I want to check my login information for Etsy without revealing it just yet.

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
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "chrome://password-manager/passwords"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 121ba48f-9e17-48ce-9bc6-a4fb17a7ebba
- 源 JSON：[evaluation_examples/examples/chrome/121ba48f-9e17-48ce-9bc6-a4fb17a7ebba.json](../../../../evaluation_examples/examples/chrome/121ba48f-9e17-48ce-9bc6-a4fb17a7ebba.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_added_to_steam_cart`

**Agent 要做什么**
Find Dota 2 game and add all DLC to cart.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.dota2.com/home`, `https://store.steampowered.com`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`page_info` 状态 `{"type": "page_info", "url": "https://store.steampowered.com/cart/"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_added_to_steam_cart`。检查 Steam 购物车状态。
  - 实际结果 `page_info`：读取页面信息。；其他参数=`{"url": "https://store.steampowered.com/cart/"}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"items": ["The Dota 2 Official Soundtrack"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 1704f00f-79e6-43a7-961b-cedd3724d5fd
- 源 JSON：[evaluation_examples/examples/chrome/1704f00f-79e6-43a7-961b-cedd3724d5fd.json](../../../../evaluation_examples/examples/chrome/1704f00f-79e6-43a7-961b-cedd3724d5fd.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_0
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`medium`
- 评测函数：`check_direct_json_object + check_direct_json_object`

**Agent 要做什么**
Find a large car from next Monday to Friday in Zurich, sorted by price.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.rentalcars.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["locationName", "dropLocationName", "filterCriteria_carCategory", "filterCriteria_sortBy"], "type": "active_tab_url_parse"}`；`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["puDay", "puMonth", "puYear", "doDay", "doMonth", "doYear"], "type": "active_tab_url_parse"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["locationName", "dropLocationName", "filterCriteria_carCategory", "filterCriteria_sortBy"]}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"dropLocationName": "Zürich", "filterCriteria_carCategory": "large", "filterCriteria_sortBy": "PRICE", "locationName": "Zürich"}}`。
  - 选项/规则：无额外 options。
- Metric 2：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["puDay", "puMonth", "puYear", "doDay", "doMonth", "doYear"]}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"doDay": "{DayD}", "doMonth": "{MonthD}", "doYear": "{Year}", "puDay": "{DayD}", "puMonth": "{MonthD}", "puYear": "{Year}"}, "relativeTime": {"from": "next Monday split", "to": "next Friday split"}, "timezone": "Europe/Zurich"}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 2888b4e6-5b47-4b57-8bf5-c73827890774
- 源 JSON：[evaluation_examples/examples/chrome/2888b4e6-5b47-4b57-8bf5-c73827890774.json](../../../../evaluation_examples/examples/chrome/2888b4e6-5b47-4b57-8bf5-c73827890774.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`medium`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Show me all men's large-size short-sleeve shirts with a discount of 50% or more.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.macys.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`url_path_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["mens_clothing", "shirts", "Men_regular_size_t", "Price_discount_range", "short_sleeve"], "type": "url_path_parse"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `url_path_parse`：解析 URL path。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["mens_clothing", "shirts", "Men_regular_size_t", "Price_discount_range", "short_sleeve"]}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"Men_regular_size_t": "L", "Price_discount_range": "50_PERCENT_ off & more", "mens_clothing": true, "shirts": true, "short_sleeve": true}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 2ad9387a-65d8-4e33-ad5b-7580065a27ca
- 源 JSON：[evaluation_examples/examples/chrome/2ad9387a-65d8-4e33-ad5b-7580065a27ca.json](../../../../evaluation_examples/examples/chrome/2ad9387a-65d8-4e33-ad5b-7580065a27ca.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.youtube.com/watch?v=IN-Eq_UripQ
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_bookmarks`

**Agent 要做什么**
Can you make a new folder for me on the bookmarks bar in my internet browser? Let's call it 'Favorites.'

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`bookmarks` 状态 `{"type": "bookmarks"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`is_expected_bookmarks`。检查 Chrome 书签状态。
  - 实际结果 `bookmarks`：读取 Chrome 书签状态。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"names": ["Favorites"], "type": "bookmark_bar_folders_names"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 2ae9ba84-3a0d-4d4c-8338-3a1478dc5fe3
- 源 JSON：[evaluation_examples/examples/chrome/2ae9ba84-3a0d-4d4c-8338-3a1478dc5fe3.json](../../../../evaluation_examples/examples/chrome/2ae9ba84-3a0d-4d4c-8338-3a1478dc5fe3.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://superuser.com/questions/1393683/how-to-change-the-username-in-google-chrome-profiles?rq=1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`exact_match`

**Agent 要做什么**
Lately I have changed my English name to Thomas. I want to update my username. Could you help me change the username in chrome profiles to Thomas?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`profile_name` 状态 `{"type": "profile_name"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`exact_match`。实际值必须与规则中的期望值精确一致。
  - 实际结果 `profile_name`：读取 Chrome profile 名称。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "Thomas"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 3299584d-8f11-4457-bf4c-ce98f7600250
- 源 JSON：[evaluation_examples/examples/chrome/3299584d-8f11-4457-bf4c-ce98f7600250.json](../../../../evaluation_examples/examples/chrome/3299584d-8f11-4457-bf4c-ce98f7600250.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.reddit.com/r/techsupport/comments/12zwymy/comment/jhtri65/?utm_source=share&utm_medium=web2x&context=3
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`exact_match`

**Agent 要做什么**
On my surface pro whenever I launch Chrome it always opens "funbrain.com." I don't want this. I cleared my cache but it still happens. What should I do?

**前置/初始状态**
- 1. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `echo {CLIENT_PASSWORD} | sudo -S apt update -y && echo {CLIENT_PASSWORD} | sudo -S apt install jq -y`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `cd /home/user/.config/google-chrome/Default && jq '. + {"session":{"restore_on_startup":4, "startup_urls":["http://funbrain.com/"]}}' Preferences > temp && mv temp Preferences`；shell=True
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 4. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`new_startup_page` 状态 `{"type": "new_startup_page"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`exact_match`。实际值必须与规则中的期望值精确一致。
  - 实际结果 `new_startup_page`：读取 Chrome 启动页设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "true"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 35253b65-1c19-4304-8aa4-6884b8218fc0
- 源 JSON：[evaluation_examples/examples/chrome/35253b65-1c19-4304-8aa4-6884b8218fc0.json](../../../../evaluation_examples/examples/chrome/35253b65-1c19-4304-8aa4-6884b8218fc0.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.laptopmag.com/articles/how-to-create-desktop-shortcuts-for-web-pages-using-chrome
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_shortcut_on_desktop`

**Agent 要做什么**
Hey, I need a quick way back to this site. Could you whip up a shortcut on my desktop for me using Chrome's built-in feature?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.mathsisfun.com/games/2048.html`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`shortcuts_on_desktop` 状态 `{"type": "shortcuts_on_desktop"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_shortcut_on_desktop`。检查桌面快捷方式是否创建。
  - 实际结果 `shortcuts_on_desktop`：读取桌面快捷方式状态。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"name": "Play Puzzle Game 2048", "type": "name"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 368d9ba4-203c-40c1-9fa3-da2f1430ce63
- 源 JSON：[evaluation_examples/examples/chrome/368d9ba4-203c-40c1-9fa3-da2f1430ce63.json](../../../../evaluation_examples/examples/chrome/368d9ba4-203c-40c1-9fa3-da2f1430ce63.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object + is_expected_url_pattern_match`

**Agent 要做什么**
Find the Monthly forecast for Manchester, GB for this month

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.accuweather.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`url_dashPart` 状态 `{"goto_prefix": "https://www.", "key": "time", "needDeleteId": false, "partIndex": -2, "returnType": "json", "type": "url_dashPart"}`；`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `url_dashPart`：解析 URL 片段。；其他参数=`{"goto_prefix": "https://www.", "key": "time", "needDeleteId": false, "partIndex": -2, "returnType": "json"}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"time": "{month}-weather"}, "relativeTime": {"from": "this month"}}`。
  - 选项/规则：无额外 options。
- Metric 2：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["/manchester/"]}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 3720f614-37fd-4d04-8a6b-76f54f8c222d
- 源 JSON：[evaluation_examples/examples/chrome/3720f614-37fd-4d04-8a6b-76f54f8c222d.json](../../../../evaluation_examples/examples/chrome/3720f614-37fd-4d04-8a6b-76f54f8c222d.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://superuser.com/questions/984668/change-interface-language-of-chrome-to-english
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
I am from the country of Atlantis, and my mother tongue is Xenothian. Please change the Google Chrome interface language to Xenothian using only Chrome’s built-in settings.

**前置/初始状态**
- 无显式前置动作；任务从对应 snapshot 的默认环境开始。

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## 44ee5668-ecd5-4366-a6ce-c1c9b8d4e938
- 源 JSON：[evaluation_examples/examples/chrome/44ee5668-ecd5-4366-a6ce-c1c9b8d4e938.json](../../../../evaluation_examples/examples/chrome/44ee5668-ecd5-4366-a6ce-c1c9b8d4e938.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://superuser.com/questions/1787991/clear-browsing-history-from-specific-site-on-chrome
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_history_deleted`

**Agent 要做什么**
I am looking for an website address I accessed a month ago, but Youtube websites which take almost all of my browsing history are interrupting my search. This is too annoying. I want to remove all my Youtube browsing history first to facilitate my search. Could you help me clear browsing history from Youtube?

**前置/初始状态**
- 1. `update_browse_history`：预置 Chrome 浏览历史。 写入浏览历史 `{"history": [{"title": "Rick Astley - Never Gonna Give You Up (Official Music Video)", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "visit_time_from_now_in_seconds": 3600}, {"title": "PSY - GANGNAM STYLE(강남스타일) M/V", "url": "https://www.youtube.com/watch?v=9bZkp7q19f0", "visit_time_from_now_in_seconds": 1631}, {"title": "Maroon 5 - Sugar (Official Music Video)", "url": "https://www.youtube.com/watch?v=3tmd-ClpJxA", "visit_time_from_now_in_seconds": 900}, {"title": "The New York Times", "url": "https://w...`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`history` 状态 `{"dest": "history.sqlite", "type": "history"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`check_history_deleted`。检查指定浏览历史是否被删除。
  - 实际结果 `history`：读取 Chrome 浏览历史。；dest=`history.sqlite`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"keywords": ["youtube"], "type": "keywords"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 47543840-672a-467d-80df-8f7c3b9788c9
- 源 JSON：[evaluation_examples/examples/chrome/47543840-672a-467d-80df-8f7c3b9788c9.json](../../../../evaluation_examples/examples/chrome/47543840-672a-467d-80df-8f7c3b9788c9.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match + check_direct_json_object + check_direct_json_object`

**Agent 要做什么**
On the current website, show me the cars available for pickup at Boston Logan Intl Airport from the 10th to the 11th of next month, sorted by the number of seats to find the largest capacity.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.budget.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`；`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject": {"day-time-info": {"0": "from", "1": "to"}, "location-info": {"0": "start_location", "1": "end_location"}}, "class_singleObject": {}, ...`；`active_tab_html_parse` 状态 `{"category": "xpath", "goto_prefix": "https://www.", "type": "active_tab_html_parse", "xpathObject": {"/html/body/div[6]/div[2]/div[1]/div/div/div[2]/section[1]/div[1]/form/div[...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 3 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["reservation#/vehicles"]}`。
  - 选项/规则：无额外 options。
- Metric 2：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject": {"day-time-info": {"0": "from", "1": "to"}, "location-info": {"0": "start_location", "1": "end_location"}}, "class_singleObject": {}, "goto_prefix": "https://www."}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"end_location": "Boston Logan Intl Airport,\n\t\t\t\t\t\t\t\tBOS", "from": "{DoW}, {Month} {Day0D}, 12:00 PM", "start_location": "Boston Logan Intl Airport,\n\t\t\t\t\t\t\t\tBOS \n\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t \n\t\t\t\t\t\t\t \n\t\t\t\...`。
  - 选项/规则：无额外 options。
- Metric 3：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "xpath", "goto_prefix": "https://www.", "xpathObject": {"/html/body/div[6]/div[2]/div[1]/div/div/div[2]/section[1]/div[1]/form/div[1]/div[1]/div[2]/div/a": "rank"}}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"rank": "Number of Seats (High to Low)"}}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 480bcfea-d68f-4aaa-a0a9-2589ef319381
- 源 JSON：[evaluation_examples/examples/chrome/480bcfea-d68f-4aaa-a0a9-2589ef319381.json](../../../../evaluation_examples/examples/chrome/480bcfea-d68f-4aaa-a0a9-2589ef319381.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://bugartisan.medium.com/disable-the-new-chrome-ui-round-in-2023-db168271f71e
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
I do not like the design of the new 2023 chrome UI. I want to keep using the original one. Can you disable the new 2023 version chrome UI for me?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## 59155008-fe71-45ec-8a8f-dc35497b6aa8
- 源 JSON：[evaluation_examples/examples/chrome/59155008-fe71-45ec-8a8f-dc35497b6aa8.json](../../../../evaluation_examples/examples/chrome/59155008-fe71-45ec-8a8f-dc35497b6aa8.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab`

**Agent 要做什么**
What are the similar names to the name carl

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.babycenter.com/child`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_active_tab`。检查 Chrome 当前活动标签页是否符合规则。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://www.babycenter.com/baby-names/details/carl-853"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 6766f2b8-8a72-417f-a9e5-56fcaa735837
- 源 JSON：[evaluation_examples/examples/chrome/6766f2b8-8a72-417f-a9e5-56fcaa735837.json](../../../../evaluation_examples/examples/chrome/6766f2b8-8a72-417f-a9e5-56fcaa735837.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://support.google.com/chrome/thread/205881926/it-s-possible-to-load-unpacked-extension-automatically-in-chrome?hl=en
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_in_list`

**Agent 要做什么**
Could you help me unzip the downloaded extension file from /home/user/Desktop/ to /home/user/Desktop/ and configure it in Chrome's extensions?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `helloExtension.zip` 到 `/home/user/Desktop/helloExtension.zip`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `echo {CLIENT_PASSWORD} | sudo -S apt-get update -y && echo {CLIENT_PASSWORD} | sudo -S apt-get install unzip -y && unzip /home/user/Desktop/helloExtension.zip -d /home/user/Desktop/ && rm /home/user/Desktop/helloExtension.zip`；shell=True
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 4. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`find_unpacked_extension_path` 状态 `{"type": "find_unpacked_extension_path"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_in_list`。实际值必须出现在期望列表或规则集合中。
  - 实际结果 `find_unpacked_extension_path`：查找解压后的 Chrome 扩展目录。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "/home/user/Desktop/helloExtension"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 6c4c23a1-42a4-43cc-9db1-2f86ff3738cc
- 源 JSON：[evaluation_examples/examples/chrome/6c4c23a1-42a4-43cc-9db1-2f86ff3738cc.json](../../../../evaluation_examples/examples/chrome/6c4c23a1-42a4-43cc-9db1-2f86ff3738cc.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Find flights from Seattle to New York on 5th next month and only show those that can be purchased with miles.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.delta.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject_child": {"mach-flight-context-info__wrapper__info--separator": {"0": "start", "1": "end"}}, "class_singleObject": {"mach-flight-context-...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject_child": {"mach-flight-context-info__wrapper__info--separator": {"0": "start", "1": "end"}}, "class_singleObject": {"mach-flight-context-info__wrapper--date": "time", "mach-global-tabs-small__wrapper__tab--active": "category"}, "goto_prefix": "https://www."}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"category": "Miles", "end": "NYC", "start": "SEA", "time": "{DoW}, {Month} {Day0D}, {Year}"}, "relativeTime": {"from": "5th next month"}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7a5a7856-f1b6-42a4-ade9-1ca81ca0f263
- 源 JSON：[evaluation_examples/examples/chrome/7a5a7856-f1b6-42a4-ade9-1ca81ca0f263.json](../../../../evaluation_examples/examples/chrome/7a5a7856-f1b6-42a4-ade9-1ca81ca0f263.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.youtube.com/watch?v=ZaZ8GcTxjXA
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_bookmarks`

**Agent 要做什么**
Can you save this webpage I'm looking at to bookmarks bar so I can come back to it later?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://blog.eleuther.ai/rotary-embeddings/`, `https://jalammar.github.io/illustrated-transformer/`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`bookmarks` 状态 `{"type": "bookmarks"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`is_expected_bookmarks`。检查 Chrome 书签状态。
  - 实际结果 `bookmarks`：读取 Chrome 书签状态。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "bookmark_bar_websites_urls", "urls": ["https://jalammar.github.io/illustrated-transformer/"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7b6c7e24-c58a-49fc-a5bb-d57b80e5b4c3
- 源 JSON：[evaluation_examples/examples/chrome/7b6c7e24-c58a-49fc-a5bb-d57b80e5b4c3.json](../../../../evaluation_examples/examples/chrome/7b6c7e24-c58a-49fc-a5bb-d57b80e5b4c3.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://support.google.com/chrome/answer/95647?hl=en&ref_topic=7438325&sjid=16867045591165135686-AP#zippy=%2Cdelete-cookies-from-a-site
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_cookie_deleted`

**Agent 要做什么**
Can you help me clean up my computer by getting rid of all the tracking things that Amazon might have saved? I want to make sure my browsing is private and those sites don't remember me.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.amazon.com`, `https://www.amazon.com/s?k=huggingface+transformers+book`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`cookie_data` 状态 `{"dest": "Cookies", "type": "cookie_data"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`is_cookie_deleted`。检查指定 cookie 是否被删除。
  - 实际结果 `cookie_data`：读取 Chrome cookie 状态。；dest=`Cookies`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"domains": [".amazon.com"], "type": "domains"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7f52cab9-535c-4835-ac8c-391ee64dc930
- 源 JSON：[evaluation_examples/examples/chrome/7f52cab9-535c-4835-ac8c-391ee64dc930.json](../../../../evaluation_examples/examples/chrome/7f52cab9-535c-4835-ac8c-391ee64dc930.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object + check_direct_json_object`

**Agent 要做什么**
Create a list of drip coffee makers that are on sale and within $25-60 and have a black finish.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://shopping.google.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["q"], "type": "active_tab_url_parse"}`；`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject_search_exist": {"fT28tf": ["Black", "$25 - $60", "On sale", "is_other_exist"]}, "goto_prefix": "https://www.", "type": "active_tab_html_...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["q"]}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect_in_result": true, "expected": {"q": "drip coffee maker"}}`。
  - 选项/规则：无额外 options。
- Metric 2：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject_search_exist": {"fT28tf": ["Black", "$25 - $60", "On sale", "is_other_exist"]}, "goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"$25 - $60": true, "Black": true, "On sale": true, "is_other_exist": false}}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 82279c77-8fc6-46f6-9622-3ba96f61b477
- 源 JSON：[evaluation_examples/examples/chrome/82279c77-8fc6-46f6-9622-3ba96f61b477.json](../../../../evaluation_examples/examples/chrome/82279c77-8fc6-46f6-9622-3ba96f61b477.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Find electric cars with a maximum price of $50,000 within 50 miles of 10001.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.cars.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["list_price_max", "maximum_distance", "zip", "fuel_slugs[]"], "type": "active_tab_url_parse"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["list_price_max", "maximum_distance", "zip", "fuel_slugs[]"]}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"fuel_slugs[]": "electric", "list_price_max": "50000", "maximum_distance": "50", "zip": "10001"}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 82bc8d6a-36eb-4d2d-8801-ef714fb1e55a
- 源 JSON：[evaluation_examples/examples/chrome/82bc8d6a-36eb-4d2d-8801-ef714fb1e55a.json](../../../../evaluation_examples/examples/chrome/82bc8d6a-36eb-4d2d-8801-ef714fb1e55a.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
On next Monday, look up a flight from Mumbai to Stockholm.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.qatarairways.com/en-hk/homepage.html`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["fromStation", "toStation", "departing"], "replace": {"departing": "time"}, "type": "active_tab_url_parse"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["fromStation", "toStation", "departing"], "replace": {"departing": "time"}}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expect_in_result": true, "expected": {"fromStation": ["BOM"], "time": ["{Year}-{Month0D}-{Day0D}"], "toStation": ["STO", "ARN"]}, "relativeTime": {"from": "next Monday"}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 93eabf48-6a27-4cb6-b963-7d5fe1e0d3a9
- 源 JSON：[evaluation_examples/examples/chrome/93eabf48-6a27-4cb6-b963-7d5fe1e0d3a9.json](../../../../evaluation_examples/examples/chrome/93eabf48-6a27-4cb6-b963-7d5fe1e0d3a9.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://superuser.com/questions/1417973/how-to-disable-google-chrome-dark-mode
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`match_in_list + is_expected_url_pattern_match`

**Agent 要做什么**
Could you assist me in turning off the dark mode feature in Google Chrome? I've noticed that while dark mode is great for reducing glare, it actually makes it more challenging for me to read text clearly, especially with my astigmatism.

**前置/初始状态**
- 1. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `mkdir -p /home/user/.config/google-chrome/Default && if [ ! -f /home/user/.config/google-chrome/Default/Preferences ]; then echo '{}' > /home/user/.config/google-chrome/Default/Preferences; fi && python3 -c "import json; p='/home/user/.config/google-chrome/Default/Preferences'; d=json.load(open(p)); d.setdefault('browser', {}).setdefault('theme', {})['col...`；shell=True
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`chrome_appearance_mode_ui` 状态 `{"type": "chrome_appearance_mode_ui"}`；`active_url_from_accessTree` 状态 `{"goto_prefix": "", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 2 个 metric。
- 评测前收尾动作：
  - 1. `sleep`：等待界面或后台状态稳定。 等待 1 秒
- Metric 1：`match_in_list`。实际值必须命中期望列表。
  - 实际结果 `chrome_appearance_mode_ui`：读取 Chrome 外观模式。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["light", "system"]}`。
  - 选项/规则：无额外 options。
- Metric 2：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": ""}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["^chrome://settings/appearance/?$"]}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 9656a811-9b5b-4ddf-99c7-5117bcef0626
- 源 JSON：[evaluation_examples/examples/chrome/9656a811-9b5b-4ddf-99c7-5117bcef0626.json](../../../../evaluation_examples/examples/chrome/9656a811-9b5b-4ddf-99c7-5117bcef0626.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.quora.com/How-do-I-set-the-security-settings-for-the-Google-Chrome-browser-for-the-best-security#:~:text=Enable%20Safe%20Browsing:%20Chrome%20has%20a%20built%2Din,Security%20%3E%20Security%20%3E%20Enable%20Safe%20Browsing.
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`exact_match`

**Agent 要做什么**
I want Chrome to warn me whenever I visit a potentially harmful or unsafe website. Can you enable this safety feature?

**前置/初始状态**
- 1. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `echo {CLIENT_PASSWORD} | sudo -S apt update -y && echo {CLIENT_PASSWORD} | sudo -S apt install jq -y`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `mkdir -p /home/user/.config/google-chrome/Default && if [ ! -f /home/user/.config/google-chrome/Default/Preferences ]; then echo '{}' > /home/user/.config/google-chrome/Default/Preferences; fi && cd /home/user/.config/google-chrome/Default && jq '. + {"safebrowsing":{"enabled":false,"enhanced":false}}' Preferences > temp && mv temp Preferences`；shell=True
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 4. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`enable_safe_browsing` 状态 `{"type": "enable_safe_browsing"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`exact_match`。实际值必须与规则中的期望值精确一致。
  - 实际结果 `enable_safe_browsing`：读取 Chrome 安全浏览设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "true"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 99146c54-4f37-4ab8-9327-5f3291665e1e
- 源 JSON：[evaluation_examples/examples/chrome/99146c54-4f37-4ab8-9327-5f3291665e1e.json](../../../../evaluation_examples/examples/chrome/99146c54-4f37-4ab8-9327-5f3291665e1e.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.youtube.com/watch?v=v0kxqB7Xa6I
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`exact_match`

**Agent 要做什么**
Please help me set Chrome to delete my browsing data automatically every time I close the browser.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`data_delete_automacally` 状态 `{"type": "data_delete_automacally"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`exact_match`。实际值必须与规则中的期望值精确一致。
  - 实际结果 `data_delete_automacally`：读取关闭浏览器时自动删除数据设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": "true"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9f3f70fc-5afc-4958-a7b7-3bb4fcb01805
- 源 JSON：[evaluation_examples/examples/chrome/9f3f70fc-5afc-4958-a7b7-3bb4fcb01805.json](../../../../evaluation_examples/examples/chrome/9f3f70fc-5afc-4958-a7b7-3bb4fcb01805.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Browse the list of women's Nike jerseys over $60.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.nba.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "class&url", "class_multiObject": {"filter-selector-link": ["over $60", "women", "jerseys", "nike"]}, "type": "active_tab_html_parse", "url_include_expected": ["ove...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class&url", "class_multiObject": {"filter-selector-link": ["over $60", "women", "jerseys", "nike"]}, "url_include_expected": ["over $60", "women", "jerseys", "nike"]}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"is_other_exist": false, "jerseys": true, "nike": true, "over $60": true, "women": true}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9f935cce-0a9f-435f-8007-817732bfc0a5
- 源 JSON：[evaluation_examples/examples/chrome/9f935cce-0a9f-435f-8007-817732bfc0a5.json](../../../../evaluation_examples/examples/chrome/9f935cce-0a9f-435f-8007-817732bfc0a5.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：online_tasks
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match`

**Agent 要做什么**
Browse list of Civil Division forms.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.justice.gov/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["forms\\?title=&field_component_target_id=431"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a728a36e-8bf1-4bb6-9a03-ef039a5233f0
- 源 JSON：[evaluation_examples/examples/chrome/a728a36e-8bf1-4bb6-9a03-ef039a5233f0.json](../../../../evaluation_examples/examples/chrome/a728a36e-8bf1-4bb6-9a03-ef039a5233f0.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match`

**Agent 要做什么**
Find the Driver License Eligibility Requirements

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.dmv.virginia.gov/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["^https://(www\\.)?dmv\\.virginia\\.gov/licenses-ids/license/applying/eligibility"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a96b564e-dbe9-42c3-9ccf-b4498073438a
- 源 JSON：[evaluation_examples/examples/chrome/a96b564e-dbe9-42c3-9ccf-b4498073438a.json](../../../../evaluation_examples/examples/chrome/a96b564e-dbe9-42c3-9ccf-b4498073438a.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_0
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab`

**Agent 要做什么**
Find discussions of community and open one with most replies.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.flightaware.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_info` 状态 `{"goto_prefix": "https://", "type": "active_tab_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_active_tab`。检查 Chrome 当前活动标签页是否符合规则。
  - 实际结果 `active_tab_info`：读取 Chrome 当前活动标签页信息。；其他参数=`{"goto_prefix": "https://"}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://discussions.flightaware.com/t/the-banter-thread/4412"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## ae78f875-5b98-4907-bbb5-9c737fc68c03
- 源 JSON：[evaluation_examples/examples/chrome/ae78f875-5b98-4907-bbb5-9c737fc68c03.json](../../../../evaluation_examples/examples/chrome/ae78f875-5b98-4907-bbb5-9c737fc68c03.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://support.google.com/chrome/thread/219988391/increase-search-results-per-page?hl=en
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
Could you please change the number of search results displayed on one page to 50? I find that having more results visible at once significantly enhances my research efficiency, as it reduces the need to constantly click through multiple pages.

**前置/初始状态**
- 无显式前置动作；任务从对应 snapshot 的默认环境开始。

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## af630914-714e-4a24-a7bb-f9af687d3b91
- 源 JSON：[evaluation_examples/examples/chrome/af630914-714e-4a24-a7bb-f9af687d3b91.json](../../../../evaluation_examples/examples/chrome/af630914-714e-4a24-a7bb-f9af687d3b91.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://www.howtogeek.com/680260/how-to-change-chromes-default-text-size/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_font_size`

**Agent 要做什么**
My grandmother has been using the Chrome lately and told me that the font size is way too small for her poor eyesight. Could you set the default font size to the largest for her?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`chrome_font_size` 状态 `{"type": "chrome_font_size"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`check_font_size`。检查 Chrome 字体大小。
  - 实际结果 `chrome_font_size`：读取 Chrome 字体大小设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"max": 99999, "min": 16, "type": "range"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## b070486d-e161-459b-aa2b-ef442d973b92
- 源 JSON：[evaluation_examples/examples/chrome/b070486d-e161-459b-aa2b-ef442d973b92.json](../../../../evaluation_examples/examples/chrome/b070486d-e161-459b-aa2b-ef442d973b92.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：online_tasks
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match + is_expected_url_pattern_match + is_expected_url_pattern_match`

**Agent 要做什么**
Show side effects of Tamiflu.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.drugs.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`；`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`；`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`or`；共 3 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["^https://(www\\.)?drugs\\.com/tamiflu\\.html#side-effects"]}`。
  - 选项/规则：无额外 options。
- Metric 2：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["^https://(www\\.)?drugs\\.com/sfx/tamiflu-side-effects\\.html"]}`。
  - 选项/规则：无额外 options。
- Metric 3：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["^https://(www\\.)?drugs\\.com/sfx/tamiflu-side-effects\\.html#common-side-effects"]}`。
  - 选项/规则：无额外 options。
- 通过条件：任一 metric 通过即可整体通过。

## b4f95342-463e-4179-8c3f-193cd7241fb2
- 源 JSON：[evaluation_examples/examples/chrome/b4f95342-463e-4179-8c3f-193cd7241fb2.json](../../../../evaluation_examples/examples/chrome/b4f95342-463e-4179-8c3f-193cd7241fb2.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`high`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Find the Next Available dates for Diamond.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.recreation.gov/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject": {"camp-sortable-column-header": {"2": "camp-sortable-column-header"}}, "class_singleObject": {}, "goto_prefix": "https://www.", "type"...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject": {"camp-sortable-column-header": {"2": "camp-sortable-column-header"}}, "class_singleObject": {}, "goto_prefix": "https://www."}`。
  - 期望结果 `gotoRecreationPage_and_get_html_content`：导航到页面并获取 HTML 参考内容。；其他参数=`{"class": "camp-sortable-column-header", "order": "2", "selector": "class"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## b7895e80-f4d1-4648-bee0-4eb45a6f1fa8
- 源 JSON：[evaluation_examples/examples/chrome/b7895e80-f4d1-4648-bee0-4eb45a6f1fa8.json](../../../../evaluation_examples/examples/chrome/b7895e80-f4d1-4648-bee0-4eb45a6f1fa8.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_0
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`high`
- 评测函数：`check_direct_json_object + check_direct_json_object`

**Agent 要做什么**
Find a Hotel in New York City with lowest price possible for 2 adults next weekend.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.tripadvisor.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "xpath", "goto_prefix": "https://www.", "type": "active_tab_html_parse", "xpathObject": {"//button[@data-automation='checkin']//div[contains(@class,'Wh')]//span": "...`；`active_tab_html_parse` 状态 `{"category": "xpath", "goto_prefix": "https://www.", "type": "active_tab_html_parse", "xpathObject": {"//button[@data-automation='checkin']//div[contains(@class,'Wh')]": "from",...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`or`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "xpath", "goto_prefix": "https://www.", "xpathObject": {"//button[@data-automation='checkin']//div[contains(@class,'Wh')]//span": "from", "//button[@data-automation='checkout']//div[contains(@class,'Wh')]//span": "to", "//button[@data-automation='roomsandguests']//div[contains(@class,'Wh')]": "adult", "//button[contains(@aria-label,'PRICE_LOW...`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"adult": "Rooms/Guests1 Room, 2 Guests", "city": "New York City Hotels", "from": "{DoW}, {Month} {Day0D}", "rank": "Price (low to high)", "to": "{DoW}, {Month} {Day0D}"}, "relativeTime": {"from": "next week Saturday", "to": "next week Sunday"}, "timezone": "America/New_York"}`。
  - 选项/规则：无额外 options。
- Metric 2：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "xpath", "goto_prefix": "https://www.", "xpathObject": {"//button[@data-automation='checkin']//div[contains(@class,'Wh')]": "from", "//button[@data-automation='checkout']//div[contains(@class,'Wh')]": "to", "//button[@data-automation='roomsandguests']//div[contains(@class,'Wh')]": "adult", "//button[contains(@aria-label,'PRICE_LOW_TO_HIGH: Pr...`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"adult": "Rooms/Guests1 Room, 2 Guests", "city": "New York City Hotels", "from": "Check In{DoW}, {Month} {Day0D}", "rank": "Price (low to high)", "to": "Check Out{DoW}, {Month} {Day0D}"}, "relativeTime": {"from": "next week Friday", "to": "next week Sunday"}, "timezone": "America/New_York"}`。
  - 选项/规则：无额外 options。
- 通过条件：任一 metric 通过即可整体通过。

## bb5e4c0d-f964-439c-97b6-bdb9747de3f4
- 源 JSON：[evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://support.google.com/chrome/answer/95426?sjid=16867045591165135686-AP
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`match_in_list`

**Agent 要做什么**
Can you make Bing the main search engine when I look stuff up on the internet?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`default_search_engine` 状态 `{"type": "default_search_engine"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill chrome`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
  - 3. `sleep`：等待界面或后台状态稳定。 等待 3 秒
- Metric 1：`match_in_list`。实际值必须命中期望列表。
  - 实际结果 `default_search_engine`：读取 Chrome 默认搜索引擎设置。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["Microsoft Bing", "Bing"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## c1fa57f3-c3db-4596-8f09-020701085416
- 源 JSON：[evaluation_examples/examples/chrome/c1fa57f3-c3db-4596-8f09-020701085416.json](../../../../evaluation_examples/examples/chrome/c1fa57f3-c3db-4596-8f09-020701085416.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_1
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`medium`
- 评测函数：`is_expected_url_pattern_match`

**Agent 要做什么**
Open the baggage fee calculator in United Airlines website.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.united.com/en/us`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_info` 状态 `{"goto_prefix": "https://www.", "type": "active_tab_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_tab_info`：读取 Chrome 当前活动标签页信息。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["united\\.com/en/us/checked-bag-fee-calculator(/.*)?"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## cabb3bae-cccb-41bd-9f5d-0f3a9fecd825
- 源 JSON：[evaluation_examples/examples/chrome/cabb3bae-cccb-41bd-9f5d-0f3a9fecd825.json](../../../../evaluation_examples/examples/chrome/cabb3bae-cccb-41bd-9f5d-0f3a9fecd825.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：online_tasks
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Browse spider-man toys for kids and sort by lowest price.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.kohls.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "class&url", "class_multiObject_li": {"pmpSearch_breadcrumb": ["Spider-Man", "Toys", "Kids"], "sbSelector": ["Price Low-High"]}, "goto_prefix": "https://www.", "typ...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class&url", "class_multiObject_li": {"pmpSearch_breadcrumb": ["Spider-Man", "Toys", "Kids"], "sbSelector": ["Price Low-High"]}, "goto_prefix": "https://www.", "url_include_expected_multichoice": {"Kids": "Kids", "S=4": "Price Low-High", "Spider-Man": "Spider-Man", "Toys": "Toys", "spiderman": "Spider-Man"}}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"is_other_exist": false, "kids": true, "price low-high": true, "spider-man": true, "toys": true}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## da46d875-6b82-4681-9284-653b0c7ae241
- 源 JSON：[evaluation_examples/examples/chrome/da46d875-6b82-4681-9284-653b0c7ae241.json](../../../../evaluation_examples/examples/chrome/da46d875-6b82-4681-9284-653b0c7ae241.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_2
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match + check_direct_json_object + check_direct_json_object`

**Agent 要做什么**
Book an appointment to apply for a transportation access pass at the Charlie Card store on the first Monday eight months later, 10:15 am, fill in my details (James Smith, james.smith@gmail.com). And do not click "book" directly. Let me review it.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.mbta.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_info` 状态 `{"type": "active_tab_info"}`；`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject_only_child": {"HAZ16": {"0": "content", "1": "time"}}, "type": "active_tab_html_parse"}`；`active_tab_html_parse` 状态 `{"category": "input", "inputObject": {"/html/body/div[2]/div/form/div[7]/div/div/div[1]/input[1]": "name", "/html/body/div[2]/div/form/div[7]/div/div/div[1]/input[2]": "mail"}, ...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 3 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_tab_info`：读取 Chrome 当前活动标签页信息。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["book/CharlieCardStoreAppointments@mbta.com/"]}`。
  - 选项/规则：无额外 options。
- Metric 2：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject_only_child": {"HAZ16": {"0": "content", "1": "time"}}}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"content": "Apply for Transportation Access Pass (TAP) CharlieCard non-auto approval", "time": "{MonthFull} {Day0D}, 10:15 AM"}, "relativeTime": {"from": "first monday eight months later"}}`。
  - 选项/规则：无额外 options。
- Metric 3：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "input", "inputObject": {"/html/body/div[2]/div/form/div[7]/div/div/div[1]/input[1]": "name", "/html/body/div[2]/div/form/div[7]/div/div/div[1]/input[2]": "mail"}}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"mail": "james.smith@gmail.com", "name": "James Smith"}}`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## e1e75309-3ddb-4d09-92ec-de869c928143
- 源 JSON：[evaluation_examples/examples/chrome/e1e75309-3ddb-4d09-92ec-de869c928143.json](../../../../evaluation_examples/examples/chrome/e1e75309-3ddb-4d09-92ec-de869c928143.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：https://in5stepstutorials.com/google-chrome/save-web-page-as-pdf-in-chrome.php
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`compare_pdfs`

**Agent 要做什么**
Computer, can you turn the webpage I'm looking at into a PDF file, save it to my Desktop with the default filename and set the margins to none?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://lilianweng.github.io/posts/2023-06-23-agent/`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/Desktop/LLM Powered Autonomous Agents _ Lil'Log.pdf`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_pdfs`。比较 PDF 文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/Desktop/LLM Powered Autonomous Agents _ Lil'Log.pdf`；dest=`LLM Powered Autonomous Agents _ Lil'Log.pdf`。
  - 期望结果 `pdf_from_url`：从 URL 生成或获取 PDF 参考内容。；path=`https://lilianweng.github.io/posts/2023-06-23-agent/`；dest=`LLM Powered Autonomous Agents _ Lil'Log_gold.pdf`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f0b971a1-6831-4b9b-a50e-22a6e47f45ba
- 源 JSON：[evaluation_examples/examples/chrome/f0b971a1-6831-4b9b-a50e-22a6e47f45ba.json](../../../../evaluation_examples/examples/chrome/f0b971a1-6831-4b9b-a50e-22a6e47f45ba.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_active_tab`

**Agent 要做什么**
Please help me find the score record for the Super Bowl of the 2019 NFL season (played in 2020) in the NFL website.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.nfl.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_url_from_accessTree` 状态 `{"goto_prefix": "https://www.", "type": "active_url_from_accessTree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_active_tab`。检查 Chrome 当前活动标签页是否符合规则。
  - 实际结果 `active_url_from_accessTree`：从 accessibility tree 近似读取当前活动 URL。；其他参数=`{"goto_prefix": "https://www."}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://www.nfl.com/scores/2019/post4"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f3b19d1e-2d48-44e9-b4e1-defcae1a0197
- 源 JSON：[evaluation_examples/examples/chrome/f3b19d1e-2d48-44e9-b4e1-defcae1a0197.json](../../../../evaluation_examples/examples/chrome/f3b19d1e-2d48-44e9-b4e1-defcae1a0197.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_0
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_expected_url_pattern_match`

**Agent 要做什么**
Find the FAQ page about ticket delivery.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://premier.ticketek.com.au/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_info` 状态 `{"type": "active_tab_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_url_pattern_match`。检查 URL 是否匹配规则或模式。
  - 实际结果 `active_tab_info`：读取 Chrome 当前活动标签页信息。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["Ticket-Delivery-FAQs"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f5d96daf-83a8-4c86-9686-bada31fc66ab
- 源 JSON：[evaluation_examples/examples/chrome/f5d96daf-83a8-4c86-9686-bada31fc66ab.json](../../../../evaluation_examples/examples/chrome/f5d96daf-83a8-4c86-9686-bada31fc66ab.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：Mind2Web
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`medium`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Compare iPhone 15 Pro Max with iPhone 14 Pro Max and iPhone 13 Pro Max

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.apple.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["modelList"], "split_list": true, "type": "active_tab_url_parse"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["modelList"], "split_list": true}`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": {"modelList": ["iphone-15-pro-max", "iphone-14-pro-max", "iphone-13-pro-max"]}, "ignore_list_order": true}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f79439ad-3ee8-4f99-a518-0eb60e5652b0
- 源 JSON：[evaluation_examples/examples/chrome/f79439ad-3ee8-4f99-a518-0eb60e5652b0.json](../../../../evaluation_examples/examples/chrome/f79439ad-3ee8-4f99-a518-0eb60e5652b0.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_2
- trajectory：`trajectories/`
- 环境标记：proxy=`True`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Search for a one way flight from Dublin to Vienna on 10th next month for 2 adults.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.ryanair.com/gb/en`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_url_parse` 状态 `{"goto_prefix": "https://www.", "parse_keys": ["originIata", "destinationIata", "tpAdults", "tpTeens", "tpChildren", "tpStartDate", "isReturn"], "replace": {"tpStartDate": "time...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_url_parse`：解析 Chrome 当前活动标签页 URL。；其他参数=`{"goto_prefix": "https://www.", "parse_keys": ["originIata", "destinationIata", "tpAdults", "tpTeens", "tpChildren", "tpStartDate", "isReturn"], "replace": {"tpStartDate": "time"}}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"destinationIata": "VIE", "isReturn": "false", "originIata": "DUB", "time": "{Year}-{Month0D}-{DayD}", "tpAdults": "2", "tpChildren": "0", "tpTeens": "0"}, "relativeTime": {"from": "10th next month"}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## fc6d8143-9452-4171-9459-7f515143419a
- 源 JSON：[evaluation_examples/examples/chrome/fc6d8143-9452-4171-9459-7f515143419a.json](../../../../evaluation_examples/examples/chrome/fc6d8143-9452-4171-9459-7f515143419a.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`chrome`
- snapshot：`chrome`
- 相关应用：`chrome`
- 来源：test_task_0
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_direct_json_object`

**Agent 要做什么**
Find flights from New York–Kennedy Airport to Chicago O'Hare Airport for tomorrow.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `google-chrome --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `socat tcp-listen:9222,fork tcp:localhost:1337`
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.delta.com/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome` 中执行用户指令。
- 2. 操作重点：在 Chrome 中根据任务目标调整浏览器设置、访问网页、处理标签页/书签/扩展/下载等状态。
- 3. 结束时要让可评测结果落在：`active_tab_html_parse` 状态 `{"category": "class", "class_multiObject_child": {"mach-flight-context-info__wrapper__info--separator": {"0": "start", "1": "end"}}, "class_singleObject": {"mach-flight-context-...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_direct_json_object`。直接检查结构化 JSON 对象是否满足字段规则。
  - 实际结果 `active_tab_html_parse`：解析当前活动标签页 HTML。；其他参数=`{"category": "class", "class_multiObject_child": {"mach-flight-context-info__wrapper__info--separator": {"0": "start", "1": "end"}}, "class_singleObject": {"mach-flight-context-info__wrapper--date": "time"}, "goto_prefix": "https://www."}`。
  - 期望结果 `rule_relativeTime`：按相对时间规则生成期望值。；rules=`{"expected": {"end": "ORD", "start": "JFK", "time": "{DoW}, {Month} {Day0D}, {Year}"}, "relativeTime": {"from": "tomorrow"}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
