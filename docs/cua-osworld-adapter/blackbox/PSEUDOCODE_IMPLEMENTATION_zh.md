# CUA Blackbox 伪代码实现草案

日期：2026-05-01

## 1. 目标

这份文档只做一件事：

> 用接近代码的方式描述方案 B 的完整执行链路。

它的作用是把“怎么跑”说清楚，方便后续按模块写代码。

---

## 2. 总体流程

```text
for each task example:
  env.reset(task_config)
  bridge.bind(env)
  start recording
  launch cua subprocess
  wait cua finish
  collect logs/artifacts
  env.evaluate()
  save result
```

---

## 3. 组件划分

## 3.1 Blackbox Runner

职责：

- 读取 benchmark task
- 创建 `DesktopEnv`
- 启动 `CUA`
- 等待任务结束
- 汇总产物

## 3.2 Bridge Executor

职责：

- 接收 CUA 的远程工具请求
- 翻译为 OSWorld controller 调用
- 返回 JSON 响应

## 3.3 Tool Translator

职责：

- 把 CUA 工具参数映射成 OSWorld 可执行动作
- 统一坐标、文本、快捷键和等待语义

---

## 4. 伪代码：Runner

```python
def run_single_example_cua_blackbox(example, env, args, result_dir):
    env.reset(task_config=example)
    env.controller.start_recording()

    bridge = BridgeExecutor(env=env, result_dir=result_dir)
    bridge.start()

    cua_proc = launch_cua(
        instruction=example["instruction"],
        run_id=bridge.run_id,
        target_os="linux",
        target_screen=(args.screen_width, args.screen_height),
        model=args.model,
        config_path=args.cua_config_path,
    )

    cua_stdout, cua_stderr, exit_code = cua_proc.wait_and_collect()

    bridge.stop()
    env.controller.end_recording(join(result_dir, "recording.mp4"))

    result = env.evaluate()
    save_result(result_dir, result, cua_stdout, cua_stderr, exit_code)
    return result
```

---

## 5. 伪代码：Bridge

```python
class BridgeExecutor:
    def __init__(self, env, result_dir):
        self.env = env
        self.result_dir = result_dir
        self.run_id = new_run_id()
        self.busy = False

    def handle_request(self, req):
        assert req.runId == self.run_id
        assert req.reqId
        assert req.tool
        assert isinstance(req.args, dict)

        if req.tool == "screenshot":
            return self._screenshot(req)
        if req.tool in ["mouse_click", "mouse_right_click", "mouse_double_click"]:
            return self._mouse_click(req)
        if req.tool == "mouse_move":
            return self._mouse_move(req)
        if req.tool == "mouse_drag":
            return self._mouse_drag(req)
        if req.tool == "mouse_scroll":
            return self._mouse_scroll(req)
        if req.tool in ["clipboard_type", "keyboard_type"]:
            return self._type_text(req)
        if req.tool in ["key_press", "hotkey"]:
            return self._keyboard(req)
        if req.tool == "wait":
            return self._wait(req)
        if req.tool == "get_screen_size":
            return self._screen_size(req)
        if req.tool == "done":
            return self._done(req)

        return error("UNSUPPORTED_TOOL", req.tool)
```

---

## 6. 伪代码：工具翻译

```python
def translate_to_pyautogui(tool, args):
    if tool == "mouse_click":
        x, y = resolve_coords(args)
        button = args.get("button", "left")
        return f"pyautogui.moveTo({x}, {y}); pyautogui.click(button='{button}')"

    if tool == "mouse_double_click":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y}); pyautogui.doubleClick()"

    if tool == "mouse_right_click":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y}); pyautogui.click(button='right')"

    if tool == "mouse_move":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y})"

    if tool == "mouse_drag":
        fx, fy, tx, ty = resolve_drag_coords(args)
        return f"pyautogui.moveTo({fx}, {fy}); pyautogui.dragTo({tx}, {ty}, duration=0.5, button='left')"

    if tool == "mouse_scroll":
        clicks = int(args["clicks"])
        return f"pyautogui.scroll({clicks})"

    if tool in ["clipboard_type", "keyboard_type"]:
        text = escape_py_string(args["text"])
        return f"pyautogui.write({text})"

    if tool == "key_press":
        return f"pyautogui.press('{args['key']}')"

    if tool == "hotkey":
        keys = ",".join([f"'{k}'" for k in args["keys"]])
        return f"pyautogui.hotkey({keys})"

    if tool == "wait":
        ms = int(args.get("ms", 1000))
        return f"pyautogui.sleep({ms / 1000.0})"

    return None
```

---

## 7. 伪代码：结果保存

```python
def save_result(result_dir, score, stdout, stderr, exit_code):
    write_text(join(result_dir, "result.txt"), str(score))
    write_text(join(result_dir, "cua.stdout.log"), stdout)
    write_text(join(result_dir, "cua.stderr.log"), stderr)
    write_json(join(result_dir, "cua_meta.json"), {
        "exit_code": exit_code,
        "score": score,
    })
```

---

## 8. 关键约束

1. 不让 `CUA` 操作宿主机。
2. 不把 `CUA` 拆成标准 `mm_agents` agent。
3. 第一阶段只保留最小工具集。
4. 所有动作最终都必须落到 OSWorld VM。

