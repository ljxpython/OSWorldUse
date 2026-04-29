# CUA 三平台评测方案

## 1. 目标

目标是系统化评测 CUA 在以下三类桌面环境中的 GUI / computer-use 能力：

- Windows：使用 `WindowsAgentArena`
- macOS：使用 `macOSWorld`
- Ubuntu：使用 `OSWorld`

本方案不强行把三套 benchmark 合并成一个统一 benchmark，而是：

- 保留各自原生任务集、环境和评测器
- 统一启动入口
- 统一结果抽取
- 统一报告生成

最终达到两个结果：

1. 能够一键启动针对任一评测集的评测流程
2. 评测结束后自动生成包含通过率、失败 case 列表的报告

## 2. 设计原则

- 不重造 benchmark：优先复用 OSWorld / WindowsAgentArena / macOSWorld 原生能力
- 不强造统一分数：不同 benchmark 的分数不直接混算，只统一展示
- 先做统一编排层，再做深度适配
- 先支持单 benchmark 一键运行，再支持批量矩阵运行
- 所有结果都落盘，避免只看终端输出

## 3. 总体方案

### 3.1 总体架构

采用“四层结构”：

1. `Benchmark Adapter` 层
   - 每个 benchmark 一个适配器
   - 负责环境准备、命令拼装、结果收集、失败识别

2. `Launcher` 层
   - 提供统一 CLI
   - 用户只关心 `跑哪个 benchmark / 哪个 profile / 哪个 agent`

3. `Normalizer` 层
   - 把不同 benchmark 的原始结果转换为统一结构

4. `Reporter` 层
   - 生成 Markdown / JSON 报告
   - 输出通过率、失败 case、关键统计

### 3.2 benchmark 与平台映射

| 平台 | benchmark | 角色 |
|---|---|---|
| Ubuntu | OSWorld | Ubuntu 主 benchmark |
| Windows | WindowsAgentArena | Windows 主 benchmark |
| macOS | macOSWorld | macOS 主 benchmark |

说明：

- Ubuntu 不用拿 Windows/macOS benchmark 替代
- macOS 不再尝试用 Ubuntu 代测
- 三个平台各自用最适合自己的 benchmark

## 4. 目录结构建议

建议在当前仓库内新增一个独立编排目录，例如：

```text
cross_platform_eval/
  README.md
  configs/
    osworld.yaml
    windows_agent_arena.yaml
    macosworld.yaml
    agent.cua.yaml
  adapters/
    base.py
    osworld_adapter.py
    waa_adapter.py
    macosworld_adapter.py
  launcher/
    cli.py
    profiles.py
  reporters/
    normalize.py
    markdown_report.py
    json_report.py
  schemas/
    result_schema.py
  outputs/
    raw/
    normalized/
    reports/
```

## 5. 统一启动方式

### 5.1 统一 CLI 目标

目标命令形式：

```bash
python -m cross_platform_eval.launcher.cli run --benchmark osworld --agent cua
python -m cross_platform_eval.launcher.cli run --benchmark windowsagentarena --agent cua
python -m cross_platform_eval.launcher.cli run --benchmark macosworld --agent cua
```

后续可扩展：

```bash
python -m cross_platform_eval.launcher.cli run --benchmark all --agent cua
```

### 5.2 参数建议

统一参数只保留高频项：

- `--benchmark`
- `--agent`
- `--tasks-file`
- `--result-root`
- `--model`
- `--max-steps`
- `--headless`
- `--profile`

各 benchmark 的特殊参数放进配置文件，不直接暴露给用户。

## 6. 适配层设计

### 6.1 OSWorld Adapter

职责：

- 调用 OSWorld 原生 runner
- 接入 CUA agent adapter
- 收集 `result.txt`、`traj.jsonl`、截图、录像、日志
- 输出统一结果

建议优先复用当前仓库已有 runner：

- `scripts/python/run_multienv.py`
- `scripts/python/run_multienv_openaicua.py`
- 以及后续自定义的 `run_multienv_cua.py`

输出抽取重点：

- task 是否完成
- domain
- example_id
- result score
- 失败时的异常信息
- 轨迹路径

### 6.2 WindowsAgentArena Adapter

职责：

- 调用 WindowsAgentArena 官方任务执行入口
- 注入 CUA agent
- 收集任务级结果和失败日志
- 转换成统一结构

建议：

