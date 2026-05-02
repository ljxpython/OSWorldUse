# Windows 任务集 / multi_app 详细 case 分析
来源目录：`evaluation_examples/examples_windows/multi_app/`。本文件覆盖 22 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 09a37c51-e625-49f4-a514-20a773797a8a
- 源 JSON：[evaluation_examples/examples_windows/multi_app/09a37c51-e625-49f4-a514-20a773797a8a.json](../../../../evaluation_examples/examples_windows/multi_app/09a37c51-e625-49f4-a514-20a773797a8a.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_writer`
- 相关应用：`word, gimp, os`
- 来源：authors
- trajectory：`trajectories/09a37c51-e625-49f4-a514-20a773797a8a`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_images`

**Agent 要做什么**
I've received a request from my friend who asked for assistance in editing an image. The document with the requirements and the picture to be adjusted are on the Desktop. Please make the necessary modifications to the image as his instructions and save the edited picture as "pic.jpg" on the Desktop. Thank you!

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `requirement.docx` 到 `C:\Users\User\Desktop\requirment.docx`；下载 `ChMkKV8wsR6IBfEtABYfc0Tgu9cAAA1lQHO_78AFh-L733.jpg` 到 `C:\Users\User\Desktop\ChMkKV8wsR6IBfEtABYfc0Tgu9cAAA1lQHO_78AFh-L733.jpg`
- 2. `open`：打开指定文件或资源。 打开 `/home/user/Desktop/requirment.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word, gimp, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\pic.jpg`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_images`。比较图片文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\pic.jpg`；dest=`pic.jpg`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/09a37c51-e625-49f4-a514-20a773797a8a/pic.jpg`；dest=`pic_Gold.jpg`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 185f29bd-5da0-40a6-b69c-ba7f4e0324ef
- 源 JSON：[evaluation_examples/examples_windows/multi_app/185f29bd-5da0-40a6-b69c-ba7f4e0324ef.json](../../../../evaluation_examples/examples_windows/multi_app/185f29bd-5da0-40a6-b69c-ba7f4e0324ef.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, os, pdf`
- 来源：authors
- trajectory：`trajectories/185f29bd-5da0-40a6-b69c-ba7f4e0324ef`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pdfs`

**Agent 要做什么**
Transfer the data from our 'Employee Performance Evaluation Summary' Excel sheet into our standardized PDF evaluation forms. Each employee's evaluation data should be accurately filled into the designated fields of the PDF form. It's crucial that the final PDF documents retain a uniform and professional look, ready for distribution to our staff or for filing purposes. Furthermore, please ensure that each PDF file is named according to the employee's name as it appears in the Excel document. This will greatly streamline our evaluation process and enhance our efficiency in managing employee performance records. Oh, use "√" as mark on characters.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Employee%20Performance%20Evaluation%20Summary.xlsx` 到 `C:\Users\User\Desktop\Employee Performance Evaluation Summary.xlsx`；下载 `IC-Simple-Performance-Review-Template-10796_PDF.pdf` 到 `C:\Users\User\Desktop\review_template.pdf`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\Employee Performance Evaluation Summary.xlsx`
- 3. `sleep`：等待界面或后台状态稳定。 等待 2 秒
- 4. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\review_template.pdf`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, os, pdf` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`cloud_file` 的 `['https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/185f29bd-5da0-40a6-b69c-ba7f4e0324ef/Alex%20Lee.pdf', 'https://huggingface.co/dataset...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_pdfs`。比较 PDF 文件。
  - 实际结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`['https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/185f29bd-5da0-40a6-b69c-ba7f4e0324ef/Alex%20Lee.pdf', 'https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/185f29bd-5da0-40a6-b...`；dest=`['Alex Lee_Gold.pdf', 'David Wilson_Gold.pdf', 'Emily Johnson_Gold.pdf', 'John Doe_Gold.pdf', 'Linda Green_Gold.pdf', 'Michael Brown_Gold.pdf', 'Sophia Carter_Gold.pdf']`；其他参数=`{"gives": [0, 1, 2, 3, 4, 5, 6], "multi": true}`。
  - 期望结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`['C:\\Users\\User\\Desktop\\Alex Lee.pdf', 'C:\\Users\\User\\Desktop\\David Wilson.pdf', 'C:\\Users\\User\\Desktop\\Emily Johnson.pdf', 'C:\\Users\\User\\Desktop\\John Doe.pdf', 'C:\\Users\\User\\Desktop\\Linda Green.pdf', 'C:\\Users\\User\\Desktop\\Michael...`；dest=`['Alex Lee.pdf', 'David Wilson.pdf', 'Emily Johnson.pdf', 'John Doe.pdf', 'Linda Green.pdf', 'Michael Brown.pdf', 'Sophia Carter.pdf']`；其他参数=`{"gives": [0, 1, 2, 3, 4, 5, 6], "multi": true}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 1f18aa87-af6f-41ef-9853-cdb8f32ebdea
- 源 JSON：[evaluation_examples/examples_windows/multi_app/1f18aa87-af6f-41ef-9853-cdb8f32ebdea.json](../../../../evaluation_examples/examples_windows/multi_app/1f18aa87-af6f-41ef-9853-cdb8f32ebdea.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`os, word`
- 来源：authors
- trajectory：`trajectories/1f18aa87-af6f-41ef-9853-cdb8f32ebdea`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_files`

**Agent 要做什么**
I've prepared some grammar tests and placed them in the 'Grammar test' folder. I've already provided the multiple-choice answers for Test 1 in the 'answer doc' file. Could you please follow the same format to write out the answers for the remaining two tests in the doc file? This way, I can distribute them to the students as a reference. Thank you.

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir "C:\Users\User\Desktop\students work" "C:\Users\User\Desktop\Lec powerpoint" "C:\Users\User\Desktop\Grammar test" "C:\Users\User\Desktop\Grammar rules PDF" C:\Users\User\Desktop\FDI`；shell=True
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `Grammer%20test%201.docx` 到 `C:\Users\User\Desktop\Grammer test 1.docx`；下载 `Grammar%20test%202.docx` 到 `C:\Users\User\Desktop\Grammer test 2.docx`；下载 `Grammer%20test%203.docx` 到 `C:\Users\User\Desktop\Grammer test 3.docx`；下载 `Answer.docx` 到 `C:\Users\User\Desktop\Answer.docx`；下载 `irregularrules02.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules02.pdf`；下载 `irregularrules01.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules01.pdf`；下载 `fragrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\fragrules.pdf`；下载 `csfsrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\csfsrules.pdf`；下载 `Public%20Lecture%20Teaching%20Plan.docx` 到 `C:\Users\User\Desktop\Public Lecture Teaching Plan.docx`；下载 `Course%20Timetable.xlsx` 到 `C:\Users\User\Desktop\Course Timetable.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `os, word` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\Answer.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Answer - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
- Metric 1：`compare_docx_files`。比较 DOCX 文档内容和格式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\Answer.docx`；dest=`Answer.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/1f18aa87-af6f-41ef-9853-cdb8f32ebdea/Answer_Gold.docx`；dest=`Answer gold.docx`。
  - 选项/规则：`{"ignore_blanks": true, "ignore_case": true}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 26150609-0da3-4a7d-8868-0faf9c5f01bb
- 源 JSON：[evaluation_examples/examples_windows/multi_app/26150609-0da3-4a7d-8868-0faf9c5f01bb.json](../../../../evaluation_examples/examples_windows/multi_app/26150609-0da3-4a7d-8868-0faf9c5f01bb.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`vs_code`
- 相关应用：`vs_code, os`
- 来源：authors
- trajectory：`trajectories/26150609-0da3-4a7d-8868-0faf9c5f01bb`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`check_python_file_by_test_suite`

**Agent 要做什么**
So, I've been dabbling with coding a Snake game in Python, and I finally got it up and running. It's pretty cool, but it's not without its quirks. The biggest issue I'm facing right now is that the snake can't seem to eat the food, no matter what. Could you help me tweak the code so the snake can actually eat the food? Thanks a bunch!

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir -p C:\Users\User\Desktop\snake`；shell=True
- 2. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `pip install pygame`
- 3. `download`：下载文件到 guest，构造任务初始素材。 下载 `food.py` 到 `C:\Users\User\Desktop\snake\food.py`；下载 `main.py` 到 `C:\Users\User\Desktop\snake\main.py`；下载 `settings.py` 到 `C:\Users\User\Desktop\snake\settings.py`；下载 `snake.py` 到 `C:\Users\User\Desktop\snake\snake.py`
- 4. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Users\User\AppData\Local\Programs\Microsoft VS Code\code.exe C:\Users\User\Desktop\snake`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vs_code, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `['C:\\Users\\User\\Desktop\\snake\\food.py', 'C:\\Users\\User\\Desktop\\snake\\main.py', 'C:\\Users\\User\\Desktop\\snake\\settings.py', 'C:\\Users\\User\\Desktop\\snake\\snake....`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_python_file_by_test_suite`。用测试套件检查 Python 文件行为。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`['C:\\Users\\User\\Desktop\\snake\\food.py', 'C:\\Users\\User\\Desktop\\snake\\main.py', 'C:\\Users\\User\\Desktop\\snake\\settings.py', 'C:\\Users\\User\\Desktop\\snake\\snake.py']`；dest=`['food.py', 'main.py', 'settings.py', 'snake.py']`；其他参数=`{"multi": true}`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/26150609-0da3-4a7d-8868-0faf9c5f01bb/test.py`；dest=`test_suite.py`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 26660ad1-6ebb-4f59-8cba-a8432dfe8d38
- 源 JSON：[evaluation_examples/examples_windows/multi_app/26660ad1-6ebb-4f59-8cba-a8432dfe8d38.json](../../../../evaluation_examples/examples_windows/multi_app/26660ad1-6ebb-4f59-8cba-a8432dfe8d38.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`multiapps`
- 相关应用：`os, browser`
- 来源：https://www.speedtest.net/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_time_in_speedtest_results`

**Agent 要做什么**
I want to test the quality of the network environment my laptop is currently in. Please measure my network situation through speedtest.net, export the measurement results, and save them to Documents\Test\Speed (if the dir does not exist, create it).

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec "ncat.exe 127.0.0.1 1337"`；shell=True
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.speedtest.net/`
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Google Chrome`
- 5. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `os, browser` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Documents\Test\Speed\Speedtest Results Export-.csv`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_time_in_speedtest_results`。比较测速结果中的时间。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Test\Speed\Speedtest Results Export-.csv`；dest=`Speedtest Results Export-.csv`；其他参数=`{"time_suffix": true}`。
  - 期望结果 `time_diff_range`：生成时间差范围期望。；其他参数=`{"diff_range_in_minutes": "60"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 2c1ebcd7-9c6d-4c9a-afad-900e381ecd5e
- 源 JSON：[evaluation_examples/examples_windows/multi_app/2c1ebcd7-9c6d-4c9a-afad-900e381ecd5e.json](../../../../evaluation_examples/examples_windows/multi_app/2c1ebcd7-9c6d-4c9a-afad-900e381ecd5e.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`未声明`
- 来源：authors
- trajectory：`trajectories/2c1ebcd7-9c6d-4c9a-afad-900e381ecd5e`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_references`

**Agent 要做什么**
Could you please take a moment to review the 'case study' file located within the 'student work' folder? I'm particularly interested in ensuring that the references section at the end of the document adheres to the APA 7th edition formatting guidelines. Making the necessary adjustments if it turns out that the current formatting does not align with APA 7 standards or exists some errors.

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir "C:\Users\User\Desktop\students work" "C:\Users\User\Desktop\Lec powerpoint" "C:\Users\User\Desktop\Grammar test" "C:\Users\User\Desktop\Grammar rules PDF" C:\Users\User\Desktop\FDI`；shell=True
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `Zheng%20He%20.docx` 到 `C:\Users\User\Desktop\students work\Zheng He .docx`；下载 `The%20literature%20reviews%20of%20weekly%20readings.docx` 到 `C:\Users\User\Desktop\students work\The literature reviews of weekly readings.docx`；下载 `The%20British%20Justice%20System.docx` 到 `C:\Users\User\Desktop\students work\The British Justice System.docx`；下载 `quiz2.docx` 到 `C:\Users\User\Desktop\students work\quiz2.docx`；下载 `quiz.docx` 到 `C:\Users\User\Desktop\students work\quiz.docx`；下载 `Q1%262%263.docx` 到 `C:\Users\User\Desktop\students work\Q1&2&3.docx`；下载 `Photo%20Ethics%20in%20Journalism.docx` 到 `C:\Users\User\Desktop\students work\Photo Ethics in Journalism.docx`；下载 `cassie.docx` 到 `C:\Users\User\Desktop\students work\cassie.docx`；下载 `case%20study.docx` 到 `C:\Users\User\Desktop\students work\case study.docx`；下载 `irregularrules02.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules02.pdf`；下载 `irregularrules01.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules01.pdf`；下载 `fragrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\fragrules.pdf`；下载 `csfsrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\csfsrules.pdf`；下载 `Public%20Lecture%20Teaching%20Plan.docx` 到 `C:\Users\User\Desktop\Public Lecture Teaching Plan.docx`；下载 `Course%20Timetable.xlsx` 到 `C:\Users\User\Desktop\Course Timetable.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `libreoffice_calc` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\students work\case study.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `case study - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
- Metric 1：`compare_references`。比较文档引用/参考文献。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\students work\case study.docx`；dest=`case study.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/2c1ebcd7-9c6d-4c9a-afad-900e381ecd5e/case%20study%20gold.docx`；dest=`case study gold.docx`。
  - 选项/规则：`{"content_only": true, "reference_base_result": 0.6}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 3a93cae4-ad3e-403e-8c12-65303b271818
- 源 JSON：[evaluation_examples/examples_windows/multi_app/3a93cae4-ad3e-403e-8c12-65303b271818.json](../../../../evaluation_examples/examples_windows/multi_app/3a93cae4-ad3e-403e-8c12-65303b271818.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`os, excel`
- 来源：authors
- trajectory：`trajectories/3a93cae4-ad3e-403e-8c12-65303b271818`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table + compare_table + compare_table`

**Agent 要做什么**
Could you please add a two-hour lecture slot to my weekly course timetable, scheduled for every Wednesday at 12 PM? It seems I accidentally omitted that when setting up my schedule. I'd appreciate you taking care of that for me. Thanks!

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir "C:\Users\User\Desktop\students work" "C:\Users\User\Desktop\Lec powerpoint" "C:\Users\User\Desktop\Grammar test" "C:\Users\User\Desktop\Grammar rules PDF" C:\Users\User\Desktop\FDI`；shell=True
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `Zheng%20He%20.docx` 到 `C:\Users\User\Desktop\students work\Zheng He .docx`；下载 `cassie.docx` 到 `C:\Users\User\Desktop\students work\cassie.docx`；下载 `case%20study.docx` 到 `C:\Users\User\Desktop\students work\case study.docx`；下载 `irregularrules02.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules02.pdf`；下载 `irregularrules01.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\irregularrules01.pdf`；下载 `fragrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\fragrules.pdf`；下载 `csfsrules.pdf` 到 `C:\Users\User\Desktop\Grammar rules PDF\csfsrules.pdf`；下载 `Public%20Lecture%20Teaching%20Plan.docx` 到 `C:\Users\User\Desktop\Public Lecture Teaching Plan.docx`；下载 `Course%20Timetable.xlsx` 到 `C:\Users\User\Desktop\Course Timetable.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `os, excel` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\Course Timetable.xlsx`；`vm_file` 的 `C:\Users\User\Desktop\Course Timetable.xlsx`；`vm_file` 的 `C:\Users\User\Desktop\Course Timetable.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`or`；共 3 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Course Timetable - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\Course Timetable.xlsx`；dest=`Course Timetable.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/3a93cae4-ad3e-403e-8c12-65303b271818/Course%20Timetable%20Gold.xlsx`；dest=`Course Timetable gold.xlsx`。
  - 选项/规则：`{"rules": [{"ignore_case": true, "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_data"}]}`。
- Metric 2：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\Course Timetable.xlsx`；dest=`Course Timetable.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/3a93cae4-ad3e-403e-8c12-65303b271818/Course%20Timetable%20Gold%202.xlsx`；dest=`Course Timetable gold 2.xlsx`。
  - 选项/规则：`{"rules": [{"ignore_case": true, "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_data"}]}`。
- Metric 3：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\Course Timetable.xlsx`；dest=`Course Timetable.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/3a93cae4-ad3e-403e-8c12-65303b271818/Course%20Timetable%20Gold%203.xlsx`；dest=`Course Timetable gold 3.xlsx`。
  - 选项/规则：`{"rules": [{"ignore_case": true, "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_data"}]}`。
- 通过条件：任一 metric 通过即可整体通过。

## 46407397-a7d5-4c6b-92c6-dbe038b1457b
- 源 JSON：[evaluation_examples/examples_windows/multi_app/46407397-a7d5-4c6b-92c6-dbe038b1457b.json](../../../../evaluation_examples/examples_windows/multi_app/46407397-a7d5-4c6b-92c6-dbe038b1457b.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`chrome`
- 相关应用：`thunderbird, chrome`
- 来源：https://marketplace.uipath.com/listings/merge-pdfs-from-gmail-email-attachments-and-upload-to-gogle-drive
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_image_list`

**Agent 要做什么**
Help me export charts, graph or other images from docx files received in email "Lecture Document" in Notes folder and upload these png files to the figures/ folder in Google Drive for later use (use numbers to name them).

**前置/初始状态**
- 1. `googledrive`：调用 Google Drive 配置/接口准备云端文件状态。 使用 `evaluation_examples/settings/googledrive/settings.yml` 执行 `["delete"]`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec "ncat.exe 127.0.0.1 1337"`；shell=True
- 4. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://news.google.com`, `https://x.com`
- 5. `login`：准备登录态或执行登录相关 setup。 登录配置 `{"platform": "googledrive", "settings_file": "evaluation_examples/settings/google/settings.json"}`
- 6. `download`：下载文件到 guest，构造任务初始素材。 下载 `file_1Yy-ZrkMq4pIQq1Y75bD2WVJXxHMTaMqE.7z` 到 `C:\Users\User\thunderbird-profile.7z`
- 7. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `C:\Program Files\7-Zip\7z.exe x C:\Users\User\thunderbird-profile.7z`
- 8. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `rd /s /q C:\Users\User\AppData\Roaming\Thunderbird`；shell=True
- 9. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `move C:\Users\User\Thunderbird C:\Users\User\AppData\Roaming\Thunderbird`；shell=True
- 10. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Mozilla Thunderbird\thunderbird.exe`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird, chrome` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`googledrive_file` 状态 `{"dest": ["1.png", "2.png", "3.png"], "query_list": [["title = 'figures' and trashed = false and 'root' in parents and mimeType = 'application/vnd.google-apps.folder'", "title =...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_image_list`。比较图片文件列表。
  - 实际结果 `googledrive_file`：从 Google Drive 获取文件状态或内容。；dest=`['1.png', '2.png', '3.png']`；其他参数=`{"query_list": [["title = 'figures' and trashed = false and 'root' in parents and mimeType = 'application/vnd.google-apps.folder'", "title = '1.png' and trashed = false"], ["title = 'figures' and trashed = false and 'root' in parents and mimeType = 'application/vnd.google-apps.folder'", "title = '2.png' and trashed = false"], ["title = 'figures' and trash...`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`['https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/46407397-a7d5-4c6b-92c6-dbe038b1457b/1.png', 'https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/46407397-a7d5-4c6b-92c6-dbe03...`；dest=`['1_gold.png', '2_gold.png', '3_gold.png']`；其他参数=`{"gives": [0, 1, 2], "multi": true}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 6d72aad6-187a-4392-a4c4-ed87269c51cf
- 源 JSON：[evaluation_examples/examples_windows/multi_app/6d72aad6-187a-4392-a4c4-ed87269c51cf.json](../../../../evaluation_examples/examples_windows/multi_app/6d72aad6-187a-4392-a4c4-ed87269c51cf.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, powerpoint, word, vlc`
- 来源：https://superuser.com/questions/923171/converting-openoffice-impress-presentation-to-video-without-screen-recording
- trajectory：`trajectories/6d72aad6-187a-4392-a4c4-ed87269c51cf`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`infeasible`

**Agent 要做什么**
Could you please converting MS Office PowerPoint presentation to video and play it with VLC?

**前置/初始状态**
- 无显式前置动作；任务从对应 snapshot 的默认环境开始。

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## 6f4073b8-d8ea-4ade-8a18-c5d1d5d5aa9a
- 源 JSON：[evaluation_examples/examples_windows/multi_app/6f4073b8-d8ea-4ade-8a18-c5d1d5d5aa9a.json](../../../../evaluation_examples/examples_windows/multi_app/6f4073b8-d8ea-4ade-8a18-c5d1d5d5aa9a.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`multiapps`
- 相关应用：`excel, chrome, os`
- 来源：author
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_conference_city_in_order`

**Agent 要做什么**
I now want to count the meeting cities of the three machine learning conferences in the past ten years from 2013 to 2019(including 2013 and 2019). I have listed the names and years of the conferences in excel. Please fill in the vacant locations.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Conference.xlsx` 到 `C:\Users\User\Desktop\ConferenceCity.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\ConferenceCity.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, chrome, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\ConferenceCity.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `ConferenceCity%20Gold.xlsx` 到 `C:\Users\User\Desktop\ConferenceCity_Gold.xlsx`
  - 2. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `ConferenceCity - Excel`
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
- Metric 1：`compare_conference_city_in_order`。检查会议城市排序。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\ConferenceCity.xlsx`；dest=`ConferenceCity.xlsx`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected": ["Scottsdale", "Atlanta", "Lake Tahoe", "Banff", "Beijing", ["Montreal", "Montréal"], "San Diego", "Lille", ["Montreal", "Montréal"], "San Juan", ["New York", "New York City", "NYC"], "Barcelona", "Toulon", "Sydney", "Long Beach", "Vancouver", "Stockholm", ["Montreal", "Montréal"], "New Orleans", "Long Beach", "Vancouver"]}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 74d5859f-ed66-4d3e-aa0e-93d7a592ce41
- 源 JSON：[evaluation_examples/examples_windows/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41.json](../../../../evaluation_examples/examples_windows/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`chrome`
- 相关应用：`chrome, os`
- 来源：authors
- trajectory：`trajectories/74d5859f-ed66-4d3e-aa0e-93d7a592ce41`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`check_json + diff_text_file + diff_text_file + diff_text_file + diff_text_file`

**Agent 要做什么**
Help me to set up an initial web extension project with help of the web tool, tagging it "happy-extension v0.0.1". Leave description blank for now. Include a background script and browser action, while other features are not required. Remember to unzip the auto-generated folder into "Documents\Projects".

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec "ncat.exe 127.0.0.1 1337"`；shell=True
- 3. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://webext.eu`
- 4. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `mkdir C:\Users\User\Documents\Projects`；shell=true
- 5. `launch`：启动指定应用或后台辅助进程。 命令 `explorer.exe C:\Users\User\Documents\Projects`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让多个可评测结果全部生成，重点包括：`vm_file` 的 `C:\Users\User\Documents\Projects\happy-extension\manifest.json`；`vm_file` 的 `C:\Users\User\Documents\Projects\happy-extension\background_script.js`；`vm_file` 的 `C:\Users\User\Documents\Projects\happy-extension\browserAction\index.html`；`vm_file` 的 `C:\Users\User\Documents\Projects\happy-extension\browserAction\style.css` 等 5 项。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 5 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_json`。检查 JSON/YAML 内容是否满足规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Projects\happy-extension\manifest.json`；dest=`manifest.json`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": [{"key": ["name"], "method": "eq", "ref": "happy-extension"}, {"key": ["version"], "method": "eq", "ref": "0.0.1"}, {"key": ["background", "scripts"], "method": "eq", "ref": ["background_script.js"]}, {"key": ["browser_action", "default_icon"], "method": "eq", "ref": {"64": "icons/icon.png"}}, {"key": ["browser_action", "default_popup"], "method": "eq", "ref": "browserAction/index.html"}, {"key": ["brow...`。
  - 选项/规则：无额外 options。
- Metric 2：`diff_text_file`。对文本文件做 diff 检查。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Projects\happy-extension\background_script.js`；dest=`background_script.js`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41/Google%20Drive%20-%20Virus%20scan%20warning.bin`；dest=`background_script.js`。
  - 选项/规则：无额外 options。
- Metric 3：`diff_text_file`。对文本文件做 diff 检查。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Projects\happy-extension\browserAction\index.html`；dest=`index.html`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41/index.html`；dest=`index.html`。
  - 选项/规则：无额外 options。
- Metric 4：`diff_text_file`。对文本文件做 diff 检查。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Projects\happy-extension\browserAction\style.css`；dest=`style.css`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41/style.css`；dest=`style.css`。
  - 选项/规则：无额外 options。
- Metric 5：`diff_text_file`。对文本文件做 diff 检查。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Projects\happy-extension\browserAction\script.js`；dest=`script.js`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/74d5859f-ed66-4d3e-aa0e-93d7a592ce41/Google%20Drive%20-%20Virus%20scan%20warning.bin`；dest=`script.js`。
  - 选项/规则：无额外 options。
- 通过条件：所有 metric 都通过才整体通过。

## 897e3b53-5d4d-444b-85cb-2cdc8a97d903
- 源 JSON：[evaluation_examples/examples_windows/multi_app/897e3b53-5d4d-444b-85cb-2cdc8a97d903.json](../../../../evaluation_examples/examples_windows/multi_app/897e3b53-5d4d-444b-85cb-2cdc8a97d903.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`chrome`
- 相关应用：`word, chrome`
- 来源：https://marketplace.uipath.com/listings/convert-word-file-to-pdf-and-store-in-onedrive
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pdfs`

**Agent 要做什么**
I have a LibreOffice Writer file form.docx on the desktop. Help me convert it to PDF format and store the PDF in the forms/ folder in my Google Drive.

**前置/初始状态**
- 1. `googledrive`：调用 Google Drive 配置/接口准备云端文件状态。 使用 `evaluation_examples/settings/googledrive/settings.yml` 执行 `["delete"]`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec "ncat.exe 127.0.0.1 1337"`；shell=True
- 4. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://www.zhihu.com/`, `https://www.coursera.org/`, `https://www.deepl.com`, `https://www.wikidata.org/wiki/Wikidata:Main_Page`
- 5. `login`：准备登录态或执行登录相关 setup。 登录配置 `{"platform": "googledrive", "settings_file": "evaluation_examples/settings/google/settings.json"}`
- 6. `download`：下载文件到 guest，构造任务初始素材。 下载 `form.docx` 到 `C:\Users\User\Desktop\form.docx`
- 7. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\form.docx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `word, chrome` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`googledrive_file` 状态 `{"dest": "form.pdf", "query": ["title = 'forms' and mimeType = 'application/vnd.google-apps.folder' and trashed = false", "( title = 'form.pdf' or title = 'form.docx.pdf' ) and ...`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_pdfs`。比较 PDF 文件。
  - 实际结果 `googledrive_file`：从 Google Drive 获取文件状态或内容。；dest=`form.pdf`；其他参数=`{"query": ["title = 'forms' and mimeType = 'application/vnd.google-apps.folder' and trashed = false", "( title = 'form.pdf' or title = 'form.docx.pdf' ) and trashed = false"], "settings_file": "evaluation_examples/settings/googledrive/settings.yml"}`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/897e3b53-5d4d-444b-85cb-2cdc8a97d903/form_gold.pdf`；dest=`form_gold.pdf`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 8e116af7-7db7-4e35-a68b-b0939c066c78
- 源 JSON：[evaluation_examples/examples_windows/multi_app/8e116af7-7db7-4e35-a68b-b0939c066c78.json](../../../../evaluation_examples/examples_windows/multi_app/8e116af7-7db7-4e35-a68b-b0939c066c78.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, os, image, pdf`
- 来源：authors
- trajectory：`trajectories/8e116af7-7db7-4e35-a68b-b0939c066c78`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Please update my bookkeeping sheet with the recent transactions from the provided folder, detailing my expenses over the past few days.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `my_bookkeeping.xlsx` 到 `C:\Users\User\Desktop\my_bookkeeping.xlsx`；下载 `receipt_0.jpeg` 到 `C:\Users\User\Desktop\receipt_0.jpeg`；下载 `receipt_1.jpg` 到 `C:\Users\User\Desktop\receipt_1.jpg`；下载 `receipt_2.jpg` 到 `C:\Users\User\Desktop\receipt_2.jpg`；下载 `receipt_3.pdf` 到 `C:\Users\User\Desktop\receipt_3.pdf`；下载 `receipt_4.jpg` 到 `C:\Users\User\Desktop\receipt_4.jpg`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\my_bookkeeping.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, os, image, pdf` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\my_bookkeeping.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `my_bookkeeping - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 1.0 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\my_bookkeeping.xlsx`；dest=`my_bookkeeping.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/8e116af7-7db7-4e35-a68b-b0939c066c78/my_bookkeeping%20Gold.xlsx`；dest=`my_bookkeeping_gold.xlsx`。
  - 选项/规则：`{"rules": [{"rules": [{"range": ["A1:A8", "B1:B8", "C1:C8", "D1:D8", "E1:E8"], "type": "exact_match"}], "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_fuzzy"}, {"rules": [{"ignore_case": true, "range": ["C9:C13"], "type": "exact_match"}], "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_fuzzy"}, {"coordinate": "D9", "props": {"value": {"method": "approx:0.1", "ref": -186.93}}, "sheet_idx": 0, "type": "check_cell"}, {"coordinate": "D10", "props": {"value": {"method": "approx:0.1", "ref": -3670}}, "sheet_idx": 0, "type": "check_cell"}, {"coordinate": "D11", "props": {"value": {"method": "approx:0.1", "ref": -5.7}}, "sheet_idx": 0, "type": "check_cell"}, {"coordinate": "D12", "props": {"value": {"method": "approx:0.1", "ref": -154.0...`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a82b78bb-7fde-4cb3-94a4-035baf10bcf0
- 源 JSON：[evaluation_examples/examples_windows/multi_app/a82b78bb-7fde-4cb3-94a4-035baf10bcf0.json](../../../../evaluation_examples/examples_windows/multi_app/a82b78bb-7fde-4cb3-94a4-035baf10bcf0.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`chrome, pdf`
- 来源：authors
- trajectory：`trajectories/a82b78bb-7fde-4cb3-94a4-035baf10bcf0`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`is_expected_bookmarks`

**Agent 要做什么**
I'm really enjoying this paper. Could you please locate the personal webpages of the initial author and the last three authors? Please include them in a browser bookmark folder titled 'Liked Authors.'

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec ncat.exe 127.0.0.1 1337`
- 3. `sleep`：等待界面或后台状态稳定。 等待 2 秒
- 4. `download`：下载文件到 guest，构造任务初始素材。 下载 `2206.08853.pdf` 到 `C:\Users\User\Desktop\2206.08853.pdf`
- 5. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\2206.08853.pdf`
- 6. `sleep`：等待界面或后台状态稳定。 等待 5 秒
- 7. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click(500, 500); pyautogui.hotkey('f11'); time.sleep(0.5); pyautogui.click(960, 540); time.sleep(0.5); pyautogui.scroll(-20)`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome, pdf` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`bookmarks` 状态 `{"type": "bookmarks"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_expected_bookmarks`。检查 Chrome 书签状态。
  - 实际结果 `bookmarks`：读取 Chrome 书签状态。。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"names": ["Liked Authors"], "type": "liked_authors_websites_urls", "urls": [["https://jimfan.me/", "https://research.nvidia.com/person/linxi-jim-fan"], ["https://research.nvidia.com/person/de-an-huang", "https://ai.stanford.edu/~dahuang/"], ["https://yukezhu.me/", "https://www.cs.utexas.edu/people/faculty-researchers/yuke-zhu", "https://experts.utexas.edu/yuke_zhu", "https://research.nvidia.com/person/yuke-zhu"],...`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## b5062e3e-641c-4e3a-907b-ac864d2e7652
- 源 JSON：[evaluation_examples/examples_windows/multi_app/b5062e3e-641c-4e3a-907b-ac864d2e7652.json](../../../../evaluation_examples/examples_windows/multi_app/b5062e3e-641c-4e3a-907b-ac864d2e7652.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, os`
- 来源：authors
- trajectory：`trajectories/b5062e3e-641c-4e3a-907b-ac864d2e7652`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Please help me to extract the name, e-mail, and affiliation of the first author from each paper in the folder and organize them in an Excel table. Include headers for each field. Sort the authors by their full names alphabetically and save the table as "Documents\authors.xlsx".

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir C:\Users\User\Documents\Papers`；shell=True
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `2312.13771.pdf` 到 `C:\Users\User\Documents\Papers\zhang_appagent.pdf`；下载 `2402.07945.pdf` 到 `C:\Users\User\Documents\Papers\niu_screenagent.pdf`；下载 `2401.13649.pdf` 到 `C:\Users\User\Documents\Papers\koh_visualwebarena.pdf`；下载 `5950bf290a1570ea401bf98882128160-Paper-Datasets_and_Benchmarks.pdf` 到 `C:\Users\User\Documents\Papers\deng_mind2web.pdf`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `explorer.exe C:\Users\User\Documents\Papers`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\authors.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\authors.xlsx`；dest=`authors.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/b5062e3e-641c-4e3a-907b-ac864d2e7652/authors-gt.xlsx`；dest=`authors-gt.xlsx`。
  - 选项/规则：`{"rules": [{"rules": [{"ignore_case": true, "range": ["A1:C1"], "type": "includes"}, {"range": ["A2:B5"], "trim_leadings": " ", "trim_trailings": " ", "type": "exact_match"}, {"ignore_case": true, "range": ["C2:C5"], "trim_leadings": " ", "trim_trailings": " ", "type": "exact_match"}], "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_fuzzy"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## c867c42d-a52d-4a24-8ae3-f75d256b5618
- 源 JSON：[evaluation_examples/examples_windows/multi_app/c867c42d-a52d-4a24-8ae3-f75d256b5618.json](../../../../evaluation_examples/examples_windows/multi_app/c867c42d-a52d-4a24-8ae3-f75d256b5618.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`thunderbird`
- 相关应用：`thunderbird, excel`
- 来源：https://www.sync.blue/en/sync/mozilla-thunderbird/google-sheets/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_csv + compare_table`

**Agent 要做什么**
Please assist me in exporting my contacts of Personal Address Book from Thunderbird into contacts.csv file in the desktop and convert it to .xlsx with Libreoffice Calc.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE`
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `thunderbird-profile-win.7z` 到 `C:\Users\User\thunderbird-profile.7z`
- 3. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `C:\Program Files\7-Zip\7z x C:\Users\User\thunderbird-profile.7z -oC:\Users\User`
- 4. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `rd /s /q C:\Users\User\AppData\Roaming\Thunderbird`；shell=True
- 5. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `move C:\Users\User\Thunderbird C:\Users\User\AppData\Roaming\Thunderbird`；shell=True
- 6. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Mozilla Thunderbird\thunderbird.exe`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `thunderbird, excel` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\contacts.csv`；`vm_file` 的 `C:\Users\User\Desktop\contacts.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 2 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_csv`。比较实际 CSV 和参考 CSV。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\contacts.csv`；dest=`contacts.csv`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/c867c42d-a52d-4a24-8ae3-f75d256b5618/contacts.csv`；dest=`contacts_gold.csv`。
  - 选项/规则：无额外 options。
- Metric 2：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\contacts.xlsx`；dest=`contacts.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/c867c42d-a52d-4a24-8ae3-f75d256b5618/contacts.xlsx`；dest=`contacts_gold.xlsx`。
  - 选项/规则：`{"rules": [{"sheet_idx0": "RI0", "sheet_idx1": "EI0", "type": "sheet_data"}]}`。
- 通过条件：所有 metric 都通过才整体通过。

## d1acdb87-bb67-4f30-84aa-990e56a09c92
- 源 JSON：[evaluation_examples/examples_windows/multi_app/d1acdb87-bb67-4f30-84aa-990e56a09c92.json](../../../../evaluation_examples/examples_windows/multi_app/d1acdb87-bb67-4f30-84aa-990e56a09c92.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`os, chrome, excel`
- 来源：authors
- trajectory：`trajectories/d1acdb87-bb67-4f30-84aa-990e56a09c92`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Hello! I'm eagerly planning a culinary adventure to Hong Kong and have curated a list of must-visit restaurants that I've been longing to explore. However, I could use some assistance in compiling a few essential details about these establishments. Would you be so kind as to help me out? It would be fantastic if you could search for these restaurants on Google Maps. I'm particularly interested in obtaining their addresses, any available websites, and contact phone numbers. If you could gather this information and input it into my form file, I would be immensely grateful. Many thanks in advance!

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `restaurants.txt` 到 `C:\Users\User\Desktop\restaurants.txt`；下载 `MUST_VISIT.xlsx` 到 `C:\Users\User\Desktop\MUST_VISIT.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\MUST_VISIT.xlsx`
- 3. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\restaurants.txt`
- 4. `sleep`：等待界面或后台状态稳定。 等待 5 秒
- 5. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `restaurants.txt`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `os, chrome, excel` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\MUST_VISIT.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `MUST_VISIT - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 1.0 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\MUST_VISIT.xlsx`；dest=`MUST_VISIT.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/d1acdb87-bb67-4f30-84aa-990e56a09c92/MUST_VISIT_gold.xlsx`；dest=`MUST_VISIT-gt.xlsx`。
  - 选项/规则：`{"rules": [{"rules": [{"range": ["A1:A6", "D1:D6"], "type": "exact_match"}, {"ignore_case": true, "normalization": [["Rd", "Road"], ["St", "Street"]], "range": ["B1:B6"], "threshold": 85, "type": "fuzzy_match"}, {"ignore_chars": " ()-", "range": ["C1:C6"], "trim_leadings": "+ ", "type": "includes"}], "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_fuzzy"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## da52d699-e8d2-4dc5-9191-a2199e0b6a9b
- 源 JSON：[evaluation_examples/examples_windows/multi_app/da52d699-e8d2-4dc5-9191-a2199e0b6a9b.json](../../../../evaluation_examples/examples_windows/multi_app/da52d699-e8d2-4dc5-9191-a2199e0b6a9b.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, chrome, word`
- 来源：GAIA
- trajectory：`trajectories/da52d699-e8d2-4dc5-9191-a2199e0b6a9b`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_docx_files`

**Agent 要做什么**
Examine the spreadsheet on the desktop, which contains a record of books read in 2022. Take the website https://howlongtoread.com/ as a reference to identify the book with the slowest reading pace, measured in words per day. I have an empty document named 'book_list_result.docx' on the desktop; please open it and record the title there.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `2023_validation_Book_Reading_Rate.xlsx` 到 `C:\Users\User\Desktop\2023_validation_Book_Reading_Rate.xlsx`；下载 `book_list_result.docx` 到 `C:\Users\User\Desktop\book_list_result.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\2023_validation_Book_Reading_Rate.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, chrome, word` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\book_list_result.docx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `book_list_result - Word`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_docx_files`。比较 DOCX 文档内容和格式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\book_list_result.docx`；dest=`book_list_result.docx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/da52d699-e8d2-4dc5-9191-a2199e0b6a9b/book_list_result_Gold.docx`；dest=`book_list_result_Gold.docx`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## deec51c9-3b1e-4b9e-993c-4776f20e8bb2
- 源 JSON：[evaluation_examples/examples_windows/multi_app/deec51c9-3b1e-4b9e-993c-4776f20e8bb2.json](../../../../evaluation_examples/examples_windows/multi_app/deec51c9-3b1e-4b9e-993c-4776f20e8bb2.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_calc`
- 相关应用：`excel, chrome, os`
- 来源：authors
- trajectory：`trajectories/deec51c9-3b1e-4b9e-993c-4776f20e8bb2`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_table`

**Agent 要做什么**
Find a paper list of all the new foundation language models issued on 11st Oct. 2023 via arxiv daily, and organize it into the sheet I opened.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `New%20Large%20Language%20Models.xlsx` 到 `C:\Users\User\Desktop\New Large Language Models.xlsx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\New Large Language Models.xlsx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `excel, chrome, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\New Large Language Models.xlsx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `New Large Language Models - Excel`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 1.0 秒
- Metric 1：`compare_table`。比较表格/工作簿内容、公式、格式、透视表或图表等规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\New Large Language Models.xlsx`；dest=`New Large Language Models.xlsx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/deec51c9-3b1e-4b9e-993c-4776f20e8bb2/New%20Large%20Language%20Models%20Gold.xlsx`；dest=`New Large Language Models Gold.xlsx`。
  - 选项/规则：`{"rules": [{"rules": [{"range": ["B2:B5", "C2:C5"], "type": "exact_match"}, {"ignore_case": true, "range": ["A2:A5"], "threshold": 90, "type": "fuzzy_match"}], "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1", "type": "sheet_fuzzy"}]}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## e2392362-125e-4f76-a2ee-524b183a3412
- 源 JSON：[evaluation_examples/examples_windows/multi_app/e2392362-125e-4f76-a2ee-524b183a3412.json](../../../../evaluation_examples/examples_windows/multi_app/e2392362-125e-4f76-a2ee-524b183a3412.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`chrome`
- 相关应用：`chrome, os, vscode`
- 来源：authors
- trajectory：`trajectories/e2392362-125e-4f76-a2ee-524b183a3412`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`check_json`

**Agent 要做什么**
I recently started using the famous personal academic homepage template from academicpages.github.io to build my own personal homepage, and I have cloned it to my local Documents\Code\Website folder. According to an online tutorial, I can configure my name and contact information in the _config.yaml file. However, I am not familiar with the YAML file format. Please help me find the sections related to the name and contact information in this file and change them to "Test Account" and "Test@gmail.com".

**前置/初始状态**
- 1. `command`：执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 命令 `mkdir C:\Users\User\Documents\Code\Website`；shell=True
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `academicpages.github.io.7z` 到 `C:\Users\User\.tmp.7z`
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `C:\Program Files\7-Zip\7z.exe x -oC:\Users\User\Documents\Code\Website C:\Users\User\.tmp.7z`
- 4. `launch`：启动指定应用或后台辅助进程。 命令 `C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=1337`
- 5. `launch`：启动指定应用或后台辅助进程。 命令 `ncat.exe -k -l 0.0.0.0 9222 --sh-exec "ncat.exe 127.0.0.1 1337"`；shell=True
- 6. `chrome_open_tabs`：在 Chrome 中打开指定标签页。 打开标签页：`https://academicpages.github.io/`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `chrome, os, vscode` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Documents\Code\Website\academicpages.github.io\_config.yml`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey('ctrl', 's'); time.sleep(0.5);`
- Metric 1：`check_json`。检查 JSON/YAML 内容是否满足规则。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Documents\Code\Website\academicpages.github.io\_config.yml`；dest=`_config.yaml`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expect": [{"key": ["name"], "method": "eq", "ref": "Test Account"}, {"key": ["author", "name"], "method": "eq", "ref": "Test Account"}, {"key": ["author", "email"], "method": "eq", "ref": "Test@gmail.com"}]}`。
  - 选项/规则：`{"is_yaml": true}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## eb303e01-261e-4972-8c07-c9b4e7a4922a
- 源 JSON：[evaluation_examples/examples_windows/multi_app/eb303e01-261e-4972-8c07-c9b4e7a4922a.json](../../../../evaluation_examples/examples_windows/multi_app/eb303e01-261e-4972-8c07-c9b4e7a4922a.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`libreoffice_impress`
- 相关应用：`powerpoint, word`
- 来源：authors
- trajectory：`trajectories/eb303e01-261e-4972-8c07-c9b4e7a4922a`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_pptx_files`

**Agent 要做什么**
Tomorrow, I'm scheduled to deliver a talk, and my PowerPoint slides and speaking notes are saved on the desktop. Help me insert my planned remarks for each slide into the "note" section of the PowerPoint as a reminder. I've completed this task for some slides; assist me in completing the remaining part.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `lecture1-2021-with-ink.pptx` 到 `C:\Users\User\Desktop\lecture1-2021-with-ink.pptx`；下载 `notes.docx` 到 `C:\Users\User\Desktop\notes.docx`
- 2. `open`：打开指定文件或资源。 打开 `C:\Users\User\Desktop\lecture1-2021-with-ink.pptx`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `powerpoint, word` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\lecture1-2021-with-ink.pptx`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `lecture1-2021-with-ink - PowerPoint`；strict=True
  - 2. `sleep`：等待界面或后台状态稳定。 等待 5 秒
  - 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.hotkey("ctrl", "s"); time.sleep(0.5); pyautogui.press("enter");`
  - 4. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- Metric 1：`compare_pptx_files`。比较 PPTX 文件内容和版式。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\lecture1-2021-with-ink.pptx`；dest=`lecture1-2021-with-ink.pptx`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/eb303e01-261e-4972-8c07-c9b4e7a4922a/lecture1-2021-with-ink_Gold.pptx`；dest=`lecture1-2021-with-ink_Gold.pptx`。
  - 选项/规则：`{"examine_bullets": false, "examine_shape": false}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f918266a-b3e0-4914-865d-4faa564f1aef
- 源 JSON：[evaluation_examples/examples_windows/multi_app/f918266a-b3e0-4914-865d-4faa564f1aef.json](../../../../evaluation_examples/examples_windows/multi_app/f918266a-b3e0-4914-865d-4faa564f1aef.json)
- 平台/集合：Windows 任务集
- 应用域：`multi_app`
- snapshot：`vscode`
- 相关应用：`vscode, os`
- 来源：GAIA
- trajectory：`trajectories/f918266a-b3e0-4914-865d-4faa564f1aef`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`未声明`
- 评测函数：`compare_text_file`

**Agent 要做什么**
Please complete the code and retrieve the output from the Python script 'calculator.py' located on the desktop and save it as 'log.txt' in the same directory as the Python file.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `calculator.zip` 到 `C:\Users\User\Desktop\calculator.zip`
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `C:\Program Files\7-Zip\7z.exe x C:\Users\User\Desktop\calculator.zip -oC:\Users\User\Desktop`
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `del C:\Users\User\Desktop\calculator.zip`；shell=True

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vscode, os` 中执行用户指令。
- 2. 操作重点：在多个 Windows 应用之间搬运信息或产物，完成跨应用编辑、导出、转换等流程。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `C:\Users\User\Desktop\log.txt`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_text_file`。比较文本文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`C:\Users\User\Desktop\log.txt`；dest=`log.txt`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/windows_osworld_file_cache/resolve/main/multi_app/f918266a-b3e0-4914-865d-4faa564f1aef/log_Gold.txt`；dest=`log_Gold.txt`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
