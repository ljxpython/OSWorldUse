# 智能体 GUI / 虚拟桌面 Benchmark 框架分类整理

本文档整理的是“让智能体在 GUI、虚拟桌面、设备或网页环境中执行任务，并对结果进行评测”的主流开源 benchmark / framework。  
更新时间：2026-04-24。

## 0. 快速对比表

| 框架 | 类别 | 主要环境 | 任务范围 | 评测特点 | 适合方向 |
|---|---|---|---|---|---|
| OSWorld | 桌面 / 系统级 | Ubuntu / Windows，虚拟机或云环境 | 桌面应用、浏览器、文件系统、多应用协作 | 任务配置 + evaluator + 轨迹 / 截图 / 录像 | desktop agent、computer-use agent |
| Windows Agent Arena | 桌面 / 系统级 | Windows 11，本地或 Azure ML | Windows GUI、多应用办公与系统任务 | 可复现环境、适合批量并行评测 | Windows agent、企业办公自动化 |
| macOSWorld | 桌面 / 系统级 | macOS | Mac 应用与系统操作 | 面向 macOS 场景的任务与评测 | macOS agent、Apple 生态 GUI 研究 |
| AndroidWorld | 移动端 / 设备级 | Android 设备 / 模拟器 | App 交互、移动端工作流 | 初始化、执行、校验链路完整 | mobile agent、跨端 GUI 研究 |
| CRAB | 跨环境 / 通用框架 | 桌面、移动端、多设备 | 跨环境任务编排 | 更偏框架化和可扩展性 | 自定义 benchmark、跨设备 agent |
| WebArena | Web / 浏览器 | 自托管网站 | 网页导航、检索、表单、交易 | 可控、稳定、便于复现 | browser agent、网页任务规划 |
| VisualWebArena | Web / 浏览器 | 自托管网页 + 视觉输入 | 多模态网页任务 | 强调视觉感知和 screen-based 操作 | 多模态 web agent |
| WebArena-Verified | Web / 浏览器 | verified 自托管网页环境 | 与 WebArena 同线任务 | 更强调评测确定性和可信度 | 严谨复现、benchmark 信度研究 |
| WebVoyager | Web / 浏览器 | 真实公开网站 | 浏览、搜索、预订、信息获取 | 自动评审为主，环境更贴近真实互联网 | 真实网站 browser agent |
| Emergence WebVoyager | Web / 浏览器后续工作 | 基于 WebVoyager 分析与清洗 | 聚焦数据质量与评测问题 | 更强调审计、清洗和严格化 | benchmark 质量研究 |

## 1. 桌面 / 操作系统级 Benchmark

这类项目最接近“给智能体在虚拟桌面里做任务并打分”这个定义。特点是：
- 环境通常是真实操作系统、虚拟机或可复现镜像
- 任务覆盖桌面应用、文件系统、系统设置、多应用协作
- 一般带任务初始化、动作执行、轨迹记录、自动评测

### OSWorld
- 定位：当前最有代表性的开源桌面 GUI benchmark 之一。
- 环境：真实操作系统环境，支持 VMware、Docker、AWS、VirtualBox 等 provider。
- 任务：覆盖浏览器、Office、图像处理、系统操作、多应用协作等桌面任务。
- 评测：每个任务带配置和 evaluator，可保存截图、动作轨迹、录像和结果统计。
- 适合场景：做 desktop agent / computer-use agent 的主基准。
- 备注：如果你的目标是“完整电脑使用能力”，它通常是首选。
- 资料：
  - GitHub: <https://github.com/xlang-ai/OSWorld>
  - 官网: <https://os-world.github.io/>
  - 论文: <https://arxiv.org/abs/2404.07972>

### Windows Agent Arena
- 定位：Windows 专项的系统级 agent benchmark。
- 环境：基于 Windows 11 环境，支持本地与 Azure ML 并行运行。
- 任务：强调真实 Windows GUI、多应用工作流和可复现实验。
- 评测：适合批量运行、并行评测和系统化记录。
- 适合场景：以 Windows 办公和桌面自动化为主的 agent 研究。
- 备注：如果你更关心企业办公软件、Windows 生态和并行评测，这套很值钱。
- 资料：
  - GitHub: <https://github.com/microsoft/WindowsAgentArena>
  - 项目页: <https://microsoft.github.io/WindowsAgentArena>
  - 论文: <https://arxiv.org/abs/2409.08264>

