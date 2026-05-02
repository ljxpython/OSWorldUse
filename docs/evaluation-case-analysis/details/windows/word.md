# Windows 任务集 / word 详细 case 分析
来源目录：`evaluation_examples/examples_windows/word/`。本文件覆盖 9 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 0810415c-bde4-4443-9047-d5f70165a697
- 源 JSON：[evaluation_examples/examples_windows/word/0810415c-bde4-4443-9047-d5f70165a697.json](../../../../evaluation_examples/examples_windows/word/0810415c-bde4-4443-9047-d5f70165a697.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://www.youtube.com/watch?v=Q_AaL6ljudU
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_line_spacing`

**Agent 要做什么**
Make the line spacing of first two paragraph into double line spacing

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Novels_Intro_Packet.docx` 到 `C:\Users\User\Novels_Intro_Packet.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Novels_Intro_Packet.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Novels_Intro_Packet.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Novels_Intro_Packet - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
- Metric 1：`compare_line_spacing`。比较文档行距。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Novels_Intro_Packet.docx`；dest=`Novels_Intro_Packet.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/0810415c-bde4-4443-9047-d5f70165a697/Novels_Intro_Packet_Gold.docx`；dest=`Novels_Intro_Packet_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 0b17a146-2934-46c7-8727-73ff6b6483e8
- 源 JSON：[evaluation_examples/examples_windows/word/0b17a146-2934-46c7-8727-73ff6b6483e8.json](../../../../evaluation_examples/examples_windows/word/0b17a146-2934-46c7-8727-73ff6b6483e8.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://askubuntu.com/questions/245695/how-do-you-insert-subscripts-and-superscripts-into-ordinary-non-formula-text-i
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_files`

**Agent 要做什么**
Help me change the 2 in "H2O" to a subscript.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `H2O_Factsheet_WA.docx` 到 `C:\Users\User\H2O_Factsheet_WA.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\H2O_Factsheet_WA.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\H2O_Factsheet_WA.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `H2O_Factsheet_WA - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
- Metric 1：`compare_docx_files`。比较 DOCX 文档内容和格式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\H2O_Factsheet_WA.docx`；dest=`H2O_Factsheet_WA.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/0b17a146-2934-46c7-8727-73ff6b6483e8/H2O_Factsheet_WA_Gold.docx`；dest=`H2O_Factsheet_WA_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 0e763496-b6bb-4508-a427-fad0b6c3e195
- 源 JSON：[evaluation_examples/examples_windows/word/0e763496-b6bb-4508-a427-fad0b6c3e195.json](../../../../evaluation_examples/examples_windows/word/0e763496-b6bb-4508-a427-fad0b6c3e195.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://ask.libreoffice.org/t/how-do-i-change-the-font-for-the-whole-document-in-writer/9220
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_font_names`

**Agent 要做什么**
Change the font to "Times New Roman" throughout the text.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Dublin_Zoo_Intro.docx` 到 `C:\Users\User\Dublin_Zoo_Intro.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Dublin_Zoo_Intro.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Dublin_Zoo_Intro.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Dublin_Zoo_Intro - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(5);`
- Metric 1：`compare_font_names`。检查/比较字体名称。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Dublin_Zoo_Intro.docx`；dest=`Dublin_Zoo_Intro.docx`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"font_name": "Times New Roman"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 3ef2b351-8a84-4ff2-8724-d86eae9b842e
- 源 JSON：[evaluation_examples/examples_windows/word/3ef2b351-8a84-4ff2-8724-d86eae9b842e.json](../../../../evaluation_examples/examples_windows/word/3ef2b351-8a84-4ff2-8724-d86eae9b842e.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://askubuntu.com/questions/1066351/how-do-you-center-align-in-libreoffice#:~:text=Ctrl%20%2B%20e%20will%20Center%20align%20the%20cursor%20for%20you.
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`is_first_line_centered`

**Agent 要做什么**
Help me center align the heading in LibreOffice.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Constitution_Template_With_Guidelines.docx` 到 `C:\Users\User\Constitution_Template_With_Guidelines.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Constitution_Template_With_Guidelines.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Constitution_Template_With_Guidelines.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Constitution_Template_With_Guidelines - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(5);`
- Metric 1：`is_first_line_centered`。检查首行居中。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Constitution_Template_With_Guidelines.docx`；dest=`Constitution_Template_With_Guidelines.docx`。
  - 期望结果：无。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 4bcb1253-a636-4df4-8cb0-a35c04dfef31
- 源 JSON：[evaluation_examples/examples_windows/word/4bcb1253-a636-4df4-8cb0-a35c04dfef31.json](../../../../evaluation_examples/examples_windows/word/4bcb1253-a636-4df4-8cb0-a35c04dfef31.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://www.libreofficehelp.com/save-export-writer-documents-in-pdf-epub-format/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pdfs`

**Agent 要做什么**
Export the current document into PDF, keep the file name

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `View_Person_Organizational_Summary.docx` 到 `C:\Users\User\View_Person_Organizational_Summary.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\View_Person_Organizational_Summary.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\View_Person_Organizational_Summary.pdf`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_pdfs`。比较 PDF 文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\View_Person_Organizational_Summary.pdf`；dest=`Constitution_Template_With_Guidelines.pdf`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/4bcb1253-a636-4df4-8cb0-a35c04dfef31/View_Person_Organizational_Summary.pdf`；dest=`Constitution_Template_With_Guidelines_Gold.pdf`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 6f81754e-285d-4ce0-b59e-af7edb02d108
- 源 JSON：[evaluation_examples/examples_windows/word/6f81754e-285d-4ce0-b59e-af7edb02d108.json](../../../../evaluation_examples/examples_windows/word/6f81754e-285d-4ce0-b59e-af7edb02d108.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://superuser.com/questions/789473/remove-duplicate-lines-in-libreoffice-openoffice-writer
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_lines`

**Agent 要做什么**
A certain railway company in Hong Kong uses a signaling system to keep track of trains in its railway system. Each line in the docx file represents a train calling at a station from 0600 to 1200 on 2022-09-22, and has the following format: time_HH:MM:SS, train_id, station_id, platform_no.. I want to remove duplicated train ids in order to know how many different trains are running from 0600 to 1200. Could you help me on this? I am doing it manually and it is very inefficient.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `HK_train_record.docx` 到 `C:\Users\User\HK_train_record.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\HK_train_record.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\HK_train_record.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `HK_train_record - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
- Metric 1：`compare_docx_lines`。调用 `compare_docx_lines` metric 比较实际结果和期望结果。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\HK_train_record.docx`；dest=`HK_train_record.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/6f81754e-285d-4ce0-b59e-af7edb02d108/HK_train_record_Gold.docx`；dest=`HK_train_record_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## b21acd93-60fd-4127-8a43-2f5178f4a830
- 源 JSON：[evaluation_examples/examples_windows/word/b21acd93-60fd-4127-8a43-2f5178f4a830.json](../../../../evaluation_examples/examples_windows/word/b21acd93-60fd-4127-8a43-2f5178f4a830.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://superuser.com/questions/1097199/how-can-i-double-space-a-document-in-libreoffice?rq=1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_line_spacing`

**Agent 要做什么**
I have been practicing professional writing lately. Now I am writing essay which requires one paragraph each for introduction, body and conclusion with single-space for introduction, double-space for body then one-and-a-half-space for conclusion. Could you help me on this?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `CCHU9045_Course_Outline_2019-20.docx` 到 `C:\Users\User\CCHU9045_Course_Outline_2019-20.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\CCHU9045_Course_Outline_2019-20.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\CCHU9045_Course_Outline_2019-20.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `CCHU9045_Course_Outline_2019-20 - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
- Metric 1：`compare_line_spacing`。比较文档行距。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\CCHU9045_Course_Outline_2019-20.docx`；dest=`CCHU9045_Course_Outline_2019-20.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/b21acd93-60fd-4127-8a43-2f5178f4a830/CCHU9045_Course_Outline_2019-20_Gold.docx`；dest=`CCHU9045_Course_Outline_2019-20_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## e528b65e-1107-4b8c-8988-490e4fece599
- 源 JSON：[evaluation_examples/examples_windows/word/e528b65e-1107-4b8c-8988-490e4fece599.json](../../../../evaluation_examples/examples_windows/word/e528b65e-1107-4b8c-8988-490e4fece599.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://www.youtube.com/watch?v=l25Evu4ohKg
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_files`

**Agent 要做什么**
Capitalize the first letter of all words.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Geography_And_Magical_Realism.docx` 到 `C:\Users\User\Geography_And_Magical_Realism.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Geography_And_Magical_Realism.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Geography_And_Magical_Realism.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Geography_And_Magical_Realism - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
- Metric 1：`compare_docx_files`。比较 DOCX 文档内容和格式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Geography_And_Magical_Realism.docx`；dest=`Geography_And_Magical_Realism.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/e528b65e-1107-4b8c-8988-490e4fece599/Geography_And_Magical_Realism%20%281%29.docx`；dest=`Geography_And_Magical_Realism_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## ecc2413d-8a48-416e-a3a2-d30106ca36cb
- 源 JSON：[evaluation_examples/examples_windows/word/ecc2413d-8a48-416e-a3a2-d30106ca36cb.json](../../../../evaluation_examples/examples_windows/word/ecc2413d-8a48-416e-a3a2-d30106ca36cb.json)
- 平台/集合：Windows 任务集
- 应用域：`word`
- snapshot：`word`
- 相关应用：`word`
- 来源：https://www.quora.com/How-can-I-insert-a-blank-page-on-libreoffice
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_files`

**Agent 要做什么**
Hey, can you throw in a blank page right after this one?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Sample_Statutory_Declaration.docx` 到 `C:\Users\User\Sample_Statutory_Declaration.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Sample_Statutory_Declaration.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word` 中执行用户指令。
- 2. 操作重点：在 Word 中处理文档，完成排版、表格、引用、页眉页脚、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Sample_Statutory_Declaration.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Sample_Statutory_Declaration - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
- Metric 1：`compare_docx_files`。比较 DOCX 文档内容和格式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Sample_Statutory_Declaration.docx`；dest=`Sample_Statutory_Declaration.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/word/ecc2413d-8a48-416e-a3a2-d30106ca36cb/Sample_Statutory_Declaration_Gold.docx`；dest=`Sample_Statutory_Declaration_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
