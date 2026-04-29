# 12 Chrome 任务端到端走读

这一篇接在 [11 Monitor 与运行结果解读](./11-monitor-and-results_zh.md) 后面看最自然。

前面几篇你已经把主干模块都拆开看过了：

- 任务 JSON
- `DesktopEnv`
- `PromptAgent`
- runner
- evaluator
- results / monitor

现在最适合做的，不是继续加新模块，而是：

- 选一个具体任务
- 把整条链从头到尾走一遍

这一篇就做这件事。

## 先说这篇选哪个任务

我选的是这个 `chrome` 任务：

- [evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)

任务指令是：

- “Can you make Bing the main search engine when I look stuff up on the internet?”

也就是：

- 把 Chrome 默认搜索引擎切成 Bing

我选它的原因很简单：

1. setup 很短
2. agent 行为容易脑补
3. evaluator 很干净
4. 成功判定依赖持久化状态，不只是看屏幕

这正好能把 OSWorld 里最重要的几层串起来。

## 一、先把这个任务 JSON 读成一句人话

先看任务文件本身：

- [evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)

你可以把它翻译成下面这句话：

- 启动一个可被控制的 Chrome 环境
- 让 agent 自己去改设置
- 最后不要靠肉眼判断，而是直接去读 Chrome 配置文件，确认默认搜索引擎是不是 Bing

这就是一个非常典型的 OSWorld 任务。

## 二、这个任务的四块核心字段

第一次读时，只抓四块就够了：

- `instruction`
- `config`
- `evaluator.postconfig`
- `evaluator`

## 三、`instruction` 是 agent 真正看到的任务目标

这个任务的 `instruction` 是：

```text
Can you make Bing the main search engine when I look stuff up on the internet?
```

它最终会进入：

- `PromptAgent.predict(instruction, obs)`

所以对 agent 来说，最关键的不是 task id，不是 source，而是这一句自然语言目标。

## 四、`config` 做了什么

这个任务的 `config` 很短，只有两步：

1. 启动 Chrome，并打开 `--remote-debugging-port=1337`
2. 启动 `socat`，把 `9222` 转发到 `1337`

对应文件：

- [evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)
- [desktop_env/controllers/setup.py](../../desktop_env/controllers/setup.py)

## 五、这两步 setup 是怎么落到代码里的

当 runner 调：

- `env.reset(task_config=example)`

时，`DesktopEnv.reset()` 会做几件事：

1. 设置 task 基本信息
2. 把 `task_config["config"]` 存到 `self.config`
3. 调 `self.setup_controller.setup(self.config, ...)`

对应文件：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)

而 `SetupController.setup(...)` 的逻辑很直接：

- 遍历每个 setup item
- 取出 `type`
- 调用同名的 `_{type}_setup(...)`

所以这个任务里的两个：

- `type: "launch"`

最后都会走到：

- `SetupController._launch_setup(...)`

## 六、`launch` 为什么不是本地起进程

这一点一定要记住。

`SetupController._launch_setup(...)` 不是在宿主机上启动 Chrome。

它会发 HTTP 请求到 guest server 的：

- `/setup/launch`

也就是说，真正被启动的是：

- 虚拟机里的 Chrome

而不是你本机的浏览器。

这也是整个仓库的一个核心心智模型：

- 宿主机只是在“远程编排”
- 真正执行 GUI 的是 guest OS

## 七、为什么这里有 `1337` 和 `9222` 两个端口

这是这个任务里最值得你注意的小细节之一。

任务 JSON 里是这样写的：

- Chrome 用 `--remote-debugging-port=1337`
- `socat` 再把 `9222 -> 1337`

而 `SetupController` / `DesktopEnv` 默认理解的 Chromium 调试端口通常是：

- `9222`

所以更合理的理解是：

- Chrome 实际监听 `1337`
- 任务再额外把仓库习惯使用的 `9222` 转发过去

这样一些依赖远程调试接口的 getter 或工具，仍然可以按统一端口访问浏览器。

这不是任务本身的业务目标，而是：

- 环境可控性准备

## 八、这一层 setup 完成后，agent 才真正开始做任务

看：

- [lib_run_single.py](../../lib_run_single.py)

单任务主循环大致是：

1. `env.reset(task_config=example)`
2. `agent.reset(...)`
3. 等待环境稳定
4. `obs = env._get_obs()`
5. `response, actions = agent.predict(instruction, obs)`
6. 对每个 action 调 `env.step(action, ...)`
7. 循环直到 `done` 或 `max_steps`
8. `env.evaluate()`

所以这类 GUI 任务的核心不是 setup，而是：

- setup 只是把舞台搭好
- 真正完成任务还是靠 agent 一步步操作界面

## 九、这个任务里，agent 实际会做什么

这里要注意一件事：

- 代码里并没有写死“点击哪里”

也就是说，仓库不会给这个任务内置一个固定动作序列。

真正的点击路径，取决于：

- 当前使用的 agent
- 观测类型
- 模型输出
- 当时页面状态

所以下面这段不是事实日志，而是根据任务目标和代码行为做的合理推测：

