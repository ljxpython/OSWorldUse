# 05 运行器与任务主循环解读

这一篇开始把前面几篇重新拼回“真实运行入口”。

如果说：

- [02 DesktopEnv 主循环解读](./02-desktopenv-main-loop_zh.md) 讲的是环境怎么工作
- [03 PromptAgent 推理主循环解读](./03-prompt-agent-predict-loop_zh.md) 讲的是 Agent 怎么工作

那这一篇讲的就是：

- 环境和 Agent 是怎么被真正串起来的
- 一次 benchmark 任务到底怎么被调度、执行、落盘和统计

这一层最值得读的文件有三个：

- [lib_run_single.py](../../lib_run_single.py)
- [run.py](../../run.py)
- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

另外还有一个结果记录辅助文件：

- [lib_results_logger.py](../../lib_results_logger.py)

## 先记住最重要的分工

这四个文件的角色并不一样：

### 1. `lib_run_single.py`

这是核心任务循环。

它回答的是：

- 一个任务开始后，环境和 Agent 怎么一来一回地跑
- 每一步截图、动作和结果是怎么保存的

### 2. `run.py`

这是单进程、单环境的读取入口。

它更适合拿来理解主线，不太适合大规模实际运行。

代码里自己也写了：

- [run.py:18](../../run.py#L18)

它已经接近“阅读入口 / 旧入口”。

### 3. `run_multienv.py`

这是多进程、多环境版本。

它更接近现在真实跑 benchmark 的方式。

### 4. `lib_results_logger.py`

它不参与动作执行，而是负责把任务结果增量写入 `results.json`。

## 一、先看最核心的 `run_single_example(...)`

对应代码：

- [lib_run_single.py:14](../../lib_run_single.py#L14)

如果你只想吃透 runner 层，这个函数是最值得优先读的。

它基本就是“一个任务到底怎么跑”的标准答案。

你可以把它拆成 10 步：

1. 为当前任务创建 runtime logger
2. `env.reset(task_config=example)`
3. `agent.reset(..., vm_ip=env.vm_ip)`
4. 等环境稳定
5. 拉第一帧 observation
6. 开始录屏
7. 进入 `while not done and step_idx < max_steps`
8. `agent.predict(...)`
9. `env.step(action, ...)`
10. `env.evaluate()`

### 1. 为什么先 reset env，再 reset agent

看这里：

- [lib_run_single.py:17](../../lib_run_single.py#L17)
- [lib_run_single.py:21](../../lib_run_single.py#L21)

顺序是：

1. 先 `env.reset(task_config=example)`
2. 再 `agent.reset(..., vm_ip=env.vm_ip)`

这样做的原因很直接：

- `env.reset()` 之后，VM 可能被回滚或重启
- guest IP 也可能变化
- 所以 agent 必须在环境 reset 之后拿到最新的 `vm_ip`

这也是为什么 `agent.reset()` 接口里会保留 `vm_ip` 参数。

### 2. 为什么中间有 `time.sleep(60)`

对应：

- [lib_run_single.py:26](../../lib_run_single.py#L26)

这不是一个很优雅的设计，但很实用。

原因是桌面环境不是纯内存状态，它涉及：

- VM 启动
- guest 内部服务恢复
- 桌面应用打开
- 文件下载完成
- UI 稳定

所以这里用一个比较粗的“等待环境稳定”方式。

你会在多个 `run_single_example_xxx` 变体里看到类似逻辑。

### 3. 主循环长什么样

主循环从这里开始：

- [lib_run_single.py:31](../../lib_run_single.py#L31)

它的核心逻辑非常直白：

1. `response, actions = agent.predict(instruction, obs)`
2. 遍历 `actions`
3. 每个动作都丢给 `env.step(...)`
4. 保存轨迹和截图

也就是说，这个系统不是：

- 每轮只输出一个动作

而是：

- 模型一次回复可以解析出多个动作

这是理解轨迹日志时很重要的一点。

### 4. 每一步会落哪些文件

单个 action 执行后，runner 会写这些内容：

#### 截图

- [lib_run_single.py:45](../../lib_run_single.py#L45)

文件名大致类似：

```text
step_1_20260428@123456789012.png
```

#### 轨迹日志

- [lib_run_single.py:48](../../lib_run_single.py#L48)

写入到：

```text
traj.jsonl
```

每一行会记录：

- `step_num`
- `action_timestamp`
- `action`
- `response`
- `reward`
- `done`
- `info`
- `screenshot_file`

这意味着：

- 你不是只能看最终结果
- 你可以完整回放 Agent 的中间决策

### 5. 任务结束不是靠 `step()` 最终评分

循环结束后，会调用：

- [lib_run_single.py:65](../../lib_run_single.py#L65)

也就是：

```python
result = env.evaluate()
```

这一点非常关键：

- `step()` 返回的 `done` 只是交互循环的停止条件之一
- 真正分数还是由 `evaluate()` 决定

### 6. 结果如何保存

任务结束后，runner 会写：

- `result.txt`
- `recording.mp4`
- `traj.jsonl`
- 各步截图

还会调用：

- [lib_run_single.py:72](../../lib_run_single.py#L72)

也就是：

```python
log_task_completion(...)
```

## 二、`lib_results_logger.py` 负责什么

对应文件：

- [lib_results_logger.py](../../lib_results_logger.py)

这个文件的作用不是每步轨迹，而是任务级结果汇总。

### 1. 写入目标

它会把结果写到：

```text
{result_dir}/summary/results.json
```

对应逻辑：

- [lib_results_logger.py:52](../../lib_results_logger.py#L52)

### 2. 为什么要单独做一个 logger

因为多进程运行时，多个任务会同时完成。

如果直接裸写同一个 JSON，很容易互相覆盖。

所以这里用了文件锁：

- [lib_results_logger.py:59](../../lib_results_logger.py#L59)

也就是 `fcntl.flock(...)`。

这个设计很朴素，但足够实用。

### 3. 单任务级结果长什么样

写入的每条结果大致包含：

- `application`
- `task_id`
- `status`
- `score`
- `timestamp`

如果失败，还会加：

- `err_message`

## 三、`run.py` 负责什么

对应文件：

- [run.py](../../run.py)

第一次阅读建议把它当成“单进程主入口说明书”。

### 1. 它做了什么

它主要负责：

1. 解析命令行参数
2. 创建 `PromptAgent`
3. 创建 `DesktopEnv`
4. 遍历任务清单
5. 对每个任务调用 `lib_run_single.run_single_example(...)`

### 2. 参数配置长什么样

参数解析在：

- [run.py:62](../../run.py#L62)

这里是理解“跑 benchmark 时到底能改哪些参数”的好入口。

尤其是：

- `provider_name`
- `observation_type`
- `action_space`
- `max_steps`
- `model`
- `result_dir`

### 3. Agent 和 Env 是怎么构造的

构造 Agent：

- [run.py:142](../../run.py#L142)

构造 Env：

- [run.py:152](../../run.py#L152)

这里最值得注意的是：

- `action_space` 由 Agent 决定，再传给环境
- `require_a11y_tree` 是根据 `observation_type` 推出来的

也就是说，runner 层承担了“把环境配置和 agent 配置对齐”的责任。

### 4. 任务是怎么枚举的

任务文件清单来自：

- `test_all_meta`

然后这里逐个打开 JSON：

- [run.py:163](../../run.py#L163)
- [run.py:165](../../run.py#L165)

所以 `run.py` 是：

- 先拿任务 ID 列表
- 再去 `evaluation_examples/examples/{domain}/{example_id}.json` 找具体任务内容

### 5. 结果目录结构

结果目录构造在：

- [run.py:184](../../run.py#L184)

结构大致是：

```text
results/
  {action_space}/
    {observation_type}/
      {model}/
        {domain}/
          {example_id}/
```

这一点很重要，因为后面很多脚本都默认这个结构。

### 6. 为什么说它更适合阅读，不一定适合真实跑大规模

因为它：

- 单进程
- 单环境
- 顺序遍历所有任务

这对于理解最清楚，但吞吐量不高。

## 四、`run_multienv.py` 为什么更实用

对应文件：

- [scripts/python/run_multienv.py](../../scripts/python/run_multienv.py)

这个文件本质上是把 `run.py` 的逻辑，改造成：

- 多进程
- 共享任务队列
- 多环境并发运行

### 1. 它的整体结构

最值得先抓的几个函数：

- `config()`
- `distribute_tasks(...)`
- `run_env_tasks(...)`
- `test(...)`

### 2. `distribute_tasks(...)` 做什么

对应：

- [run_multienv.py:136](../../scripts/python/run_multienv.py#L136)

它会把：

```python
{domain: [example_id1, example_id2, ...]}
```

拍平成：

```python
[(domain, example_id), ...]
```

这样就适合塞进共享任务队列。

### 3. `run_env_tasks(...)` 才是 worker 主循环

对应：

- [run_multienv.py:166](../../scripts/python/run_multienv.py#L166)

这个函数很像“每个子进程里的 `run.py`”。

它会：

1. 创建一个 `DesktopEnv`
2. 创建一个 `PromptAgent`
3. 不断从 `task_queue` 里取任务
4. 对每个任务调用 `lib_run_single.run_single_example(...)`

这说明一个很重要的设计选择：

- 每个子进程只维护一个环境实例和一个 agent 实例
- 再重复消费多个任务

而不是每个任务都新建整个运行器对象。

### 4. 为什么它默认更适合大规模跑

因为：

- 多个进程并行消费任务
- 对 AWS / Docker / 多 VM provider 更友好
- 结果目录结构和单进程版本兼容

但代价是：

- 日志更复杂
- 调试不如单进程直观

### 5. 为什么它还要处理 signal

对应：

- [run_multienv.py:144](../../scripts/python/run_multienv.py#L144)
- [run_multienv.py:272](../../scripts/python/run_multienv.py#L272)

这部分是为了：

- `Ctrl+C`
- 进程终止
- 子进程异常退出

时，尽量把 VM / Docker / 云实例清干净。

这在桌面环境 benchmark 里尤其重要，因为残留环境成本很高。

## 五、把三层主线重新拼起来

到这里，你可以把这几层重新接回去看：

### 环境层

- `DesktopEnv`

负责：

- 启动世界
- 获取观测
- 执行动作
- 评测结果

### Agent 层

- `PromptAgent`

负责：

- 读 observation
- 组 prompt
- 调模型
- 解析动作

### Runner 层

- `lib_run_single.py`
- `run.py`
- `run_multienv.py`

负责：

- 把环境和 Agent 串起来
- 控制任务循环
- 写轨迹、截图、录屏、结果

## 六、现在最值得你自己动手看的 4 个地方

### 1. 盯着 `run_single_example(...)` 看一整轮

建议把下面几行对着读一遍：

- [lib_run_single.py:18](../../lib_run_single.py#L18)
- [lib_run_single.py:27](../../lib_run_single.py#L27)
- [lib_run_single.py:32](../../lib_run_single.py#L32)
- [lib_run_single.py:40](../../lib_run_single.py#L40)
- [lib_run_single.py:65](../../lib_run_single.py#L65)

如果你把这 5 个点串起来，整条主循环就基本清楚了。

### 2. 看一次任务结果目录

找一个真实跑过的任务目录，看看里面的：

- `traj.jsonl`
- `result.txt`
- `runtime.log`
- `recording.mp4`
- `step_*.png`

这比单看代码更容易理解 runner 的职责。

### 3. 对比 `run.py` 和 `run_multienv.py`

重点比较：

- 如何构造 `Agent`
- 如何构造 `Env`
- 如何枚举任务
- 如何处理异常

你会更清楚什么是“主循环”，什么是“并发壳子”。

### 4. 看 `results/summary/results.json`

如果你已经跑过任务，去看汇总文件。

这样你就会知道：

- 每步数据写在哪里
- 每任务汇总写在哪里

## 七、读完这篇后你应该能回答的问题

如果下面这些问题你都能回答，runner 这一层就算吃透第一轮了：

1. 一个任务 JSON 是在哪一层被真正加载的？
2. `run_single_example(...)` 为什么要先 reset env 再 reset agent？
3. 为什么结果目录里既有 `traj.jsonl`，又有 `results.json`？
4. 为什么真正评分不在 `step()` 里完成？
5. `run.py` 和 `run_multienv.py` 的边界分别是什么？
6. 多进程版本为什么需要专门做 signal cleanup？

## 八、下一步该读什么

如果继续沿“非 agent 深入”方向走，最自然的下一步有两个选项：

1. `providers`
   重点看不同运行底座是怎么适配的
2. `evaluators`
   重点看 benchmark 是怎么判分的

如果你问我哪个更适合现在继续：

我建议先看 `evaluators`。

因为你现在已经知道：

- 任务怎么跑
- 最后会调 `env.evaluate()`

这时候继续往下看“结果到底怎么算”，衔接最自然。
