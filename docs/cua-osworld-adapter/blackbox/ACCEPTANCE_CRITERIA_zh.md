# CUA Blackbox 验收标准

日期：2026-05-01

## 1. 验收目的

这份文档定义：

> 方案 B 做到什么程度，才算可以进入下一阶段。

---

## 2. 验收总原则

验收只看三件事：

1. CUA 是否真的在操作 OSWorld VM。
2. OSWorld 是否能稳定完成任务评测。
3. 结果是否可追踪、可复现、可定位失败原因。

---

## 3. 验收分层

## 3.1 必须通过

以下是 hard gate，必须全部通过：

- [ ] 能启动 `CUA` 二进制
- [ ] 能执行一个最小 OSWorld 任务
- [ ] `CUA` 的动作作用在 OSWorld VM，而不是宿主机
- [ ] `screenshot` 能稳定返回
- [ ] `mouse_click` 能稳定生效
- [ ] `clipboard_type` 能稳定输入文本
- [ ] `env.evaluate()` 能正常运行
- [ ] 结果文件能保存

## 3.2 建议通过

以下是 soft gate，建议通过但不作为第一阶段硬门槛：

- [ ] `mouse_drag` 可用
- [ ] `mouse_scroll` 可用
- [ ] `hotkey` 可用
- [ ] 子进程 stderr 可读
- [ ] 任务中断后能清理

---

## 4. 具体验收项

## 4.1 启动验收

验收点：

- `cua run` 能启动
- `cua run --nodeid` 能启动
- OSWorld runner 能拉起 `CUA`

通过标准：

- 不报配置错误
- 不报权限错误
- 不报找不到二进制错误

## 4.2 Bridge 验收

验收点：

- `screenshot` 返回有效图像
- `mouse_click` 触发目标点击
- `clipboard_type` 触发目标输入
- `key_press` / `hotkey` 生效

通过标准：

- 返回 JSON 可解析
- 错误返回明确
- 不污染宿主机

## 4.3 任务执行验收

验收点：

- 至少一个 benchmark task 能完整跑完
- CUA 不会卡死在无限循环
- CUA 能退出并返回结果

通过标准：

- 有 `result.txt`
- 有日志
- 有录屏

## 4.4 评测验收

验收点：

- `env.evaluate()` 能返回分数
- 分数能写回结果目录
- 结果和任务对应关系正确

通过标准：

- 不丢任务 ID
- 不丢 example ID
- 不丢 domain 信息

## 4.5 稳定性验收

验收点：

- 连续跑多个任务不崩
- 异常时能清理进程
- 失败时能定位到工具层、bridge 层或 CUA 层

通过标准：

- 失败日志完整
- 无僵尸进程
- 无重复占用

---

## 5. 验收场景

## 5.1 Smoke Test

场景：

- 单任务
- 单环境
- 低步数

目标：

- 验证链路可通

## 5.2 Functional Test

场景：

- 多个基础 GUI 任务

目标：

- 验证工具映射正确

## 5.3 Regression Test

场景：

- 重复运行同一任务

目标：

- 验证结果一致性
- 验证日志稳定性

---

## 6. 验收输出物

验收完成后，结果目录至少应包含：

- `result.txt`
- `runtime.log`
- `recording.mp4`
- `cua.stdout.log`
- `cua.stderr.log`
- `cua_meta.json`

---

## 7. 不通过的判定

以下任一情况视为不通过：

- `CUA` 仍在操作宿主机
- screenshot 不稳定
- 动作执行无效
- 无法调用 `env.evaluate()`
- 无法定位失败来源
- 无法清理进程

---

## 8. 最终验收结论模板

建议最终记录格式如下：

```text
验收结论：通过 / 不通过
任务范围：...
覆盖场景：...
主要问题：...
后续动作：...
```

