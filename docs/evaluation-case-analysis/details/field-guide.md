# 评测明细字段说明
这份说明给 detailed case 文档兜底，防止看到 `result.type`、`expected.type`、`metric` 就两眼一黑。

## 执行链路
1. `config` 在 `env.reset(task_config=example)` 阶段执行，用来准备初始环境。
2. Agent 根据 `instruction` 操作 GUI，最后通常以 `DONE` 结束。
3. `evaluator.postconfig` 在 `evaluate()` 前执行，用来保存文件、激活窗口或等待状态稳定。
4. evaluator 通过 `result getter -> expected getter -> metric` 判定结果。
5. `func = infeasible` 是特例：最后动作为 `FAIL` 才通过。

## 常见前置动作类型
| type | 含义 |
| --- | --- |
| `activate_window` | 激活指定窗口，让后续操作或评测落在正确应用上。 |
| `chrome_close_tabs` | 关闭指定 Chrome 标签页。 |
| `chrome_open_tabs` | 在 Chrome 中打开指定标签页。 |
| `close_window` | 关闭指定窗口。 |
| `command` | 执行命令型 setup，和 execute 类似，用于创建目录、移动文件等环境准备。 |
| `download` | 下载文件到 guest，构造任务初始素材。 |
| `execute` | 在 guest 中执行命令，通常用于准备文件、写配置或触发保存/导出。 |
| `googledrive` | 调用 Google Drive 配置/接口准备云端文件状态。 |
| `launch` | 启动指定应用或后台辅助进程。 |
| `login` | 准备登录态或执行登录相关 setup。 |
| `open` | 打开指定文件或资源。 |
| `sleep` | 等待界面或后台状态稳定。 |
| `update_browse_history` | 预置 Chrome 浏览历史。 |

## 常见 getter 类型
| type | 含义 |
| --- | --- |
| `accessibility_tree` | 读取当前界面的 accessibility tree。 |
| `active_tab_html_parse` | 解析当前活动标签页 HTML。 |
| `active_tab_info` | 读取 Chrome 当前活动标签页信息。 |
| `active_tab_url_parse` | 解析 Chrome 当前活动标签页 URL。 |
| `active_url_from_accessTree` | 从 accessibility tree 近似读取当前活动 URL。 |
| `audio_in_slide` | 提取演示文稿中的音频。 |
| `background_image_in_slide` | 提取演示文稿背景图。 |
| `bookmarks` | 读取 Chrome 书签状态。 |
| `cache_file` | 读取本地 cache 中的文件。 |
| `chrome_appearance_mode_ui` | 读取 Chrome 外观模式。 |
| `chrome_font_size` | 读取 Chrome 字体大小设置。 |
| `cloud_file` | 从云端或数据缓存下载 gold/参考文件。 |
| `content_from_vm_file` | 读取 VM 文件内容。 |
| `cookie_data` | 读取 Chrome cookie 状态。 |
| `data_delete_automacally` | 读取关闭浏览器时自动删除数据设置。 |
| `default_search_engine` | 读取 Chrome 默认搜索引擎设置。 |
| `default_video_player` | 读取默认视频播放器设置。 |
| `enable_do_not_track` | 读取 Chrome Do Not Track 设置。 |
| `enable_safe_browsing` | 读取 Chrome 安全浏览设置。 |
| `find_installed_extension_name` | 查找已安装扩展名称。 |
| `find_unpacked_extension_path` | 查找解压后的 Chrome 扩展目录。 |
| `gimp_config_file` | 读取 GIMP 配置文件。 |
| `googledrive_file` | 从 Google Drive 获取文件状态或内容。 |
| `gotoRecreationPage_and_get_html_content` | 导航到页面并获取 HTML 参考内容。 |
| `history` | 读取 Chrome 浏览历史。 |
| `info_from_website` | 从网站获取参考信息。 |
| `list_directory` | 列出 VM 目录内容。 |
| `new_startup_page` | 读取 Chrome 启动页设置。 |
| `open_tabs_info` | 读取 Chrome 当前打开的标签页列表。 |
| `page_info` | 读取页面信息。 |
| `pdf_from_url` | 从 URL 生成或获取 PDF 参考内容。 |
| `profile_name` | 读取 Chrome profile 名称。 |
| `rule` | 直接使用 JSON 中声明的规则对象。 |
| `rule_relativeTime` | 按相对时间规则生成期望值。 |
| `shortcuts_on_desktop` | 读取桌面快捷方式状态。 |
| `time_diff_range` | 生成时间差范围期望。 |
| `url_dashPart` | 解析 URL 片段。 |
| `url_path_parse` | 解析 URL path。 |
| `vlc_config` | 读取 VLC 配置。 |
| `vlc_playing_info` | 读取 VLC 播放状态。 |
| `vm_command_error` | 在 VM 中执行命令并读取错误/异常输出。 |
| `vm_command_line` | 在 VM 中执行命令并读取 stdout。 |
| `vm_file` | 从 VM 指定路径取实际产物文件。 |
| `vm_screen_size` | 读取 VM 屏幕尺寸。 |
| `vm_terminal_output` | 读取终端输出。 |
| `vm_wallpaper` | 读取 VM 桌面壁纸。 |
| `vm_window_size` | 读取 VM 窗口尺寸。 |
| `vscode_config` | 读取 VS Code 配置。 |

