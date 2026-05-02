# Windows 任务集 / ppt 详细 case 分析
来源目录：`evaluation_examples/examples_windows/ppt/`。本文件覆盖 7 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 3b27600c-3668-4abd-8f84-7bcdebbccbdb
- 源 JSON：[evaluation_examples/examples_windows/ppt/3b27600c-3668-4abd-8f84-7bcdebbccbdb.json](../../../../evaluation_examples/examples_windows/ppt/3b27600c-3668-4abd-8f84-7bcdebbccbdb.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://www.libreofficehelp.com/change-slide-background-impress/#All_Slides
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`evaluate_presentation_fill_to_rgb_distance`

**Agent 要做什么**
Please make the background blue on all my slides. I was stuck by finding the entrance to do that for a while...

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `lec17-gui-events.pptx` 到 `C:\Users\User\lec17-gui-events.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\lec17-gui-events.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\lec17-gui-events.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `lec17-gui-events - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`evaluate_presentation_fill_to_rgb_distance`。检查演示文稿填充色与目标 RGB 的距离。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\lec17-gui-events.pptx`；dest=`lec17-gui-events.pptx`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"rgb": [0, 0, 255]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 455d3c66-7dc6-4537-a39a-36d3e9119df7
- 源 JSON：[evaluation_examples/examples_windows/ppt/455d3c66-7dc6-4537-a39a-36d3e9119df7.json](../../../../evaluation_examples/examples_windows/ppt/455d3c66-7dc6-4537-a39a-36d3e9119df7.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://stackoverflow.com/questions/75626383/how-export-libreoffice-impress-to-image
- trajectory：`trajectories/455d3c66-7dc6-4537-a39a-36d3e9119df7`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_images`

**Agent 要做什么**
Could you help me export the PowerPoint file to a .png image file and save it as res.png at the same position as the file?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `wssf-project-plan-on-a-page.pptx` 到 `C:\Users\User\wssf-project-plan-on-a-page.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\wssf-project-plan-on-a-page.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\res.png`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `wssf-project-plan-on-a-page - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_images`。比较图片文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\res.png`；dest=`res.png`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/ppt/455d3c66-7dc6-4537-a39a-36d3e9119df7/res.png`；dest=`res_gold.png`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 550ce7e7-747b-495f-b122-acdc4d0b8e54
- 源 JSON：[evaluation_examples/examples_windows/ppt/550ce7e7-747b-495f-b122-acdc4d0b8e54.json](../../../../evaluation_examples/examples_windows/ppt/550ce7e7-747b-495f-b122-acdc4d0b8e54.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://technical-tips.com/blog/software/text-in-libreoffice-strikethrough--6948#:~:text=To%20strikethrough%20Text%20in%20LibreOffice%201%20In%20your,effect%22%20can%20your%20additionally%2C%20for%20example%2C%20double%20underline.
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pptx_files`

**Agent 要做什么**
I am checking our soccer club's to-do list for the last semester and adding strike-through sign on the line we have already accomplished. Could you help me add a strike-through on the first and second line on Page 5?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `New_Club_Spring_2018_Training.pptx` 到 `C:\Users\User\New_Club_Spring_2018_Training.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\New_Club_Spring_2018_Training.pptx`
- 3. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- 4. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; time.sleep(4); pyautogui.doubleClick(x=200, y=650); time.sleep(0.5);pyautogui.mouseDown(); pyautogui.mouseUp(); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\New_Club_Spring_2018_Training.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `New_Club_Spring_2018_Training - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_pptx_files`。比较 PPTX 文件内容和版式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\New_Club_Spring_2018_Training.pptx`；dest=`New_Club_Spring_2018_Training.pptx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/ppt/550ce7e7-747b-495f-b122-acdc4d0b8e54/New_Club_Spring_2018_Training_Gold.pptx`；dest=`New_Club_Spring_2018_Training_Gold.pptx`。
  - 选项/规则：`{"examine_shape": false}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 5d901039-a89c-4bfb-967b-bf66f4df075e
- 源 JSON：[evaluation_examples/examples_windows/ppt/5d901039-a89c-4bfb-967b-bf66f4df075e.json](../../../../evaluation_examples/examples_windows/ppt/5d901039-a89c-4bfb-967b-bf66f4df075e.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://superuser.com/questions/986776/how-can-i-stretch-an-image-in-a-libreoffice-impress-presentation-to-fill-the-pag
- trajectory：`trajectories/5d901039-a89c-4bfb-967b-bf66f4df075e`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`check_image_stretch_and_center`

**Agent 要做什么**
I want to turn the rectangular image of Columbus on the first page into a cover page. Could you help me stretch this image to fill the entire page, keeping its proportion and centering the image?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `CPD_Background_Investigation_Process.pptx` 到 `C:\Users\User\CPD_Background_Investigation_Process.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\CPD_Background_Investigation_Process.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\CPD_Background_Investigation_Process.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `CPD_Background_Investigation_Process - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_image_stretch_and_center`。检查幻灯片图片是否拉伸并居中。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\CPD_Background_Investigation_Process.pptx`；dest=`CPD_Background_Investigation_Process.pptx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/ppt/5d901039-a89c-4bfb-967b-bf66f4df075e/CPD_Background_Investigation_Process.pptx`；dest=`CPD_Background_Investigation_Process_Original.pptx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9ec204e4-f0a3-42f8-8458-b772a6797cab
- 源 JSON：[evaluation_examples/examples_windows/ppt/9ec204e4-f0a3-42f8-8458-b772a6797cab.json](../../../../evaluation_examples/examples_windows/ppt/9ec204e4-f0a3-42f8-8458-b772a6797cab.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://www.tiktok.com/@lil.d1rt_/video/7247574148887629083
- trajectory：`trajectories/9ec204e4-f0a3-42f8-8458-b772a6797cab`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pptx_files`

**Agent 要做什么**
Make a duplicate of the last two slides for me, please.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `MLA_Workshop_061X_Works_Cited.pptx` 到 `C:\Users\User\MLA_Workshop_061X_Works_Cited.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\MLA_Workshop_061X_Works_Cited.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\MLA_Workshop_061X_Works_Cited.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `MLA_Workshop_061X_Works_Cited - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_pptx_files`。比较 PPTX 文件内容和版式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\MLA_Workshop_061X_Works_Cited.pptx`；dest=`MLA_Workshop_061X_Works_Cited.pptx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/ppt/9ec204e4-f0a3-42f8-8458-b772a6797cab/MLA_Workshop_061X_Works_Cited_Gold.pptx`；dest=`MLA_Workshop_061X_Works_Cited_Gold.pptx`。
  - 选项/规则：`{"examine_shape": false}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a097acff-6266-4291-9fbd-137af7ecd439
- 源 JSON：[evaluation_examples/examples_windows/ppt/a097acff-6266-4291-9fbd-137af7ecd439.json](../../../../evaluation_examples/examples_windows/ppt/a097acff-6266-4291-9fbd-137af7ecd439.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://www.youtube.com/watch?v=DDmEvjs4iBw
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pptx_files`

**Agent 要做什么**
Could you help me save my slides as pre.pptx on the Desktop?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Secrets-of-Monetizing-Video.pptx` 到 `C:\Users\User\Downloads\Secrets-of-Monetizing-Video.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Downloads\Secrets-of-Monetizing-Video.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\users\User\Desktop\pre.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_pptx_files`。比较 PPTX 文件内容和版式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\users\User\Desktop\pre.pptx`；dest=`pre.pptx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/ppt/a097acff-6266-4291-9fbd-137af7ecd439/Secrets-of-Monetizing-Video.pptx`；dest=`Secrets-of-Monetizing-Video.pptx`。
  - 选项/规则：`{"examine_shape": false}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## ce88f674-ab7a-43da-9201-468d38539e4a
- 源 JSON：[evaluation_examples/examples_windows/ppt/ce88f674-ab7a-43da-9201-468d38539e4a.json](../../../../evaluation_examples/examples_windows/ppt/ce88f674-ab7a-43da-9201-468d38539e4a.json)
- 平台/集合：Windows 任务集
- 应用域：`ppt`
- snapshot：`ppt`
- 相关应用：`ppt`
- 来源：https://justclickhere.co.uk/resources/change-slides-in-impress-to-portrait/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`check_slide_orientation_Portrait`

**Agent 要做什么**
Please set my slides upright instead of sideways.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `AM_Last_Page_Template.pptx` 到 `C:\Users\User\AM_Last_Page_Template.pptx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\AM_Last_Page_Template.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `ppt` 中执行用户指令。
- 2. 操作重点：在 PowerPoint 中处理演示文稿，完成页面、布局、颜色、导出等操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\AM_Last_Page_Template.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `AM_Last_Page_Template - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`check_slide_orientation_Portrait`。检查幻灯片是否为纵向。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\AM_Last_Page_Template.pptx`；dest=`AM_Last_Page_Template.pptx`。
  - 期望结果：无。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
