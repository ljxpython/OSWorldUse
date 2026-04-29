# 13 Calc 任务端到端走读

这一篇接在 [12 Chrome 任务端到端走读](./12-chrome-task-end-to-end_zh.md) 后面看最顺。

上一篇我们选了一个 `chrome` 任务，重点看的是：

- GUI 改设置
- 最后通过配置文件判分

这次我换一个 `libreoffice_calc` 任务，重点会不一样：

- GUI 改表格
- 最后通过文件结果判分

而且这个任务还有一个特别值得学的点：

- 它不是只比 `xlsx` 内部值
- 而是专门比“屏幕上显示出来的结果”

这能帮你真正理解：

- 为什么 Calc 任务的 evaluator 常常又抓 `xlsx`，又抓 `csv`

## 先说这篇选哪个任务

我选的是这个任务：

- [evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json](../../evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json)

任务指令是：

- 把 `Old ID` 列里的数字复制到 `New 7 Digit Id` 列
- 并在前面补零，补到 7 位
- 不要动无关区域

这是一个很好的代表任务，因为它同时具备：

1. `download + open` 的 setup
2. 真实的 Calc GUI 操作
3. `postconfig` 里的保存和格式导出
4. `vm_file + cloud_file` 双文件取回
5. `compare_table` 的规则化表格比对

## 一、先把任务 JSON 翻译成一句人话

这个任务本质上是在说：

- 给你一个 Excel 文件
- 让 agent 在 Calc 里补一列格式化后的 ID
- 最后不仅要保存工作簿，还要把它导出成 CSV
- evaluator 再把你的结果和 gold 文件做严格比对

也就是说，它不是简单的：

- “我看你是不是点对了”

而是：

- “我最终要拿到你改完后的文件，并且逐项验证”

## 二、先看 `config`：任务一开始做了什么

任务 JSON 的 `config` 只有两步：

1. `download`
2. `open`

对应文件：

- [evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json](../../evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json)
- [desktop_env/controllers/setup.py](../../desktop_env/controllers/setup.py)

## 三、`download` 不是下到宿主机，而是下到 guest 里

这里最容易产生错觉。

任务里写的是：

- 从 HuggingFace 下载 `Customers_New_7digit_Id.xlsx`
- 放到 `/home/user/Customers_New_7digit_Id.xlsx`

这个路径是：

- guest OS 内部路径

不是你本地项目目录。

在代码上，这一步会走：

- `SetupController.setup(...)`
- `SetupController._download_setup(...)`

它会先把文件缓存到本地，再通过 guest server 的上传接口传进虚拟机。

所以你可以把这一步理解成：

- “把任务输入文件注入到被测桌面环境里”

## 四、`open` 是怎么把文件交给 Calc 的

第二步：

- `type = "open"`

会走到：

- `SetupController._open_setup(path)`

这一步会请求 guest server 的：

- `/setup/open_file`

所以真正打开这个 `.xlsx` 的，不是宿主机上的 LibreOffice，而是：

- guest OS 里的 LibreOffice Calc

这和前面 `chrome` 任务是同一套大原则：

- 宿主机负责编排
- guest OS 负责真实 GUI 执行

## 五、setup 完成后，runner 才开始让 agent 做事

对应文件：

- [lib_run_single.py](../../lib_run_single.py)

主循环还是那条熟悉的链：

1. `env.reset(task_config=example)`
2. `agent.reset(...)`
3. `obs = env._get_obs()`
4. `agent.predict(instruction, obs)`
5. `env.step(action, ...)`
6. 记录截图和轨迹
7. 最后 `env.evaluate()`

所以这个任务真正困难的部分，不在 setup，而在 agent 是否能正确：

- 找到 `Old ID`
- 找到 `New 7 Digit Id`
- 填出 7 位补零结果
- 不破坏其他区域

## 六、这里没有预置“固定操作脚本”

这一点和前面 `chrome` 任务一样，也要再次强调。

代码里并没有写死：

- 点哪个单元格
- 选哪一列
- 输入什么公式

任务 JSON 只定义：

- 初始文件
- 自然语言目标
- 评测方式

真正怎么完成，仍然取决于 agent。

也就是说，下面这些只是合理推测，不是仓库内置轨迹：

