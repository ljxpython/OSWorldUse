# CUA 评测成本与本地环境配置核算

## 1. 文档目标

这份文档用于回答两个问题：

1. 如果按照各 benchmark 官方推荐方式部署，需要花多少钱
2. 如果尽量改成本地运行，宿主机需要准备什么样的硬件配置

当前关注的平台与 benchmark 映射如下：

- macOS：`macOSWorld`
- Ubuntu：`OSWorld`
- Windows：`WindowsAgentArena`

说明：

- 本文优先从 **CUA 本地验证和低成本实验** 角度核算
- 不把三套 benchmark 强行统一部署
- 但会统一评估“如果未来三套环境都要装，本地机器要准备多少资源”

## 2. 当前宿主机假设

当前讨论默认宿主机是：

- macOS
- Apple Silicon
- 使用 `VMware Fusion`

这会影响两点：

1. `macOSWorld` 本地替代路线更偏向 `Fusion + macOS VM`
2. `OSWorld` 的 Ubuntu 本地路线可以走 `Fusion`
3. `Windows` 本地路线在 Apple Silicon 上存在明显兼容和生态风险，不建议直接假设“本地稳跑”

## 3. macOSWorld 成本核算

### 3.1 官方默认路线：AWS-hosted macOS instances

`macOSWorld` 官方 README 明确写的是：

- 本地 Python testbench
- 云端 AWS macOS 实例

也就是说，本地机器是“控制端”，真正执行 benchmark 的是 AWS 上的 Mac。

相关本地代码和文档证据：

- `readme.md` 写明：`local Python testbench + cloud-hosted AWS macOS instances`
- `instructions/configure_aws_env.md` 明确要求：
  - AWS 账号
  - Dedicated Host
  - macOS instance
- `run.py` / `testbench.py` 要求：
  - `--instance_id`
  - `--ssh_host`
  - `--ssh_pkey`

### 3.2 AWS 价格估算

按 AWS 官方 `ap-southeast-1`（Singapore）价格表估算：

- `MAC2 Dedicated Host`：约 **`$0.779 / 小时`**
- 但 EC2 Mac Dedicated Host 存在 **24 小时最低计费**

因此：

```text
最低一次分配成本 ≈ 0.779 × 24 = 18.696 美元
```

可以记成：

- **最低试水成本：约 `$18.70`**

### 3.3 macOSWorld 跑一轮的大概费用

仓库 README 提到：

- 每个任务大约 `15-20` 分钟
- snapshot recovery 是主要瓶颈

若按 `202` 个任务粗略估算单语言完整执行：

- 202 × 15 分钟 ≈ 50.5 小时
- 202 × 20 分钟 ≈ 67.3 小时

按 `$0.779 / 小时` 估算主机费用：

- **约 `$39 - $53` / 单语言完整跑一遍**

如果按 5 种语言全跑：

- **约 `$197 - $262`**

备注：

- 上述主要是 Host 成本
- 还未计入少量 EBS / IP / 流量成本
- 但这些通常不是大头

### 3.4 结论

如果预算敏感，`macOSWorld` 走 AWS 官方路线的成本结论是：

- 适合正式 benchmark
- 不适合低预算频繁试错

## 4. macOSWorld 本地替代路线核算

### 4.1 是否可本地化

可以探索。

虽然 README 默认主推 AWS，但代码层面其实保留了 `VMware` 路线：

- `testbench.py` 支持 `--vmx_path`
- `run.py` 支持 `--vmx_path`
- `utils/run_task.py` 中：
  - `vmx_path != None` 走 VMware snapshot 恢复
  - 否则走 AWS EC2 镜像恢复

### 4.2 本地 VMware 路线的直接成本

如果已经有本机 Mac 和 VMware Fusion：

- **云资源成本：接近 0**
- 主要成本变成：
  - 磁盘空间
  - 宿主机内存
  - 宿主机 CPU
  - 你自己改造和调试时间

