# CUA 冻结字段表

日期：2026-05-01

## 1. 目的

这份表只回答一件事：

> 在 `CUA` 参与 OSWorld 评测时，哪些字段必须冻结，哪些字段可以变，但必须通过版本号显式记录。

这里的“冻结”不是说永远不能改，而是说：

- 在同一个 `eval_profile` 内不能偷偷改
- 一旦改了，就必须升版本、重跑回归、保留旧结果

---

## 2. 冻结原则

1. 评测面冻结，代码实现可替换。
2. 只要影响分数可比性，就必须版本化。
3. 不覆盖旧结果，只新增新版本目录。
4. 任何破坏性变更都必须带协议版本变化。

---

## 3. 冻结字段表

| 层级 | 冻结字段 | 示例 | 允许变化方式 | 说明 |
|---|---|---|---|---|
| Benchmark 身份 | `task_set` | `evaluation_examples/test_all.json` | 新建 `eval_profile` | 任务集一变，分数就不能和旧结果直接混比。 |
| Benchmark 身份 | `evaluator` | metric / result getter | 新建 `eval_profile` | 评分规则变更必须显式记录。 |
| 环境配置 | `os_type` | `Ubuntu` | 新建 `eval_profile` | 第一阶段只允许 `Ubuntu`。 |
| 环境配置 | `provider_name` | `vmware` / `aws` | 新建 `eval_profile` | provider 变化会影响环境行为。 |
| 环境配置 | `screen_size` | `1920x1080` | 新建 `eval_profile` | 坐标、截图和动作映射都依赖它。 |
| 环境配置 | `action_space` | `pyautogui` | 新建 `eval_profile` | 第一阶段只做 `pyautogui`。 |
| 环境配置 | `observation_type` | `screenshot` | 新建 `eval_profile` | 观测形态变了，adapter 也要变。 |
| 环境配置 | `max_steps` | `15` | 新建 `eval_profile` | 步数限制属于评测条件。 |
| 环境配置 | `sleep_after_execution` | `0.0` | 新建 `eval_profile` | 会影响动作可见性和稳定性。 |
| Adapter 协议 | `bridge_protocol_version` | `bridge-v1` | 新增协议版本 | 远程工具请求/响应格式必须版本化。 |
| Adapter 协议 | `action_schema` | `WAIT/DONE/FAIL/pyautogui` | 新增 adapter 版本 | 任何动作集合变化都要记录。 |
| Adapter 协议 | `required_input` | `instruction + screenshot` | 新增 adapter 版本 | 输入契约一旦变就不是同一条链路。 |
| Adapter 协议 | `required_output` | `response + actions + debug` | 新增 adapter 版本 | 返回字段要稳定。 |
| 结果结构 | `result_dir` 结构 | `results/<profile>/<version>/...` | 新建目录 | 旧结果不能被覆盖。 |
| 结果结构 | `artifact list` | `traj.jsonl`, `result.txt`, `recording.mp4` | 新增版本目录 | 产物命名要一致。 |
| 版本元数据 | `osworld_version` | commit hash | 新版本记录 | 便于复现。 |
| 版本元数据 | `cua_version` | commit / binary / tag | 新版本记录 | 便于比较 `CUA` 升级前后差异。 |
| 版本元数据 | `adapter_version` | `v1`, `v2` | 新版本记录 | 适配层改动必须显式可见。 |
| 版本元数据 | `eval_profile` | `ubuntu-screenshot-pyautogui-v1` | 新版本 profile | 用来锁定一次可比的评测配置。 |

---

## 4. 允许变化但必须版本化的内容

以下内容可以变化，但不能默默变化：

- `CUA` 模型本体
- prompt 文本
- reasoning 策略
- 内部 tool 实现
- 历史管理
- action 解析细节
- 任务调度策略

只要其中任意一项变化，就至少要更新下面之一：

- `cua_version`
- `adapter_version`
- `eval_profile`

---

## 5. 建议的版本规则

### 5.1 `eval_profile`

一个 `eval_profile` 应该同时锁定：

- OSWorld 版本
- task set
- provider / OS / screen / action / observation
- max steps
- adapter protocol

示例：

```text
ubuntu-screenshot-pyautogui-v1
```

### 5.2 `adapter_version`

如果只是兼容同一输出协议内的小修小补：

- 走 patch / minor

如果输出格式或协议断裂：

- 走 major
- 保留旧版本 adapter

### 5.3 `cua_version`

`CUA` 自身只要发生以下变化，就要改版本号：

- 模型替换
- prompt 体系变化
- 输出格式变化
- loop 语义变化

---

## 6. 结果记录最小字段

每次评测结果都至少记录：

```json
{
  "osworld_version": "commit-hash",
  "cua_version": "commit-or-binary-version",
  "adapter_version": "v1",
  "bridge_protocol_version": "bridge-v1",
  "eval_profile": "ubuntu-screenshot-pyautogui-v1"
}
```

建议额外记录：

- `prompt_version`
- `task_set`
- `screen_size`
- `result_dir`
- `run_id`

