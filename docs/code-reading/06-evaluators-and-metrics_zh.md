# 06 Evaluator 与 Metrics 解读

这一篇接在 [05 运行器与任务主循环解读](./05-runner-and-task-loop_zh.md) 后面看最自然。

因为上一层你已经知道：

- 一个任务最终会走到 `env.evaluate()`
- runner 层真正写分数的地方，依赖的是 `evaluate()` 返回值

这一篇要解决的问题就是：

- `evaluator` 字段在任务 JSON 里到底是什么意思
- getter 和 metric 是怎么配合起来的
- 为什么同样叫“评测”，有的任务是查命令输出，有的任务是比文件，有的任务是比图片或表格

## 先记住最核心的抽象

这个项目的 evaluator 可以先粗暴理解成：

`result_getter -> expected_getter -> metric`

也就是：

1. 先取“实际结果”
2. 再取“期望结果”
3. 最后用 metric 比较

这个抽象落地在：

- [desktop_env/desktop_env.py:338](../../desktop_env/desktop_env.py#L338)
- [desktop_env/desktop_env.py:429](../../desktop_env/desktop_env.py#L429)

你如果只记一件事，就记这个。

## 一、`evaluate()` 为什么能这么灵活

`DesktopEnv.evaluate()` 本身没有写死任何应用逻辑。

它只是根据任务 JSON 里的 `evaluator` 配置，动态拼出：

- `self.metric`
- `self.result_getter`
- `self.expected_getter`
- `self.metric_options`

这一层逻辑在：

- [desktop_env/desktop_env.py:338](../../desktop_env/desktop_env.py#L338)

所以它的灵活性来自两个目录：

- [desktop_env/evaluators/getters](../../desktop_env/evaluators/getters)
- [desktop_env/evaluators/metrics](../../desktop_env/evaluators/metrics)

## 二、先看 `evaluator` 结构本身

任务 JSON 里的 `evaluator` 通常会包含这些字段：

- `func`
- `result`
- `expected`
- `options`
- `conj`
- `postconfig`

不是每个任务都会全部使用，但理解这几个字段很关键。

### 1. `func`

这是 metric 名字。

例如：

- `match_in_list`
- `check_include_exclude`
- `compare_table`
- `check_image_size`

`DesktopEnv` 会通过：

```python
getattr(metrics, func)
```

把这个名字解析成真正的 Python 函数。

对应代码：

- [desktop_env/desktop_env.py:349](../../desktop_env/desktop_env.py#L349)

### 2. `result`

这是“实际结果”怎么取。

例如：

- 从 VM 里跑一条命令
- 从 VM 里下载一个文件
- 从 Chrome 配置里读默认搜索引擎

`DesktopEnv` 会通过：

```python
getattr(getters, "get_" + result_type)
```

去找对应 getter。

对应代码：

- [desktop_env/desktop_env.py:353](../../desktop_env/desktop_env.py#L353)

### 3. `expected`

这是“期望结果”怎么取。

它不一定是固定字面值，也可能是：

- 一个规则对象
- 一个云端 gold 文件
- 一个相对时间规则

对应代码：

- [desktop_env/desktop_env.py:363](../../desktop_env/desktop_env.py#L363)

### 4. `options`

这是传给 metric 的附加参数。

例如：

- `ignore_case`
- `rules`
- 表格比对里的复杂规则

对应代码：

- [desktop_env/desktop_env.py:372](../../desktop_env/desktop_env.py#L372)

### 5. `conj`

只有多 metric 时才重要。

它控制多个 metric 是：

- `and`
- 还是 `or`

对应代码：

- [desktop_env/desktop_env.py:352](../../desktop_env/desktop_env.py#L352)

### 6. `postconfig`

这是很多人第一次读代码最容易忽略的点。

在真正评测前，环境还会先执行一轮 `postconfig`：

- [desktop_env/desktop_env.py:434](../../desktop_env/desktop_env.py#L434)

你可以把它理解成：

- “评测前最后的收尾动作”

例如：

- 保存文件
- 关闭并重开应用
- 等待界面稳定

很多任务不是直接拿当前状态就能评测，所以需要这一步。

## 三、getter 是干什么的

getters 负责“取结果”，不负责判分。

它们的返回值可以非常不同：

- 字符串
- 文件路径
- JSON / dict
- 图片文件路径
- 列表

你可以把 getter 理解成：

- “把 VM 里的状态提取出来，变成 metric 能消费的输入”

## 四、metrics 是干什么的

metrics 负责“比较”和“打分”。

它们通常输入的是：

- result
- expected
- 可选 options

输出通常是：

- `1.0`
- `0.0`
- 或者一个介于 0 和 1 的分数

你可以把 metric 理解成：

- “把提取出来的状态，和目标状态做比对”

## 五、为什么 `getattr(metrics, func)` 能工作

因为 getters 和 metrics 在各自的 `__init__.py` 里做了大量导出。

例如：

- [desktop_env/evaluators/getters/__init__.py](../../desktop_env/evaluators/getters/__init__.py)
- [desktop_env/evaluators/metrics/__init__.py](../../desktop_env/evaluators/metrics/__init__.py)

这意味着：

- 任务 JSON 里写的是字符串名字
- 环境运行时再通过模块导出表去解析成函数对象

这是一种很经典的“字符串配置 -> 函数映射”设计。

## 六、先看一个最简单的单 metric 例子

推荐从这个任务开始：

- [evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)

它的 evaluator 核心是：

- `func = "match_in_list"`
- `result.type = "default_search_engine"`
- `expected.type = "rule"`

### 1. `result.type = "default_search_engine"` 是怎么解析的

环境会去找：

- `get_default_search_engine`

这个函数在：

- [desktop_env/evaluators/getters/chrome.py](../../desktop_env/evaluators/getters/chrome.py)

它做的事情很典型：

1. 根据 OS 找 Chrome 配置文件路径
2. 从 VM 里把配置文件抓出来
3. 解析 JSON
4. 返回默认搜索引擎名字

这说明 getter 不一定非要依赖 GUI，它完全可以直接读软件配置文件。

### 2. `expected.type = "rule"` 是怎么解析的

这会走：

- [desktop_env/evaluators/getters/misc.py:87](../../desktop_env/evaluators/getters/misc.py#L87)

也就是：

```python
def get_rule(env, config):
    return config["rules"]
```

这类 expected 的意思很简单：

- 规则本身就是 expected
- 不需要额外计算

### 3. `match_in_list` 又做了什么

它在：

- [desktop_env/evaluators/metrics/general.py](../../desktop_env/evaluators/metrics/general.py)

逻辑非常直接：

- 如果 result 在 expected 列表里，就返回 1
- 否则返回 0

所以整个评测链可以还原成：

1. getter 取出默认搜索引擎，比如 `"Bing"`
2. rule getter 返回 `["Microsoft Bing", "Bing"]`
3. `match_in_list("Bing", [...]) -> 1.0`

这就是最基础的 evaluator 模式。

## 七、再看一个“命令输出判定”的例子

你在 [quickstart.py](../../quickstart.py) 里已经见过这种风格：

- `result.type = "vm_command_line"`
- `func = "check_include_exclude"`

对应 getter：

- [desktop_env/evaluators/getters/general.py](../../desktop_env/evaluators/getters/general.py)

对应 metric：

- [desktop_env/evaluators/metrics/general.py](../../desktop_env/evaluators/metrics/general.py)

### 1. `get_vm_command_line(...)`

它会：

1. 调用 guest 内部 `/execute`
2. 跑一条命令
3. 返回命令输出文本

也就是说，这是一种“把 guest 当成黑盒系统来查状态”的评测方式。

### 2. `check_include_exclude(...)`

它会看：

- 输出里是否包含某些关键字
- 输出里是否不包含某些关键字

这是最轻量也最常见的一类 metric。

它特别适合：

- 文件是否存在
- 命令行工具是否安装成功
- 某条配置是否生效

## 八、再看一个文件比对例子

文件类 getter 最常见的是：

- [desktop_env/evaluators/getters/file.py](../../desktop_env/evaluators/getters/file.py)

这里最值得先看两个函数：

- `get_vm_file(...)`
- `get_cloud_file(...)`

### 1. `get_vm_file(...)`

职责是：

- 从 VM 下载结果文件到本地缓存目录
- 返回本地缓存后的文件路径

所以很多 metric 并不是直接操作 VM 文件，而是操作：

- runner 机器上的临时缓存文件

### 2. `get_cloud_file(...)`

职责是：

- 把 cloud 上的 gold 文件下载到本地 cache
- 返回本地 gold 文件路径

这意味着：

- result 和 expected 很多时候最终都会落成本地文件路径
- metric 再在本地比对它们

这种设计很实用，因为：

- metric 不用知道 VM 网络细节
- 只需要专心做文件比较

## 九、看一个表格类 metric 例子

推荐看这个任务：

- [evaluation_examples/examples/libreoffice_calc/21df9241-f8d7-4509-b7f1-37e501a823f7.json](../../evaluation_examples/examples/libreoffice_calc/21df9241-f8d7-4509-b7f1-37e501a823f7.json)

它的 evaluator 核心是：

- `func = "compare_table"`
- `result.type = "vm_file"`
- `expected.type = "cloud_file"`
- `options.rules = [...]`

### 1. 为什么 `postconfig` 很重

这个任务里评测前会先：

- 保存表格
- 调 LibreOffice 导出 CSV

这说明：

- 最终评测并不是直接看当前 UI
- 而是把编辑结果转成更适合比较的文件格式

### 2. 为什么 `result` 和 `expected` 都是多文件

这个任务里：

- 一个是 `.xlsx`
- 一个是 `.csv`

目的是让 `compare_table` 能按不同规则选择不同载体：

- 有些规则比工作簿内部值
- 有些规则比最终显示内容

### 3. `compare_table(...)` 为什么复杂

它在：

- [desktop_env/evaluators/metrics/table.py](../../desktop_env/evaluators/metrics/table.py)

这是整个 evaluator 层里比较重的一类 metric。

复杂的原因不是代码写法花，而是表格天然复杂：

- sheet 选择
- 公式值 vs 显示值
- 格式
- 行列
- 图表
- 过滤器

所以 `compare_table` 实际上是一个规则驱动的小框架。

## 十、看一个多 metric 例子

推荐看这个 GIMP 任务：

- [evaluation_examples/examples/gimp/d16c99dc-2a1e-46f2-b350-d97c86c85c15.json](../../evaluation_examples/examples/gimp/d16c99dc-2a1e-46f2-b350-d97c86c85c15.json)

它的 evaluator 是：

- `func = ["check_image_size", "check_structure_sim_resized"]`
- `conj = "and"`

### 1. 这意味着什么

这个任务不是只看一个条件。

它要求至少同时满足：

1. 图片尺寸正确
2. 图片结构相似度也合理

这很符合图像任务的特点：

- 只看尺寸不够
- 只看结构相似也不够

### 2. 在 `evaluate()` 里怎么处理

对应：

- [desktop_env/desktop_env.py:452](../../desktop_env/desktop_env.py#L452)

环境会：

1. 逐个调用 result_getter
2. 逐个调用 expected_getter
3. 逐个跑 metric
4. 根据 `conj` 决定最终结果

当 `conj = "and"` 时：

- 只要某个 metric 为 0，就可能直接返回 0

这是一个非常实用的短路逻辑。

## 十一、`postconfig` 为什么经常被低估

很多人第一次读 evaluator，会只盯：

- `func`
- `result`
- `expected`

但实际上 `postconfig` 很常决定这个任务能不能被正确评测。

原因很简单：

- UI 状态不稳定
- 有些结果必须保存后才能读取
- 有些应用必须切回特定窗口
- 有些文件必须导出成另一种格式

所以：

- `postconfig` 是评测前的环境收尾动作
- 它不属于 Agent 工作
- 也不属于 metric 逻辑
- 但它是 evaluator 正常工作的必要前提

## 十二、你现在应该怎么读 getters / metrics

不要试图一次把所有 getter 和 metric 全看完。

更有效的方式是按“任务样例驱动”去看。

推荐顺序：

1. 看任务 JSON 的 `evaluator`
2. 找 `result.type`
3. 找 `expected.type`
4. 找 `func`
5. 对照 `postconfig`

也就是说，你应该让任务来带你读 evaluator，而不是反过来。

## 十三、现在最值得你做的 4 个小实验

### 实验 1：手动追一个单 metric 链

用 Chrome 默认搜索引擎任务。

目标：

- 从 JSON 一直追到 getter、metric、最终分数

### 实验 2：手动追一个命令行检查链

用 `vm_command_line + check_include_exclude` 风格的任务。

目标：

- 理解“系统状态检查型评测”是怎么工作的

### 实验 3：手动追一个文件比较链

看 `vm_file + cloud_file + compare_table`。

目标：

- 理解为什么评测经常先把 result / expected 都拉成本地文件

### 实验 4：手动追一个多 metric 链

用 GIMP 的 resize 任务。

目标：

- 理解 `conj = and/or` 的作用

## 十四、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，说明 evaluator 这层第一轮已经过关：

1. `evaluator.func` 和 `result.type` 的区别是什么？
2. 为什么 `expected.type = "rule"` 不需要真的访问外部状态？
3. `get_vm_file()` 和 `get_cloud_file()` 为什么都返回本地路径？
4. 为什么很多任务必须先跑 `postconfig` 才能评测？
5. `conj = "and"` 的短路逻辑在什么地方实现？
6. 为什么同一个 benchmark 体系里会同时存在命令行检查、配置文件读取、图片比较和表格比较？

## 十五、下一步该读什么

如果继续沿“非 agent 深入”的路线，最自然的下一步有两个方向：

1. `providers`
   去看不同运行底座是怎么适配的
2. `controllers/server`
   去看环境内部 HTTP 接口是怎么提供截图、执行命令和取 accessibility tree 的

如果你问我哪个更适合现在继续：

我建议先看 `controllers + server`。

因为你现在已经知道：

- 环境怎么返回 observation
- runner 怎么调主循环
- evaluator 怎么判结果

接下来最自然的问题就是：

- 这些 `/screenshot`、`/execute`、`/accessibility` 接口在 guest 里到底是怎么实现的
