from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.reporting import (  # noqa: E402
    blackbox_result_root,
    build_blackbox_summary,
    load_args_json,
    load_task_set_file,
    summary_metadata_from_args,
)
from scripts.python.cua_case_resolver import resolve_case_path  # noqa: E402


DEFAULT_CASES_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "examples")
DEFAULT_CUA_CASES_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "cua_blackbox", "cases")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def safe_read_json(path: str) -> Any | None:
    try:
        return read_json(path)
    except Exception:
        return None


def safe_read_text(path: str) -> str:
    try:
        return read_text(path)
    except Exception:
        return ""


def compact_json(data: Any, limit: int = 220) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if len(raw) <= limit:
        return raw
    return raw[: limit - 3] + "..."


def truncate(text: str, limit: int = 80) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def score_label(score: float | None) -> str:
    if score is None:
        return "未产出结果"
    if score >= 1.0:
        return "通过"
    if score > 0:
        return "部分完成"
    return "未通过"


def format_rule_summary(case_payload: dict[str, Any]) -> str:
    evaluator = case_payload.get("evaluator") or {}
    func_name = evaluator.get("func") or "unknown"
    result_meta = compact_json(evaluator.get("result") or {}, limit=120)
    expected_meta = compact_json(evaluator.get("expected") or {}, limit=160)
    return f"评测函数={func_name}；实际读取={result_meta}；期望={expected_meta}"


def describe_config_step(item: dict[str, Any]) -> str:
    step_type = str(item.get("type") or "unknown")
    parameters = item.get("parameters") or {}
    if step_type == "launch":
        command = parameters.get("command") or []
        return f"launch {' '.join(map(str, command))}".strip()
    if step_type == "chrome_open_tabs":
        urls = parameters.get("urls_to_open") or []
        return f"chrome_open_tabs {', '.join(map(str, urls[:3]))}"
    if step_type == "chrome_close_tabs":
        return f"chrome_close_tabs {compact_json(parameters, limit=120)}"
    if step_type == "sleep":
        return f"sleep {parameters.get('seconds')}s"
    if step_type == "activate_window":
        return f"activate_window {parameters.get('window_name') or parameters.get('window') or compact_json(parameters)}"
    return f"{step_type} {compact_json(parameters, limit=120)}".strip()


def collect_case_paths(domain: str, task_id: str) -> dict[str, str]:
    case_json = resolve_case_path(
        domain,
        task_id,
        cases_dir=DEFAULT_CASES_DIR,
        cua_cases_dir=DEFAULT_CUA_CASES_DIR,
    )
    return {"case_json": case_json}


def quantize_point(x: int | None, y: int | None, bucket: int = 24) -> tuple[int | None, int | None]:
    if x is None or y is None:
        return (x, y)
    return (round(x / bucket) * bucket, round(y / bucket) * bucket)


