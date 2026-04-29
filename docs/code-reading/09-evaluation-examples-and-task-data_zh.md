# 09 evaluation_examples 与任务数据解读

这一篇接在 [08 Providers 与生命周期解读](./08-providers-lifecycle_zh.md) 后面看很自然。

因为到这一步你已经知道：

- 环境怎么跑
- Agent 怎么推理
- runner 怎么调度
- evaluator 怎么打分
- provider 怎么提供 guest 资源

现在回过头来看：

- 这些代码到底是被什么数据驱动的？

答案就是：

- `evaluation_examples/`

这一层本质上是整个系统的数据驱动入口。

## 先记住最重要的一句话

这个项目不是“先写死任务逻辑，再让 agent 跑”。

而是：

- 任务定义主要放在 JSON 里
- 代码负责解释这些 JSON

也就是说，`evaluation_examples/` 不是附属资料，而是核心输入。

## 一、先看目录结构

第一次阅读建议先把目录结构建立起来。

核心目录大致是：

- `evaluation_examples/examples/`
- `evaluation_examples/examples_windows/`
- `evaluation_examples/test_all.json`
- `evaluation_examples/settings/`

你可以把它们分别理解成：

### 1. `examples/`

Linux / Ubuntu 主任务集。

按应用域分目录，例如：

- `chrome`
- `gimp`
- `libreoffice_calc`
- `libreoffice_impress`
- `libreoffice_writer`
- `multi_apps`
- `os`
- `thunderbird`
- `vlc`
- `vs_code`

### 2. `examples_windows/`

Windows 任务集。

例如：

- `excel`
- `multi_app`
- `ppt`
- `word`

### 3. `test_all.json`

任务索引文件。

它不包含任务详情，只负责告诉 runner：

- 每个 domain 下有哪些 example id

### 4. `settings/`

某些需要账号、OAuth、代理或应用配置的任务，会依赖这里的设置文件。

## 二、`test_all.json` 到底干什么

对应文件：

- [evaluation_examples/test_all.json](../../evaluation_examples/test_all.json)

它的结构大致是：

```json
{
  "chrome": ["id1", "id2", "..."],
  "gimp": ["id3", "id4", "..."],
  ...
}
```

这个文件的职责非常单纯：

- 给 runner 一份“任务清单”

它并不存放：

- instruction
- config
- evaluator

这些内容都在单个任务 JSON 里。

### 它是怎么接进 runner 的

你在：

- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

里会看到相同模式：

1. 先读取 `test_all.json`
2. 遍历 domain 和 example_id
3. 再去 `examples/{domain}/{example_id}.json` 打开具体任务

所以：

- `test_all.json` 是任务入口索引
- 单个任务 JSON 才是任务正文

## 三、单个任务 JSON 里通常有什么

推荐先对照这个简单例子看：

- [evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)

一个任务 JSON 最常见的字段有：

- `id`
- `snapshot`
- `instruction`
- `source`
- `config`
- `trajectory`
- `related_apps`
- `evaluator`
- `proxy`
- `fixed_ip`
- `possibility_of_env_change`

不是每个字段都在每个任务里同样重要，但这些字段的角色最好先弄清。

## 四、字段逐个怎么看

### 1. `id`

任务唯一标识。

这个值会被用在很多地方：

- 结果目录
- cache 目录
- 日志命名

在环境里：