- agent 大概率会打开 Chrome 设置
- 找到 Search engine / 默认搜索引擎设置
- 把当前值改成 Bing
- 然后返回 `DONE`

你要养成这个阅读习惯：

- 任务 JSON 定义目标
- 但不定义固定点击轨迹

这和很多“录制回放式自动化”完全不同。

## 十、如果 action space 是 `pyautogui`，中间链路是什么

如果你用的是默认链路，比如：

- `action_space="pyautogui"`

那这个任务里的主执行链通常是：

1. agent 看 screenshot / a11y tree
2. 模型输出 `pyautogui` 代码
3. `PromptAgent.parse_actions()` 把代码块解析成 action 字符串列表
4. `DesktopEnv.step()` 直接执行这些代码
5. `PythonController.execute_python_command()` 把命令发给 guest server
6. guest 里的 `pyautogui` 真正操作 Chrome

如果你脑子里能把这 6 步串起来，就不会再把“任务逻辑”和“执行协议”混在一起。

## 十一、这个任务真正有意思的地方，在评测

这个任务不是靠看页面上有没有 Bing 字样来判断成功。

它的 evaluator 是：

- `func = "match_in_list"`
- `result.type = "default_search_engine"`
- `expected.type = "rule"`

这说明它最后走的是：

- 从浏览器配置里取“当前默认搜索引擎”
- 再和预期列表做匹配

也就是说，这个任务是：

- 状态型评测

而不是单纯的界面型评测。

## 十二、`DesktopEnv` 是怎么把 evaluator 绑定起来的

当 `env.reset(task_config=example)` 时，`DesktopEnv._set_task_info()` 会进一步调用：

- `_set_evaluator_info(task_config)`

在这里，环境会做三件事：

1. 用 `self.evaluator["func"]` 找到 metric 函数
2. 用 `self.evaluator["result"]["type"]` 找到 result getter
3. 用 `self.evaluator["expected"]["type"]` 找到 expected getter

对于这个任务，最终绑定出来的是：

- `metric = metrics.match_in_list`
- `result_getter = getters.get_default_search_engine`
- `expected_getter = getters.get_rule`

对应文件：

- [desktop_env/desktop_env.py](../../desktop_env/desktop_env.py)
- [desktop_env/evaluators/getters/__init__.py](../../desktop_env/evaluators/getters/__init__.py)
- [desktop_env/evaluators/metrics/__init__.py](../../desktop_env/evaluators/metrics/__init__.py)

这一步非常重要，因为它说明：

- evaluator 并不是 if/else 写死在环境里的
- 而是按字符串动态映射

## 十三、为什么评测前还要做 `postconfig`

这个任务的 `evaluator.postconfig` 有三步：

1. `pkill chrome`
2. 重新启动 Chrome
3. `sleep 3`

这看起来像“多此一举”，但其实很合理。

更可信的理解是：

- agent 改完设置后，Chrome 内存中的状态未必已经完全刷到磁盘
- 先关掉再重启一次，更像是在验证“持久化后的默认状态”

从代码看，这三步会在：

- `env.evaluate()`

开头通过：

- `self.setup_controller.setup(postconfig, ...)`

先执行掉。

所以这里不是“跑完任务再顺手开一下 Chrome”，而是：

- postconfig 本身就是评测流程的一部分

## 十四、`result.type = default_search_engine` 实际干了什么

对应 getter：

- [desktop_env/evaluators/getters/chrome.py](../../desktop_env/evaluators/getters/chrome.py)

`get_default_search_engine(env, config)` 的逻辑是：

1. 先判断 guest OS 类型
2. 再根据平台构造 Chrome / Chromium 的 Preferences 文件路径
3. 通过 `env.controller.get_file(...)` 把这个文件从 guest 取回来
4. `json.loads(...)`
5. 读取：
   `default_search_provider_data -> template_url_data -> short_name`
6. 返回搜索引擎短名，例如 `Google` 或 `Bing`

也就是说，这个 getter 根本不看当前屏幕。

它看的是真实配置文件。

这就是 OSWorld 很值得学的一点：

- UI 任务不一定只用 UI 来评测

## 十五、这个 getter 对 ARM / x86 的分支值得你留意

`get_default_search_engine(...)` 在 Linux 下会分两条路径：

- ARM: `~/snap/chromium/common/chromium/Default/Preferences`
- 非 ARM: `~/.config/google-chrome/Default/Preferences`

这说明在仓库里：

- task setup 的浏览器启动方式
- evaluator 的配置文件读取方式

并不一定完全集中在同一处统一抽象。

你读代码时要把这两层分开看：

1. setup 关心“把浏览器起起来”
2. getter 关心“到哪读持久化状态”

如果你后面自己改任务或适配新平台，这种细节会很关键。

## 十六、`expected.type = rule` 干了什么

这个任务的 expected 部分是：

```json
{
  "type": "rule",
  "rules": {
    "expected": [
      "Microsoft Bing",
      "Bing"
    ]
  }
}
```

这里对应的 getter 是：

- `get_rule(...)`

