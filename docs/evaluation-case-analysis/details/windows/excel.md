# Windows 任务集 / excel 详细 case 分析
来源目录：`evaluation_examples/examples_windows/excel/`。本文件覆盖 11 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 3aaa4e37-dc91-482e-99af-132a612d40f3
- 源 JSON：[evaluation_examples/examples_windows/excel/3aaa4e37-dc91-482e-99af-132a612d40f3.json](../../../../evaluation_examples/examples_windows/excel/3aaa4e37-dc91-482e-99af-132a612d40f3.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.quora.com/How-can-you-import-export-CSV-files-with-LibreOffice-Calc-or-OpenOffice
- trajectory：`trajectories/3aaa4e37-dc91-482e-99af-132a612d40f3`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_csv`

**Agent 要做什么**
Could you help me to export the current sheet to a csv file? Export the contents just as they are shown on the screen. Just keep the other options untouched. A default csv format is ok. The csv should share the file name with the original xlsx.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Export_Calc_to_CSV.xlsx` 到 `c:\Users\User\Export_Calc_to_CSV.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `c:\Users\User\Export_Calc_to_CSV.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `c:\Users\User\Export_Calc_to_CSV.csv`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_csv`。比较实际 CSV 和参考 CSV。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`c:\Users\User\Export_Calc_to_CSV.csv`；dest=`Export_Calc_to_CSV.csv`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/3aaa4e37-dc91-482e-99af-132a612d40f3/Export_Calc_to_CSV.csv`；dest=`Export_Calc_to_CSV_gold.csv`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 4188d3a4-077d-46b7-9c86-23e1a036f6c1
- 源 JSON：[evaluation_examples/examples_windows/excel/4188d3a4-077d-46b7-9c86-23e1a036f6c1.json](../../../../evaluation_examples/examples_windows/excel/4188d3a4-077d-46b7-9c86-23e1a036f6c1.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.libreofficehelp.com/freeze-unfreeze-rows-columns-ranges-calc/
- trajectory：`trajectories/4188d3a4-077d-46b7-9c86-23e1a036f6c1`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Help me freeze the range A1:B1 on this sheet to keep the headers always visible

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Freeze_row_column2.xlsx` 到 `c:\users\User\Freeze_row_column.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `c:\users\User\Freeze_row_column.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `c:\users\User\Freeze_row_column.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Freeze_row_column - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; pyautogui.hotkey("ctrl", "s");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`c:\users\User\Freeze_row_column.xlsx`；dest=`Freeze_row_column.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/4188d3a4-077d-46b7-9c86-23e1a036f6c1/Freeze_row_column2_gold.xlsx`；dest=`Freeze_row_column_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "freeze"}, {"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 51b11269-2ca8-4b2a-9163-f21758420e78
- 源 JSON：[evaluation_examples/examples_windows/excel/51b11269-2ca8-4b2a-9163-f21758420e78.json](../../../../evaluation_examples/examples_windows/excel/51b11269-2ca8-4b2a-9163-f21758420e78.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.reddit.com/r/LibreOfficeCalc/comments/186pcc6/how_to_arrange_numbers_in_a_column_from_minimum/
- trajectory：`trajectories/51b11269-2ca8-4b2a-9163-f21758420e78`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Could you help me to sort the records according to the amounts ascendingly?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Arrang_Value_min_to_max.xlsx` 到 `c:\users\User\Arrang_Value_min_to_max.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `c:\users\User\Arrang_Value_min_to_max.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `c:\users\User\Arrang_Value_min_to_max.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Arrang_Value_min_to_max - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; pyautogui.hotkey("ctrl", "s");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`c:\users\User\Arrang_Value_min_to_max.xlsx`；dest=`Arrang_Value_min_to_max.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/51b11269-2ca8-4b2a-9163-f21758420e78/Arrang_Value_min_to_max_gold.xlsx`；dest=`Arrang_Value_min_to_max_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 6054afcb-5bab-4702-90a0-b259b5d3217c
- 源 JSON：[evaluation_examples/examples_windows/excel/6054afcb-5bab-4702-90a0-b259b5d3217c.json](../../../../evaluation_examples/examples_windows/excel/6054afcb-5bab-4702-90a0-b259b5d3217c.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/JTbZ8sRxkdU
- trajectory：`trajectories/6054afcb-5bab-4702-90a0-b259b5d3217c`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Some data are missed by now and are filled by 'N/A' temporarily. Please hide them in the table for now. Do not delete them and filter is no needed.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Date_Budget_Variance_HideNA.xlsx` 到 `C:\Users\User\Date_Budget_Variance_HideNA.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Date_Budget_Variance_HideNA.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Date_Budget_Variance_HideNA.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Date_Budget_Variance_HideNA - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Date_Budget_Variance_HideNA.xlsx`；dest=`Date_Budget_Variance_HideNA.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/6054afcb-5bab-4702-90a0-b259b5d3217c/Date_Budget_Variance_HideNA_gold.xlsx`；dest=`Date_Budget_Variance_HideNA_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}, {"props": ["hidden"], "sheet_idx0": 0, "sheet_idx1": "EI0", "type": "row_props"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7a4e4bc8-922c-4c84-865c-25ba34136be1
- 源 JSON：[evaluation_examples/examples_windows/excel/7a4e4bc8-922c-4c84-865c-25ba34136be1.json](../../../../evaluation_examples/examples_windows/excel/7a4e4bc8-922c-4c84-865c-25ba34136be1.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/bvUhr1AHs44
- trajectory：`trajectories/7a4e4bc8-922c-4c84-865c-25ba34136be1`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Reorder the columns to be "Date", "First Name", "Last Name", "Order ID", "Sales"

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Name_Order_Id_move_column.xlsx` 到 `C:\Users\User\Name_Order_Id_move_column.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Name_Order_Id_move_column.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Name_Order_Id_move_column.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Name_Order_Id_move_column - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Name_Order_Id_move_column.xlsx`；dest=`Name_Order_Id_move_column.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/7a4e4bc8-922c-4c84-865c-25ba34136be1/Name_Order_Id_move_column_gold.xlsx`；dest=`Name_Order_Id_move_column_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7efeb4b1-3d19-4762-b163-63328d66303b
- 源 JSON：[evaluation_examples/examples_windows/excel/7efeb4b1-3d19-4762-b163-63328d66303b.json](../../../../evaluation_examples/examples_windows/excel/7efeb4b1-3d19-4762-b163-63328d66303b.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/4jzXfZNhfmk
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Fill the Sequence Numbers as "No. #" in the "Seq No." column

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Order_Sales_Serial%23.xlsx` 到 `C:\Users\User\Order_Sales_Serial#.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Order_Sales_Serial#.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Order_Sales_Serial#.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Order_Sales_Serial# - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Order_Sales_Serial#.xlsx`；dest=`Order_Sales_Serial#.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/7efeb4b1-3d19-4762-b163-63328d66303b/Order_Sales_Serial%23_gold.xlsx`；dest=`Order_Sales_Serial#_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 8b1ce5f2-59d2-4dcc-b0b0-666a714b9a14
- 源 JSON：[evaluation_examples/examples_windows/excel/8b1ce5f2-59d2-4dcc-b0b0-666a714b9a14.json](../../../../evaluation_examples/examples_windows/excel/8b1ce5f2-59d2-4dcc-b0b0-666a714b9a14.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/Hbcwu6IQ1ns
- trajectory：`trajectories/8b1ce5f2-59d2-4dcc-b0b0-666a714b9a14`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Given a partial calendar, please highlight all the weekends (Satureday & Sunday) by setting the cell background as red (#ff0000).

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Calendar_Highlight_Weekend_Days.xlsx` 到 `C:\Users\User\Calendar_Highlight_Weekend_Days.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Calendar_Highlight_Weekend_Days.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Calendar_Highlight_Weekend_Days.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Calendar_Highlight_Weekend_Days - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Calendar_Highlight_Weekend_Days.xlsx`；dest=`Calendar_Highlight_Weekend_Days.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/8b1ce5f2-59d2-4dcc-b0b0-666a714b9a14/Calendar_Highlight_Weekend_Days_gold.xlsx`；dest=`Calendar_Highlight_Weekend_Days_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}, {"props": ["bgcolor"], "sheet_idx0": 0, "sheet_idx1": "EI0", "type": "style"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a9f325aa-8c05-4e4f-8341-9e4358565f4f
- 源 JSON：[evaluation_examples/examples_windows/excel/a9f325aa-8c05-4e4f-8341-9e4358565f4f.json](../../../../evaluation_examples/examples_windows/excel/a9f325aa-8c05-4e4f-8341-9e4358565f4f.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/A0gmEBRKXWs
- trajectory：`trajectories/a9f325aa-8c05-4e4f-8341-9e4358565f4f`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Remove the adundant whitespaces and canonicalize the letter cases by capitalizing the first letter of each words and leave other letters as lower case.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Movie_titles_garbage_clean.xlsx` 到 `C:\Users\User\Movie_title_garbage_clean.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Movie_title_garbage_clean.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Movie_title_garbage_clean.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Movie_title_garbage_clean - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Movie_title_garbage_clean.xlsx`；dest=`Movie_title_garbage_clean.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/a9f325aa-8c05-4e4f-8341-9e4358565f4f/Movie_titles_garbage_clean_gold.xlsx`；dest=`Movie_title_garbage_clean_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## abed40dc-063f-4598-8ba5-9fe749c0615d
- 源 JSON：[evaluation_examples/examples_windows/excel/abed40dc-063f-4598-8ba5-9fe749c0615d.json](../../../../evaluation_examples/examples_windows/excel/abed40dc-063f-4598-8ba5-9fe749c0615d.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://help.libreoffice.org/7.6/ro/text/scalc/guide/remove_duplicates.html?&DbPAR=SHARED&System=UNIX
- trajectory：`trajectories/abed40dc-063f-4598-8ba5-9fe749c0615d`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Check the names in column "Names with duplicates" and put the unique ones in column "Unique Names". Keep the original order.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Names_Duplicate_Unique.xlsx` 到 `C:\Users\User\Names_Duplicate_Unique.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Names_Duplicate_Unique.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Names_Duplicate_Unique.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Names_Duplicate_Unique - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Names_Duplicate_Unique.xlsx`；dest=`Names_Duplicate_Unique.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/abed40dc-063f-4598-8ba5-9fe749c0615d/Names_Duplicate_Unique_gold.xlsx`；dest=`Names_Duplicate_Unique_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## eb03d19a-b88d-4de4-8a64-ca0ac66f426b
- 源 JSON：[evaluation_examples/examples_windows/excel/eb03d19a-b88d-4de4-8a64-ca0ac66f426b.json](../../../../evaluation_examples/examples_windows/excel/eb03d19a-b88d-4de4-8a64-ca0ac66f426b.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/t9JLUaT55UQ
- trajectory：`trajectories/eb03d19a-b88d-4de4-8a64-ca0ac66f426b`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Transpose the table and paste it starting from B8.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Students_Class_Subject_Marks.xlsx` 到 `C:\Users\User\Students_Class_Subject_Marks.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Students_Class_Subject_Marks.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Students_Class_Subject_Marks.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Students_Class_Subject_Marks - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Students_Class_Subject_Marks.xlsx`；dest=`Students_Class_Subject_Marks.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/eb03d19a-b88d-4de4-8a64-ca0ac66f426b/Students_Class_Subject_Marks_gold.xlsx`；dest=`Students_Class_Subject_Marks_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## ecb0df7a-4e8d-4a03-b162-053391d3afaf
- 源 JSON：[evaluation_examples/examples_windows/excel/ecb0df7a-4e8d-4a03-b162-053391d3afaf.json](../../../../evaluation_examples/examples_windows/excel/ecb0df7a-4e8d-4a03-b162-053391d3afaf.json)
- 平台/集合：Windows 任务集
- 应用域：`excel`
- snapshot：`excel`
- 相关应用：`excel`
- 来源：https://www.youtube.com/shorts/tXOovKn0H68
- trajectory：`trajectories/ecb0df7a-4e8d-4a03-b162-053391d3afaf`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Enable each cell in the column"Pass/Fail/Held" is a drop down list

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Order_Id_Mark_Pass_Fail.xlsx` 到 `C:\Users\User\Order_Id_Mark_Pass_Fail.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Order_Id_Mark_Pass_Fail.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel` 中执行用户指令。
- 2. 操作重点：在 Excel 中处理电子表格，完成公式、格式、透视表、筛选、图表或导出。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Order_Id_Mark_Pass_Fail.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Order_Id_Mark_Pass_Fail - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Order_Id_Mark_Pass_Fail.xlsx`；dest=`Order_Id_Mark_Pass_Fail.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/excel/ecb0df7a-4e8d-4a03-b162-053391d3afaf/Order_Id_Mark_Pass_Fail%20%281%29.xlsx`；dest=`Order_Id_Mark_Pass_Fail_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": 0, "sheet_idx1": "EI0", "type": "sheet_data"}, {"dv_props": [{"formula1": {"method": "str_set_eq", "ref": ["Pass", "Fail", "Held"]}, "ranges": {"method": "spreadsheet_range", "ref": ["D2:D29", "D2:D1048576"]}, "type": {"method": "eq", "ref": "list"}}], "sheet_idx": 0, "type": "data_validation"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