- agent 可能先观察列名
- 选中目标列第一格
- 输入公式或批量填充逻辑
- 让新列显示 7 位补零的文本
- 最后返回 `DONE`

你要继续保持这个心智模型：

- OSWorld 定义的是任务，不是回放脚本

## 七、这个任务最关键的部分其实在 `postconfig`

和很多简单任务不同，这个 Calc 任务的 `evaluator.postconfig` 很长，而且很有信息量。

它做了这些事：

1. `activate_window`
2. `sleep`
3. 发送 `Ctrl+S`
4. `sleep`
5. 调 LibreOffice 命令行把 `xlsx` 转成 `csv`

对应文件：

- [evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json](../../evaluation_examples/examples/libreoffice_calc/0bf05a7d-b28b-44d2-955a-50b41e24012a.json)
- [desktop_env/controllers/setup.py](../../desktop_env/controllers/setup.py)

这几步非常值得你仔细理解。

## 八、为什么评测前还要先 `activate_window`

第一步：

- `activate_window`

会走：

- `SetupController._activate_window_setup(...)`

它的作用不是“再帮 agent 操作一次”，而是：

- 确保接下来的 `Ctrl+S` 真正发给 Calc 窗口

因为如果此时焦点不在 LibreOffice Calc 上，后面的保存快捷键就可能发错地方。

这说明 `postconfig` 不是随手写几条命令，而是：

- 明确考虑了桌面应用状态和窗口焦点

## 九、为什么还要显式发送 `Ctrl+S`

这一步非常关键。

任务不是只要求界面上看起来对，而是要让文件真的写回磁盘。

所以 evaluator 在正式取文件前，先通过：

- `python -c "import pyautogui; pyautogui.hotkey('ctrl', 's')"`

强制保存一次。

你可以把这一步理解成：

- “把 GUI 内存状态尽可能刷回文件系统”

这和前一篇 `chrome` 任务里的：

- 先重启 Chrome 再读配置

本质上是一类思路：

- evaluator 更在乎持久化后的真实状态

## 十、为什么保存后还要再导出 CSV

这是这篇最值得你记住的点。

`postconfig` 最后会执行：

- `libreoffice --convert-to csv ... Customers_New_7digit_Id.xlsx`

目的不是多余导出一份副本，而是为了让后面的评测能够检查：

- 工作表“打印出来/显示出来”的内容

不是只检查：

- Excel 文件内部的原始值

这两个概念在 Calc / Excel 任务里经常不一样。

## 十一、为什么这个任务不能只比 `xlsx` 内部值

因为任务要求是：

- 前面补零到 7 位

这个要求有一个典型坑：

- 内部值可能仍然是数字
- 但显示格式是带前导零的文本或格式化数字

如果只比原始内部数值，就很可能看不出：

- 屏幕上显示是不是 `0001234`

所以这个任务最后选的是：

- `sheet_print`

而不是：

- `sheet_data`

这正是 evaluator 设计最有意思的地方。

## 十二、这个任务的 `result` 和 `expected` 为什么都是“双文件”

任务 evaluator 里你会看到：

- `result.type = "vm_file"`
- `expected.type = "cloud_file"`
- 而且两边都 `multi = true`

对应文件：

- [desktop_env/evaluators/getters/file.py](../../desktop_env/evaluators/getters/file.py)

结果侧会取回：

1. `Customers_New_7digit_Id.xlsx`
2. `Customers_New_7digit_Id-Sheet1.csv`

期望侧会下载：

1. `Customers_New_7digit_Id_gold.xlsx`
2. `Customers_New_7digit_Id_gold-Sheet1.csv`

所以这个任务不是拿一个文件判分，而是：

- 用一组相关文件共同支持比对

## 十三、一个容易忽略但非常重要的实现细节

虽然 `result` / `expected` 都是多文件，但：

- `get_vm_file(...)`
- `get_cloud_file(...)`

默认真正“返回给 metric”的只有第一项。

也就是：

- 返回 `xlsx` 的本地缓存路径

第二个 CSV 文件不会直接作为 metric 参数返回，但仍然会被下载到任务 cache 目录里。

这意味着：

- `compare_table` 的入口参数表面上只拿到了 `xlsx`
- 但它仍然可以通过约定好的命名规则去找到旁边那份 `csv`

这一步如果不看代码，很难第一眼反应过来。

