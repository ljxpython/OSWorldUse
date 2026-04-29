# 10 Actions 与 Action Space 解读

这一篇接在 [09 evaluation_examples 与任务数据解读](./09-evaluation-examples-and-task-data_zh.md) 后面看最合适。

因为到了这一步，你已经知道：

- 任务 JSON 是怎么定义的
- `DesktopEnv` 怎么 reset / step / evaluate
- `PromptAgent` 怎么根据观测生成下一步
- controller 和 guest server 怎么通信

现在还差最后一块关键拼图：

- Agent 输出的“动作”到底长什么样？
- 环境又是怎么把这个动作真正执行到虚拟机里的？

这一层就是：

- `action space`

## 先记住最重要的一句话

在这个项目里，`action space` 不只是“有哪些鼠标键盘操作”。

它更准确地说是：

- Agent 和环境之间的输出协议

也就是说，模型最后吐出来的内容，必须满足某种约定格式，环境才能接得住并执行。

## 一、这个仓库里其实有两种主动作表示

对应到代码里，最常见的是这两类：

- `computer_13`
- `pyautogui`

另外还有：

- `claude_computer_use`

但从 `DesktopEnv.step()` 的执行分支看，它当前基本走的是和 `pyautogui` 相近的路径。

### 1. `computer_13`

这是结构化动作。

也就是模型返回一个 JSON 风格的动作对象，例如：

```json
{
  "action_type": "CLICK",
  "parameters": {
    "x": 800,
    "y": 420
  }
}
```

这种表示的特点是：

- 结构清楚
- 动作类型固定
- 参数显式
- 更像“动作 DSL”

### 2. `pyautogui`

这是代码型动作。

也就是模型直接返回可执行的 Python 代码，例如：

```python
pyautogui.click(800, 420)
```

或者：

```python
pyautogui.hotkey('ctrl', 'l')
pyautogui.typewrite('spotify')
pyautogui.press('enter')
```

这种表示的特点是：

- 灵活
- 表达力强
- 模型更容易一次写出多步组合动作
- 但也更容易产生“代码合法但行为不稳”的问题

### 3. `quickstart.py` 默认用的是哪种

你已经跑过的入口：

- [quickstart.py](../../quickstart.py)

默认就是：

- `action_space="pyautogui"`

所以你现在最直接接触到的真实执行链，主要是：

- 模型或脚本生成 `pyautogui` 代码
- `DesktopEnv.step()` 把它转发给 guest server 执行

## 二、`desktop_env/actions.py` 在定义什么

对应文件：

- [desktop_env/actions.py](../../desktop_env/actions.py)

这个文件最核心的内容有两个：

- `KEYBOARD_KEYS`
- `ACTION_SPACE`

### 1. `KEYBOARD_KEYS`

这是允许按下的键名集合。

后面在：

- `PRESS`
- `KEY_DOWN`
- `KEY_UP`
- `HOTKEY`

这些动作里会被 controller 用来做校验。

### 2. `ACTION_SPACE`

这里列出了 `computer_13` 风格动作的 schema。

你第一次看时，重点记住这些动作类别就够了：

- `MOVE_TO`
- `CLICK`
- `MOUSE_DOWN`
- `MOUSE_UP`
- `RIGHT_CLICK`
- `DOUBLE_CLICK`
- `DRAG_TO`
- `SCROLL`
- `TYPING`
- `PRESS`
- `KEY_DOWN`
- `KEY_UP`
- `HOTKEY`
- `WAIT`
- `FAIL`
- `DONE`

### 3. 这份 schema 的作用是什么

它的作用不只是“给人看”。

它至少承担了三层语义：

1. 告诉你结构化动作有哪些类型
2. 告诉 prompt 设计时模型应该输出什么格式
3. 告诉 controller 最终需要支持哪些动作语义

但你要注意一个容易误解的点：

- `ACTION_SPACE` 并没有被做成一个统一的运行时验证器

也就是说，执行时不是先拿动作去和这份 schema 做通用校验，然后再执行。

当前更接近的是：

- prompt 侧靠文字约束
- parser 侧做格式解析
- controller 侧按 `if/elif` 分支检查参数并执行

所以它更像：

- “动作协议定义”

而不是一个严格的“统一验证层”。

### 4. 坐标范围是怎么定的

`desktop_env/actions.py` 里写死了：

- `X_MAX = 1920`
- `Y_MAX = 1080`

这表示 prompt 里默认把屏幕当成 1920x1080 来描述。

这和环境初始化里：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

的默认 `screen_size=(1920, 1080)` 是一致的。

这也解释了为什么大部分动作坐标都是按这个分辨率理解。