- 尽量不改官方 benchmark 内核
- 优先通过“自定义 agent 接口”接入
- 若官方支持批量运行，优先复用其 batch 入口

输出抽取重点：

- task id
- app/workflow 类型
- pass/fail
- 失败原因
- 原始 artifacts 路径

### 6.3 macOSWorld Adapter

职责：

- 调用 macOSWorld 官方任务执行入口
- 接入 CUA agent
- 抽取任务结果、日志和失败 case

建议：

- 优先遵循 macOSWorld 的自定义 agent 接入方式
- 不自己改写任务 evaluator

输出抽取重点：

- task id
- app category
- pass/fail
- 安全子集任务标记
- 原始执行轨迹

## 7. 统一结果格式

建议定义统一结果 schema：

```json
{
  "benchmark": "osworld",
  "platform": "ubuntu",
  "run_id": "20260425_xxx",
  "agent": "cua",
  "model": "xxx",
  "task_id": "chrome/bb5e4c0d-f964-439c-97b6-bdb9747de3f4",
  "task_name": "Can you make Bing the main search engine...",
  "status": "passed",
  "score": 1.0,
  "duration_sec": 123.4,
  "steps": 11,
  "failure_type": null,
  "failure_reason": null,
  "artifacts": {
    "log": "...",
    "traj": "...",
    "video": "...",
    "screenshots_dir": "..."
  },
  "raw_result": {}
}
```

其中统一字段至少包括：

- benchmark
- platform
- task_id
- status
- score
- failure_type
- failure_reason
- artifacts

## 8. 报告生成

### 8.1 报告输出物

每次运行至少输出两类文件：

1. `JSON` 明细
   - 供后续程序处理

2. `Markdown` 报告
   - 供人直接阅读

### 8.2 报告内容

每个 benchmark 报告至少包含：

- benchmark 名称
- 平台
- agent / model / profile
- 总任务数
- 通过数
- 失败数
- 通过率
- 失败 case 列表
- 每个失败 case 的简要原因

建议报告结构：

```text
# CUA Evaluation Report

## Summary
- Benchmark: OSWorld
- Platform: Ubuntu
- Total: 100
- Passed: 63
- Failed: 37
- Pass Rate: 63.0%

## Failure Cases
| task_id | failure_type | failure_reason | artifact |
|---|---|---|---|
```

### 8.3 聚合报告

后续再补一个总报告：

- Ubuntu / Windows / macOS 三份 benchmark 报告汇总到一个总表
- 只做展示，不计算跨 benchmark 综合分

## 9. 一键运行流程

### 9.1 单 benchmark 一键运行

流程：

1. 读取 benchmark 配置
2. 检查环境依赖
3. 启动 benchmark 原生流程
4. 运行 CUA agent
5. 收集原始结果
6. 归一化
7. 生成报告

### 9.2 未来的全量矩阵运行

后续可扩展为：

```bash
python -m cross_platform_eval.launcher.cli run --benchmark all --agent cua
```

实际执行顺序建议：

1. `OSWorld (Ubuntu)`
2. `WindowsAgentArena`
3. `macOSWorld`

原因：

- Ubuntu 接入成本最低，先跑通链路
- Windows 第二，便于补齐企业办公场景
- macOS 第三，通常环境和权限问题最多

## 10. 分阶段实施计划

### Phase 1：MVP

目标：

- 跑通单 benchmark 一键执行
- 自动生成单 benchmark 报告

范围：

- 先接 `OSWorld`
- 定义统一 schema
- 实现 Markdown/JSON 报告

交付：

- `osworld_adapter.py`
- `cli.py`
- `normalize.py`
- `markdown_report.py`

### Phase 2：Windows 接入

目标：

- 接入 `WindowsAgentArena`
- 保持 CLI 不变

交付：

- `waa_adapter.py`
- Windows 结果解析器

### Phase 3：macOS 接入

目标：

- 接入 `macOSWorld`
- 支持三平台单独运行

交付：

- `macosworld_adapter.py`
- macOS 报告解析器

### Phase 4：全量聚合

目标：

- 支持 `--benchmark all`
- 自动产出总报告

交付：

- 聚合报告器
- 多 benchmark 批处理器

## 11. 风险与难点

### 11.1 最大风险

1. 三个 benchmark 的 agent 接口不完全一致
2. 三个 benchmark 的结果文件格式不一致
3. 环境依赖差异大，尤其是 macOS 权限和 Windows 自动化权限
4. CUA 现有运行时和 benchmark 的控制循环可能不完全对齐

