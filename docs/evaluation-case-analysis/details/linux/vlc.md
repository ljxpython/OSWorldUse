# Linux/Ubuntu 主任务集 / vlc 详细 case 分析
来源目录：`evaluation_examples/examples/vlc/`。本文件覆盖 17 个 case。

说明：`过程` 是根据 `instruction`、`config`、`evaluator` 推断出的操作路径；如果需要真实点击轨迹，要看 trajectory 数据，而不是把这里当录像脚本。

## 215dfd39-f493-4bc3-a027-8a97d72c61bf
- 源 JSON：[evaluation_examples/examples/vlc/215dfd39-f493-4bc3-a027-8a97d72c61bf.json](../../../../evaluation_examples/examples/vlc/215dfd39-f493-4bc3-a027-8a97d72c61bf.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/1224784/how-to-change-vlcs-splash-screen
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_qt_bgcone`

**Agent 要做什么**
Can you disable the cone icon in the splash screen? I am tired of its skeuomorphic design.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_qt_bgcone`。检查 VLC 背景锥图配置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_qt_bgcone": 0}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 386dbd0e-0241-4a0a-b6a2-6704fba26b1c
- 源 JSON：[evaluation_examples/examples/vlc/386dbd0e-0241-4a0a-b6a2-6704fba26b1c.json](../../../../evaluation_examples/examples/vlc/386dbd0e-0241-4a0a-b6a2-6704fba26b1c.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/1708415/pause-and-play-vlc-in-background?rq=1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_global_key_play_pause`

**Agent 要做什么**
I am reading lecture note in PDF while a music video is running in VLC media player. But I find I need to switch to the player every time I need to pause/start.Could you help me change the setting to allow pausing the video using keyboard shortcut without minimizing the PDF reader? I want to focus on the lecture note and don't be disturbed by the app switching.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `lecture_pdf.pdf` 到 `/home/user/Desktop/lecture.pdf`
- 2. `download`：下载文件到 guest，构造任务初始素材。 下载 `Colorful-Flowers%28chosic.com%29.mp3` 到 `/home/user/Desktop/Colorful-Flowers.mp3`
- 3. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show --start-time=10 /home/user/Desktop/Colorful-Flowers.mp3`；shell=True
- 4. `open`：打开指定文件或资源。 打开 `/home/user/Desktop/lecture.pdf`
- 5. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `lecture.pdf — 6.006 Introduction to Algorithms, Lecture 2: Data Structures`；strict=True
- 6. `sleep`：等待界面或后台状态稳定。 等待 0.5 秒
- 7. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; pyautogui.press('f11');`
- 8. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_global_key_play_pause`。检查 VLC 全局播放/暂停快捷键。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_global_key_play_pause": 1}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 59f21cfb-0120-4326-b255-a5b827b38967
- 源 JSON：[evaluation_examples/examples/vlc/59f21cfb-0120-4326-b255-a5b827b38967.json](../../../../evaluation_examples/examples/vlc/59f21cfb-0120-4326-b255-a5b827b38967.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://docs.videolan.me/vlc-user/desktop/3.0/en/basic/media.html#playing-a-file
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_vlc_playing`

**Agent 要做什么**
Could you play the music video that's saved on my desktop for me via vlc?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28Official%20Music%20Video%29.mp4` 到 `/home/user/Desktop/Rick Astley - Never Gonna Give You Up (Official Music Video).mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_playing_info` 状态 `{"dest": "status.xml", "type": "vlc_playing_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_vlc_playing`。检查 VLC 播放状态。
  - 实际结果 `vlc_playing_info`：读取 VLC 播放状态。；dest=`status.xml`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"file_name": "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4", "type": "file_name"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 5ac2891a-eacd-4954-b339-98abba077adb
- 源 JSON：[evaluation_examples/examples/vlc/5ac2891a-eacd-4954-b339-98abba077adb.json](../../../../evaluation_examples/examples/vlc/5ac2891a-eacd-4954-b339-98abba077adb.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/1412810/how-to-prevent-vlc-media-player-from-auto-closing-after-video-end#:%7E:text=Click%20on%20%22Media%22on%20the,VLC%20player%20after%20video%20ending
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_play_and_exit`

**Agent 要做什么**
My VLC Media Player has been auto-closing once the video ends. It is very annoying. Could you help me prevent the VLC Media Player from auto-closing once the video ends?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pathlib,re; p=pathlib.Path.home()/'.config/vlc/vlcrc'; p.parent.mkdir(parents=True, exist_ok=True); txt=p.read_text() if p.exists() else ''; txt=(re.sub(r'(?m)^#?\s*play-and-exit=.*$', 'play-and-exit=1', txt) if re.search(r'(?m)^#?\s*play-and-exit=', txt) else (txt + ('' if txt.endswith('\n') or txt == '' else '\n') + 'play-and-exit=1\n')...`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`check_play_and_exit`。检查 VLC 播放后退出设置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_play_and_exit": 0}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 7882ed6e-bece-4bf0-bada-c32dc1ddae72
- 源 JSON：[evaluation_examples/examples/vlc/7882ed6e-bece-4bf0-bada-c32dc1ddae72.json](../../../../evaluation_examples/examples/vlc/7882ed6e-bece-4bf0-bada-c32dc1ddae72.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://wiki.videolan.org/Digital_Restrictions_Management/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
Play the latest season of 'Stranger Things' purchased from the Google Play Movies & TV store directly in VLC.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## 8ba5ae7a-5ae5-4eab-9fcc-5dd4fe3abf89
- 源 JSON：[evaluation_examples/examples/vlc/8ba5ae7a-5ae5-4eab-9fcc-5dd4fe3abf89.json](../../../../evaluation_examples/examples/vlc/8ba5ae7a-5ae5-4eab-9fcc-5dd4fe3abf89.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://docs.videolan.me/vlc-user/desktop/3.0/en/basic/recording/playing.html#choose-your-recordings-folder
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_vlc_recordings_folder`

**Agent 要做什么**
Help me modify the folder used to store my recordings to Desktop

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_vlc_recordings_folder`。检查 VLC 录制目录。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"recording_file_path": "/home/user/Desktop"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 8d9fd4e2-6fdb-46b0-b9b9-02f06495c62f
- 源 JSON：[evaluation_examples/examples/vlc/8d9fd4e2-6fdb-46b0-b9b9-02f06495c62f.json](../../../../evaluation_examples/examples/vlc/8d9fd4e2-6fdb-46b0-b9b9-02f06495c62f.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://www.youtube.com/watch?v=XHprwDJ0-fU&t=436s
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_vlc_fullscreen`

**Agent 要做什么**
Can you enable fullscreen mode in VLC so that the video fill up the whole screen?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Optimus%20-%20Gen%202.mp4` 到 `/home/user/Desktop/Gen 2.mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show --start-time=15 '/home/user/Desktop/Gen 2.mp4'`；shell=True
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vm_screen_size` 状态 `{"type": "vm_screen_size"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_vlc_fullscreen`。检查 VLC 是否全屏。
  - 实际结果 `vm_screen_size`：读取 VM 屏幕尺寸。。
  - 期望结果 `vm_window_size`：读取 VM 窗口尺寸。；其他参数=`{"app_class_name": "vlc"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 8f080098-ddb1-424c-b438-4e96e5e4786e
- 源 JSON：[evaluation_examples/examples/vlc/8f080098-ddb1-424c-b438-4e96e5e4786e.json](../../../../evaluation_examples/examples/vlc/8f080098-ddb1-424c-b438-4e96e5e4786e.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://medium.com/@jetscribe_ai/how-to-extract-mp3-audio-from-videos-using-vlc-media-player-beeef644ebfb
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`compare_audios`

**Agent 要做什么**
Could you convert the song from this music video as an MP3 file? I'd like to have it on my device to play whenever I want. Please save the file just on the desktop and title the file "Baby Justin Bieber.mp3." I really appreciate your help!

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Baby%20Justin%20Bieber.mp4` 到 `/home/user/Desktop/Baby Justin Bieber.mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show --start-time=73 '/home/user/Desktop/Baby Justin Bieber.mp4'`；shell=True
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/Desktop/Baby Justin Bieber.mp3`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_audios`。比较音频文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/Desktop/Baby Justin Bieber.mp3`；dest=`baby.mp3`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/ubuntu_osworld_file_cache/resolve/main/vlc/8f080098-ddb1-424c-b438-4e96e5e4786e/Baby%20Justin%20Bieber.mp3`；dest=`baby_gold.mp3`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## 9195653c-f4aa-453d-aa95-787f6ccfaae9
- 源 JSON：[evaluation_examples/examples/vlc/9195653c-f4aa-453d-aa95-787f6ccfaae9.json](../../../../evaluation_examples/examples/vlc/9195653c-f4aa-453d-aa95-787f6ccfaae9.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/1513285/how-can-i-increase-the-maximum-volume-output-by-vlc?rq=1
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_qt_max_volume`

**Agent 要做什么**
I like watching movies (using VLC) on my laptop and sometimes the volume is too low for my taste even when the volume in VLC is set to the maximum of 125% on the volume control. Can you increase the max volume of the video to the 200% of the original volume?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_qt_max_volume`。检查 VLC 最大音量配置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_qt_max_volume": 200}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## a5bbbcd5-b398-4c91-83d4-55e1e31bbb81
- 源 JSON：[evaluation_examples/examples/vlc/a5bbbcd5-b398-4c91-83d4-55e1e31bbb81.json](../../../../evaluation_examples/examples/vlc/a5bbbcd5-b398-4c91-83d4-55e1e31bbb81.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/776056/how-to-hide-bottom-toolbar-in-vlc
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_qt_minimal_view`

**Agent 要做什么**
Enable VLC Minimal Interface in window mode so the bottom playback controls are hidden, and make sure the setting persists after restarting VLC. I often multitask on my computer, and the persistent toolbar in VLC is very distracting.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_qt_minimal_view`。检查 VLC minimal view 配置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_qt_minimal_view": 1}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## aa4b5023-aef6-4ed9-bdc9-705f59ab9ad6
- 源 JSON：[evaluation_examples/examples/vlc/aa4b5023-aef6-4ed9-bdc9-705f59ab9ad6.json](../../../../evaluation_examples/examples/vlc/aa4b5023-aef6-4ed9-bdc9-705f59ab9ad6.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://www.dedoimedo.com/computers/vlc-rotate-videos.html
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`compare_videos`

**Agent 要做什么**
Hey, could you turn this video the right way up for me? And once it's flipped around, could you save it for me with the name '1984_Apple_Macintosh_Commercial.mp4' on the main screen where all my files are?

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `flipped_1984_Apple_Macintosh_Commercial.mp4` 到 `/home/user/Desktop/flipped_1984_Apple_Macintosh_Commercial.mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show /home/user/Desktop/flipped_1984_Apple_Macintosh_Commercial.mp4`；shell=True
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/1984_Apple_Macintosh_Commercial.mp4`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_videos`。比较视频文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/1984_Apple_Macintosh_Commercial.mp4`；dest=`1984_Apple_Macintosh_Commercial.mp4`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/ubuntu_osworld_file_cache/resolve/main/vlc/aa4b5023-aef6-4ed9-bdc9-705f59ab9ad6/1984_Apple_Macintosh_Commercial.mp4`；dest=`1984_Apple_Macintosh_Commercial_gold.mp4`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## bba3381f-b5eb-4439-bd9e-80c22218d5a7
- 源 JSON：[evaluation_examples/examples/vlc/bba3381f-b5eb-4439-bd9e-80c22218d5a7.json](../../../../evaluation_examples/examples/vlc/bba3381f-b5eb-4439-bd9e-80c22218d5a7.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://developer.apple.com/streaming/examples/ - Apple HLS test streams for developers
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`is_vlc_playing`

**Agent 要做什么**
Can you start streaming the video from this link for me? https://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_playing_info` 状态 `{"dest": "status.xml", "type": "vlc_playing_info"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`is_vlc_playing`。检查 VLC 播放状态。
  - 实际结果 `vlc_playing_info`：读取 VLC 播放状态。；dest=`status.xml`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "url", "url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## cb130f0d-d36f-4302-9838-b3baf46139b6
- 源 JSON：[evaluation_examples/examples/vlc/cb130f0d-d36f-4302-9838-b3baf46139b6.json](../../../../evaluation_examples/examples/vlc/cb130f0d-d36f-4302-9838-b3baf46139b6.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://www.vlchelp.com/increase-brightness-contrast-videos/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`infeasible`

**Agent 要做什么**
Automatically adjust the brightness and contrast of this video to match my room's lighting.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 判断任务在当前环境和应用能力下不可行，不能擅自创建不存在的账号、功能、外部条件或伪造产物。
- 2. 需要向用户明确表达不可完成的原因，并以 `FAIL` 动作结束；评测只认最后动作为 `FAIL`。

**判定标准**
- 评测函数：`infeasible`。
- 判定逻辑：`DesktopEnv.evaluate()` 检查最后一个 agent action；只有最后动作为 `FAIL` 才返回 1，否则返回 0。
- 这类 case 的核心不是产物文件，而是 agent 是否正确拒绝不可行请求。

## d06f0d4d-2cd5-4ede-8de9-598629438c6e
- 源 JSON：[evaluation_examples/examples/vlc/d06f0d4d-2cd5-4ede-8de9-598629438c6e.json](../../../../evaluation_examples/examples/vlc/d06f0d4d-2cd5-4ede-8de9-598629438c6e.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://superuser.com/questions/1039392/changing-colour-of-vlc-volume-slider
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_qt_slider_colours`

**Agent 要做什么**
Can you change the color of the volume slider to black-ish color? I often use the player in a low-light environment, and a darker color scheme would be less straining on my eyes, especially during nighttime usage.

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_qt_slider_colours`。检查 VLC slider colours 配置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"type": "blackish"}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## efcf0d81-0835-4880-b2fd-d866e8bc2294
- 源 JSON：[evaluation_examples/examples/vlc/efcf0d81-0835-4880-b2fd-d866e8bc2294.json](../../../../evaluation_examples/examples/vlc/efcf0d81-0835-4880-b2fd-d866e8bc2294.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://www.youtube.com/watch?v=XHprwDJ0-fU&t=436s, https://help.ubuntu.com/stable/ubuntu-help/look-background.html.en
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`compare_images`

**Agent 要做什么**
Make this part of the video my computer's background picture

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Interstellar%20Movie%20-%20Official%20Trailer.mp4` 到 `/home/user/Desktop/Interstellar Movie - Official Trailer.mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show --start-time=120.5 --stop-time=121 --play-and-pause '/home/user/Desktop/Interstellar Movie - Official Trailer.mp4'`；shell=True
- 3. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vm_wallpaper` 状态 `{"dest": "result_wallpaper.png", "type": "vm_wallpaper"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_images`。比较图片文件。
  - 实际结果 `vm_wallpaper`：读取 VM 桌面壁纸。；dest=`result_wallpaper.png`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/ubuntu_osworld_file_cache/resolve/main/vlc/efcf0d81-0835-4880-b2fd-d866e8bc2294/interstellar.png`；dest=`interstellar_wallpaper_gold.png`。
  - 选项/规则：`{"reference_base_result": 0.11}`。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## f3977615-2b45-4ac5-8bba-80c17dbe2a37
- 源 JSON：[evaluation_examples/examples/vlc/f3977615-2b45-4ac5-8bba-80c17dbe2a37.json](../../../../evaluation_examples/examples/vlc/f3977615-2b45-4ac5-8bba-80c17dbe2a37.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`chrome`
- 相关应用：`vlc`
- 来源：https://www.reddit.com/r/Fedora/comments/rhljzd/how_to_run_multiple_instances_of_vlc_media_player/
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`check_one_instance_when_started_from_file`

**Agent 要做什么**
I want to watch two or more videos in same time on VLC. I tried to run multiple instances of VLC. It worked but can't play videos on those new instances. When I play video it plays on first instance instead of new instance. Is there any way to solve this problem?

**前置/初始状态**
- 1. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show`；shell=True
- 2. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vlc_config` 状态 `{"dest": "vlcrc", "type": "vlc_config"}`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：
  - 1. `launch`：启动指定应用或后台辅助进程。 命令 `pkill vlc`
  - 2. `launch`：启动指定应用或后台辅助进程。 命令 `vlc --no-audio --no-video-title-show`；shell=True
- Metric 1：`check_one_instance_when_started_from_file`。检查 VLC 文件启动单实例设置。
  - 实际结果 `vlc_config`：读取 VLC 配置。；dest=`vlcrc`。
  - 期望结果 `rule`：直接使用 JSON 中声明的规则对象。；rules=`{"expected_one_instance_when_started_from_file": 0}`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。

## fba2c100-79e8-42df-ae74-b592418d54f4
- 源 JSON：[evaluation_examples/examples/vlc/fba2c100-79e8-42df-ae74-b592418d54f4.json](../../../../evaluation_examples/examples/vlc/fba2c100-79e8-42df-ae74-b592418d54f4.json)
- 平台/集合：Linux/Ubuntu 主任务集
- 应用域：`vlc`
- snapshot：`base_setup`
- 相关应用：`vlc`
- 来源：https://www.youtube.com/watch?v=XHprwDJ0-fU&t=436s
- trajectory：`trajectories/`
- 环境标记：proxy=`False`，fixed_ip=`False`，possibility_of_env_change=`low`
- 评测函数：`compare_images`

**Agent 要做什么**
Snap a photo of the current video scene, save it as 'interstellar.png', and put it on the Desktop, please.

**前置/初始状态**
- 1. `download`：下载文件到 guest，构造任务初始素材。 下载 `Interstellar%20Movie%20-%20Official%20Trailer.mp4` 到 `/home/user/Desktop/Interstellar Movie - Official Trailer.mp4`
- 2. `launch`：启动指定应用或后台辅助进程。 命令 `VLC_VERBOSE=-1 vlc --no-audio --no-video-title-show --start-time=120.5 --stop-time=121 --play-and-pause '/home/user/Desktop/Interstellar Movie - Official Trailer.mp4'`；shell=True
- 3. `sleep`：等待界面或后台状态稳定。 等待 1 秒
- 4. `activate_window`：激活指定窗口，让后续操作或评测落在正确应用上。 窗口 `Interstellar Movie - Interstellar Movie - Official Trailer - VLC media player`
- 5. `execute`：在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 命令 `python -c import pyautogui; import time; pyautogui.click({SCREEN_WIDTH_HALF}, {SCREEN_HEIGHT_HALF}); time.sleep(0.5);`

**过程（从 JSON 推断，不是人工轨迹）**
- 1. 从前置动作准备好的窗口、文件、网页或系统状态出发，在 `vlc` 中执行用户指令。
- 2. 操作重点：在 VLC 中完成播放、显示、录制、音频/视频设置或媒体产物相关操作。
- 3. 结束时要让可评测结果落在：`vm_file` 的 `/home/user/Desktop/interstellar.png`。
- 4. 完成后应以 `DONE` 结束；普通可行任务如果最后动作为 `FAIL` 会直接判 0。

**判定标准**
- 组合逻辑：`and`；共 1 个 metric。
- 评测前收尾动作：无。
- Metric 1：`compare_images`。比较图片文件。
  - 实际结果 `vm_file`：从 VM 指定路径取实际产物文件。；path=`/home/user/Desktop/interstellar.png`；dest=`interstellar.png`。
  - 期望结果 `cloud_file`：从云端或数据缓存下载 gold/参考文件。；path=`https://huggingface.co/datasets/xlangai/ubuntu_osworld_file_cache/resolve/main/vlc/fba2c100-79e8-42df-ae74-b592418d54f4/interstellar.png`；dest=`interstellar_gold.png`。
  - 选项/规则：无额外 options。
- 通过条件：该 metric 返回通过分数，且 agent 没有以 `FAIL` 结束。