## 三、PromptAgent 是怎么决定“要输出 JSON 还是代码”的

对应文件：

- [mm_agents/agent.py](../../mm_agents/agent.py)
- [mm_agents/prompts.py](../../mm_agents/prompts.py)

这里最重要的入口是：

- `PromptAgent.__init__`

## 四、`observation_type` 和 `action_space` 是一起决定 prompt 的

在初始化时，`PromptAgent` 会根据两件事选系统提示词：

- 观测类型 `observation_type`
- 动作空间 `action_space`

例如：

- `screenshot + computer_13` -> `SYS_PROMPT_IN_SCREENSHOT_OUT_ACTION`
- `screenshot + pyautogui` -> `SYS_PROMPT_IN_SCREENSHOT_OUT_CODE`
- `screenshot_a11y_tree + computer_13` -> `SYS_PROMPT_IN_BOTH_OUT_ACTION`
- `screenshot_a11y_tree + pyautogui` -> `SYS_PROMPT_IN_BOTH_OUT_CODE`

这点很重要，因为它说明：

- 动作空间不是执行阶段临时决定的
- 而是在 Agent 构造时就已经决定了模型“该按什么协议说话”

### 1. `computer_13` prompt 的特点

在：

- [mm_agents/prompts.py](../../mm_agents/prompts.py)

里，`*_OUT_ACTION` 这类 prompt 会直接把动作 schema 贴给模型。

也就是说，模型会被明确要求输出：

- JSON 风格动作对象

### 2. `pyautogui` prompt 的特点

而 `*_OUT_CODE` 这类 prompt 会明确要求模型返回：

- `pyautogui` Python 代码块

并且通常还会强调：

- 不要调用截图函数
- 不要依赖历史变量
- 可以返回多行代码
- 遇到结束或不可做时返回 `WAIT` / `DONE` / `FAIL`

### 3. 一个值得注意的实现细节

`computer_13` 的动作 schema，在 prompt 文件里其实是复制进去的。

这意味着：

- `mm_agents/prompts.py` 有自己的一份动作描述
- `desktop_env/actions.py` 也有一份动作定义

从工程上看，这带来一个你后面读代码时要留意的点：

- 动作协议存在“定义重复”

也就是说，如果以后有人改了一边没改另一边，就可能出现：

- prompt 让模型输出一种格式
- controller 却按另一种格式执行

这不是你现在要改的东西，但它是理解这个模块时值得记住的风险点。

## 五、模型返回后，是怎么被解析成动作列表的

还是看：

- [mm_agents/agent.py](../../mm_agents/agent.py)

关键入口是：

- `PromptAgent.parse_actions(...)`

它的逻辑非常直接：

- `computer_13` -> `parse_actions_from_string(response)`
- `pyautogui` -> `parse_code_from_string(response)`
- `som + pyautogui` -> `parse_code_from_som_string(response, masks)`

### 1. `parse_actions_from_string`

这个函数处理结构化动作。

支持几种常见返回形式：

- 直接返回 `WAIT` / `DONE` / `FAIL`
- ```json ... ``` 代码块
- 普通 ``` ... ``` 代码块
- 纯 JSON 字符串

最后得到的是：

- `List[action]`

其中每个 `action` 通常是一个 dict，或者是特殊字符串。

### 2. `parse_code_from_string`

这个函数处理 `pyautogui` 代码动作。

它会：

1. 先做一个简单的分号切分和清理
2. 提取代码块里的内容
3. 识别末尾是不是 `WAIT` / `DONE` / `FAIL`
4. 返回代码字符串列表

所以对 `pyautogui` 来说，动作列表里装的通常不是 dict，而是：

- Python 代码字符串

### 3. `parse_code_from_som_string`

这个分支是给 `som` 观测用的。

它会先把每个候选框生成类似：

```python
tag_1 = (x, y)
tag_2 = (x, y)
```

这样的局部变量，再把模型输出的代码拼接上去。

这说明：

- 某些 action space 的变化，不只是执行层差异
- 还会反过来影响模型提示和解析逻辑

## 六、`WAIT` / `DONE` / `FAIL` 是全链路里的特殊动作

这一点很容易忽略，但它很关键。

无论你用的是：

- `computer_13`
- `pyautogui`

这三个特殊动作都会被统一处理：

- `WAIT`
- `DONE`
- `FAIL`

在：

- [mm_agents/agent.py](../../mm_agents/agent.py)

里，它们会被 parser 识别出来。

在：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

的 `step()` 里，它们会先被环境拦截：

- `WAIT` -> `sleep(pause)`
- `DONE` -> `done = True`
- `FAIL` -> `done = True` 且写入失败信息