### 4.3 macOS 本地 VM 推荐配置

#### 最低能启动

- 磁盘：`80GB`
- 内存：`8GB`
- CPU：`4 核`

#### 比较实际

- 磁盘：`120GB`
- 内存：`12GB`
- CPU：`6 核`

#### 推荐

- 磁盘：`120GB - 160GB`
- 内存：`16GB`
- CPU：`6 - 8 核`

#### 如果要留较多 snapshot / benchmark 文件

- 磁盘：`200GB+`

### 4.4 本地 VMware 路线的额外坑

当前 `macOSWorld` 代码虽然支持 VMware，但其工具实现更偏 `vmrun -T ws`（Workstation 口径）：

- 不一定能在 macOS 宿主机上的 `Fusion` 直接无改动使用
- 需要做 `vmrun -T fusion` 兼容

所以：

- 本地 VMware 路线不是零成本开箱即用
- 但相较 AWS，仍然是低预算实验的更优路线

## 5. OSWorld Ubuntu 本地环境核算

### 5.1 本地可行性

在当前 Apple Silicon Mac 上，Ubuntu 是三套环境里**最适合本地化**的一条：

- `OSWorld` 本身就支持 VMware provider
- 当前仓库代码在 macOS/ARM 下会自动选择 `Ubuntu-arm` 镜像

### 5.2 已知镜像下载体积

根据官方镜像下载头信息：

- `Ubuntu-arm.zip`：约 **12.29 GB**

说明：

- 这是压缩包体积
- 解压后实际占用会明显更大
- 再加 snapshot，实际磁盘需求不能只按 12GB 算

### 5.3 Ubuntu VM 推荐配置

#### 最低可跑

- 磁盘：`80GB`
- 内存：`8GB`
- CPU：`4 核`

#### 比较实际

- 磁盘：`100GB`
- 内存：`12GB`
- CPU：`4 - 6 核`

#### 推荐

- 磁盘：`120GB`
- 内存：`12GB - 16GB`
- CPU：`6 核`

## 6. Windows 本地环境核算

### 6.1 先说现实判断

在当前 **Apple Silicon Mac** 上，本地跑 Windows benchmark 不是最稳的选择。

原因：

- `OSWorld` 当前 VMware 路线里的 Windows 镜像是 `x86`
- Apple Silicon 本地 Fusion 更偏 `Windows ARM`
- benchmark 环境、预装应用、自动化兼容性都可能出现偏差

因此：

- **Windows 本地 benchmark 不建议作为当前主线**
- 更适合：
  - 单独的 Windows 11 真机
  - x86 主机
  - 或后续云端/企业机器

### 6.2 已知镜像下载体积

根据官方镜像下载头信息：

- `Windows-x86.zip`：约 **26.23 GB**

说明：

- 这也是压缩包体积
- 解压后的 VM 占用会大得多
- Windows + Office + snapshot 很吃盘

### 6.3 Windows VM 预算配置

如果未来在合适的 Windows/x86 宿主环境上本地跑：

#### 最低可跑

- 磁盘：`120GB`
- 内存：`8GB`
- CPU：`4 核`

#### 比较实际

- 磁盘：`150GB`
- 内存：`12GB`
- CPU：`6 核`

#### 推荐

- 磁盘：`180GB - 200GB`
- 内存：`16GB`
- CPU：`6 - 8 核`

## 7. 三套环境合并后的本地配置预算

这里分三种情况：

### 7.1 只安装，不并发运行

即：

- 三套 VM 镜像都保留在本地
- 同一时间只跑一个 benchmark

建议按下面预算准备：

#### 磁盘

- macOS VM：`120GB - 160GB`
- Ubuntu VM：`100GB - 120GB`
- Windows VM：`150GB - 200GB`
- 工具链 / benchmark 代码 / 结果 / 日志 / 额外 snapshot：`50GB - 100GB`

