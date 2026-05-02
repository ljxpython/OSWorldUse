# 评测标准体系与准确性保证

这篇文档回答一个核心问题：OSWorld 怎么判断 agent 是否完成了我们预期的指令，以及这套评测为什么比“看起来做完了”靠谱。

先把结论钉死：OSWorld 不是让 LLM 当裁判看截图，也不是让 agent 自己说“我完成了”。它把任务完成后的 VM 状态、文件、网页、配置或应用状态提取出来，再和预设规则或 gold 文件做程序化比较。

## 一、评测对象是什么

每个 case 的核心评测对象来自 `evaluation_examples/` 里的单个 JSON。

一个 case 通常由三部分驱动：

- `instruction`：给 agent 的自然语言任务。
- `config`：任务开始前的环境准备动作。
- `evaluator`：任务结束后如何判定成功。

所以评测标准不是临时写在代码里的，而是由 case JSON 明确声明。代码负责解释这些 JSON，执行 setup、提取结果、比较结果。

## 二、整体评测链路

完整链路可以理解成：

```text
case JSON
  -> reset 时执行 config，准备初始环境
  -> agent 根据 instruction 操作 GUI
  -> agent 用 DONE / FAIL 结束
  -> evaluate() 执行 postconfig
  -> result getter 提取实际结果
  -> expected getter 提取期望结果
  -> metric 比较实际结果和期望结果
  -> 返回分数
```

对应代码主入口：

- `DesktopEnv._set_evaluator_info()`：把 JSON 里的 `func`、`result`、`expected`、`options` 解析成真实 getter/metric。
- `DesktopEnv.evaluate()`：执行评测，包括 `postconfig`、不可行任务判断、单 metric / 多 metric 组合。

## 三、前置环境如何保证一致

`config` 负责把任务起点固定下来。常见动作包括：

- `download`：下载任务素材，例如文档、表格、图片、压缩包。
- `launch`：启动应用，例如 Chrome、LibreOffice、GIMP、VLC。
- `open`：打开指定文件。
- `execute` / `command`：在 guest 内执行命令，准备目录、配置、profile 或测试文件。
- `chrome_open_tabs`：预先打开指定网页。
- `activate_window`：激活目标窗口。
- `sleep`：等待应用状态稳定。

这一步解决的是“agent 从哪里开始”的问题。没有固定初始状态，评测结果就会漂，跑出来的分数也没意义。

## 四、agent 要做什么

agent 只看 `instruction` 和当前 GUI 状态，然后通过动作空间操作系统。

评测通常不关心 agent 具体怎么点、怎么拖、怎么输入。它关心的是 agent 结束后是否留下了可验证的最终状态：

- 文件是否生成在预期路径。
- 文档、表格、演示文稿内容是否符合 gold 文件。
- Chrome 当前 URL、书签、cookie、扩展、设置是否符合规则。
- 应用配置文件是否被正确修改。
- VLC/GIMP/VS Code 等应用状态或产物是否符合 metric。
- 不可行任务是否正确拒绝并以 `FAIL` 结束。

这点很重要：过程可以多样，但结果必须可验。

## 五、评测前 postconfig 是干什么的

很多 GUI 应用不会立刻把状态落盘。比如：

- LibreOffice 文档需要保存后才能比较文件。
- GIMP 图片需要导出后才有结果文件。
- 窗口需要激活后 accessibility tree 才可靠。
- 某些 UI 状态需要等待。

所以 `evaluator.postconfig` 会在 `evaluate()` 开始时执行，用来做评测前收尾。它不是 agent 的操作成绩，而是评测系统为了读取最终状态做的稳定化处理。

常见 `postconfig` 包括：

- 激活窗口。
- 等待几秒。
- 模拟 `ctrl+s` 保存。
- 导出文件。
- 关闭/重启应用以刷新配置。

## 六、result getter 如何取实际结果

`result` 定义“实际结果从哪里来”。代码会根据 `result.type` 找到对应 getter。

常见 result getter：

| 类型 | 作用 |
| --- | --- |
| `vm_file` | 从 VM 里取 agent 生成或修改后的文件。 |
| `vm_command_line` | 在 VM 中执行命令，读取命令输出。 |
| `active_url_from_accessTree` | 从 accessibility tree 读取 Chrome 当前 URL。 |
| `active_tab_url_parse` | 解析当前活动标签页 URL 参数。 |
| `bookmarks` | 读取 Chrome 书签。 |
| `open_tabs_info` | 读取 Chrome 打开的标签页。 |
| `gimp_config_file` | 读取 GIMP 配置。 |
| `vlc_config` | 读取 VLC 配置。 |
| `vscode_config` | 读取 VS Code 配置。 |
| `accessibility_tree` | 读取当前界面的 accessibility tree。 |

这一步的关键是：尽量从结构化状态、文件或配置中取证，而不是靠主观截图判断。

## 七、expected getter 如何取期望结果

`expected` 定义“标准答案从哪里来”。常见来源有两类：

- `rule`：JSON 内联规则，例如期望 URL、字段、开关值、包含/排除文本。
- `cloud_file`：下载 gold 文件，例如标准 `.xlsx`、`.docx`、`.pptx`、`.png`、`.pdf`。

文件类任务通常用 gold 文件，因为文档、表格、演示文稿的正确性很难靠一句规则描述完整。

规则类任务适合状态明确的场景，例如：

- Chrome Do Not Track 是否开启。
- 当前活动标签页是否是某个 URL。
- 某个配置项是否等于指定值。
- 命令输出是否包含某些文本。