这意味着它们不是普通桌面操作，而是：

- trajectory 控制信号

也就是告诉运行器：

- 继续等等
- 我认为任务完成了
- 我认为任务做不下去了

## 七、环境执行时，`DesktopEnv.step()` 怎么分发动作

对应文件：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

`step()` 的核心分发逻辑可以脑补成这样：

```text
action
  -> 先处理 WAIT / DONE / FAIL
  -> 如果 action_space == computer_13:
       controller.execute_action(action)
  -> 如果 action_space == pyautogui / claude_computer_use:
       controller.execute_python_command(...)
  -> sleep(pause)
  -> _get_obs()
```

这里最关键的是：

- `computer_13` 走“结构化动作执行”
- `pyautogui` 走“代码字符串执行”

这是两条完全不同的中间层协议。

### 1. `computer_13` 分支

环境会把 dict 动作直接交给：

- `self.controller.execute_action(action)`

此时 controller 负责：

- 检查参数
- 选择对应的 pyautogui 调用
- 在 guest 里真正执行

### 2. `pyautogui` 分支

如果动作不是特殊字符串，环境会认为它本身就是可执行代码。

然后：

- 如果 `action` 是字符串，就直接执行这段代码
- 如果 `action` 是 dict，就取其中的 `action['command']`

### 3. `<` 字符有一个专门修复

在 `pyautogui` 分支里，执行前会先过：

- `_fix_pyautogui_less_than_bug(...)`

对应文件：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

这个函数是专门修：

- `pyautogui` 输入 `<` 时可能变成 `>` 的问题

它会把某些：

- `pyautogui.press('<')`
- `pyautogui.typewrite("a<b")`

改写成更稳的：

- `pyautogui.hotkey("shift", ",")`

这是一个很典型的“真实桌面自动化坑”。

也说明这个项目不是纯逻辑模拟，而是真的踩过 guest OS 输入层问题。

## 八、`PythonController` 是怎么把动作变成真实输入的

对应文件：

- [desktop_env/controllers/python.py](../../desktop_env/controllers/python.py)

这一层你可以把它理解成：

- “环境到 guest server 的远程控制代理”

它不是直接在宿主机上操作鼠标键盘，而是：

1. 拼出要执行的 Python 命令
2. 通过 HTTP 发给虚拟机里的 server
3. 让 guest OS 内部去执行 `pyautogui`

### 1. `execute_python_command(...)`

这个函数会把命令包成：

```python
python -c "import pyautogui; import time; pyautogui.FAILSAFE = False; ..."
```

然后发到：

- guest server 的 `/execute` 接口

对应 server 端代码在：

- [desktop_env/server/main.py](../../desktop_env/server/main.py)

这也是为什么你要把 controller 理解成：

- 远程命令转发器

而不是本地输入模拟器。

### 2. `execute_action(...)`

这个函数就是 `computer_13` 分支真正的执行器。

它本质上是一个很长的 `if/elif` 分发器：

- `MOVE_TO` -> `pyautogui.moveTo(...)`
- `CLICK` -> `pyautogui.click(...)`
- `RIGHT_CLICK` -> `pyautogui.rightClick(...)`
- `DOUBLE_CLICK` -> `pyautogui.doubleClick(...)`
- `DRAG_TO` -> `pyautogui.dragTo(...)`
- `SCROLL` -> `pyautogui.hscroll(...)` / `pyautogui.vscroll(...)`
- `TYPING` -> `pyautogui.typewrite(...)`
- `PRESS` -> `pyautogui.press(...)`
- `KEY_DOWN` -> `pyautogui.keyDown(...)`
- `KEY_UP` -> `pyautogui.keyUp(...)`
- `HOTKEY` -> `pyautogui.hotkey(...)`

也就是说：

- `computer_13` 不是一种完全不同的底层执行技术

它最后还是会落到：

- `pyautogui`

只不过中间多了一层：

- 结构化动作 -> controller 翻译 -> pyautogui 命令

### 3. `MOVE_TO` 有一点“人为动作感”

你如果看 `execute_action(...)` 会发现：

- 鼠标移动会随机选一个 easing 函数
- duration 也会随机在一小段范围内变化

这表示系统并不是每次都瞬移鼠标，而是尝试带一点：

- 更自然的轨迹

### 4. 并不是所有参数都做了统一强校验

controller 对键盘动作会检查：

- key 是否在 `KEYBOARD_KEYS` 里

但其他动作更多是：

- 检查参数是否存在
- 再按分支执行

所以如果你后面调试动作错误，要优先判断三类问题：

1. 模型返回格式不对
2. 参数名不对
3. 坐标或动作语义虽然合法，但点错了位置

