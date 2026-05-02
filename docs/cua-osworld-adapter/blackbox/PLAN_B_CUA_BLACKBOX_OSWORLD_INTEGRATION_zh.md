# 方案 B：CUA 黑盒运行时接入 OSWorld 评测计划

日期：2026-05-01

## 1. 文档目的

这份文档专门细化 **方案 B**：

> 尽量不改 `CUA` 源码，把 `CUA` 作为黑盒二进制 / 黑盒运行时，通过远程工具桥接接入 OSWorld，并完成 benchmark 评测。

这份方案的目标不是把 `CUA` 改造成一个标准 `mm_agents` agent，而是：

- 最大化复用 `CUA` 现有 runtime
- 最小化修改 `CUA` 源码
- 让 `CUA` 的动作真正作用在 OSWorld VM 上
- 最终仍然复用 OSWorld 的任务初始化与 `env.evaluate()` 打分能力

---

## 2. 方案定位

## 2.1 核心思路

方案 B 的控制权放在 `CUA` 一侧，而不是 OSWorld 一侧。

整体链路变成：

```text
OSWorld runner
  -> env.reset(task)
  -> 启动 CUA 二进制 / CUA CLI
  -> CUA 进入自己的 step loop
  -> CUA 通过远程执行桥接请求 screenshot / mouse / keyboard
  -> OSWorld bridge 把这些请求转发到 VM controller
  -> CUA 运行结束
  -> OSWorld env.evaluate()
```

也就是说：

- `CUA` 负责推理、历史、循环、终止逻辑
- OSWorld 负责环境准备、VM 控制、最终评测

## 2.2 为什么叫“黑盒”

这里说的黑盒有两层含义：

1. `CUA` 尽量作为现成产物运行
2. OSWorld 不尝试拆解 `CUA` 内部的 `predict()` / `tool.execute()` / `brain` / `doneGate`

我们只关心：

- 如何启动它
- 如何让它操作的是 benchmark VM
- 如何收集它的产物
- 如何在结束后调用 OSWorld evaluator

---

## 3. 为什么方案 B 更适合“少改 CUA”

## 3.1 当前 CUA 的真实形态

当前 `CUA` 不是一个现成 Python SDK，而是一个完整 TypeScript runtime：

- 有自己的 `run()` 主循环
- 有自己的 `tool registry`
- 有自己的 `screenshot / mouse / keyboard / shell / officecli`
- 有自己的 `brain` / `doneGate`
- 有自己的 CLI 与 HTTP 服务模式

也就是说，当前 `CUA` 更像：

```text
完整 Agent Runtime
```

而不是：

```text
一个单步可调用的 Python agent class
```

## 3.2 方案 A 的隐性代价

如果走方案 A，把 `CUA` 包成 `mm_agents/cua/agent.py`，虽然看起来是“只在 OSWorld 侧写 adapter”，但实际往往会演变成：

- 在 Python 里重写一套 prompt 组装
- 重写一套 response parse
- 重写一套 action schema 映射
- 重写一套历史管理

最后很容易变成：

> 做了一个 “CUA-like adapter”，而不是在跑原生 CUA。

## 3.3 方案 B 的复用点

方案 B 可以直接复用 `CUA` 的这些现成能力：

- CLI 入口
- `run()` 主循环
- screenshot-based planning
- action schema
- history / brain / doneGate / 记录产物
- `--nodeid` 远程执行模式

因此，如果你的优先级是“尽量不改 `CUA` 源码”，方案 B 更匹配。

---

## 4. 方案 B 的边界

## 4.1 第一阶段要做什么

第一阶段只做：

- Ubuntu benchmark
- screenshot 驱动
- GUI 动作远程转发到 OSWorld VM
- `CUA` 能完整跑完一条 OSWorld task
- OSWorld 能调用 `env.evaluate()` 给出分数

## 4.2 第一阶段不做什么

第一阶段不做：

- 把 `CUA` 接成标准 `mm_agents` agent
- 多平台统一接入
- 完整保留所有 `shell_exec / officecli / wait_for_user` 语义
- 完整复用 OSWorld 标准 `traj.jsonl` 逐步结构
- 让 `CUA` 与 OSWorld 日志体系完全统一

## 4.3 关键原则

第一阶段要坚持两个原则：

1. 不让 `CUA` 操作宿主机
2. 不为了“形式统一”去重写 `CUA` 核心 loop

---

