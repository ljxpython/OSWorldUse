# 11 Monitor 与运行结果解读

这一篇接在 [10 Actions 与 Action Space 解读](./10-actions-and-action-space_zh.md) 后面看最顺。

因为到这里你已经知道：

- 任务怎么定义
- 环境怎么执行
- Agent 怎么出动作
- controller 怎么把动作落到 guest 里

现在你还需要补上最后一层：

- 跑完之后，结果都存哪了？
- monitor 页面到底在看什么？
- 如果一个任务跑挂了，第一眼应该先查哪个文件？

这篇就只解决这三件事。

## 先记住最重要的一句话

这个项目里：

- `results/...` 才是真正的事实来源
- `monitor/` 只是把这些文件再展示一遍

也就是说，monitor 本身并不决定任务状态。

它只是读取：

- `traj.jsonl`
- `runtime.log`
- `result.txt`
- `recording.mp4`
- 截图文件

然后推断出页面上的：

- Running
- Done
- Error

## 一、结果目录是怎么组织的

先看：

- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

这两个入口都会把单任务结果目录组织成类似结构：

```text
results/
  {action_space}/
    {observation_type}/
      {model}/
        args.json
        {domain}/
          {task_id}/
            traj.jsonl
            runtime.log
            result.txt
            recording.mp4
            step_1_xxx.png
            step_2_xxx.png
            ...
```

例如：

```text
results/
  pyautogui/
    screenshot/
      gpt-4o/
        args.json
        chrome/
          bb5e4c0d-.../
            traj.jsonl
            runtime.log
            result.txt
            recording.mp4
            step_1_20260428@130000123456.png
```

### 1. 为什么目录要分三层

这里的三层非常重要：

- `action_space`
- `observation_type`
- `model`

因为在这个仓库里，同一批任务可能会被：

- 不同动作协议跑
- 不同观测输入跑
- 不同模型跑

所以 monitor 不是只看一个总结果目录，而是默认以这组三元组作为“当前实验配置”。

## 二、`args.json` 是模型级配置快照

对应代码：

- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

runner 启动时会先写：

- `results/{action_space}/{observation_type}/{model}/args.json`

这里保存的是本次运行时的命令行参数快照。

例如通常会有：

- `model`
- `action_space`
- `observation_type`
- `max_steps`
- `sleep_after_execution`
- `result_dir`

这很有用，因为你过几天回头看结果时，可以先确认：

- 这批结果到底是用什么参数跑出来的

而 monitor 也会读取这个文件，把其中的：

- `max_steps`

以及其他附加参数展示到配置面板里。

## 三、单个任务目录里最重要的文件有哪些

这一层建议你先记住 6 个文件。

### 1. `traj.jsonl`

这是最核心的过程记录。

对应代码：

- [lib_run_single.py](../../lib_run_single.py)

每执行一步，runner 就往里面追加一行 JSON，大致包含：

- `step_num`
- `action_timestamp`
- `action`
- `response`
- `reward`
- `done`
- `info`
- `screenshot_file`

你可以把它理解成：

- 逐步轨迹日志

如果你只看一个文件来复盘任务，优先看它。

### 2. `runtime.log`

这个文件来自单任务 logger。

它主要记录：

- 每步运行时日志
- agent 返回内容
- 结束条件
- 异常信息

monitor 在详情页里展示的：

- agent intent
- message exit / thought exit

就是从这个文件里抠出来的。

### 3. `result.txt`

这是最后的评测分数。

通常就是：

- `0`
- `1`
- 或某个 0 到 1 之间的分数

它是判断“这个任务最终得分多少”的最直接文件。

runner 在统计当前 success rate 时，也会去扫这些 `result.txt`。

### 4. `recording.mp4`

这是整条任务轨迹的视频录屏。

它不是每一步的结构化数据，而是：

- 整段实际桌面执行录像

如果你怀疑：