### macOSWorld
- 定位：macOS 平台上的 GUI agent benchmark。
- 环境：真实 macOS 应用和系统操作场景。
- 任务：覆盖多种系统与应用任务，并包含安全子集。
- 评测：目标是补齐 macOS 方向长期缺位的问题。
- 适合场景：研究 Mac 生态下的 computer-use agent。
- 备注：方向重要，但生态成熟度目前仍弱于 OSWorld / Windows Agent Arena。
- 资料：
  - GitHub: <https://github.com/showlab/macosworld>
  - 论文: <https://arxiv.org/abs/2506.04135>

## 2. 移动端 / 设备级 GUI Benchmark

这类项目不是“桌面 PC”，但方法论基本一致：也是让 agent 在真实 GUI 里完成任务，再做可重复评测。

### AndroidWorld
- 定位：Android GUI agent benchmark。
- 环境：Android 设备 / 模拟器中的真实 App 交互。
- 任务：基于真实 App 和参数化任务定义，可扩展出大量任务变体。
- 评测：具备初始化、执行、校验的完整链路。
- 适合场景：移动端 agent、跨设备 agent、GUI 操作泛化研究。
- 备注：如果你想研究 GUI agent 的跨平台能力，它是非常关键的一块。
- 资料：
  - GitHub: <https://github.com/google-research/android_world>
  - 论文: <https://arxiv.org/abs/2405.14573>

## 3. 跨环境 / 通用型 Benchmark 框架

这类项目不只服务某一个操作系统，而是更偏“任务编排与评测框架”，可用于桌面、移动端甚至多设备环境。

### CRAB
- 定位：跨环境、多设备的 benchmark / framework。
- 环境：支持把任务组织成跨设备或跨环境工作流。
- 任务：可用于桌面和移动场景，不局限于单个平台。
- 评测：更强调框架能力和任务编排，而不是单一系统 benchmark。
- 适合场景：自己扩展任务、搭建混合场景 benchmark、做 agent framework 研究。
- 备注：它更像“搭 benchmark 的框架”，而不是单一平台上的标准答案。
- 资料：
  - GitHub: <https://github.com/camel-ai/crab>
  - 论文: <https://arxiv.org/abs/2407.01511>

## 4. Web / 浏览器环境 Benchmark

这类项目也是 GUI agent 领域的重要分支，但严格说它们主要覆盖浏览器环境，不等于完整桌面系统。

### WebArena
- 定位：Web agent benchmark 的经典项目。
- 环境：自托管网站环境，可控、可复现。
- 任务：网页导航、表单、检索、购物、后台管理等。
- 评测：强调稳定性、可复现性和统一比较。
- 适合场景：研究 browser agent、网页操作、规划和长链路任务。
- 备注：很多后续 web benchmark 都是从它这条线长出来的。
- 资料：
  - GitHub: <https://github.com/web-arena-x/webarena>
  - 论文: <https://arxiv.org/abs/2307.13854>

### VisualWebArena
- 定位：WebArena 的多模态扩展版本。
- 环境：网页环境，但更强调视觉感知。
- 任务：视觉驱动网页任务，要求模型结合截图和网页状态做决策。
- 评测：适合多模态 browser agent 对比。
- 适合场景：研究视觉网页 agent、screen-based 浏览器操作。
- 资料：
  - GitHub: <https://github.com/web-arena-x/visualwebarena>
  - 论文: <https://arxiv.org/abs/2401.13649>

### WebArena-Verified
- 定位：更强调确定性和评测可信度的 WebArena 变体。
- 环境：以 verified、可审计为目标的网页 benchmark。
- 任务：延续 WebArena 任务风格，但更重视评测信号质量。
- 评测：比传统 LLM-as-a-judge 更强调可验证性。
- 适合场景：对 benchmark 信度要求较高的研究或复现实验。
- 资料：
  - GitHub: <https://github.com/ServiceNow/webarena-verified>