## 5. 现有 CUA 能力中哪些可以直接复用

## 5.1 可直接复用

- 二进制打包能力
- `cua run`
- `cua serve`
- `cua exec`
- `--nodeid` 远程工具模式
- 现有 action schema
- 现有 screenshot / mouse / keyboard 抽象

## 5.2 最值得复用的是哪一层

最值得复用的是：

```text
CUA CLI + CUA run loop + openclaw-style remote tool protocol
```

而不是：

```text
CUA 本地 screenshot / 本地 mouse / 本地 keyboard 实现
```

原因很简单：

- 本地工具默认打宿主机
- benchmark 要打 VM
- 但是远程工具调用协议已经存在

## 5.3 为什么不优先用 `cua serve`

`cua serve` 虽然可用，但它暴露的是：

- HTTP SSE 任务执行入口

它本质仍然是完整 run loop 服务化，不是“每步返回动作”的 agent API。

所以第一阶段用它并不会降低接入复杂度，反而会多一层服务管理。

因此更推荐：

- 直接启动 `cua` 二进制的 `run` 命令
- 配 `--nodeid`
- 从 OSWorld runner 侧监管整个子进程

---

## 6. 总体架构

## 6.1 逻辑架构

```text
OSWorld Runner
  |
  | 1. env.reset(task)
  v
DesktopEnv / PythonController / VM Server
  ^
  | 2. bridge 将远程调用转成 controller 操作
  |
OSWorld OpenClaw-Compatible Bridge
  ^
  | 3. CUA 远程工具调用
  |
CUA Binary / CUA CLI (run --nodeid ...)
```

## 6.2 职责拆分

### OSWorld Runner 负责

- 加载 task
- 创建 DesktopEnv
- reset benchmark VM
- 启动 bridge
- 启动 `cua` 子进程
- 等待其完成
- 收集产物
- 调用 `env.evaluate()`

### Bridge 负责

- 接收 `CUA` 发来的远程工具请求
- 将请求翻译成 OSWorld 可执行动作
- 回传 screenshot / tool result / error

### CUA 负责

- 观察 screenshot
- 决定下一步 action
- 调用远程工具
- 管理自己的运行循环
- 在成功/失败时退出

---

## 7. Bridge 层设计

## 7.1 设计目标

bridge 的目标不是重做一个 agent，而是：

> 实现一个 “OpenClaw-compatible executor for OSWorld VM”

也就是对 `CUA` 来说，它看到的是“远程设备工具调用接口”；  
对 OSWorld 来说，它看到的是“把远程工具请求翻译成 VM controller 调用的代理层”。

## 7.2 Bridge 的最小能力集

第一阶段建议只支持这些 tool：

- `screenshot`
- `mouse_click`
- `mouse_right_click`
- `mouse_double_click`
- `mouse_move`
- `mouse_scroll`
- `mouse_drag`
- `press_mouse`
- `release_mouse`
- `clipboard_type`
- `keyboard_type`
- `key_press`
- `hotkey`
- `get_screen_size`
- `wait`
- `done`

## 7.3 第一阶段建议禁用的能力

以下能力建议直接返回“不支持”或在 prompt 层不暴露：

- `shell_exec`
- `shell_sh`
- `officecli`
- `record_info`
- `read_record`
- `wait_for_user`
- `osascript_exec`

原因：

- 这些能力不是 benchmark MVP 必需
- 有些只适合本地桌面
- 有些需要额外状态管理
- 有些会把问题扩展成“通用远程 agent runtime”工程

## 7.4 action 到 OSWorld 执行的映射

bridge 层不一定必须调用 `env.step()`，更稳的做法是直接调用 `env.controller`：

- screenshot：`env.controller.get_screenshot()`
- pyautogui 字符串动作：`env.controller.execute_python_command(...)`
- bash / python script：必要时调用 `run_bash_script` / `run_python_script`

但第一阶段建议统一策略：

- 所有 GUI tool 最终都编译为 guest VM 内执行的 `pyautogui` Python 代码

这样行为会更一致。

## 7.5 screenshot 返回格式

bridge 需要支持：

- base64 返回
- 或本地路径 + bridge 侧读取再上传

第一阶段建议：

- 统一直接返回 base64 或内存图片字节
- 不先引入附件上传系统

这样最容易打通。

---

## 8. Runner 设计

## 8.1 为什么不能直接复用标准 `run_single_example(...)`