- 坐标点歪了
- 页面在抖
- 任务中途弹窗

视频通常比日志更直观。

### 5. `step_*.png`

这是每一步执行后的截图。

文件名里带有：

- step 编号
- 动作时间戳

monitor 详情页就是逐步把这些 PNG 嵌进去展示。

### 6. `summary/results.json`

这个文件不在单任务目录里，而在：

- `results/summary/results.json`

对应代码：

- [lib_results_logger.py](../../lib_results_logger.py)

它是一个实时追加的汇总文件，会记录每个任务的：

- application
- task_id
- status
- score
- timestamp

这个文件的特点是：

- 带文件锁
- 多进程下也能安全追加

所以如果你以后想做自己的统计脚本，这个文件比遍历所有 task 目录更方便。

## 四、`traj.jsonl` 是怎么写出来的

还是看：

- [lib_run_single.py](../../lib_run_single.py)

`run_single_example(...)` 的核心流程是：

1. `env.reset(task_config=example)`
2. `agent.reset(...)`
3. 等待环境稳定
4. `obs = env._get_obs()`
5. `agent.predict(instruction, obs)`
6. `env.step(action, ...)`
7. 把当前 step 的截图和轨迹行写入结果目录
8. 循环直到 `done` 或 `max_steps`
9. `env.evaluate()`
10. 写 `result.txt`

也就是说：

- `traj.jsonl` 记录的是执行期
- `result.txt` 记录的是评测期最终输出

这两者不是一回事。

### 1. 为什么截图文件名里要带时间戳

因为一个 step 里可能会对应多个动作，或者不同 agent 实现的写法会有差异。

带时间戳至少解决了两件事：

- 文件名不冲突
- 你可以大致对齐动作执行时间

### 2. 异常时也会补一条轨迹

在：

- [run.py](../../run.py)

里，如果单任务执行异常，代码会尝试：

- 停止录屏
- 往 `traj.jsonl` 里追加一条带 `Error` 的记录

所以当你看到 monitor 上某个任务是 `Error`，通常可以先去看：

- `traj.jsonl` 最后一行

## 五、runner 是怎么判断“一个任务已经跑完了”的

看：

- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

这里有个很实用的函数：

- `get_unfinished(...)`

它的逻辑很直接：

- 如果某个 task 目录里已经有 `result.txt`，就当它跑完了
- 如果没有 `result.txt`，就把那个目录下已有文件清空，等下次重跑

这意味着：

- `result.txt` 在这个项目里，不只是“分数文件”
- 它同时也是“是否完成”的标记文件

这点很关键。

因为它解释了为什么你中途打断一次批跑后，重启 runner 可能会：

- 清理掉那些没完成的半截轨迹目录

## 六、monitor 的核心思路是什么

对应目录：

- [monitor](../../monitor)

这部分本质上就是一个 Flask 小服务。

主入口：

- [monitor/main.py](../../monitor/main.py)

你可以把它理解成三层：

1. 读任务定义
2. 读结果目录
3. 把状态渲染成网页和 API

## 七、monitor 读取哪批结果，是怎么决定的

这一点非常重要。

monitor 不是固定盯着一个：

- `results/某个目录`

而是有一套“当前配置”概念。

### 1. 三元组配置

monitor 当前查看的是哪一组结果，取决于：

- `action_space`
- `observation_type`
- `model_name`

它们共同决定：

- `RESULTS_BASE_PATH/{action_space}/{observation_type}/{model_name}`

### 2. 默认配置从哪来

`monitor/main.py` 里的：

- `get_default_config()`

会先扫描 `RESULTS_BASE_PATH`，尝试找到第一组现有配置。

如果找不到，才回退到 `.env` 里的默认值。

所以真实行为是：

- 有结果目录时，优先按磁盘上现有配置自动选
- 没有结果目录时，才靠 `.env`

### 3. `.env` 主要配置什么

对应文件：