它做的事非常简单：

- 原样返回 `rules`

也就是说，这个任务的 expected 并不是要去 guest 里读取另一个状态，而只是把规则包装成 metric 的第二个参数。

## 十七、`match_in_list` 最后怎么给分

对应 metric：

- [desktop_env/evaluators/metrics/general.py](../../desktop_env/evaluators/metrics/general.py)

逻辑非常直接：

1. 取出 `rules["expected"]`
2. 判断 `result in expected_list`
3. 命中返回 `1.0`
4. 否则返回 `0.0`

所以这个任务最终判分可以压成一句话：

- `get_default_search_engine()` 返回的短名，只要是 `Microsoft Bing` 或 `Bing`，就算成功

## 十八、把这个任务的 evaluate 链路压成 6 步

如果你要在脑子里快速回放一次，这个任务的评测阶段就是：

1. 先执行 `postconfig`
2. 读取 Chrome Preferences 文件
3. 提取默认搜索引擎短名
4. 读取 expected 规则
5. 调 `match_in_list`
6. 返回 `0.0` 或 `1.0`

这条链足够清楚时，你后面看别的任务也不容易乱。

## 十九、这个任务最终会在结果目录里留下什么

跑完后你通常会在对应 task 目录里看到：

- `traj.jsonl`
- `runtime.log`
- `result.txt`
- `recording.mp4`
- 每一步截图

其中这个任务最值得看的三样是：

### 1. `traj.jsonl`

看 agent 一共走了多少步，最后是不是返回了 `DONE`。

### 2. `runtime.log`

看模型当时的输出、退出条件、有没有异常。

### 3. `result.txt`

看 evaluator 最终打了几分。

如果 `result.txt = 0`，但你觉得肉眼上已经切成 Bing 了，那就说明：

- agent 可能只改了表面 UI
- 或设置没真正持久化
- 或 evaluator 读取的不是你以为的那个 profile 状态

这正是端到端任务里最有价值的排查入口。

## 二十、这个任务在 monitor 里会怎么显示

对照：

- [monitor/main.py](../../monitor/main.py)
- [monitor/templates/task_detail.html](../../monitor/templates/task_detail.html)

这个任务在 monitor 详情页里，你通常会看到：

- 基本 instruction
- 当前状态
- step 数
- 每一步截图
- 录屏
- result

但要记住：

- monitor 展示的是执行过程
- 真正决定成功与否的，还是 evaluator 的结果文件

也就是说：

- 页面看起来像成功，不等于 evaluator 会给 1 分

## 二十一、你从这个任务里应该学到什么

这个任务虽然小，但它把 OSWorld 的核心设计特点都暴露出来了。

### 1. 任务定义和执行分开

JSON 只定义目标、setup 和评测，不提供固定操作脚本。

### 2. setup 和评测都是可编排步骤

`config` 和 `postconfig` 都走 `SetupController`。

### 3. GUI 行为和成功判定可以分离

agent 通过 GUI 改设置，但 evaluator 通过文件状态判分。

### 4. 成功不等于“看起来对”

真正的成功是：

- 状态被持久化
- getter 读出来的结果满足 metric

## 二十二、如果你要自己手动验证一次，这样最有效

你可以按这个顺序做一次人工排查。

### 1. 先看任务 JSON

确认：

- setup 起了什么
- evaluator 要什么

### 2. 再看 `traj.jsonl`

确认：

- agent 最后是否真的走到了设置页并返回 `DONE`

### 3. 再看 `result.txt`

确认：

- evaluator 是否真的给了 1 分

### 4. 如果结果不对，再去看 getter 逻辑

也就是：

- `get_default_search_engine(...)`

看看它到底读的是哪个 Preferences 文件路径。

## 二十三、两个你可以立刻做的小实验

### 1. 手动打开这个任务 JSON，再口头复述一次链路

你可以试着不看文档，自己复述：

- 它怎么 setup
- agent 做什么
- evaluator 读什么
- metric 怎么判断

如果能说顺，就说明你已经不是“看懂文件”，而是“看懂链路”了。

### 2. 在代码里全局搜索 `default_search_engine`

重点看：

- getter 导出
- getter 实现
- 任务 JSON 引用

这样你会更直观看到：

- 一个 `result.type` 是怎么一路连到具体 Python 函数上的

## 二十四、读完这一篇后，下一步最顺的方向

接下来你有两个都很自然的方向。

### 方向 A：再挑一个 evaluator 更复杂的任务

比如：

- 需要多个 metric 组合
- 需要文件内容比对
- 需要网页信息抽取

这样你会看到 OSWorld 不只是简单布尔判分。

### 方向 B：挑一个操作路径更复杂的应用域

例如：

- `libreoffice_calc`
- `gimp`
- `thunderbird`

这样你会更直观地看到：

- agent 动作复杂度
- evaluator 复杂度

是如何一起上升的。

如果你愿意，我下一篇可以继续补：

- `13-calc-task-end-to-end_zh.md`

专门挑一个带文件结果校验和多步骤配置的 Calc 任务，再做一次完整走读。