标准 `run_single_example(...)` 假设：

- runner 每轮调用 `agent.predict(...)`
- runner 自己调用 `env.step(...)`

方案 B 不满足这个前提，因为：

- `CUA` 自己持有 step loop
- runner 只负责启动和等待它

所以第一阶段应该新增一条 blackbox runner。

## 8.2 推荐新增文件

建议新增：

```text
scripts/python/run_multienv_cua_blackbox.py
lib_run_single.py            # 新增 run_single_example_cua_blackbox()
osworld_cua_bridge/
  __init__.py
  executor.py
  protocol.py
  translator.py
```

如果希望先最小实现，也可以：

```text
scripts/python/run_multienv_cua_blackbox.py
lib_run_single.py
mm_agents/cua_blackbox/
  bridge.py
```

但从可维护性看，建议把 bridge 独立成目录。

## 8.3 `run_single_example_cua_blackbox()` 职责

建议职责如下：

1. `env.reset(task_config=example)`
2. 启动 bridge，上下文绑定当前 `env`
3. 生成本次 run 的临时目录
4. 启动 `cua` 二进制子进程
5. 等待其退出，收集 stdout/stderr/run artifacts
6. 根据退出状态写 result metadata
7. 调 `env.evaluate()`
8. 保存 OSWorld 风格结果目录

## 8.4 输入参数建议

需要至少包括：

- `path_to_cua_binary`
- `cua_config_path`
- `cua_runs_dir`
- `bridge_endpoint` 或 `bridge_node_id`
- `max_steps`
- `model/provider/base_url/api_key` 覆盖项

## 8.5 结果产物建议

结果目录建议包含两类内容：

### OSWorld 侧

- `result.txt`
- `runtime.log`
- `recording.mp4`
- `osworld_meta.json`

### CUA 侧

- `cua.stdout.log`
- `cua.stderr.log`
- `cua_run_dir.txt`
- `cua_steps.json`
- `cua_steps.jsonl`

这样可以避免一开始就强行把两边日志揉成一种格式。

---

## 9. CUA 子进程启动设计

## 9.1 建议的调用形态

建议由 OSWorld runner 启动：

```bash
cua run "<instruction>" \
  --nodeid osworld-node \
  --target-os linux \
  --target-screen 1920x1080 \
  --max-steps <n> \
  --config <path>
```

## 9.2 为什么要显式传 target-screen

OSWorld benchmark 的 screen size 是确定的。  
如果不显式传：

- 远程坐标映射可能依赖自动检测
- 自动检测链路更长
- 第一阶段调试成本更高

所以推荐：

- 先在 runner 里把 benchmark screen size 明确传给 `CUA`

## 9.3 为什么建议优先用二进制而不是 `node dist/cli/bin.js`

优先用二进制的原因：

- 更符合“黑盒产物”目标
- 运行依赖更少
- 后面迁移到其他环境更容易

但开发期可以先用：

```bash
node dist/cli/bin.js run ...
```

先验证桥接是否通，再切换到二进制。

---

## 10. Bridge 协议建议

## 10.1 协议原则

协议不必追求通用，只要做到：

- 能支撑 `CUA --nodeid` 的最小工具集合
- 错误可观测
- screenshot 能稳定返回

## 10.2 请求字段建议

最小请求结构：

```json
{
  "runId": "run-123",
  "reqId": "tool-001",
  "tool": "mouse_click",
  "args": {
    "x": 100,
    "y": 200
  }
}
```

## 10.3 响应字段建议

### 成功

```json
{
  "ok": true,
  "payload": {
    "type": "tool_result",
    "output": "clicked at (100, 200)"
  }
}
```

### 截图

```json
{
  "ok": true,
  "payload": {
    "type": "image_base64",
    "mime": "image/png",
    "width": 1920,
    "height": 1080,
    "imageBase64": "..."
  }
}
```

### 失败

```json
{
  "ok": false,
  "error": {
    "code": "EXEC_FAILED",
    "message": "tool execution failed"
  }
}
```

## 10.4 是否必须完全兼容 openclaw

第一阶段建议：

- 外部格式尽量兼容
- 内部实现不需要真的引入 openclaw

也就是说：

- `CUA` 看到的是兼容接口
- OSWorld 内部自己实现一个轻量 executor 即可

---

## 11. 与 OSWorld 现有能力的结合方式

## 11.1 环境准备仍由 OSWorld 完成

这部分完全不需要改：