## 十四、`compare_table` 是怎么把 `xlsx` 和 `csv` 串起来的

对应文件：

- [desktop_env/evaluators/metrics/table.py](../../desktop_env/evaluators/metrics/table.py)

这个函数一开始会：

1. 用 `openpyxl` / `pandas` 打开 `xlsx`
2. 读取 sheet 名称
3. 根据 rule 决定后续是比内部值、打印值、样式、图表还是别的东西

而当 rule 类型是：

- `sheet_print`

时，它会走 `_load_sheet(book: str, index: str)` 这条分支。

这里的关键逻辑是：

```text
csv_name = {xlsx_without_ext}-{sheet_name}.csv
```

也就是说，如果 metric 拿到的是：

- `Customers_New_7digit_Id.xlsx`

而 sheet 名是：

- `Sheet1`

那它就会自动去找：

- `Customers_New_7digit_Id-Sheet1.csv`

这就解释了为什么任务要同时准备：

- xlsx
- 对应 sheet 导出的 csv

## 十五、`sheet_idx0 = 0` 和 `sheet_idx1 = "EI0"` 在说什么

这个任务的 rule 是：

```json
{
  "type": "sheet_print",
  "sheet_idx0": 0,
  "sheet_idx1": "EI0"
}
```

第一次看会有点抽象，但其实不复杂。

### 1. `sheet_idx0 = 0`

表示：

- 结果 workbook 的第 0 张 sheet

### 2. `sheet_idx1 = "EI0"`

表示：

- 期望 workbook 的第 0 张 sheet

`EI` 的意思可以粗暴记成：

- Expected Index

这个索引不是为了直接比 sheet 对象本身，而是为了先解析出：

- 结果 sheet 名
- 期望 sheet 名

然后再按这些 sheet 名去定位对应的 CSV 文件。

## 十六、`sheet_print` 真正在比什么

在 `compare_table(...)` 里，`sheet_print` 最终比较的是：

- 两边 CSV 的文本行列表是否完全一致

也就是说，比的是：

- 打印/显示出来的值

不是：

- 单元格底层公式对象
- 单元格内部原始数值

这一点非常契合这个任务的需求，因为“补零到 7 位”本质上是：

- 显示语义

而不只是：

- 数值语义

## 十七、为什么这个任务还能顺便约束“不要动无关区域”

任务指令里还有一句很重要：

- 不要触碰无关区域

它没有单独写成另一条 metric，但其实已经间接体现在：

- 整张 sheet 的打印值比对

因为如果你误改了别的格子，导出的 CSV 整体内容就会和 gold 不一致，`sheet_print` 也就过不了。

所以这个任务虽然只有一条 metric，但约束力其实不弱。

## 十八、把这个任务的 evaluate 链路压成 8 步

如果你要在脑子里快速回放一次，这个任务的评测阶段可以压成这样：

1. 激活 Calc 窗口
2. 发送 `Ctrl+S`
3. 用 LibreOffice 命令把 xlsx 转成 csv
4. 从 guest 取回结果 `xlsx`
5. 从 guest 取回结果 `csv`
6. 下载 gold `xlsx`
7. 下载 gold `csv`
8. `compare_table` 用 `sheet_print` 比两边导出的显示结果

这条链比前一篇 `chrome` 的 getter/metric 链更长，也更有“文件评测”的味道。

## 十九、这类 Calc 任务里，GUI 和 evaluator 是怎么分工的

这个任务特别适合帮助你建立一个更精确的分工观。

### 1. GUI 层负责完成编辑

也就是：

- 在 Calc 里找到位置
- 填公式或填结果
- 让界面状态看起来正确

### 2. evaluator 层负责验证持久化后的文件

也就是：

- 先保存
- 再导出
- 再拉回本地
- 再做结构化比对

这说明 OSWorld 的 Calc 题不是：

- “你在屏幕上看着差不多就算过”

而是：

- “文件内容和显示结果都要真的对”

## 二十、如果 action space 是 `pyautogui`，这个任务中间链是什么

如果你还是走默认 `pyautogui` 路线，那执行主链和前面差不多：

1. agent 看 screenshot / a11y tree
2. 模型输出点击、键入、快捷键等 `pyautogui` 代码
3. `PromptAgent.parse_actions()` 解析成动作列表
4. `DesktopEnv.step()` 逐条执行
5. `PythonController.execute_python_command()` 转发到 guest
6. `pyautogui` 在 Calc 里真实操作表格