## 九、把整条链路用一个例子串起来

假设模型要执行“点击浏览器地址栏”。

### 路径 A：`computer_13`

模型输出：

```json
{
  "action_type": "CLICK",
  "parameters": {
    "x": 840,
    "y": 84
  }
}
```

之后流程是：

1. `PromptAgent.parse_actions()` 解析成 dict
2. `DesktopEnv.step()` 发现 action space 是 `computer_13`
3. `PythonController.execute_action()` 识别 `CLICK`
4. 拼成 `pyautogui.click(x=840, y=84)`
5. 发给 guest server 执行

### 路径 B：`pyautogui`

模型输出：

```python
pyautogui.click(840, 84)
```

之后流程是：

1. `PromptAgent.parse_actions()` 解析成代码字符串
2. `DesktopEnv.step()` 发现 action space 是 `pyautogui`
3. 环境直接把这段代码交给 `execute_python_command()`
4. guest server 在虚拟机内部执行它

所以你可以把两者的差别总结成一句话：

- `computer_13` 是“先出动作对象，再由 controller 翻译”
- `pyautogui` 是“直接出可执行代码”

## 十、为什么这个设计值得你特别理解

因为它直接决定了三个阅读方向。

### 1. 你在 debug 什么问题

如果是 `computer_13` 出错，你通常要查：

- prompt 有没有让模型按 schema 输出
- parser 有没有正确解析 JSON
- `execute_action` 有没有支持那个动作参数组合

如果是 `pyautogui` 出错，你通常要查：

- 模型生成的代码本身对不对
- 坐标对不对
- 特殊字符输入有没有踩到系统问题

### 2. 你在扩展什么能力

如果你未来要新增动作能力，例如：

- 拖拽变体
- 文本选择
- 更复杂的组合键

对于 `computer_13`，你通常要同时改：

- 动作 schema
- prompt 文案
- parser 兼容性
- `execute_action`

而对于 `pyautogui`，更多可能只需要：

- 在 prompt 中允许模型这么写
- 确保 guest 中 `pyautogui` 能执行

### 3. 你在权衡什么 tradeoff

`computer_13` 的优点是：

- 约束更强
- 更容易统计动作类型
- 更容易做行为分析

`pyautogui` 的优点是：

- 表达力更高
- 多步操作更自然
- 对模型来说生成门槛更低

所以这不是“哪个高级哪个低级”的问题，而是：

- 强约束协议
- 自由代码协议

两种设计取舍不同。

## 十一、你现在可以自己做的几个小实验

### 1. 观察 `quickstart.py` 走的是哪条分支

看：

- [quickstart.py](../../quickstart.py)
- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

重点确认：

- 默认 `action_space` 是 `pyautogui`
- `env.step("pyautogui.rightClick()")` 会直接走代码执行分支

### 2. 手动构造一个 `computer_13` 动作

你可以把 `quickstart.py` 里的：

```python
obs, reward, done, info = env.step("pyautogui.rightClick()")
```

临时换成：

```python
obs, reward, done, info = env.step({
    "action_type": "RIGHT_CLICK",
    "parameters": {"x": 960, "y": 540}
})
```

然后观察：

- 环境是不是还能正常执行
- 这次会走 `execute_action(...)` 而不是直接执行代码

### 3. 故意构造一个非法键名

例如：

```python
obs, reward, done, info = env.step({
    "action_type": "PRESS",
    "parameters": {"key": "not_a_real_key"}
})
```

这样你可以亲自看到：

- controller 的键盘参数校验在哪一层触发

### 4. 搜一遍 `WAIT` / `DONE` / `FAIL`

建议全局搜索：

- `WAIT`
- `DONE`
- `FAIL`

你会更直观地看到：

- 它们不是单个 agent 的局部约定
- 而是贯穿 prompt、parser、环境 step、evaluate 的全链路控制信号

## 十二、读完这一篇后，下一步看什么最顺

如果你已经能把：

- 模型输出
- parser 解析
- `DesktopEnv.step()`
- controller 执行

这四层串起来，那接下来最适合继续看的方向有两个。

### 方向 A：看结果是怎么被记录和展示的

可以继续看：

- `monitor/`
- 运行结果目录
- 轨迹、截图、日志的组织方式

### 方向 B：挑一个真实应用域深挖

例如：

- `chrome`
- `libreoffice_calc`
- `gimp`

去对照任务 JSON、实际界面和动作轨迹，看这个 action space 在真实任务里是怎么被用起来的。

如果你愿意，我下一篇可以继续补：

- `11-monitor-and-results_zh.md`

把运行结果、日志、可视化页面、轨迹产物怎么读这一层接上。