- [desktop_env/desktop_env.py:330](../../desktop_env/desktop_env.py#L330)

它会被拿来构造任务级 cache 目录。

### 2. `snapshot`

表示这个任务希望运行在什么初始环境快照上。

例如：

- `chrome`
- `gimp`
- `libreoffice_calc`
- `thunderbird`

它的语义更偏“任务所属环境场景”，不是直接被 `DesktopEnv` 原样读取的核心字段。

更准确地说，它是任务设计语义的一部分，和 provider 层的资源准备相呼应。

### 3. `instruction`

这是给 Agent 的自然语言任务目标。

它最终会进入：

- `PromptAgent.predict(instruction, obs)`

所以这是 agent 视角最核心的任务字段。

### 4. `source`

这是任务出处。

例如：

- 教程
- StackOverflow
- 产品文档
- 用户论坛

它主要是任务来源说明，不直接参与执行。

### 5. `config`

这是任务前置准备动作。

它会在：

- `env.reset(task_config=example)`

期间被交给：

- `SetupController.setup(config)`

去执行。

你已经在前面的文档里见过：

- `download`
- `launch`
- `open`
- `execute`

这些都是 `config` 里的常见 setup 类型。

### 6. `trajectory`

这是任务对应轨迹目录的引用。

从项目演进上看，它更偏：

- 人工示范 / 标注 / 参考轨迹入口

它不是主运行循环的关键字段，但对数据集构建和分析很重要。

### 7. `related_apps`

这是任务关联应用列表。

例如：

- `["chrome"]`
- `["thunderbird", "libreoffice_calc"]`

它在理解任务跨度时很有用，尤其是：

- 单应用任务
- 多应用任务

### 8. `evaluator`

这是评测定义。

这一层你在上一篇已经单独读过。

在任务数据视角里，你可以把它理解成：

- “这个任务做完以后，怎样判定它成功”

### 9. `proxy`

表示这个任务是否依赖代理。

不是所有任务都需要，但涉及某些站点、网络环境或区域限制时会用到。

在环境里：

- [desktop_env/desktop_env.py:257](../../desktop_env/desktop_env.py#L257)

会决定是否启用 proxy 相关 setup 逻辑。

### 10. `fixed_ip`

表示这个任务是否依赖固定 IP 条件。

这是偏环境语义的字段，不是大多数任务分析时的第一关注点。

### 11. `possibility_of_env_change`

这是一个很有任务设计意味的字段。

例如：

- `low`

它用来描述：

- 任务运行过程中外部环境变化风险大不大

这个字段不一定被核心执行逻辑强依赖，但对 benchmark 设计和任务稳定性分析很有价值。

## 五、先看一个最简单的单应用任务

还是用这个例子：

- [chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json](../../evaluation_examples/examples/chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4.json)

它的特点很清晰：

- `related_apps` 只有 `chrome`
- `config` 只负责启动 Chrome 和远程调试桥
- `evaluator` 用 `default_search_engine + match_in_list`

这是理解单应用任务最好的起点。

## 六、再看一个多应用任务

推荐这个：

- [multi_apps/c867c42d-a52d-4a24-8ae3-f75d256b5618.json](../../evaluation_examples/examples/multi_apps/c867c42d-a52d-4a24-8ae3-f75d256b5618.json)

这个任务要求：

- 从 Thunderbird 导出联系人
- 再转成 LibreOffice Calc 的 `.xlsx`

它的特点很典型：

### 1. `related_apps` 明显是多应用

```json
["thunderbird", "libreoffice_calc"]
```

### 2. `config` 也更复杂

它不仅启动应用，还会：

- 下载 Thunderbird profile
- 解压 profile
- 再启动 Thunderbird

这说明任务数据不仅描述目标，也描述环境状态准备。

### 3. evaluator 也会是多 metric

它会同时比较：

- `contacts.csv`
- `contacts.xlsx`

所以这个例子特别适合你理解：

- 多应用任务如何在数据层表达

## 七、再看一个 Windows 任务

推荐这个：

- [examples_windows/excel/3aaa4e37-dc91-482e-99af-132a612d40f3.json](../../evaluation_examples/examples_windows/excel/3aaa4e37-dc91-482e-99af-132a612d40f3.json)

它的特点是：

### 1. 路径是 Windows 风格

例如：

```text
c:\Users\User\Export_Calc_to_CSV.xlsx
```

这说明任务 JSON 本身就是平台感知的。

### 2. `snapshot` 也换成了 Windows 应用语义

例如：

- `excel`

### 3. evaluator 模式本身并没有变

虽然平台换了，但仍然是：

- `result`
- `expected`
- `func`

这说明 evaluator 抽象本身是跨平台的，真正变化的是：

- guest 路径
- 应用类型
- provider / controller / accessibility 实现

## 八、`settings/` 目录是做什么的

`evaluation_examples/settings/` 不是任务本体，但很多任务离不开它。

这里目前能看到的子目录包括：

- `google`
- `googledrive`
- `proxy`
- `thunderbird`

### 1. Google 账号设置

例如：

- [settings/google/settings.json.template](../../evaluation_examples/settings/google/settings.json.template)

它是一个模板，大致告诉你：

- 某些 Google 相关任务需要账号信息

### 2. Google Drive OAuth 设置

例如：

- [settings/googledrive/settings.yml](../../evaluation_examples/settings/googledrive/settings.yml)

这说明某些任务不只是网页登录，还需要 Drive API / OAuth 配置。

### 3. Proxy 设置

例如：

- `settings/proxy/dataimpulse.json`

这和任务 JSON 里的 `proxy: true/false` 字段会配合使用。

所以：

- 任务是否需要代理，定义在任务 JSON
- 代理怎么配置，放在 `settings/`

## 九、为什么说任务数据是“驱动系统”的

把前面几层重新串起来，你会发现：

### 1. runner 被 `test_all.json` 驱动

它先根据 task index 决定跑哪些任务。

### 2. `DesktopEnv.reset()` 被单任务 JSON 驱动

它会读取：

- `instruction`
- `config`
- `evaluator`

### 3. `SetupController` 被 `config` 驱动

不同任务的前置准备完全来自 JSON 数据。

### 4. `evaluate()` 被 `evaluator` 驱动

不同任务的成功判定逻辑也来自 JSON 配置。

所以这个项目最重要的特征之一就是：

- 代码提供统一框架
- 任务数据定义具体 benchmark 行为

## 十、`evaluation_examples/README.md` 该怎么看

对应文件：

- [evaluation_examples/README.md](../../evaluation_examples/README.md)

这份 README 的价值主要在于：

- 提示这是 benchmark 数据目录
- 说明任务 JSON 的基本格式

但它也有明显的“历史版本”气息。

你在实际理解仓库时，应该：

- 把它当作总体说明
- 但以真实 JSON 样例和当前代码实现为准

也就是说：

- README 给概念
- 真实样例给事实

## 十一、第一次读任务数据时最容易忽略的几点

### 1. `config` 不是“解释说明”，而是真会执行的动作

这是最容易误解的地方。

任务 JSON 里的 `config` 不只是任务描述，它会真的交给 `SetupController` 执行。

### 2. `evaluator` 不是引用脚本路径，而是内联评测配置

你不需要去找每个任务一个单独 evaluator 文件。

任务 JSON 里自己就定义了：

- getter
- metric
- options

### 3. `related_apps` 不是摆设

这个字段很适合快速判断任务复杂度。

例如：

- 单应用 vs 多应用

### 4. Windows 和 Linux 的任务并不是同一份配置

它们在：

- 路径
- snapshot
- 打开的应用
- 某些配置动作

上都会不同。

## 十二、现在最值得你做的 4 个小实验

### 实验 1：拿一个任务，手工追 `config`

目标：

- 看它最终会触发哪些 `_xxx_setup()`

### 实验 2：拿一个任务，手工追 `evaluator`

目标：

- 看它会调用哪些 getter / metric

### 实验 3：对比一个 Linux 任务和一个 Windows 任务

目标：

- 理解“同一个 benchmark 抽象如何跨平台落地”

### 实验 4：看 `multi_apps` 任务

目标：

- 理解多应用任务的数据复杂度为什么更高

## 十三、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，任务数据这一层第一轮就算过关：

1. `test_all.json` 和单个任务 JSON 的关系是什么？
2. 单个任务 JSON 最重要的字段有哪些？
3. `config` 和 `evaluator` 分别驱动哪两层代码？
4. 为什么 `settings/` 要单独放在 `evaluation_examples/` 下？
5. `examples` 和 `examples_windows` 的差别主要体现在哪？
6. 为什么说这个项目是“任务数据驱动”的？

## 十四、下一步该读什么

到这一步，主干链路其实已经相当完整了：

- 任务数据
- provider
- guest server
- controller
- environment
- evaluator
- runner
- agent

如果继续往下走，后面更适合按你的兴趣分方向：

### 方向 1：继续系统层

可以继续看：

- `desktop_env/actions.py`

重点理解：

- `computer_13` 这种结构化动作空间

### 方向 2：继续 benchmark 设计层

可以继续挑：

- 某个 domain
- 某类任务
- 某种 evaluator 模式

做专题式阅读。

如果你问我现在最推荐哪个：

我建议下一篇去看：

- `desktop_env/actions.py`

因为这会把“Agent 输出动作”和“环境执行动作”之间的最后一层抽象补完整。 
