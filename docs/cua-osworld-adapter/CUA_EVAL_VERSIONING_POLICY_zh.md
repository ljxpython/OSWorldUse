# CUA 版本兼容与评测策略

日期：2026-05-01

## 1. 目的

这份文档定义一件事：

> 当 `CUA` 未来更新后，OSWorld 应该怎样继续评测，才能尽量不改 `CUA` 本体，同时保证历史结果还能复现、还能比较。

核心原则很简单：

- `OSWorld` 冻结评测面
- `CUA` 只在协议内升级
- 不能把版本变化直接混进 benchmark 规则

---

## 2. 必须冻结的部分

以下内容一旦进入正式评测，就应视为稳定面：

- `OSWorld` 仓库版本或 commit hash
- task set 版本
- evaluator / metric 规则
- env 配置
- observation contract
- action contract
- 结果目录结构
- 兼容层协议版本

其中最重要的是两条：

1. `OSWorld` 侧动作契约不能频繁变
2. `CUA` 和 `OSWorld` 之间的桥接协议要有版本号

---

## 3. 允许变化的部分

以下内容可以随 `CUA` 版本升级而变化：

- 模型本体
- prompt
- reasoning 策略
- 内部工具实现
- 历史管理方式
- 解析器细节
- `CUA` 内部的执行 loop

但有一个前提：

> 只要最终输出仍能被当前版本 adapter 归一化成同一个 OSWorld action contract，就不需要改 benchmark 主链路。

---

## 4. 评测分层

未来每次 `CUA` 更新后，建议按三层做评测。

### 4.1 兼容性 smoke test

先只验证最小闭环：

- 能启动
- 能读取 screenshot
- 能输出动作
- 动作能落到 OSWorld VM
- 能正常结束

这一步不看分数，只看链路是否通。

### 4.2 回归评测

在同一套固定 benchmark 上跑一遍：

- 同一 task set
- 同一 env 配置
- 同一 evaluator
- 同一 adapter 版本

这一步用于看版本升级是否带来真实行为变化。

### 4.3 横向对比

只比较满足下面条件的结果：

- 同一 benchmark release
- 同一 adapter major version
- 同一评测配置

如果这些条件不一致，就不能把分数直接混在一起。

---

## 5. 版本分层

建议把版本分成四层记录。

### 5.1 `osworld_version`

记录 OSWorld 的仓库版本或 commit。

### 5.2 `adapter_version`

记录 OSWorld 侧适配层版本。

这个版本最关键，因为它决定：

- CUA 输出如何被归一化
- 动作如何落到 `env.step()`
- 哪些能力被屏蔽

### 5.3 `cua_version`

记录 CUA 自身版本：

- commit hash
- tag
- binary 版本号
- model name

### 5.4 `eval_profile`

记录评测配置：

- task set
- screen size
- step limit
- prompt/version template
- 运行参数

---

## 6. 推荐评测流程

当 `CUA` 版本升级时，建议按下面顺序跑。

1. 先跑兼容性 smoke test。
2. 再跑固定的小样本回归集。
3. 如果通过，再跑完整 benchmark。
4. 结果写入新的版本目录，不覆盖旧结果。
5. 只在同一版本族内比较分数。

这套顺序的目标不是“跑得最多”，而是“先确认没破坏协议，再看分数变化”。

---

## 7. 协议变更规则

### 7.1 只改 CUA，不改协议

如果 CUA 只是换模型、换 prompt、换内部工具实现，但输出协议不变：

- 不改 OSWorld 主链路
- 不改 benchmark 规则
- 只新增一个 `cua_version`

### 7.2 输出变了，但 adapter 可吸收

如果 CUA 输出格式变了，但 adapter 还能稳定归一化：

- 只升级 `adapter_version`
- 保留旧 adapter
- 不覆盖历史结果

### 7.3 需要新能力

如果 CUA 新版本真的引入了旧协议表达不了的能力：

- 不直接改旧 benchmark
- 新增可选 capability 版本
- 仍保留旧评测路径

---

## 8. 结果目录要求

每次评测结果都应记录这些元数据：

```json
{
  "osworld_version": "commit-or-tag",
  "adapter_version": "v1",
  "cua_version": "commit-or-tag",
  "eval_profile": "ubuntu-screenshot-pyautogui-v1",
  "task_set": "evaluation_examples/test_all.json",
  "screen_size": [1920, 1080]
}
```

建议额外保存：

- `adapter_config_hash`
- `prompt_version`
- `bridge_protocol_version`
- `run_timestamp`

---

## 9. 比较规则

建议以后只允许下面两种比较：

1. 同一 `adapter_version` 下，不同 `cua_version` 的比较
2. 同一 `cua_version` 下，不同 `adapter_version` 的兼容性回归

不建议比较：

- 不同 benchmark release 的分数
- 不同 task set 的分数
- 不同评测配置下的分数
- 没有版本记录的分数

---

## 10. 最终结论

以后 `CUA` 升级时，评测不应该重新定义 benchmark。

正确做法是：

- benchmark 面冻结
- adapter 面版本化
- `CUA` 面只做可替换实现
- 历史结果按版本族保存

这样才能做到：

1. 新版 `CUA` 可以继续评测
2. 旧版结果还能复现
3. 分数变化能解释
4. `CUA` 本体尽量少改
