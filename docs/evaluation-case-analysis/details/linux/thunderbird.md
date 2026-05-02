# Linux/Ubuntu 主任务集 / thunderbird 详细 case 分析
来源目录：`evaluation_examples/examples/thunderbird/`。本文件覆盖 15 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 08c73485-7c6d-4681-999d-919f5c32dcfa
- 源 JSON：[evaluation_examples/examples/thunderbird/08c73485-7c6d-4681-999d-919f5c32dcfa.json](../../../../evaluation_examples/examples/thunderbird/08c73485-7c6d-4681-999d-919f5c32dcfa.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://superuser.com/questions/544480/how-to-apply-automatic-message-filters-to-subfolders-too?noredirect=1&lq=1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_prefs`

**Agent 要做什么**
Thunderbird's message filters seem to only fire on Inbox automatically. If you want to filter on subfolders, you'd have to start this filter manually. I am wondering if the filter can be applied automatically. Could you help me apply automatic message filters to subfolders

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_prefs`。检查 Thunderbird 偏好设置。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`；dest=`thunder-prefs.js`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": {"mail.imap.use_status_for_biff": {"method": "eq", "ref": false}, "mail.server.default.applyIncomingFilters": {"method": "eq", "ref": true}}, "unexpect": {"mail.server.default.autosync_offline_stores": {"method": "eq", "ref": false}}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 10a730d5-d414-4b40-b479-684bed1ae522
- 源 JSON：[evaluation_examples/examples/thunderbird/10a730d5-d414-4b40-b479-684bed1ae522.json](../../../../evaluation_examples/examples/thunderbird/10a730d5-d414-4b40-b479-684bed1ae522.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://superuser.com/questions/1757333/how-can-i-view-thunderbird-in-full-dark-mode
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_prefs`

**Agent 要做什么**
Considering I work late into the night and use Thunderbird frequently, I find that a full dark mode would be easier on my eyes during those hours. Can you help me enable a complete dark mode in Thunderbird?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_prefs`。检查 Thunderbird 偏好设置。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`；dest=`thunder-prefs.js`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": {"extensions.activeThemeID": {"method": "re", "ref": "dark"}}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 15c3b339-88f7-4a86-ab16-e71c58dcb01e
- 源 JSON：[evaluation_examples/examples/thunderbird/15c3b339-88f7-4a86-ab16-e71c58dcb01e.json](../../../../evaluation_examples/examples/thunderbird/15c3b339-88f7-4a86-ab16-e71c58dcb01e.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.wikihow.com/Access-Gmail-With-Mozilla-Thunderbird
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_accessibility_tree`

**Agent 要做什么**
Help me access my outlook account with address "anonym-x2024@outlook.com" and password 'password' (without ') in Thunderbird. Just fill in the information and stay on that page. I will check it manually later.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile-blank.tar.gz` 到 `/home/user/Desktop/thunderbird-profile-blank.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv -f /home/user/Desktop/thunderbird-profile-blank.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`accessibility_tree` 状态 `{"type": "accessibility_tree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `sleep`：等待界面或后台状态稳定。 等待 1.0 秒
- Metric 1：`check_accessibility_tree`。检查 accessibility tree 中的控件/文本状态。
  - 实际结果 `accessibility_tree`：读取当前界面的 accessibility tree。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`[{"xpath": "//application[@name='Thunderbird']//*[contains(text(), 'anonym-x2024@outlook.com') or contains(@name, 'anonym-x2024@outlook.com')]"}, {"xpath": "//application[@name='Thunderbird']//*[contains(@name, 'password') or contains(@name, 'Password')]"}]`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 3f28fe4f-5d9d-4994-a456-efd78cfae1a3
- 源 JSON：[evaluation_examples/examples/thunderbird/3f28fe4f-5d9d-4994-a456-efd78cfae1a3.json](../../../../evaluation_examples/examples/thunderbird/3f28fe4f-5d9d-4994-a456-efd78cfae1a3.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.adsigner.com/user-manual/signatures/setup-email-client-thunderbird/#:~:text=is%20probably%20hidden.-,Right%20click%20on%20the%20empty%20space%20at%20the%20top%20of,signature%20from%20a%20file%20instead.
- trajectory：`trajectories/6766f2b8-8a72-417f-a9e5-56fcaa735837`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_prefs`

**Agent 要做什么**
Set up a plain text signature for my email account in Thunderbird. The first line is my name "Anonym" and the second line is my affiliation "XYZ Lab".

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_prefs`。检查 Thunderbird 偏好设置。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`；dest=`thunder-prefs.js`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": {"mail.identity.id1.htmlSigText": {"method": "re.S", "ref": "Anonym\\nXYZ Lab"}}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 3f49d2cc-f400-4e7d-90cc-9b18e401cc31
- 源 JSON：[evaluation_examples/examples/thunderbird/3f49d2cc-f400-4e7d-90cc-9b18e401cc31.json](../../../../evaluation_examples/examples/thunderbird/3f49d2cc-f400-4e7d-90cc-9b18e401cc31.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.reddit.com/r/Thunderbird/comments/182dg5p/unified_inbox_howto/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_json`

**Agent 要做什么**
I've got a bunch of email accounts in Thunderbird, and it's a hassle to check them one by one. Can you show me how to set up a unified inbox so I can see all my emails in one place?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/xulstore.json`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_json`。检查 JSON/YAML 内容是否满足规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/xulstore.json`；dest=`xulstore.json`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": [{"key": ["chrome://messenger/content/messenger.xhtml", "folderTree", "mode"], "method": "re", "ref": "\\bsmart\\b"}]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 5203d847-2572-4150-912a-03f062254390
- 源 JSON：[evaluation_examples/examples/thunderbird/5203d847-2572-4150-912a-03f062254390.json](../../../../evaluation_examples/examples/thunderbird/5203d847-2572-4150-912a-03f062254390.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://support.mozilla.org/en-US/kb/organize-your-messages-using-filters
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_filter`

**Agent 要做什么**
Create a local folder called "Promotions" and create a filter to auto move the inbox emails whose subject contains “discount” to the new folder

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/ImapMail/outlook.office365.com/msgFilterRules.dat`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Message Filters`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_filter`。检查 Thunderbird 邮件过滤器。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/ImapMail/outlook.office365.com/msgFilterRules.dat`；dest=`msgFilterRules.dat`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": [{"action": "Move to folder", "actionValue": "mailbox://nobody@Local%20Folders/Promotions", "condition": ["AND (subject,contains,discount)"], "enabled": "yes"}]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7b1e1ff9-bb85-49be-b01d-d6424be18cd0
- 源 JSON：[evaluation_examples/examples/thunderbird/7b1e1ff9-bb85-49be-b01d-d6424be18cd0.json](../../../../evaluation_examples/examples/thunderbird/7b1e1ff9-bb85-49be-b01d-d6424be18cd0.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.quora.com/How-do-I-open-a-Thunderbird-profile-manager-utility
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_accessibility_tree`

**Agent 要做什么**
Could you help me open up the profile management tabpage in Thunderbird? I want the profile management tabpage inside Thunderbird app, but not the profile chooser dialog during app launch.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/Desktop/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv -f /home/user/Desktop/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`accessibility_tree` 状态 `{"type": "accessibility_tree"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_accessibility_tree`。检查 accessibility tree 中的控件/文本状态。
  - 实际结果 `accessibility_tree`：读取当前界面的 accessibility tree。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`[{"selectors": ["application[name=Thunderbird] page-tab-list[attr|id=\"tabmail-tabs\"]>page-tab[name=\"About Profiles\"]"]}]`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9b7bc335-06b5-4cd3-9119-1a649c478509
- 源 JSON：[evaluation_examples/examples/thunderbird/9b7bc335-06b5-4cd3-9119-1a649c478509.json](../../../../evaluation_examples/examples/thunderbird/9b7bc335-06b5-4cd3-9119-1a649c478509.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://support.mozilla.org/en-US/questions/1259354
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_filter`

**Agent 要做什么**
Set up to forward every email received by anonym-x2024@outlook.com in the future to anonym-x2024@gmail.com. Please don't touch the online account. Just locally in the Thunderbird!

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/ImapMail/outlook.office365.com/msgFilterRules.dat`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Message Filters`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_filter`。检查 Thunderbird 邮件过滤器。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/ImapMail/outlook.office365.com/msgFilterRules.dat`；dest=`msgFilterRules.dat`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": [{"action": "Forward", "actionValue": "anonym-x2024@gmail.com", "condition": ["ALL"], "enabled": "yes"}]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9bc3cc16-074a-45ac-9bdc-b2a362e1daf3
- 源 JSON：[evaluation_examples/examples/thunderbird/9bc3cc16-074a-45ac-9bdc-b2a362e1daf3.json](../../../../evaluation_examples/examples/thunderbird/9bc3cc16-074a-45ac-9bdc-b2a362e1daf3.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.quora.com/How-do-I-backup-email-files-in-Mozilla-Thunderbird
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_list`

**Agent 要做什么**
Could you help me back up all the email files in my inbox to ~/emails.bak? Please save them separately in eml format.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`cache_file` 的 `emails.bak.ls`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `ls -R /home/user/emails.bak`
- Metric 1：`check_list`。检查列表内容是否满足规则。
  - 实际结果 `cache_file`：读取本地 cache 中的文件。；path=`emails.bak.ls`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": ["歡迎使用新的 Outlook.com 帳戶.*\\.eml", "A Test E-mail.*\\.eml"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a10b69e1-6034-4a2b-93e1-571d45194f75
- 源 JSON：[evaluation_examples/examples/thunderbird/a10b69e1-6034-4a2b-93e1-571d45194f75.json](../../../../evaluation_examples/examples/thunderbird/a10b69e1-6034-4a2b-93e1-571d45194f75.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://support.mozilla.org/bm/questions/1027435
- trajectory：`trajectories/2ad9387a-65d8-4e33-ad5b-7580065a27ca`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_list`

**Agent 要做什么**
Create two local folders in Thunderbird for me: COMPANY and UNIVERSITY.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`cache_file` 的 `thunder-local-folder.ls`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `ls -R /home/user/.thunderbird/t5q2a5hp.default-release/Mail/Local Folders`
- Metric 1：`check_list`。检查列表内容是否满足规则。
  - 实际结果 `cache_file`：读取本地 cache 中的文件。；path=`thunder-local-folder.ls`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": ["\\bCOMPANY\\.msf\\b", "\\bCOMPANY/?(?!\\.msf)", "\\bUNIVERSITY\\.msf\\b", "\\bUNIVERSITY/?(?!\\.msf)"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a1af9f1c-50d5-4bc3-a51e-4d9b425ff638
- 源 JSON：[evaluation_examples/examples/thunderbird/a1af9f1c-50d5-4bc3-a51e-4d9b425ff638.json](../../../../evaluation_examples/examples/thunderbird/a1af9f1c-50d5-4bc3-a51e-4d9b425ff638.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://superuser.com/questions/1764409/how-to-send-email-with-thunderbird-without-configuring-an-incoming-email-service
- trajectory：`trajectories/99146c54-4f37-4ab8-9327-5f3291665e1e`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
Due to certain security considerations and the nature of my work, I prefer not to configure an incoming email service in Thunderbird. However, I still need to send emails. Can you help me set up Thunderbird to send emails from anonym-x2024@outlook.com without configuring its incoming email service?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile-blank.tar.gz` 到 `/home/user/thunderbird-profile-blank.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile-blank.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## d38192b0-17dc-4e1d-99c3-786d0117de77
- 源 JSON：[evaluation_examples/examples/thunderbird/d38192b0-17dc-4e1d-99c3-786d0117de77.json](../../../../evaluation_examples/examples/thunderbird/d38192b0-17dc-4e1d-99c3-786d0117de77.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://support.mozilla.org/en-US/kb/how-use-attachments
- trajectory：`trajectories/d088f539-cab4-4f9a-ac92-9999fc3a656e`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_list`

**Agent 要做什么**
Attach the my AWS bill to the email. The bill is stored at ~/aws-bill.pdf. Don't close it or send it. I haven't finish all the contents.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `invoice0123456789.pdf` 到 `/home/user/aws-bill.pdf`；下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`；下载 `New-month%20AWS%20Bill.html` 到 `/home/user/.aws-bill-mail-body.html`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird -compose "from='Anonym Tester <anonym-x2024@outlook.com>',to=assistant@outlook.com,subject='New-month AWS Bill',body='$(cat /home/user/.aws-bill-mail-body.html)'"`；shell=True

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`cache_file` 的 `check-attachments.output`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `show-thunderbird-attachments.py` 到 `/home/user/show-thunderbird-attachments.py`；下载 `cssselect-1.3.0-py3-none-any.whl` 到 `/home/user/cssselect-1.3.0-py3-none-any.whl`
  - 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `pip install /home/user/cssselect-1.3.0-py3-none-any.whl`
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python /home/user/show-thunderbird-attachments.py New-month AWS Bill aws-bill.pdf`
- Metric 1：`check_list`。检查列表内容是否满足规则。
  - 实际结果 `cache_file`：读取本地 cache 中的文件。；path=`check-attachments.output`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": ["Attachment added!"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## dd84e895-72fd-4023-a336-97689ded257c
- 源 JSON：[evaluation_examples/examples/thunderbird/dd84e895-72fd-4023-a336-97689ded257c.json](../../../../evaluation_examples/examples/thunderbird/dd84e895-72fd-4023-a336-97689ded257c.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://support.mozilla.org/en-US/kb/organize-your-messages-using-filters
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`run_sqlite3`

**Agent 要做什么**
Add a star to every email in local Bills folder

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/global-messages-db.sqlite`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`run_sqlite3`。执行 sqlite3 查询并检查结果。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/global-messages-db.sqlite`；dest=`global-messages-db.sqlite`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"sql": "SELECT COALESCE((SELECT COUNT(*) FROM messageAttributes WHERE attributeID = 58 AND value = 1 AND messageID IN (SELECT id FROM messages WHERE folderID = 13)), 0) = (SELECT COUNT(*) FROM messages WHERE folderID = 13);"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## dfac9ee8-9bc4-4cdc-b465-4a4bfcd2f397
- 源 JSON：[evaluation_examples/examples/thunderbird/dfac9ee8-9bc4-4cdc-b465-4a4bfcd2f397.json](../../../../evaluation_examples/examples/thunderbird/dfac9ee8-9bc4-4cdc-b465-4a4bfcd2f397.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://www.wikihow.com/Remove-an-Email-Account-from-Thunderbird
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_csv`

**Agent 要做什么**
Help me to remove the account "anonym-x2024@outlook.com"

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/Desktop/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv -f /home/user/Desktop/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`cache_file` 的 `thunderbird-accounts.csv`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `firefox_decrypt.py` 到 `/home/user/Desktop/firefox_decrypt.py`
  - 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python3 /home/user/Desktop/firefox_decrypt.py /home/user/.thunderbird -n -c 2 -f csv -d ,`
- Metric 1：`check_csv`。检查 CSV 内容是否满足规则。
  - 实际结果 `cache_file`：读取本地 cache 中的文件。；path=`thunderbird-accounts.csv`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"unexpect": [{"url": "imap://outlook.office365.com", "user": "anonym-x2024@outlook.com"}]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f201fbc3-44e6-46fc-bcaa-432f9815454c
- 源 JSON：[evaluation_examples/examples/thunderbird/f201fbc3-44e6-46fc-bcaa-432f9815454c.json](../../../../evaluation_examples/examples/thunderbird/f201fbc3-44e6-46fc-bcaa-432f9815454c.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`thunderbird`
- snapshot：`thunderbird`
- 相关应用：`thunderbird`
- 来源：https://superuser.com/questions/1781004/how-do-i-remove-the-indentation-and-character-in-quoted-text-of-a-reply-mess
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_thunderbird_prefs`

**Agent 要做什么**
When I reply to an email, it quotes the original message but offsets it with an indentation and ">" character. I would like to quote the original message with no indentation, and no special character. Could you help me remove the indentation and ">" for me?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile.tar.gz` 到 `/home/user/thunderbird-profile.tar.gz`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `tar -xzv --recursive-unlink -f /home/user/thunderbird-profile.tar.gz -C /home/user/`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `/usr/bin/thunderbird`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird` 中执行用户指令。
- 2. 操作重点：在 Thunderbird 中完成邮件、联系人、过滤器、文件夹或偏好设置操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `close_window`：关闭指定窗口。 关闭窗口 `Mail.thunderbird`
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_thunderbird_prefs`。检查 Thunderbird 偏好设置。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/.thunderbird/t5q2a5hp.default-release/prefs.js`；dest=`thunder-prefs.js`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": {"mail.identity.id1.auto_quote": {"method": "eq", "ref": false}}}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