### WebVoyager
- 定位：真实公开网站上的 web agent benchmark。
- 环境：基于 Selenium 等方式直接操作真实互联网网站。
- 任务：覆盖真实网站上的浏览、搜索、预订、信息获取等任务。
- 评测：大量使用 GPT-4V 风格的自动评审。
- 适合场景：研究“真实网站上的 browser agent”表现。
- 备注：依赖真实网站，因此在复现性、长期稳定性和评测一致性上通常弱于自托管 benchmark。
- 资料：
  - GitHub: <https://github.com/MinorJerry/WebVoyager>
  - 论文: <https://arxiv.org/abs/2401.13919>

### Emergence WebVoyager
- 定位：对 WebVoyager 进行审计、清洗和增强后的后续工作。
- 作用：指出原始 WebVoyager 在任务歧义、操作变异和评测透明性上的问题，并提出更严格版本。
- 适合场景：研究 WebVoyager 数据质量、评测鲁棒性和 benchmark 清洗问题。
- 资料：
  - 论文: <https://arxiv.org/abs/2603.29020>

## 5. 如何理解这些项目的关系

### 如果你的目标是完整桌面智能体
优先看：
- OSWorld
- Windows Agent Arena
- macOSWorld

这三类项目更接近“电脑使用 agent”的真实定义，因为它们覆盖的不只是浏览器，还包括应用程序、文件、系统状态和多应用协同。

### 如果你的目标是浏览器智能体
优先看：
- WebArena
- VisualWebArena
- WebArena-Verified
- WebVoyager

这条线更适合研究网页导航、视觉网页理解、在线任务完成和 browser agent。

### 如果你的目标是移动端或跨设备
优先看：
- AndroidWorld
- CRAB

前者偏 Android GUI，后者偏跨环境框架能力。

## 6. 一句话总结

- `OSWorld / Windows Agent Arena / macOSWorld`：系统级、桌面级 benchmark。
- `AndroidWorld`：移动端 GUI benchmark。
- `CRAB`：跨环境任务和评测框架。
- `WebArena / VisualWebArena / WebArena-Verified / WebVoyager`：浏览器环境 benchmark。

## 7. 选型建议

### 如果你要做完整电脑使用能力评测
优先顺序通常是：
- OSWorld
- Windows Agent Arena
- macOSWorld

原因：
- 它们更接近真实操作系统使用场景
- 能覆盖浏览器之外的应用、文件和系统状态
- 更适合验证 computer-use agent 的端到端能力

### 如果你要做浏览器智能体评测
优先顺序通常是：
- WebArena
- VisualWebArena
- WebArena-Verified
- WebVoyager

原因：
- 这条线更聚焦网页任务
- 部署和调试成本通常低于完整桌面环境
- 更适合研究网页导航、多模态网页理解和在线任务完成

### 如果你要做移动端或跨设备研究
优先顺序通常是：
- AndroidWorld
- CRAB

原因：
- AndroidWorld 更像标准化移动端 benchmark
- CRAB 更适合做跨环境任务编排和自定义扩展

## 8. 调研时建议重点关注的维度

看这些框架时，建议重点比较下面几个维度：
- 环境是否可复现：是真实网站、虚拟机镜像，还是自托管环境
- 任务是否稳定：任务会不会因为外部网站变化而失效
- 评测是否可靠：是规则评测、程序执行式评测，还是 LLM / VLM 自动打分
- 场景覆盖是否够广：只覆盖浏览器，还是覆盖完整操作系统
- 部署成本是否可接受：本地能不能跑，是否依赖云资源、闭源镜像或特殊账号配置
- 是否适合你的研究目标：研究 browser agent、desktop agent、mobile agent，还是通用 agent framework

## 9. 四段式结构对比

为了方便做更细的调研，可以把每个框架统一拆成四层：
- 环境层：任务运行在哪里，环境是否可控、可复现
- 任务层：任务怎么定义，覆盖什么场景
- 评测层：任务完成情况怎么判定
- 结果记录层：会记录哪些轨迹、日志、截图或统计结果