- [monitor/.env](../../monitor/.env)

最关键的环境变量有：

- `TASK_CONFIG_PATH`
- `EXAMPLES_BASE_PATH`
- `RESULTS_BASE_PATH`
- `ACTION_SPACE`
- `OBSERVATION_TYPE`
- `MODEL_NAME`
- `MAX_STEPS`

其中最容易配错的是前三个路径。

一旦这三个路径不对，页面就会出现：

- 没任务
- 没结果
- 详情页 404

## 八、monitor 首页到底在干什么

你可以看：

- [monitor/templates/index.html](../../monitor/templates/index.html)
- [monitor/static/index.js](../../monitor/static/index.js)

首页并不是一次性把所有明细全读完。

默认走的是：

- `/api/tasks/brief`

也就是“简版状态接口”。

这样做的原因很现实：

- 任务多的时候，不能每次首页刷新都把所有 `traj.jsonl` 全量读一遍

### 1. 首页显示哪些信息

首页主要展示：

- 总任务数
- Active 数
- Completed 数
- Error 数
- Score banner
- 每个 domain 的统计

这些信息基本都来自：

- 任务列表
- 每个 task 的 brief status

### 2. Score banner 是怎么算的

前端会把所有已完成任务的 `result` 读出来，做两层展示：

- `totalScore`
- `averageScore * 100%`

也就是说页面上的 accuracy 百分比，本质上就是：

- 完成任务的平均分

如果任务分数是 0/1，那它就近似等于成功率。

## 九、monitor 是怎么推断任务状态的

这是这部分代码里最值得读的逻辑之一。

在：

- [monitor/main.py](../../monitor/main.py)

里，状态大致是这样推断的。

### 1. `Not Started`

如果：

- task 目录还不存在

### 2. `Preparing`

如果：

- task 目录存在
- 但 `traj.jsonl` 还不存在

### 3. `Initializing`

如果：

- `traj.jsonl` 已存在
- 但里面还没有 step

### 4. `Running`

如果：

- 已经有 step
- 但还没触发结束条件

### 5. `Done`

如果：

- `traj.jsonl` 最后一条里 `done == True`

### 6. `Done (Message Exit)` / `Done (Thought Exit)`

如果：

- `runtime.log` 末尾出现了对应 exit 标记

### 7. `Done (Max Steps)`

如果：

- step 数达到 `max_steps`

### 8. `Error`

如果：

- 最后一条 step 或轨迹记录里带 `Error`

这个推断逻辑很“工程化”，不是完美语义建模，而是：

- 优先用已有文件结构快速恢复运行状态

## 十、为什么首页和详情页读取策略不一样

在 `monitor/main.py` 里你会看到两套状态接口：

- `get_task_status_with_config(...)`
- `get_task_status_brief_with_config(...)`

原因很简单：

- 详情页可以慢一点，因为你只看一个任务
- 首页必须快一点，因为它要扫全部任务

所以简版接口会做一些优化：

- 用 `wc -l` 统计 `traj.jsonl` 行数
- 用 `tail -n 1` 读最后一行
- 用 `tail -n 2` 看日志结尾

而不是把整个轨迹全读进来。

这就是为什么首页刷新更快，而详情页信息更全。

## 十一、任务详情页展示了什么

可以看：

- [monitor/templates/task_detail.html](../../monitor/templates/task_detail.html)

它会展示：

- 基本任务信息
- 当前状态
- 当前 step 数
- last update
- exit condition
- result
- 录屏视频
- 每一步的动作和截图

### 1. 截图是怎么取的

详情页里的每张图，都是通过接口：

- `/task/{task_type}/{task_id}/screenshot/{filename}`

去结果目录里找对应 PNG。

### 2. 视频是怎么取的

录屏则走：

- `/task/{task_type}/{task_id}/recording`

本质上还是把 `recording.mp4` 当静态文件发回去。

### 3. agent intent 从哪来