所以这个任务难的不是“协议不同”，而是：

- GUI 精度要求更高
- evaluator 更严格

## 二十一、为什么这个任务比前一篇 Chrome 更能代表文件型 benchmark

因为它把 OSWorld 另一大类任务的典型模式完整暴露出来了：

- 输入是文件
- 操作发生在桌面应用里
- 成功判定最终回到文件

这和 `chrome` 任务里的：

- 输入是应用状态
- 成功判定回到配置文件

是同一设计哲学的两个变体。

你可以把两篇放在一起看：

- `chrome` 更像“软件配置状态题”
- `calc` 更像“文档/表格结果题”

## 二十二、这个任务跑完后，你应该优先看哪几个文件

如果你自己调试一次这个任务，建议按这个顺序看结果目录。

### 1. `traj.jsonl`

看 agent 走了多少步、最后是不是 `DONE`。

### 2. `runtime.log`

看 agent 当时的响应和退出条件。

### 3. `result.txt`

看 evaluator 最终给了 0 还是 1。

### 4. task cache 里的结果文件

尤其是：

- 拉回来的结果 `xlsx`
- 拉回来的结果 `csv`
- 对应的 gold 文件

如果最终分数不对，这几份文件是最值得对照的。

## 二十三、如果你看到 `result = 0`，最可能的几类原因

这个任务的失败通常可以先从三类问题排查。

### 1. GUI 操作没完成

例如：

- 填错列
- 没批量填完整
- 改到了不该改的格子

### 2. 保存或导出没成功

例如：

- `Ctrl+S` 没打到 Calc 窗口
- 导出 CSV 失败
- 文件没及时写回磁盘

### 3. 显示值和内部值不一致

例如：

- 内部数字对了
- 但显示格式不是 7 位补零

这第三类，正是这个任务用 `sheet_print` 的原因。

## 二十四、从代码设计上，这个任务最值得你记住哪三件事

### 1. `postconfig` 不是附属品

它经常是评测链条不可缺的一环。

### 2. `multi file` 不等于 metric 直接收到一组路径

很多时候 metric 只显式拿到主文件，其余文件按命名约定在旁边配合使用。

### 3. `sheet_print` 和 `sheet_data` 语义完全不同

一个偏显示结果，一个偏内部数据。

如果你以后自己设计 evaluator，这个区分必须非常清楚。

## 二十五、读完这一篇后，你应该能回答什么

到这里你应该能回答下面几个问题：

1. 这个 Calc 任务为什么要在评测前再保存一次？
2. 为什么 evaluator 还要再导出一份 CSV？
3. `compare_table` 怎么从一个 `xlsx` 路径推到对应的 `csv` 文件？
4. 为什么这个任务选 `sheet_print` 而不是 `sheet_data`？
5. “不要动无关区域”是怎么被 evaluator 间接约束住的？

如果这五个问题你都能答出来，说明你已经真正吃透了一类很典型的 OSWorld 文档任务。

## 二十六、你现在最适合做的两个小实验

### 1. 对照 `table.py` 自己手推一次文件名

拿这个任务的结果文件名，自己推一遍：

- `Customers_New_7digit_Id.xlsx`
- `Sheet1`
- 最终对应哪一个 CSV

只要这一步你能手推对，`compare_table` 的这层约定你就真的理解了。

### 2. 再找一个 `compare_table` 任务，看 rule 类型是否不同

比如去看其他 Calc 任务里有没有：

- `sheet_data`
- `style`
- `chart`

你会很快发现：

- 同样叫表格评测，内部其实细分得很深

## 二十七、接下来再看哪部分最顺

如果还继续沿“具体任务端到端”这条线走，下一步最有价值的是再挑一个：

- 多 metric 组合
- 或带样式 / 图表比对

的 Calc 任务。

这样你会看到 `compare_table` 不只是比单元格文本，还能往：

- 样式
- 图表
- 数据透视表

这些方向扩展。

如果你愿意，我下一篇可以继续补：

- `14-calc-chart-or-style-task-end-to-end_zh.md`

专门选一个带 `chart` 或 `style` rule 的 Calc 任务，继续往深处走。