### 11.2 规避方式

- 不修改 benchmark 核心逻辑，优先写适配层
- 不统一动作协议，先统一结果协议
- 报告层尽量后置，先保真抽取原始结果
- 先跑通 Ubuntu，再接 Windows 和 macOS

## 12. 方案判断标准

这份方案合理与否，建议用下面 5 条判断：

1. 是否避免了重写 benchmark
2. 是否把统一点放在“启动”和“报告”，而不是硬统一任务
3. 是否允许后续替换 agent，而不是只服务 CUA
4. 是否允许单 benchmark 独立运行和调试
5. 是否能在 MVP 阶段尽快出第一份可读报告

## 13. 推荐落地顺序

建议按下面顺序执行：

1. 在当前仓库中先落 `cross_platform_eval/` 骨架
2. 先做 `OSWorld + CUA` MVP
3. 把结果标准化和报告打通
4. 再接 `WindowsAgentArena`
5. 最后接 `macOSWorld`

## 14. 一句话总结

推荐方案不是“统一 benchmark”，而是：

**以 OSWorld / WindowsAgentArena / macOSWorld 作为各平台原生 benchmark，以统一启动器 + 统一结果归一化 + 统一报告生成器作为上层编排层。**

这样做的好处是：

- benchmark 可信度高
- 接入路径清晰
- 不会因为硬统一而把三套优秀 benchmark 改残
- 最终也能满足“一键运行”和“自动出报告”的目标

## 15. 当前阶段策略调整

结合当前资源情况，建议将实施顺序调整为：

1. **当前主线：macOSWorld**
   - 先验证 CUA 在 macOS benchmark 上能否跑通
   - 先打通 agent 接口、任务执行、结果收集、报告生成

2. **次主线：WindowsAgentArena 预研**
   - 如果暂时没有可用 Windows 设备、Windows 11 VM 或 Azure 资源，则先不落地执行
   - 保留适配层设计，待设备条件具备后再接入

3. **延后：OSWorld / Ubuntu**
   - Ubuntu 评测不是当前一号目标
   - 在 macOS 路线稳定后，再回头补 Ubuntu

当前阶段更准确的策略不是“三平台同时推进”，而是：

- 先完成 `macOSWorld` 的单 benchmark 跑通
- 再把统一启动和报告层抽出来
- 最后逐步接 Windows 和 Ubuntu

## 16. macOS 方向补充选型

虽然 `macOSWorld` 是当前 macOS benchmark 的首选，但它不是唯一值得纳入方案的项目。

### 16.1 角色划分建议

| 项目 | 角色 | 是否作为主 benchmark |
|---|---|---|
| macOSWorld | macOS 主 benchmark | 是 |
| MMBench-GUI | 补充型跨平台评测框架 | 否 |
| OpenAdapt | 工程验证 / agent automation 平台 | 否 |
| computer_use_ootb | agent baseline / 工程参考实现 | 否 |

### 16.2 推荐用法

#### macOSWorld

用途：

- 作为 macOS 主 benchmark
- 用于产出正式 benchmark 结果
- 用于评估 CUA 在 Mac 原生应用和系统操作上的任务完成能力

优点：

- 专门面向 macOS
- 有完整任务集和评测流程
- 支持自定义 agent 接入

缺点：

- 默认部署依赖 AWS macOS 云主机
- 社区规模较小
- 工程成熟度仍在爬坡

#### MMBench-GUI

用途：

- 作为补充评测框架
- 适合做跨平台 / 分层评测
- 可用于补充诊断某些 GUI 能力

优点：

- 平台覆盖广
- 更偏框架化
- 后续可能适合统一一部分评测编排

缺点：

- 不应直接替代 macOSWorld 作为 macOS 主 benchmark
- 更像补充体系，不是当前 macOS 主线标准答案

#### OpenAdapt

用途：

- 作为工程验证工具
- 用于验证 agent 自动化链路是否稳定
- 用于录制、回放、调试和工程实验

优点：

- 工程成熟度和社区热度较高
- 更像平台级工具

缺点：

- 不是标准化 macOS benchmark
- 不适合直接作为正式 benchmark 分数来源

#### computer_use_ootb

用途：

- 作为 baseline agent 参考实现
- 用于学习已有 macOS/Windows computer-use agent 工程写法

优点：