def _bbox_center(bbox: list[Any] | None) -> tuple[int | None, int | None]:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return (None, None)
    try:
        x1, y1, x2, y2 = [int(float(v)) for v in bbox]
    except Exception:
        return (None, None)
    return ((x1 + x2) // 2, (y1 + y2) // 2)


@dataclass
class BridgeSummary:
    request_count: int
    action_count: int
    screenshot_count: int
    tool_counts: dict[str, int]
    first_actions: list[str]
    repeated_hotspots: list[str]
    last_action: str
    max_repeat_count: int
    dominant_issue_hint: str


def summarize_bridge_requests(path: str) -> BridgeSummary:
    tool_counts: Counter[str] = Counter()
    first_actions: list[str] = []
    action_patterns: Counter[str] = Counter()
    last_action = "无"
    request_count = 0
    action_count = 0
    screenshot_count = 0

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                request_count += 1
                payload = json.loads(line)
                request = payload.get("request") or {}
                response = payload.get("response") or {}
                tool = str(request.get("tool") or "unknown")
                tool_counts[tool] += 1
                if tool == "screenshot":
                    screenshot_count += 1
                    continue

                action_count += 1
                args = request.get("args") or {}
                mapped = (((response.get("payload") or {}).get("mappedArgs")) or {})
                if tool == "mouse_click":
                    x = mapped.get("x")
                    y = mapped.get("y")
                    if x is None or y is None:
                        x, y = _bbox_center(args.get("bbox"))
                    qx, qy = quantize_point(x, y)
                    action = f"点击({x},{y})" if x is not None and y is not None else "点击(未知坐标)"
                    pattern = f"mouse_click@{qx},{qy}"
                elif tool == "mouse_scroll":
                    clicks = args.get("clicks")
                    x = mapped.get("x")
                    y = mapped.get("y")
                    qx, qy = quantize_point(x, y)
                    action = f"滚动({clicks})"
                    pattern = f"mouse_scroll@{qx},{qy}:{clicks}"
                elif tool == "key_press":
                    key = args.get("key")
                    action = f"按键({key})"
                    pattern = f"key_press:{key}"
                elif tool == "clipboard_type":
                    text = truncate(str(args.get("text") or ""), limit=32)
                    action = f"粘贴文本({text})"
                    pattern = f"clipboard_type:{text}"
                elif tool == "type":
                    text = truncate(str(args.get("text") or ""), limit=32)
                    action = f"输入文本({text})"
                    pattern = f"type:{text}"
                else:
                    action = f"{tool}({truncate(compact_json(args, limit=60), limit=60)})"
                    pattern = f"{tool}:{compact_json(args, limit=60)}"

                if len(first_actions) < 12:
                    first_actions.append(action)
                last_action = action
                action_patterns[pattern] += 1
    except FileNotFoundError:
        return BridgeSummary(0, 0, 0, {}, [], [], "无", 0, "缺少 bridge_requests.jsonl")
    except Exception as exc:
        return BridgeSummary(0, 0, 0, {}, [], [], "无", 0, f"bridge_requests 解析失败: {exc}")

    repeated_hotspots: list[str] = []
    max_repeat_count = 0
    for pattern, count in action_patterns.most_common(5):
        max_repeat_count = max(max_repeat_count, count)
        if count < 3:
            continue
        repeated_hotspots.append(f"{pattern} 重复 {count} 次")

    dominant_issue_hint = ""
    if max_repeat_count >= 5:
        dominant_issue_hint = "存在明显重复操作，疑似陷入局部循环或控件定位不稳定"
    elif action_count == 0 and screenshot_count > 0:
        dominant_issue_hint = "只有截图没有实际动作，疑似等待/识别阶段卡住"
    elif action_count <= 2 and request_count > 10:
        dominant_issue_hint = "有效动作很少，疑似页面加载/状态识别不足"

    return BridgeSummary(
        request_count=request_count,
        action_count=action_count,
        screenshot_count=screenshot_count,
        tool_counts=dict(tool_counts),
        first_actions=first_actions,
        repeated_hotspots=repeated_hotspots,
        last_action=last_action,
        max_repeat_count=max_repeat_count,
        dominant_issue_hint=dominant_issue_hint,
    )


def summarize_runtime_log(path: str) -> list[str]:
    text = safe_read_text(path)
    if not text:
        return []
    highlights: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("[osworld]"):
            highlights.append(line)
        if len(highlights) >= 8:
            break
    return highlights


def classify_case(
    *,
    score: float | None,
    failure_type: str | None,
    failure_reason: str | None,
    bridge: BridgeSummary,
    env_change_risk: str,
) -> tuple[str, bool, str, str]:
    if score is not None and score >= 1.0:
        if failure_type:
            return (
                "通过但伴随异常",
                True,
                "medium",
                f"最终得分通过，但运行中记录了 {failure_type}，需要关注稳定性或评测链路抖动。",
            )
        return ("正常通过", False, "high", "分数达到 1.0，且没有记录失败元数据。")

    if failure_type == "controller_exec_failed":
        return (
            "执行层失败",
            True,
            "high",
            "控制器执行动作时报错，更像 bridge/环境执行层问题，而不是单纯任务理解错误。",
        )
    if failure_type == "tool_translation_failed":
        return (
            "动作翻译失败",
            True,
            "high",
            "模型动作被桥接层翻译失败，属于工具链/协议层异常。",
        )
    if failure_type == "screenshot_failed":
        return (
            "观测失败",
            True,
            "high",
            "截图链路失败，模型后续判断失去观测依据，优先排查环境与桥接层。",
        )
    if failure_type == "evaluate_failed":
        return (
            "评测阶段异常",
            True,
            "high",
            "运行已经走到评测阶段，但 evaluator/后处理失败，存在明显假阴性风险。",
        )
    if failure_type == "cua_reported_failure":
        return (
            "模型主动失败",
            False,
            "high",
            "CUA 主动报告失败，通常代表它判断当前路径不可继续或无法完成任务。",
        )
    if failure_type == "cua_timeout":
        if bridge.max_repeat_count >= 5:
            return (
                "超时且疑似策略循环",
                False,
                "medium",
                "运行超时，且存在高频重复操作，更像是模型在局部界面反复尝试，没有收敛到正确路径。",
            )
        if bridge.action_count <= 2 or bridge.screenshot_count > bridge.action_count * 3:
            return (
                "超时且疑似等待/环境卡顿",
                True,
                "medium",
                "运行超时，但有效动作偏少，截图占比高，疑似页面加载、焦点状态或环境响应导致推进不足。",
            )
        return (
            "超时未完成",
            env_change_risk != "low",
            "medium",
            "运行达到 max_duration 仍未收敛，通常是策略效率不足与环境响应慢共同作用。",
        )

    if score is not None and score == 0:
        if env_change_risk != "low":
            return (
                "未通过，存在环境漂移风险",
                True,
                "low",
                "未通过且 case 自带环境变化风险标记，既可能是策略问题，也可能受到页面/环境漂移影响。",
            )
        return (
            "未通过，疑似收尾或策略问题",
            False,
            "medium",
            "没有明确 failure metadata，但最终得分为 0，更像是任务理解、路径选择或收尾状态未命中 evaluator。",
        )

    if score is not None and 0 < score < 1:
        return (
            "部分完成",
            env_change_risk != "low",
            "medium",
            "已经完成部分目标，但最终状态未完全命中评测标准，通常需要优化收尾动作或精度。",
        )

    return (
        "结果不足",
        True,
        "low",
        f"结果信息不足，failure_type={failure_type}，failure_reason={failure_reason}。",
    )


def build_optimizations(
    *,
    failure_type: str | None,
    score: float | None,
    bridge: BridgeSummary,
    suspected_environmental: bool,
) -> list[str]:
    suggestions: list[str] = []

    if failure_type == "controller_exec_failed":
        suggestions.extend(
            [
                "先增强 openclaw/pyautogui 控制器的错误重试与窗口焦点校验，避免单次动作失败直接拖垮整题。",
                "把失败动作附近的截图、坐标映射和 controllerResult 一起入库，便于定位是坐标偏移、权限还是窗口遮挡。",
            ]
        )
    elif failure_type == "tool_translation_failed":
        suggestions.extend(
            [
                "补齐高频工具参数模式的翻译兜底，至少对 click/type/scroll 这类高频动作做更鲁棒的参数规范化。",
                "在桥接层增加失败动作的回退策略，例如无法翻译时退化到更简单的 click/type 组合。",
            ]
        )
    elif failure_type == "screenshot_failed":
        suggestions.extend(
            [
                "优先修截图链路稳定性，增加截图失败后的短重试与窗口可见性检测。",
                "把截图失败前后的 bridge 请求、屏幕尺寸、窗口焦点统一落盘，减少后续人工排查成本。",
            ]
        )
    elif failure_type == "evaluate_failed":
        suggestions.extend(
            [
                "优先复查 evaluator/postconfig，确认是不是评测前重启应用、读取状态失败或规则过严导致的假阴性。",
                "对 evaluate_failed case 增加自动人工复核清单：录像、最终截图、postconfig 前后状态。",
            ]
        )
    elif failure_type == "cua_timeout":
        if bridge.max_repeat_count >= 5:
            suggestions.extend(
                [
                    "给 CUA 增加重复动作检测与早停重规划逻辑，避免在同一坐标或同一控件附近无限打转。",
                    "对高频循环场景补充 UI 状态识别提示，例如识别设置页侧栏、搜索框、确认开关等关键控件。",
                ]
            )
        else:
            suggestions.extend(
                [
                    "优化等待策略：页面切换、应用启动和配置页加载后加显式稳定判断，而不是仅依赖固定 sleep。",
                    "对长路径任务优先减少无效截图/观察回合，提高单步推进效率，必要时按 domain 定制快捷路径。",
                ]
            )
    elif score is not None and score == 0:
        suggestions.extend(
            [
                "加强任务收尾校验，在宣布 DONE 前主动检查 evaluator 关心的最终状态是否已经落盘。",
                "对低分 case 增加 domain-specific 操作模板，减少在设置页、菜单层级和多应用切换中的随机探索。",
            ]
        )

    if suspected_environmental:
        suggestions.append("把该 case 加入环境复核池：优先回看 recording.mp4 与最终截图，确认是不是环境抖动或评测假阴性。")

    if not suggestions:
        suggestions.append("当前 case 未暴露明显异常，建议保持现有路径，并把成功动作序列沉淀为同类任务模板。")

    return suggestions[:3]


def build_execution_summary(task_dir: str) -> tuple[BridgeSummary, list[str], str]:
    bridge = summarize_bridge_requests(os.path.join(task_dir, "bridge_requests.jsonl"))
    runtime_highlights = summarize_runtime_log(os.path.join(task_dir, "runtime.log"))
    if bridge.request_count == 0:
        text = "未读到 bridge_requests.jsonl，无法还原详细动作链，只能依赖 run_meta/failure 信息。"
    else:
        tool_rank = ", ".join(f"{name}×{count}" for name, count in Counter(bridge.tool_counts).most_common(5))
        first_actions = " → ".join(bridge.first_actions[:8]) if bridge.first_actions else "无有效动作"
        repeated = "；".join(bridge.repeated_hotspots[:3]) if bridge.repeated_hotspots else "无明显重复热点"
        hint = f"；观察结论：{bridge.dominant_issue_hint}" if bridge.dominant_issue_hint else ""
        text = (
            f"CUA 共发起 {bridge.request_count} 次 bridge 请求，其中有效动作 {bridge.action_count} 次、截图 {bridge.screenshot_count} 次；"
            f"工具分布：{tool_rank or '无'}。前序关键动作：{first_actions}。重复热点：{repeated}。"
            f"最后一个有效动作：{bridge.last_action}{hint}"
        )
    return bridge, runtime_highlights, text


def build_case_analysis(row: dict[str, Any], case_payload: dict[str, Any] | None) -> dict[str, Any]:
    domain = row["domain"]
    task_id = row["task_id"]
    task_dir = row["result_dir"]
    case_payload = case_payload or {}

    run_meta = safe_read_json(os.path.join(task_dir, "run_meta.json")) or {}
    failure_payload = safe_read_json(os.path.join(task_dir, "failure.json")) or {}
    cua_meta = safe_read_json(os.path.join(task_dir, "cua_meta.json")) or {}
    result_txt = safe_read_text(os.path.join(task_dir, "result.txt")).strip()

    bridge, runtime_highlights, execution_text = build_execution_summary(task_dir)

    env_change_risk = str(case_payload.get("possibility_of_env_change") or "unknown")
    diagnosis_label, suspected_environmental, confidence, diagnosis_reason = classify_case(
        score=row.get("score"),
        failure_type=row.get("failure_type"),
        failure_reason=row.get("failure_reason"),
        bridge=bridge,
        env_change_risk=env_change_risk,
    )
    optimizations = build_optimizations(
        failure_type=row.get("failure_type"),
        score=row.get("score"),
        bridge=bridge,
        suspected_environmental=suspected_environmental,
    )

    config_items = case_payload.get("config") or []
    postconfig_items = ((case_payload.get("evaluator") or {}).get("postconfig") or [])
    overview = {
        "instruction": case_payload.get("instruction") or "缺少 case 定义",
        "source": case_payload.get("source"),
        "snapshot": case_payload.get("snapshot"),
        "related_apps": case_payload.get("related_apps") or [],
        "env_flags": {
            "proxy": case_payload.get("proxy"),
            "fixed_ip": case_payload.get("fixed_ip"),
            "possibility_of_env_change": env_change_risk,
        },
        "initial_state": [describe_config_step(item) for item in config_items[:8]],
        "evaluator": format_rule_summary(case_payload),
        "postconfig": [describe_config_step(item) for item in postconfig_items[:6]],
    }

    evaluation = {
        "score": row.get("score"),
        "score_label": score_label(row.get("score")),
        "raw_result_text": result_txt,
        "status": row.get("status"),
        "failure_type": row.get("failure_type"),
        "failure_reason": row.get("failure_reason"),
        "failure_count": row.get("failure_count"),
    }

    diagnosis = {
        "label": diagnosis_label,
        "suspected_environmental": suspected_environmental,
        "confidence": confidence,
        "reason": diagnosis_reason,
        "runtime_highlights": runtime_highlights,
    }

    artifacts = {
        "task_dir": task_dir,
        "recording": os.path.join(task_dir, "recording.mp4") if os.path.exists(os.path.join(task_dir, "recording.mp4")) else None,
        "bridge_requests": os.path.join(task_dir, "bridge_requests.jsonl") if os.path.exists(os.path.join(task_dir, "bridge_requests.jsonl")) else None,
        "traj": os.path.join(task_dir, "traj.jsonl") if os.path.exists(os.path.join(task_dir, "traj.jsonl")) else None,
        "runtime_log": os.path.join(task_dir, "runtime.log") if os.path.exists(os.path.join(task_dir, "runtime.log")) else None,
        "failure_json": os.path.join(task_dir, "failure.json") if os.path.exists(os.path.join(task_dir, "failure.json")) else None,
        "case_json": collect_case_paths(domain, task_id)["case_json"],
    }

    quality_check = {
        "has_instruction": bool(overview["instruction"]),
        "has_execution_summary": bool(execution_text),
        "has_result_judgement": evaluation["score_label"] != "",
        "has_diagnosis": bool(diagnosis_reason),
        "has_optimization": bool(optimizations),
        "has_case_definition": bool(case_payload),
    }

    return {
        "domain": domain,
        "task_id": task_id,
        "overview": overview,
        "execution": {
            "summary": execution_text,
            "tool_counts": bridge.tool_counts,
            "first_actions": bridge.first_actions,
            "repeated_hotspots": bridge.repeated_hotspots,
            "last_action": bridge.last_action,
            "request_count": bridge.request_count,
            "action_count": bridge.action_count,
            "screenshot_count": bridge.screenshot_count,
        },
        "evaluation": evaluation,
        "diagnosis": diagnosis,
        "optimization": optimizations,
        "artifacts": artifacts,
        "run_meta": run_meta,
        "failure_payload": failure_payload,
        "cua_meta": {
            "duration_seconds": cua_meta.get("duration_seconds"),
            "exit_code": cua_meta.get("exit_code"),
            "bridge_error_count": cua_meta.get("bridge_error_count"),
            "bridge_failure_types": cua_meta.get("bridge_failure_types"),
        },
        "quality_check": quality_check,
    }


def render_case_markdown(case: dict[str, Any]) -> str:
    overview = case["overview"]
    execution = case["execution"]
    evaluation = case["evaluation"]
    diagnosis = case["diagnosis"]
    optimization = case["optimization"]
    artifacts = case["artifacts"]

    lines = [
        f"## {case['domain']} / {case['task_id']}",
        f"- Case 概述：{overview['instruction']}",
        f"- 来源：{overview.get('source') or '无'}",
        f"- 初始状态：{'；'.join(overview['initial_state']) if overview['initial_state'] else '无显式前置动作'}",
        f"- 评测标准：{overview['evaluator']}",
        f"- CUA 怎么执行：{execution['summary']}",
        f"- 评测结果：{evaluation['score_label']}（score={evaluation.get('score')}，status={evaluation.get('status')}，failure_type={evaluation.get('failure_type') or '无'}）",
        f"- 为什么未通过/风险点：{diagnosis['reason']}",
        f"- 应该如何优化：{'；'.join(optimization)}",
        f"- 关键产物：task_dir={artifacts['task_dir']}，recording={artifacts.get('recording') or '无'}",
        "",
    ]
    return "\n".join(lines)


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate full per-case analysis for CUA blackbox result directories")
    parser.add_argument("--result_dir", type=str, default="./results_cua_blackbox")
    parser.add_argument("--action_space", type=str, default="pyautogui")
    parser.add_argument("--observation_type", type=str, default="screenshot")
    parser.add_argument("--model", type=str, default="cua-blackbox")
    parser.add_argument("--result_root", type=str, default="")
    parser.add_argument("--test_all_meta_path", type=str, default="")
    parser.add_argument("--output_json", type=str, default="")
    parser.add_argument("--output_md", type=str, default="")
    return parser.parse_args()


def main() -> int:
    args = config()
    result_root = args.result_root or blackbox_result_root(args)
    saved_args = load_args_json(result_root)
    task_set_path = args.test_all_meta_path or str(saved_args.get("test_all_meta_path") or "")
    task_set = load_task_set_file(task_set_path) if task_set_path else {}
    summary = build_blackbox_summary(
        result_root,
        task_set=task_set,
        task_set_path=task_set_path,
        metadata=summary_metadata_from_args(saved_args if saved_args else args),
    )

    rows = summary.get("rows") or []
    analyses: list[dict[str, Any]] = []
    missing_case_definitions: list[dict[str, str]] = []

    for row in rows:
        case_path = collect_case_paths(row["domain"], row["task_id"])["case_json"]
        case_payload = safe_read_json(case_path)
        if not case_payload:
            missing_case_definitions.append({"domain": row["domain"], "task_id": row["task_id"], "case_json": case_path})
        analyses.append(build_case_analysis(row, case_payload))

    total_cases = len(rows)
    if len(analyses) != total_cases:
        raise RuntimeError(f"analysis coverage mismatch: rows={total_cases}, analyses={len(analyses)}")

    quality_counts = Counter()
    for analysis in analyses:
        for key, value in (analysis.get("quality_check") or {}).items():
            if value:
                quality_counts[key] += 1

    coverage = {
        "expected_cases": total_cases,
        "analyzed_cases": len(analyses),
        "coverage_ratio": 1.0 if total_cases == len(analyses) else (len(analyses) / total_cases if total_cases else 0.0),
        "missing_case_definition_count": len(missing_case_definitions),
        "missing_case_definitions": missing_case_definitions,
        "quality_counts": dict(quality_counts),
    }

    output = {
        "generated_at": now_iso(),
        "analysis_version": "v1",
        "result_root": result_root,
        "task_set_path": task_set_path,
        "summary_totals": summary.get("totals") or {},
        "coverage": coverage,
        "cases": analyses,
    }

    summary_dir = os.path.join(result_root, "summary")
    os.makedirs(summary_dir, exist_ok=True)
    output_json = args.output_json or os.path.join(summary_dir, "case_analysis.json")
    output_md = args.output_md or os.path.join(summary_dir, "case_analysis.md")

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    md_lines = [
        "# CUA Blackbox 全量逐 Case 分析",
        "",
        f"- generated_at: {output['generated_at']}",
        f"- result_root: {result_root}",
        f"- expected_cases: {coverage['expected_cases']}",
        f"- analyzed_cases: {coverage['analyzed_cases']}",
        f"- coverage_ratio: {coverage['coverage_ratio']:.4f}",
        f"- missing_case_definition_count: {coverage['missing_case_definition_count']}",
        f"- summary_totals: {compact_json(output['summary_totals'], limit=280)}",
        "",
        "## 质量保证",
        "",
        "- 本文件逐条遍历 summary rows 生成，不是人工挑样本。",
        "- 如果 analyzed_cases != expected_cases，脚本会直接报错退出，不会悄悄少分析。",
        "- 每个 case 都强制填充 5 个检查项：概述、执行摘要、结果判定、原因诊断、优化建议。",
        "",
    ]
    for case in analyses:
        md_lines.append(render_case_markdown(case))

    with open(output_md, "w", encoding="utf-8") as file:
        file.write("\n".join(md_lines))

    print(f"result_root={result_root}")
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")
    print(f"expected_cases={coverage['expected_cases']}")
    print(f"analyzed_cases={coverage['analyzed_cases']}")
    print(f"missing_case_definition_count={coverage['missing_case_definition_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