## 八、metric 如何判定成功

`evaluator.func` 指向 metric。metric 的工作是把实际结果和期望结果比较，返回分数。

常见 metric 类型：

| 类型 | 代表函数 | 判定方式 |
| --- | --- | --- |
| 精确值比较 | `exact_match`、`literal_match` | 实际值必须等于期望值。 |
| 包含/排除检查 | `check_include_exclude`、`check_list` | 输出必须包含要求内容，且不能包含禁止内容。 |
| URL/浏览器状态 | `is_expected_active_tab`、`is_expected_url_pattern_match`、`is_expected_bookmarks` | 检查标签页、URL、书签、cookie、扩展或设置。 |
| 文件比较 | `compare_text_file`、`diff_text_file`、`compare_archive` | 比较生成文件和 gold 文件。 |
| 表格比较 | `compare_table`、`compare_csv` | 比较 sheet、单元格、格式、公式、透视表、筛选、图表等。 |
| 文档比较 | `compare_docx_files`、`compare_docx_tables`、`compare_line_spacing` | 比较 Word/Writer 文档内容和格式。 |
| 演示文稿比较 | `compare_pptx_files`、`check_transition`、`check_slide_orientation_Portrait` | 比较 PPT/Impress 页面、版式、颜色、转场等。 |
| 图片/媒体比较 | `compare_images`、`check_structure_sim`、`compare_audios`、`compare_videos` | 比较图片结构、颜色、尺寸、音频或视频。 |
| 不可行任务 | `infeasible` | 只有最后动作为 `FAIL` 才通过。 |

普通任务如果最后动作为 `FAIL`，会直接判 0。不可行任务反过来，必须最后 `FAIL` 才算正确。

## 九、多 metric 如何组合

复杂 case 可以有多个 metric：

```json
{
  "func": ["compare_csv", "compare_table"],
  "conj": "and"
}
```

`conj` 控制组合逻辑：

- `and`：所有 metric 都通过，整体才通过。
- `or`：任一 metric 通过，整体就通过。

这能避免单一指标太弱。比如一个表格任务既要生成 CSV，又要生成 XLSX；一个图片任务既要尺寸正确，又要结构相似。

## 十、准确性靠什么保证

这套评测的准确性主要靠下面几层保证。

### 1. 固定起点

`snapshot + config` 固定初始环境，避免每次运行从不同状态开始。

### 2. 明确目标

`instruction` 给 agent，`evaluator` 给评测系统。目标和判定标准都写在 case JSON 里，不靠临场解释。

### 3. 结构化取证

优先读取文件、配置、URL、命令输出、accessibility tree，而不是让模型看截图猜。

### 4. gold 文件对比

复杂产物使用 gold 文件做参考，例如表格、文档、演示文稿、图片、PDF。这样能把“做成什么样”落到可比较的对象上。

### 5. 专用 metric

不同应用用不同 metric。表格用 `compare_table`，文档用 `compare_docx_files`，网页状态用 URL/HTML/配置 getter。不是全靠文本 diff 这种粗糙玩意。

### 6. 多条件组合

复杂任务用多个 metric 和 `and` 组合，减少 agent 只满足一个表面条件就蒙混过关的可能。

### 7. 评测前状态稳定化

`postconfig` 负责保存、等待、激活窗口、导出结果，减少 UI 延迟和未落盘导致的误判。

### 8. 不可行任务单独建模

`infeasible` 明确考察 agent 能不能拒绝不可能完成的任务。它不是看文件结果，而是看最后是否正确 `FAIL`。

## 十一、它不能保证什么

老王得把丑话说前头：这套系统能保证“符合 evaluator 定义的成功条件”，不能保证“人类语义上的绝对正确”。

主要风险有：

- evaluator 写得太宽，agent 可能钻空子。
- evaluator 写得太窄，正确但不同路径的结果可能被误杀。
- 动态网页、时间、网络、代理、登录态会导致结果漂移。
- 图片相似度、OCR、accessibility tree 这类近似评测可能误判。
- gold 文件如果错了，评测会跟着错。
- `postconfig` 如果假设错误，可能把 agent 的结果保存/导出失败。

所以评测准确性不是自动来的，case 设计必须认真。

## 十二、设计新 case 的评测准则

新增 case 时，建议按这个顺序设计：

1. 明确 agent 的自然语言目标，只写当前需要完成的事。
2. 用 `config` 固定初始环境，准备必要文件、页面、应用和账号状态。
3. 定义最终可验证证据，优先选择文件、配置、URL、命令输出等结构化结果。
4. 为复杂产物准备 gold 文件，不要用模糊文字描述糊弄。
5. 选择最贴近应用语义的 metric，不要拿文本 diff 硬比所有东西。
6. 必要时使用多个 metric 和 `and`，同时检查内容、格式、路径、状态。
7. 加 `postconfig` 处理保存、导出、等待、窗口激活。
8. 对动态网页、时间、外部服务任务标注环境变化风险，并尽量减少依赖。
9. 对不可行任务使用 `infeasible`，并在 instruction 里明确要求 agent 不要伪造、不越权。
10. 跑一次验证，确认失败路径能判 0，成功路径能判 1。

## 十三、一句话总结

OSWorld 的评测准确性来自“任务数据驱动 + 固定初始环境 + 结构化状态提取 + gold/规则比较 + 专用 metric + 多条件组合”。它不是万能裁判，但只要 evaluator 写得严谨，就能把 agent 的 GUI 行为变成可复现、可审计、可量化的分数。