- provider
- snapshot revert
- task setup
- proxy setup
- evaluator config

也就是说，仍然复用：

- `DesktopEnv.reset(task_config=example)`

## 11.2 最终评分仍由 OSWorld 完成

这部分也不需要改：

- `env.evaluate()`

这保证 benchmark 结果仍然可比。

## 11.3 录屏和初始观测仍由 OSWorld 管

建议保留：

- `env.controller.start_recording()`
- `env.controller.end_recording()`

这样即使 `CUA` 自己也记录 step artifacts，OSWorld 这边仍然有统一视频结果。

---

## 12. 实施分阶段清单

## Phase 0：确认先决条件

1. `CUA` 能本地编译或打二进制
2. `CUA run --nodeid ...` 在独立环境下可运行
3. OSWorld benchmark 环境本身可正常 reset / screenshot / pyautogui
4. 明确第一阶段只跑 Ubuntu screenshot tasks

## Phase 1：Bridge MVP

1. 新建 OSWorld bridge 目录
2. 实现 screenshot 请求
3. 实现 click / type / hotkey / scroll / wait
4. 跑一个最小 smoke task
5. 确认 `CUA` 不再误操作宿主机

## Phase 2：Blackbox Runner MVP

1. 新增 `run_single_example_cua_blackbox()`
2. 新增 `run_multienv_cua_blackbox.py`
3. 启动 `cua` 子进程
4. 收集 stdout/stderr 和 CUA run 目录
5. 接上 `env.evaluate()`

## Phase 3：批量评测准备

1. 统一结果目录结构
2. 统一日志命名
3. 增加失败分类
4. 增加超时 / 中断 / 子进程清理
5. 在小规模 tasks 上验证稳定性

## Phase 4：增强与收敛

1. 已支持 `app_open`
2. 已支持 `get_cursor_position`
3. 决定是否支持 `wait_for_user`
4. 决定是否把 blackbox 结果再转成更标准的 OSWorld `traj.jsonl`

---

## 13. 风险清单

## 13.1 最大风险：远程工具语义不完全一致

虽然 `CUA` 已经有远程调用能力，但 benchmark VM 的行为和普通桌面可能不同：

- 剪贴板
- 双击节奏
- 滚动尺度
- 焦点切换

这会导致“同样的 CUA 决策，在 benchmark VM 上表现不同”。

## 13.2 第二个风险：日志和调试链路分裂

方案 B 天生是两套系统：

- OSWorld 日志
- CUA 日志

所以必须从一开始就约定好：

- runId
- example_id
- 结果目录结构
- stdout/stderr 保存方式

## 13.3 第三个风险：过早支持太多工具

如果第一阶段就支持：

- shell
- officecli
- wait_for_user
- records

项目会迅速从“benchmark 接入”变成“通用远程 agent runtime”。

所以第一阶段一定要收紧工具面。

---

## 14. 与方案 A 的关系

方案 B 不是替代方案 A 的永久答案，而是：

> 一个更适合“少改 CUA、先快速验证 benchmark 接入”的路径。

推荐策略是：

1. 先用方案 B 验证：
   - `CUA` 是否能在 OSWorld VM 上真实工作
   - benchmark 任务是否能跑通
   - 哪类工具语义最容易出问题
2. 如果后续需要长期维护，再决定是否收敛到方案 A 的标准 `mm_agents` adapter

也就是说：

- 方案 B 更适合 MVP / 原生保真验证
- 方案 A 更适合长期标准化接入

---

## 15. 当前推荐结论

如果当前目标是：

- 尽量不改 `CUA` 源码
- 保留原生 `CUA` runtime
- 先做接入验证和 benchmark 可跑通

那么推荐顺序是：

1. 先做方案 B 的 bridge MVP
2. 再做 blackbox runner
3. 先用少量 Ubuntu tasks 做 smoke test
4. 跑通后再决定是否继续演进到方案 A

---

## 16. 下一步代码实施建议

下一步开始写代码时，建议严格按这个顺序：

1. 先实现 bridge 的 `screenshot`
2. 再实现 `mouse_click`
3. 再实现 `clipboard_type`
4. 然后实现 blackbox runner 最小闭环
5. 最后才补 `scroll / drag / hotkey / wait / done`

不要一上来同时写：

- 全量工具
- 多环境 runner
- 完整结果合并

先把单任务、单环境、单进程跑通才是正确顺序。