### OSWorld
- 环境层：以真实操作系统和虚拟化环境为核心，支持 VMware、Docker、AWS、VirtualBox 等 provider，属于标准的系统级运行环境。
- 任务层：任务以桌面使用场景为主，覆盖浏览器、Office、图像处理、系统设置、文件操作和多应用协同。
- 评测层：任务通常自带 evaluator，能够按规则或程序化检查任务是否完成。
- 结果记录层：一般会记录动作轨迹、截图、录像和最终统计结果，适合做端到端实验复盘。

### Windows Agent Arena
- 环境层：基于 Windows 11 运行环境，支持本地和 Azure ML 等并行评测模式。
- 任务层：围绕 Windows GUI、办公任务、系统操作和多应用工作流展开。
- 评测层：强调可复现和可批量运行，适合大规模对比不同 agent。
- 结果记录层：更强调实验执行管理、批量结果收集和并行评测输出。

### macOSWorld
- 环境层：聚焦 macOS 环境，补齐 Apple 桌面生态上的 benchmark 空白。
- 任务层：覆盖 Mac 应用、系统操作和安全相关子任务。
- 评测层：围绕 macOS GUI 任务执行结果进行判断，属于系统级评测范式。
- 结果记录层：通常会保留任务执行过程和评测结果，用于对比不同模型在 macOS 场景的表现。

### AndroidWorld
- 环境层：运行在 Android 设备或模拟器中，属于移动端 GUI 环境。
- 任务层：任务围绕真实 App 和移动端工作流组织，并支持参数化扩展。
- 评测层：具有比较完整的初始化、执行和结果校验逻辑。
- 结果记录层：重点记录任务执行链路和是否完成目标，便于移动端 agent 对比。

### CRAB
- 环境层：不绑定单一平台，可覆盖桌面、移动端甚至多设备协作环境。
- 任务层：更强调跨环境任务编排，可以把多个设备或多个场景串成一个工作流。
- 评测层：偏框架化，方便研究者自定义任务检查逻辑。
- 结果记录层：更适合作为实验框架来组织日志、任务状态和跨环境执行结果。

### WebArena
- 环境层：以自托管网站为主，环境相对稳定、可控、易复现。
- 任务层：聚焦网页导航、搜索、表单填写、后台管理和交易类任务。
- 评测层：规则化和环境内可验证检查较强，适合做稳定的 browser agent 对比。
- 结果记录层：通常保留网页交互轨迹、任务状态和实验结果，便于做统一比较。

### VisualWebArena
- 环境层：继承 WebArena 的网页环境，但更强调截图和视觉输入。
- 任务层：任务依赖视觉理解，要求模型同时处理网页结构和页面视觉线索。
- 评测层：沿用 web benchmark 的可验证任务判断方式，同时更考验视觉决策能力。
- 结果记录层：除网页交互结果外，通常更重视视觉观测和多模态执行轨迹。

### WebArena-Verified
- 环境层：仍然是自托管、可审计的网页环境，但更强调 verified 设置。
- 任务层：任务设计与 WebArena 同线，但更重视任务定义和结果信号的稳定性。
- 评测层：重点提升评测确定性，减少不透明或不稳定的判定方式。
- 结果记录层：更适合做高可信 benchmark 对比和复现实验记录。

### WebVoyager
- 环境层：直接运行在真实公开网站上，环境更接近真实互联网，但也更容易受外部变化影响。
- 任务层：覆盖浏览、搜索、预订、信息收集等真实网站任务。
- 评测层：较多依赖自动评审，特别适合考察真实在线网页任务表现。
- 结果记录层：重点在网页操作过程和任务完成结果，适合分析真实网站中的 agent 行为。

### Emergence WebVoyager
- 环境层：建立在对 WebVoyager 的后验分析之上，本身更偏 benchmark 审计工作而不是独立运行环境。
- 任务层：核心不是增加新任务类型，而是分析原任务集中的歧义、变异和质量问题。
- 评测层：重点是指出原始评测的脆弱点，并推动更严格、透明的评测方式。
- 结果记录层：更重视数据质量分析、任务清洗结果和 benchmark 修订依据。

## 10. 这些桌面 Agent 测评是不是都建立在虚拟环境中

### 10.1 结论先说

不是“全部都是”，但如果只看 **主流、严肃、系统级的桌面 benchmark**，可以近似认为：