## 常见 metric 含义
| func | 含义 |
| --- | --- |
| `check_accessibility_tree` | 检查 accessibility tree 中的控件/文本状态。 |
| `check_auto_saving_time` | 检查自动保存时间设置。 |
| `check_brightness_decrease_and_structure_sim` | 检查亮度降低且结构仍相似。 |
| `check_config_status` | 检查应用配置状态。 |
| `check_contrast_increase_and_structure_sim` | 检查对比度增强且结构仍相似。 |
| `check_csv` | 检查 CSV 内容是否满足规则。 |
| `check_direct_json_object` | 直接检查结构化 JSON 对象是否满足字段规则。 |
| `check_file_exists_and_structure_sim` | 检查文件存在且图片结构相似。 |
| `check_font_size` | 检查 Chrome 字体大小。 |
| `check_global_key_play_pause` | 检查 VLC 全局播放/暂停快捷键。 |
| `check_gnome_favorite_apps` | 检查 GNOME 收藏应用栏。 |
| `check_green_background` | 检查背景是否变为绿色。 |
| `check_highlighted_words` | 检查高亮词。 |
| `check_history_deleted` | 检查指定浏览历史是否被删除。 |
| `check_image_file_size` | 检查图片文件大小。 |
| `check_image_mirror` | 检查图片镜像结果。 |
| `check_image_size` | 检查图片尺寸。 |
| `check_image_stretch_and_center` | 检查幻灯片图片是否拉伸并居中。 |
| `check_include_exclude` | 检查文本/输出是否包含必需内容且不包含禁止内容。 |
| `check_italic_font_size_14` | 检查斜体和 14 号字体。 |
| `check_json` | 检查 JSON/YAML 内容是否满足规则。 |
| `check_json_keybindings` | 检查 VS Code 快捷键 JSON。 |
| `check_json_settings` | 检查 VS Code 设置 JSON。 |
| `check_left_panel` | 检查 Impress 左侧面板状态。 |
| `check_line_number` | 检查文件行号相关条件。 |
| `check_list` | 检查列表内容是否满足规则。 |
| `check_moved_jpgs` | 检查 JPG 文件移动结果。 |
| `check_mp3_meta` | 检查 MP3 元数据。 |
| `check_one_instance_when_started_from_file` | 检查 VLC 文件启动单实例设置。 |
| `check_page_number_colors` | 检查页码颜色。 |
| `check_palette_and_structure_sim` | 检查调色板模式和结构相似度。 |
| `check_pdf_pages` | 检查 PDF 页数或页面规则。 |
| `check_play_and_exit` | 检查 VLC 播放后退出设置。 |
| `check_presenter_console_disable` | 检查演示者控制台关闭设置。 |
| `check_python_file_by_test_suite` | 用测试套件检查 Python 文件行为。 |
| `check_qt_bgcone` | 检查 VLC 背景锥图配置。 |
| `check_qt_max_volume` | 检查 VLC 最大音量配置。 |
| `check_qt_minimal_view` | 检查 VLC minimal view 配置。 |
| `check_qt_slider_colours` | 检查 VLC slider colours 配置。 |
| `check_saturation_increase_and_structure_sim` | 检查饱和度增强且结构仍相似。 |
| `check_slide_orientation_Portrait` | 检查幻灯片是否为纵向。 |
| `check_structure_sim` | 检查图片结构相似度。 |
| `check_structure_sim_resized` | 检查缩放后的结构相似度。 |
| `check_structure_sim_with_threshold` | 按阈值检查图片结构相似度。 |
| `check_tabstops` | 检查制表位。 |
| `check_textbox_on_leftside` | 检查文本框是否在左侧。 |
| `check_thunderbird_filter` | 检查 Thunderbird 邮件过滤器。 |
| `check_thunderbird_folder` | 检查 Thunderbird 文件夹。 |
| `check_thunderbird_prefs` | 检查 Thunderbird 偏好设置。 |
| `check_transition` | 检查幻灯片转场。 |
| `check_triangle_position` | 检查三角形位置。 |
| `compare_archive` | 比较压缩包内容。 |
| `compare_audios` | 比较音频文件。 |
| `compare_conference_city_in_order` | 检查会议城市排序。 |
| `compare_config` | 比较配置文件或配置规则。 |
| `compare_csv` | 比较实际 CSV 和参考 CSV。 |
| `compare_docx_files` | 比较 DOCX 文档内容和格式。 |
| `compare_docx_files_and_ignore_new_lines` | 比较 DOCX 文档，忽略换行差异。 |
| `compare_docx_images` | 比较 DOCX 中的图片。 |
| `compare_docx_tables` | 比较 DOCX 表格。 |
| `compare_epub` | 比较 EPUB 文件。 |
| `compare_font_names` | 检查/比较字体名称。 |
| `compare_image_list` | 比较图片文件列表。 |
| `compare_image_text` | 检查图片文本识别结果。 |
| `compare_images` | 比较图片文件。 |
| `compare_line_spacing` | 比较文档行距。 |
| `compare_pdf_images` | 比较 PDF 渲染出的图片。 |
| `compare_pdfs` | 比较 PDF 文件。 |
| `compare_pptx_files` | 比较 PPTX 文件内容和版式。 |
| `compare_python_pure_text` | 比较 Python 文件纯文本内容。 |
| `compare_references` | 比较文档引用/参考文献。 |
| `compare_result_files` | 比较运行结果文件。 |
| `compare_subscript_contains` | 检查文档下标内容。 |
| `compare_table` | 比较表格/工作簿内容、公式、格式、透视表或图表等规则。 |
| `compare_text_file` | 比较文本文件。 |
| `compare_time_in_speedtest_results` | 比较测速结果中的时间。 |
| `compare_unique_train_records` | 检查去重后的火车记录。 |
| `compare_videos` | 比较视频文件。 |
| `compare_zip_files` | 比较 ZIP 文件内容。 |
| `contains_page_break` | 检查文档是否包含分页符。 |
| `diff_text_file` | 对文本文件做 diff 检查。 |
| `evaluate_colored_words_in_tables` | 检查表格中的彩色文字。 |
| `evaluate_presentation_fill_to_rgb_distance` | 检查演示文稿填充色与目标 RGB 的距离。 |
| `evaluate_strike_through_last_paragraph` | 检查最后一段删除线。 |
| `exact_match` | 实际值必须与规则中的期望值精确一致。 |
| `file_contains` | 检查文件是否包含指定内容。 |
| `fuzzy_place_math` | 模糊匹配地点/数学类结果。 |
| `has_page_numbers_in_footers` | 检查页脚页码。 |
| `infeasible` | 不可行任务判定：最终动作为 FAIL 才算通过。 |
| `is_added_to_steam_cart` | 检查 Steam 购物车状态。 |
| `is_cookie_deleted` | 检查指定 cookie 是否被删除。 |
| `is_expected_active_tab` | 检查 Chrome 当前活动标签页是否符合规则。 |
| `is_expected_active_tab_approximate` | 近似检查 Chrome 当前活动标签页/URL。 |
| `is_expected_bookmarks` | 检查 Chrome 书签状态。 |
| `is_expected_installed_extensions` | 检查 Chrome 已安装扩展集合。 |
| `is_expected_search_query` | 检查搜索查询。 |
| `is_expected_tabs` | 检查 Chrome 打开的标签页集合。 |
| `is_expected_url_pattern_match` | 检查 URL 是否匹配规则或模式。 |
| `is_extension_installed` | 检查扩展是否安装。 |
| `is_first_line_centered` | 检查首行居中。 |
| `is_in_list` | 实际值必须出现在期望列表或规则集合中。 |
| `is_in_vm_clickboard` | 检查 VM 剪贴板内容。 |
| `is_shortcut_on_desktop` | 检查桌面快捷方式是否创建。 |
| `is_utc_0` | 检查时区是否为 UTC+0。 |
| `is_vlc_fullscreen` | 检查 VLC 是否全屏。 |
| `is_vlc_playing` | 检查 VLC 播放状态。 |
| `is_vlc_recordings_folder` | 检查 VLC 录制目录。 |
| `literal_match` | 实际对象和值必须与期望对象字面一致。 |
| `match_in_list` | 实际值必须命中期望列表。 |
| `run_sqlite3` | 执行 sqlite3 查询并检查结果。 |