合计：

- **最低建议：`450GB+`**
- **实际推荐：`600GB+`**
- **更稳妥：`1TB SSD`**

#### 内存

因为一次只跑一个：

- **最低建议：`32GB` 宿主机内存**
- **推荐：`64GB` 宿主机内存**

#### CPU

- **最低：8 个有效 CPU 核**
- **推荐：10-12 个以上有效 CPU 核**

### 7.2 两套环境交替调试，偶尔并发

例如：

- 宿主机开一个 VM
- 本地还跑 IDE、浏览器、agent、报告脚本

建议：

- 磁盘：`1TB SSD`
- 内存：`64GB`
- CPU：`12 核以上`

### 7.3 真要多环境并发 benchmark

如果你的目标是：

- macOS / Ubuntu / Windows 多套环境并发跑

那当前这台普通开发机思路就不对了。

建议：

- **内存：`96GB - 128GB`**
- **磁盘：`2TB SSD`**
- **CPU：高性能桌面级或工作站级**

这已经接近小型实验服务器思路，不适合普通个人 Mac 笔记本。

## 8. 当前阶段最务实的预算建议

### 8.1 如果只想先验证 macOSWorld

建议：

- 先不走 AWS
- 先尝试本地 VMware/Fusion 路线

宿主机建议：

- 内存：`32GB` 起
- 更推荐：`64GB`
- 磁盘：至少 `512GB` 可用
- 更推荐：`1TB`

### 8.2 如果未来还要补 Ubuntu

建议宿主机目标配置直接提到：

- **内存：`64GB`**
- **磁盘：`1TB SSD`**

### 8.3 如果未来还想把 Windows 也本地化

建议不要在当前阶段把它当硬目标。

原因：

- Windows 在 Apple Silicon 本地路线不稳定
- 你很可能为兼容性付出大量额外时间

更建议：

- 未来 Windows 用单独 Windows 设备或云环境
- 本地机器重点承担 macOS + Ubuntu

## 9. 建议的资源决策

### 方案 A：低预算起步

目标：

- 先把 `macOSWorld` 跑通

建议配置：

- 宿主机：`32GB RAM + 512GB SSD`
- 本地仅起一个 macOS VM

适合：

- 单 benchmark 接入验证

### 方案 B：中期可持续开发

目标：

- `macOSWorld + OSWorld(Ubuntu)` 都能在本地折腾

建议配置：

- 宿主机：`64GB RAM + 1TB SSD`

适合：

- agent 迭代
- 单环境 benchmark 调试
- 留足 snapshot 和日志空间

### 方案 C：全平台重度实验

目标：

- 三平台都保留环境
- 偶尔并发

建议配置：

- 宿主机：`96GB+ RAM + 2TB SSD`
- 或拆到多台机器

适合：

- 团队化实验
- 持续批量 benchmark

## 10. 最终结论

### 成本层面

- `macOSWorld` 官方 AWS 路线：**贵**
- 最低试水成本就接近 **`$18.70`**
- 认真跑 benchmark 会很快到 **`$40-$50+`**，全语言更贵

### 本地层面

- 最值得本地化的是：
  - `macOSWorld` 的 VMware/Fusion 路线
  - `OSWorld` 的 Ubuntu 路线

- 最不建议当前阶段强上本地的是：
  - `Windows` benchmark on Apple Silicon Mac

### 宿主机采购 / 准备建议

如果目标是未来逐步覆盖 `macOS + Ubuntu`，并为 Windows 预留空间：

- **最低可接受：`32GB RAM + 512GB SSD`**
- **推荐实用档：`64GB RAM + 1TB SSD`**
- **重度实验档：`96GB+ RAM + 2TB SSD`**

一句话版本：

**想省钱，就先本地化 `macOSWorld(Fusion)` 和 `OSWorld(Ubuntu)`；Windows 先别硬塞进当前这台 Apple Silicon Mac。**