- 它们大多数都运行在 **隔离、可恢复的环境** 中
- 这个环境通常不是研究者自己的日常宿主机桌面
- 常见形式包括：
  - 本地虚拟机
  - 云端虚拟机 / 云主机
  - 容器中托管的虚拟桌面 / 模拟器
  - 真实设备或模拟器，但同样要求可恢复和可隔离

换句话说：

- **benchmark 运行框架** 往往依赖可恢复环境
- **benchmark 数据集 / 任务 JSON / evaluator 规则** 本身并不一定“建在 VM 里”

### 10.2 为什么大多数 benchmark 不直接跑宿主机

原因主要有：

- 需要 `reset` 到干净初始状态
- 需要实验可复现
- 需要并行批量运行
- 需要避免宿主机个人状态干扰
- 需要减少人工干预

如果直接跑研究者自己的桌面，通常会出现：

- 环境污染
- 文件和应用残留
- 通知 / 弹窗干扰
- 无法稳定恢复状态
- benchmark 结果可信度下降

### 10.3 典型项目对应的环境形态

#### OSWorld

- 属于典型的 **VM / 云环境 benchmark**
- 支持 `VMware / Docker / AWS / VirtualBox`
- 本质上依赖 Ubuntu / Windows 的可恢复系统环境

结论：

- **是隔离环境 benchmark**
- 也是典型的 `VM-first` 路线

#### Windows Agent Arena

- 也是隔离环境 benchmark
- 但不是只有单一本地 VM 路线
- 典型形态包括：
  - 本地 Windows 11 镜像 / 可复现环境
  - Azure ML / 云端并行评测环境

结论：

- **是隔离环境 benchmark**
- 更准确地说是 `reproducible Windows environment-first`

#### macOSWorld

- 官方主线是：
  - 本地 Python testbench
  - 云端 AWS-hosted macOS instances
- 代码层面也保留了 VMware 路线

结论：

- **是隔离环境 benchmark**
- 官方默认甚至不是普通本地 VM，而是 `AWS-hosted macOS instances`

#### AndroidWorld

- 运行在 Android emulator / device 环境中
- 不属于传统桌面 VM，但同样不是宿主机日常桌面

结论：

- **也是隔离环境**
- 更偏 `emulator / device-first`

#### MMBench-GUI

- 更像多平台 benchmark / 评测框架
- 不等于它自己内置一套统一 VM 环境
- 更适合理解为：可以接不同环境后端的评测层

结论：

- **不是典型 VM-first benchmark**
- 更像 `framework-first`

#### OpenAdapt / openadapt-evals

- 更偏工程平台和评测基础设施
- 关注记录、执行、回放、评估
- 可以接 benchmark，但自身不等于一个标准系统级 benchmark

结论：

- **不属于典型 VM-first benchmark**
- 更像 `host-native / platform-first`

### 10.4 一个更准确的分类法

如果不想再用“是不是虚拟机”这种太粗的分法，建议改成下面四类：

| 类型 | 特征 | 代表项目 |
|---|---|---|
| VM-first | 任务运行在本地或云端 VM，强调 snapshot / reset / 隔离 | OSWorld |
| Cloud-instance-first | 任务运行在云端专用实例，环境恢复依赖镜像或云 API | macOSWorld |
| Emulator / device-first | 运行在模拟器或远程设备中 | AndroidWorld |
| Framework-first | 更关注任务编排和评测框架，不绑定单一环境形态 | MMBench-GUI, CRAB, OpenAdapt |

### 10.5 对 CUA 评测的直接启发

如果目标是严肃评测 CUA：

- `OSWorld / WindowsAgentArena / macOSWorld` 这类 benchmark
  - 最好仍然跑在它们各自假设的隔离环境中
- “直接跑你自己的宿主机桌面”
  - 更适合：
    - 开发期验证
    - demo
    - agent 工程调试
  - 不太适合直接作为正式 benchmark 主结果

### 10.6 一句话总结

不是所有桌面 agent 测评都建立在传统虚拟机中。  
但 **主流、标准化、可复现的桌面系统级 benchmark，绝大多数都建立在某种隔离可恢复环境中**，只是这个环境不一定总是传统本地 VM，也可能是：

- 云端实例
- 模拟器
- 容器托管环境
- 远程设备