- 更偏现成 agent runtime
- 对工程落地参考价值高

缺点：

- 不是 benchmark
- 不负责标准任务和打分

### 16.3 macOS 方向最终建议

macOS 方向建议采用“三件套”：

1. `macOSWorld`：主 benchmark
2. `MMBench-GUI`：补充型 cross-platform / 能力诊断
3. `OpenAdapt / computer_use_ootb`：工程参考与调试辅助

## 17. macOSWorld 默认 AWS 路线说明

### 17.1 “AWS-hosted macOS instances” 的准确含义

`macOSWorld` 的默认设计不是“在你本机 Mac 上直接跑 benchmark”，而是：

- **本地机器**运行 Python testbench
- testbench 通过 **SSH + VNC** 去控制一台 **AWS 上的 macOS EC2 实例**
- 每个任务执行前，通过 **镜像 / snapshot recovery** 把云端 macOS 环境恢复到指定初始状态

也就是说：

- 你的本地机器主要是“控制端”
- 真正跑任务的是 AWS 上的 macOS 机器

### 17.2 本地代码中的证据

你本地这份 `macosworld` 代码已经明确写了这点：

- `readme.md` 写明：`macOSWorld consists of a local Python testbench script and cloud-hosted AWS macOS instances.`
- `instructions/configure_aws_env.md` 写明环境配置包括：
  - AWS 账号
  - Dedicated Host
  - macOS instance
- `run.py` / `testbench.py` 需要这些参数：
  - `--instance_id`
  - `--ssh_host`
  - `--ssh_pkey`

### 17.3 为什么它默认走 AWS

原因主要有三点：

1. **可复现性**
   - benchmark 需要可重复恢复到固定初始状态

2. **环境控制**
   - 云上实例更容易统一镜像、账号、权限、VNC、SSH

3. **任务隔离**
   - 每个任务需要干净环境，snapshot/image 恢复是核心能力

### 17.4 这是不是意味着只能上 AWS

**不完全是。**

从你本地代码看，`macOSWorld` 并不是完全锁死 AWS：

- `testbench.py` 明确支持 `--vmx_path`
- 代码里要求的是：`instance_id` 或 `vmx_path` 二选一
- `utils/run_task.py` 中也分了两条恢复路径：
  - AWS EC2 image recovery
  - VMware snapshot revert

这说明：

- **官方 README 默认主推 AWS**
- **代码层面其实保留了 VMware 本地运行口子**

### 17.5 当前最务实的理解

对你现在的落地来说，可以这么理解：

- **默认官方主线**：AWS macOS 实例
- **可探索的本地替代路线**：VMware 本地 macOS VM

但要注意：

- 本地 VMware 路线不是 README 主路径
- 更像“代码已支持 + 社区实现可参考”
- 工程成熟度和踩坑成本大概率高于 AWS 官方路径

### 17.6 对我们方案的影响

因此在方案上，macOSWorld 建议拆成两条部署策略：

#### Route A：官方标准路线

- AWS macOS instance
- 适合做标准 benchmark
- 优先保证结果可信和流程一致

#### Route B：本地实验路线

- VMware-based macOS VM
- 适合低成本调试、开发期验证
- 适合先接 agent、先打通链路
- 不建议直接把它包装成“官方标准结果”

附加提醒：

- 当前 `macOSWorld` 代码虽然支持 `--vmx_path`，但其 VMware 工具实现更偏 `vmrun -T ws`（Workstation 口径）
- 如果宿主机是 macOS 且使用 `VMware Fusion`，通常还需要补一层兼容改造
- 因此本地 VMware 路线应被视为“可探索路线”，不是当前官方主路径

## 18. 建议的 macOS 实施策略

建议先这样落地：

### Step 1：先做 macOSWorld 接口验证

- 先不追求大规模 benchmark
- 先完成：
  - CUA 接入
  - 单任务运行
  - 结果落盘
  - 报告抽取

### Step 2：选择部署路线

二选一：

- 想先求稳：走 AWS 官方路径
- 想先省钱和便于调试：先试本地 VMware 路线

### Step 3：补充工程参考

如果 CUA 接入过程中遇到 agent 工程问题：

- 参考 `computer_use_ootb`
- 参考 `OpenAdapt`

### Step 4：后续再扩展

- 成功跑通 macOSWorld 后，再补 WindowsAgentArena
- 最后再决定是否回到 OSWorld/Ubuntu
