# CUA Blackbox Bridge 协议设计

日期：2026-05-01

## 1. 目的

这份文档只定义一件事：

> OSWorld 侧的 bridge 如何给 CUA 提供“远程设备工具”能力。

目标不是复刻 openclaw 全量协议，而是定义一个 **足够稳定、足够小、足够可实现** 的最小协议层。

---

## 2. 设计原则

1. 请求必须幂等可追踪。
2. 响应必须可机器解析。
3. screenshot 必须稳定返回。
4. 第一阶段只支持 benchmark MVP 必需工具。
5. 所有工具最终都要落到 OSWorld VM，而不是宿主机。

---

## 3. 角色划分

## 3.1 CUA 侧

CUA 负责：

- 决策下一步动作
- 组织自己的 run loop
- 调用远程工具
- 处理返回结果

## 3.2 OSWorld bridge 侧

bridge 负责：

- 接收远程工具请求
- 校验 runId / reqId / tool / args
- 调用 OSWorld controller
- 返回标准 JSON 响应

## 3.3 OSWorld env 侧

env 负责：

- reset
- 观测采集
- action 执行
- 最终评分

---

## 4. 请求协议

## 4.1 最小请求结构

```json
{
  "runId": "run-123",
  "reqId": "step-001",
  "tool": "mouse_click",
  "args": {
    "x": 100,
    "y": 200
  }
}
```

## 4.2 字段说明

- `runId`
  - 一次任务运行的唯一 ID
  - 用于串联日志、截图、错误和输出
- `reqId`
  - 单次工具调用 ID
  - 用于调试、幂等和追踪
- `tool`
  - 工具名，不带前缀
- `args`
  - 工具参数对象

## 4.3 校验规则

- `runId` 必填
- `reqId` 必填
- `tool` 必填
- `args` 必须是对象
- 未知工具必须返回明确错误

---

## 5. 响应协议

## 5.1 工具成功

```json
{
  "ok": true,
  "payload": {
    "type": "tool_result",
    "output": "clicked at (100, 200)"
  }
}
```

## 5.2 截图成功

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

## 5.3 工具失败

```json
{
  "ok": false,
  "error": {
    "code": "EXEC_FAILED",
    "message": "tool execution failed",
    "details": {}
  }
}
```

## 5.4 约束

- 成功响应必须带 `ok: true`
- 失败响应必须带 `ok: false`
- 错误信息必须短、明确、可读

---

## 6. 支持工具

## 6.1 第一阶段支持

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
- `wait`
- `app_open`
- `get_screen_size`
- `done`

## 6.2 第一阶段禁用

- `shell_exec`
- `shell_sh`
- `officecli`
- `record_info`
- `read_record`
- `wait_for_user`
- `osascript_exec`
- `get_cursor_position`

---

## 7. 工具映射

## 7.1 screenshot

输入：

```json
{"runId":"r1","reqId":"t1","tool":"screenshot","args":{}}
```

输出：

- 当前屏幕截图
- 统一使用 PNG

## 7.2 mouse_click / mouse_right_click / mouse_double_click / mouse_move

要求支持：

- `x/y`
- `bbox`
- `bbox_format`

规则：

- 优先使用 `x/y`
- 没有 `x/y` 时再解析 `bbox`
- `bbox` 统一换算成中心点

## 7.3 mouse_drag

输入坐标格式：

- `fromX/fromY/toX/toY`
- 或 `from_bbox/to_bbox`

## 7.4 mouse_scroll

输入：

- `clicks`
- 可选 `x/y`
- 可选 `bbox`

## 7.5 clipboard_type / keyboard_type

建议优先把文本输入统一走：

- 剪贴板粘贴

如果 clipboard 不稳定，再降级为键盘输入。

## 7.6 key_press / hotkey

- `key_press`
  - 单键
- `hotkey`
  - 键组合数组

## 7.7 wait

- 输入 `ms`
- 默认 1000
- 必须是非负整数

## 7.8 done

输入：

```json
{"reason":"task completed"}
```

要求：

- 只作为终止信号
- 不执行 GUI 操作

---

## 8. 错误码建议

- `BAD_REQUEST`
- `UNKNOWN_TOOL`
- `EXEC_FAILED`
- `INVALID_ARGS`
- `UNSUPPORTED_TOOL`
- `TIMEOUT`
- `ENV_NOT_READY`
- `BUSY`

---

## 9. 日志建议

bridge 至少要记录：

- `runId`
- `reqId`
- `tool`
- `args`
- `startTs`
- `endTs`
- `status`
- `error`

建议每次请求都能定位到：

- 这一次调用是谁发的
- 最后落到了哪一个 VM action
- 失败发生在哪一层

---

## 10. 与 OSWorld 的结合方式

bridge 最终应该调用的不是 OSWorld 的模型层，而是：

- `DesktopEnv`
- `PythonController`
- `SetupController`

也就是说：

- 负责执行的对象是 OSWorld env
- 负责观测的对象也是 OSWorld env
- bridge 只是薄薄的一层适配

---

## 11. 最小验收标准

只要满足以下条件，bridge 就算第一阶段可用：

1. 能返回 screenshot
2. 能执行 click
3. 能执行 text input
4. 能返回明确错误
5. 能稳定服务同一个 runId
6. 能让 CUA 真正操作 OSWorld VM