详情页里显示的：

- `Agent Intent`

不是从 `traj.jsonl` 直接读出来的，而是从：

- `runtime.log`

里抽取 `Responses: [...]` 那些日志行得到的。

这也解释了一个现象：

- 如果某个 agent 的 logger 结构不完全一致，详情页里的 intent 展示可能就不完整

也就是说，monitor 更像一个实用 viewer，不是严格统一协议的可视化层。

## 十二、结果缓存是怎么回事

monitor 里还有一个容易忽略的实现：

- `TASK_STATUS_CACHE`

它会缓存某个配置下的任务状态，尤其是：

- 已完成任务
- Error 任务

这样做是为了避免页面反复刷新时反复读很多文件。

但它也带来一个副作用：

- 你手工改了结果文件后，页面未必立刻反映

所以前端专门提供了：

- `Clear Cache`

按钮，对应后端接口：

- `/api/clear-cache`

## 十三、你自己查问题时，推荐的排查顺序

如果你以后跑一批任务，建议按这个顺序看。

### 1. 先看 `result.txt`

确认：

- 最终有没有得分
- 是 0、1 还是中间值

### 2. 再看 `traj.jsonl`

确认：

- 一共走了几步
- 最后一条动作是什么
- `done` / `info` 长什么样

### 3. 再看 `runtime.log`

确认：

- agent 当时怎么想的
- 有没有 message exit / thought exit
- 有没有异常日志

### 4. 最后看 `recording.mp4`

确认：

- 真正界面上发生了什么

如果是坐标、弹窗、加载时机问题，视频通常最有用。

## 十四、你自己跑 monitor 时，需要理解什么

如果你只是本地理解代码，不一定非要上 Docker。

按代码逻辑，本地直接跑 monitor 主要就是：

1. 配好 `monitor/.env`
2. 让 `RESULTS_BASE_PATH` 指向你的结果目录
3. 启动 `monitor/main.py`

你真正需要关注的是：

- 路径对不对
- 结果目录里有没有这组三元组
- `args.json` 是否存在

而不是先纠结页面样式。

## 十五、读完这一篇后，你对项目应该能回答什么

到这里你应该已经能回答下面这些问题：

1. 一个任务跑完后，结果目录是怎么组织的？
2. `traj.jsonl` 和 `result.txt` 分别负责什么？
3. monitor 为什么要区分 brief status 和 detail status？
4. monitor 页面上的状态，是怎么从文件里推断出来的？
5. 为什么切换 `action_space / observation_type / model` 后，页面会跳到不同的一组结果？

如果这五个问题你都能答出来，说明你已经不只是会“跑项目”，而是已经能自己排查一批结果了。

## 十六、建议的两个小实验

### 1. 亲自打开一个 task 目录

找一条你已经跑过的任务，按这个顺序直接看文件：

- `traj.jsonl`
- `runtime.log`
- `result.txt`

然后对照 monitor 页面，看每一块信息是从哪来的。

### 2. 故意切到另一组配置

如果你本地有多套结果，例如不同 model 或 observation type，可以观察：

- monitor 首页配置面板如何切换
- URL 里的 `action_space` / `observation_type` / `model_name` 如何变化
- 页面为什么会立即换到另一套结果视图

## 十七、接下来再看哪部分最顺

如果你想继续沿着“主链路”学习，下一步比较自然的是选一个具体应用域做一次完整追踪。

例如：

- `chrome`
- `libreoffice_calc`
- `gimp`

把下面几样放在一起看：

- 一个任务 JSON
- 对应的运行轨迹目录
- 录屏
- evaluator

这样你会真正把“任务定义 -> 环境执行 -> agent 动作 -> 结果判分 -> 页面展示”这一条链闭合起来。

如果你愿意，我下一篇可以继续补：

- `12-chrome-task-end-to-end_zh.md`

选一个具体的 `chrome` 任务，带你做一次完整代码走读。
