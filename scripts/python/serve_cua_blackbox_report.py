from __future__ import annotations

import argparse
import hashlib
import html
import json
import mimetypes
import os
import posixpath
import sys
import urllib.parse
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)


@dataclass(frozen=True)
class ReportRef:
    id: str
    result_root: str
    report_path: str


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve CUA blackbox reports through a read-only local web UI")
    parser.add_argument("--result_root", action="append", default=[], help="Result root containing report/report.json. Can be repeated.")
    parser.add_argument("--results_dir", action="append", default=[], help="Directory to scan for report/report.json. Can be repeated.")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--scan_depth", type=int, default=5)
    parser.add_argument("--open_browser", action="store_true")
    return parser.parse_args()


def _abs_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def _report_id(report_path: str) -> str:
    digest = hashlib.sha1(report_path.encode("utf-8")).hexdigest()[:10]
    basename = os.path.basename(os.path.dirname(os.path.dirname(report_path))) or "report"
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in basename).strip("-") or "report"
    return f"{safe_name}-{digest}"


def _report_ref_from_path(path: str) -> ReportRef | None:
    expanded = _abs_path(path)
    if os.path.isfile(expanded):
        if os.path.basename(expanded) != "report.json":
            return None
        report_dir = os.path.dirname(expanded)
        result_root = os.path.dirname(report_dir) if os.path.basename(report_dir) == "report" else report_dir
        return ReportRef(id=_report_id(expanded), result_root=result_root, report_path=expanded)

    if not os.path.isdir(expanded):
        return None

    if os.path.basename(expanded) == "report":
        report_path = os.path.join(expanded, "report.json")
        result_root = os.path.dirname(expanded)
    else:
        result_root = expanded
        report_path = os.path.join(expanded, "report", "report.json")

    if os.path.isfile(report_path):
        return ReportRef(id=_report_id(report_path), result_root=result_root, report_path=report_path)
    return None


def _scan_reports(root: str, max_depth: int) -> list[ReportRef]:
    root = _abs_path(root)
    if not os.path.isdir(root):
        return []

    refs: list[ReportRef] = []
    root_depth = root.rstrip(os.sep).count(os.sep)
    for current, dirs, files in os.walk(root):
        depth = current.rstrip(os.sep).count(os.sep) - root_depth
        if depth > max_depth:
            dirs[:] = []
            continue
        if os.path.basename(current) == "report" and "report.json" in files:
            ref = _report_ref_from_path(os.path.join(current, "report.json"))
            if ref:
                refs.append(ref)
            dirs[:] = []
    return refs


def discover_reports(args: argparse.Namespace) -> list[ReportRef]:
    refs: list[ReportRef] = []
    for path in args.result_root:
        ref = _report_ref_from_path(path)
        if ref:
            refs.append(ref)

    scan_dirs = args.results_dir or [os.path.join(ROOT_DIR, "results_cua_blackbox")]
    for path in scan_dirs:
        refs.extend(_scan_reports(path, args.scan_depth))

    deduped: dict[str, ReportRef] = {}
    for ref in refs:
        deduped[ref.report_path] = ref
    return list(deduped.values())


def _read_report(ref: ReportRef) -> dict[str, Any]:
    with open(ref.report_path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload if isinstance(payload, dict) else {}


def _report_summary(ref: ReportRef) -> dict[str, Any]:
    try:
        payload = _read_report(ref)
        totals = ((payload.get("summary") or {}).get("summary") or {}).get("totals") or {}
        conclusion = payload.get("conclusion") or {}
        return {
            "id": ref.id,
            "title": payload.get("title") or ref.id,
            "generated_at": payload.get("generated_at"),
            "result_root": ref.result_root,
            "report_path": ref.report_path,
            "status": conclusion.get("status", "unknown"),
            "total_tasks": totals.get("total_tasks"),
            "scored_tasks": totals.get("scored_tasks"),
            "failed_tasks": totals.get("failed_tasks"),
            "pending_tasks": totals.get("pending_tasks"),
            "average_score": totals.get("average_score"),
        }
    except Exception as exc:
        return {
            "id": ref.id,
            "title": ref.id,
            "generated_at": None,
            "result_root": ref.result_root,
            "report_path": ref.report_path,
            "status": "load_error",
            "error": str(exc),
        }


def _safe_artifact_path(ref: ReportRef, raw_path: str) -> str | None:
    if not raw_path:
        return None
    expanded = _abs_path(raw_path)
    root = _abs_path(ref.result_root)
    try:
        if os.path.commonpath([root, expanded]) != root:
            return None
    except ValueError:
        return None
    return expanded


def _directory_listing(path: str, ref: ReportRef) -> bytes:
    rows = []
    for name in sorted(os.listdir(path)):
        if name.startswith("."):
            continue
        child = os.path.join(path, name)
        suffix = "/" if os.path.isdir(child) else ""
        rows.append(
            f'<li><a href="/artifact/{urllib.parse.quote(ref.id)}?path={urllib.parse.quote(child)}">'
            f"{html.escape(name + suffix)}</a></li>"
        )
    body = f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Artifacts</title></head>
<body><h1>{html.escape(path)}</h1><ul>{''.join(rows)}</ul></body>
</html>"""
    return body.encode("utf-8")


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


class ReportServer(BaseHTTPRequestHandler):
    refs: dict[str, ReportRef] = {}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = posixpath.normpath(parsed.path)
        if path == "/":
            self._send_bytes(INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/reports":
            reports = [_report_summary(ref) for ref in self.refs.values()]
            self._send_json({"reports": reports})
            return
        if path.startswith("/api/reports/"):
            report_id = urllib.parse.unquote(path.rsplit("/", 1)[-1])
            self._send_report(report_id)
            return
        if path.startswith("/artifact/"):
            report_id = urllib.parse.unquote(path.rsplit("/", 1)[-1])
            query = urllib.parse.parse_qs(parsed.query)
            self._send_artifact(report_id, query.get("path", [""])[0])
            return
        self.send_error(HTTPStatus.NOT_FOUND, "not found")

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[serve_cua_blackbox_report] {self.address_string()} - {format % args}")

    def _send_report(self, report_id: str) -> None:
        ref = self.refs.get(report_id)
        if not ref:
            self.send_error(HTTPStatus.NOT_FOUND, "unknown report")
            return
        try:
            payload = _read_report(ref)
        except Exception as exc:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
            return
        payload["_server"] = {
            "id": ref.id,
            "result_root": ref.result_root,
            "report_path": ref.report_path,
            "artifact_policy": "only paths under result_root are served",
        }
        self._send_json(payload)

    def _send_artifact(self, report_id: str, raw_path: str) -> None:
        ref = self.refs.get(report_id)
        if not ref:
            self.send_error(HTTPStatus.NOT_FOUND, "unknown report")
            return
        path = _safe_artifact_path(ref, raw_path)
        if not path:
            self.send_error(HTTPStatus.FORBIDDEN, "artifact path is outside result_root")
            return
        if os.path.isdir(path):
            self._send_bytes(_directory_listing(path, ref), "text/html; charset=utf-8")
            return
        if not os.path.isfile(path):
            self.send_error(HTTPStatus.NOT_FOUND, "artifact not found")
            return
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as file:
            self._send_bytes(file.read(), mime_type)

    def _send_json(self, payload: Any) -> None:
        self._send_bytes(_json_bytes(payload), "application/json; charset=utf-8")

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CUA Blackbox Reports</title>
  <style>
    :root {
      --ink: #101b18;
      --muted: #6b746f;
      --paper: #f7f0df;
      --panel: rgba(255, 253, 247, .9);
      --line: #e0d5bf;
      --ok: #1f7a4d;
      --bad: #b33b2e;
      --warn: #9a651c;
      --accent: #0a6678;
      --shadow: 0 24px 70px rgba(25, 22, 16, .14);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 10% 5%, rgba(10, 102, 120, .18), transparent 28rem),
        radial-gradient(circle at 90% 8%, rgba(154, 101, 28, .20), transparent 26rem),
        linear-gradient(145deg, #efe3c8, #fbf8ef 46%, #ecf2ed);
      font-family: "Avenir Next", "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
      min-height: 100vh;
    }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 38px 22px 70px; }
    .hero {
      padding: 34px;
      border: 1px solid rgba(16, 27, 24, .08);
      border-radius: 30px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }
    .eyebrow { margin: 0 0 10px; color: var(--muted); letter-spacing: .09em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(34px, 6vw, 64px); line-height: .98; letter-spacing: -.05em; }
    h2 { margin: 30px 0 14px; letter-spacing: -.02em; }
    .controls { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr; gap: 12px; margin-top: 24px; }
    select, input {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fffdf7;
      color: var(--ink);
      font: inherit;
    }
    .cards { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; margin-top: 20px; }
    .card { padding: 18px; border: 1px solid var(--line); border-radius: 20px; background: rgba(255,253,247,.78); }
    .card span { display: block; color: var(--muted); font-size: 13px; }
    .card strong { display: block; margin-top: 4px; font-size: 30px; letter-spacing: -.03em; }
    .badge { display: inline-flex; padding: 7px 12px; border-radius: 999px; color: white; font-weight: 800; letter-spacing: .04em; }
    .badge.pass { background: var(--ok); }
    .badge.fail { background: var(--bad); }
    .badge.unknown, .badge.load_error { background: var(--warn); }
    section {
      margin-top: 22px;
      padding: 22px;
      border: 1px solid rgba(16, 27, 24, .08);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: 0 12px 34px rgba(25, 22, 16, .08);
      overflow: hidden;
    }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
    td { word-break: break-word; }
    a { color: var(--accent); text-decoration: none; font-weight: 650; }
    a:hover { text-decoration: underline; }
    .muted { color: var(--muted); }
    .notice { margin: 0; padding-left: 18px; }
    .notice.blockers li { color: var(--bad); }
    .notice.warnings li { color: var(--warn); }
    .split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 860px) {
      .wrap { padding: 20px 12px 44px; }
      .hero { padding: 24px; }
      .controls { grid-template-columns: 1fr; }
      .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .split { grid-template-columns: 1fr; }
      section { overflow-x: auto; }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <p class="eyebrow">read-only local report viewer</p>
      <h1>CUA Blackbox Reports</h1>
      <div class="controls">
        <select id="reportSelect"></select>
        <input id="searchInput" placeholder="搜索 task / domain / failure / artifact">
        <select id="suiteFilter"><option value="">所有 suite</option></select>
        <select id="statusFilter"><option value="">所有状态</option><option>PASS</option><option>FAIL</option><option>UNKNOWN</option></select>
      </div>
    </header>
    <div id="content"></div>
  </main>
  <script>
    let reports = [];
    let current = null;

    const $ = (id) => document.getElementById(id);
    const esc = (value) => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    const statusLabel = (value) => value === true ? 'PASS' : value === false ? 'FAIL' : String(value || 'UNKNOWN').toUpperCase();
    const badge = (status) => `<span class="badge ${esc(String(status).toLowerCase())}">${esc(String(status).toUpperCase())}</span>`;

    async function init() {
      const response = await fetch('/api/reports');
      const payload = await response.json();
      reports = payload.reports || [];
      const select = $('reportSelect');
      select.innerHTML = reports.length
        ? reports.map(item => `<option value="${esc(item.id)}">${esc(item.title)} - ${esc(item.status)}</option>`).join('')
        : '<option value="">未发现 report/report.json</option>';
      select.onchange = () => loadReport(select.value);
      ['searchInput', 'suiteFilter', 'statusFilter'].forEach(id => $(id).oninput = render);
      if (reports.length) await loadReport(reports[0].id);
      else renderEmpty();
    }

    async function loadReport(id) {
      const response = await fetch(`/api/reports/${encodeURIComponent(id)}`);
      current = await response.json();
      const suites = Array.from(new Set((current.test_matrix || []).map(item => item.suite).filter(Boolean))).sort();
      $('suiteFilter').innerHTML = '<option value="">所有 suite</option>' + suites.map(item => `<option>${esc(item)}</option>`).join('');
      render();
    }

    function renderEmpty() {
      $('content').innerHTML = `<section><h2>没有可展示的报告</h2><p class="muted">请使用 --result_root 指向包含 report/report.json 的结果目录，或使用 --results_dir 扫描结果目录。</p></section>`;
    }

    function render() {
      if (!current) return renderEmpty();
      const summary = current.summary || {};
      const totals = ((summary.summary || {}).totals) || {};
      const conclusion = current.conclusion || {};
      const metadata = ((summary.summary || {}).metadata) || {};
      const cards = [
        ['Total', totals.total_tasks ?? 'NA'],
        ['Scored', totals.scored_tasks ?? 'NA'],
        ['Failed', totals.failed_tasks ?? 'NA'],
        ['Pending', totals.pending_tasks ?? 'NA'],
        ['Average', totals.average_score ?? 'NA'],
      ].map(([k, v]) => `<article class="card"><span>${esc(k)}</span><strong>${esc(v)}</strong></article>`).join('');

      $('content').innerHTML = `
        <section>
          <div>${badge(conclusion.status || 'unknown')}</div>
          <p class="muted">结果目录：${esc(current.result_root || current._server?.result_root || '')}</p>
          <div class="cards">${cards}</div>
        </section>
        <section class="split">
          <div><h2>阻塞项</h2>${notice(conclusion.blockers, 'blockers', '无阻塞项')}</div>
          <div><h2>提醒</h2>${notice(conclusion.warnings, 'warnings', '无提醒')}</div>
        </section>
        <section><h2>环境</h2>${table(['字段', '值'], Object.entries(metadata))}</section>
        <section><h2>Domain 汇总</h2>${domainTable(summary.domains || {})}</section>
        <section><h2>失败分类</h2>${failureTable((summary.failures || {}).by_failure_type || {})}</section>
        <section><h2>测试矩阵</h2>${matrixTable(filteredMatrix())}</section>
        <section><h2>Artifacts</h2>${artifactTable(current.artifacts || [])}</section>
      `;
    }

    function notice(items, cls, emptyText) {
      if (!items || !items.length) return `<p class="muted">${esc(emptyText)}</p>`;
      return `<ul class="notice ${cls}">${items.map(item => `<li>${esc(item)}</li>`).join('')}</ul>`;
    }

    function table(headers, rows) {
      if (!rows || !rows.length) return '<p class="muted">无数据</p>';
      return `<table><thead><tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${esc(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
    }

    function domainTable(domains) {
      const rows = Object.entries(domains).sort().map(([domain, data]) => [domain, data.total_tasks, data.scored_tasks, data.failed_tasks, data.pending_tasks, data.average_score]);
      return table(['domain', 'total', 'scored', 'failed', 'pending', 'average'], rows);
    }

    function failureTable(failures) {
      const rows = Object.entries(failures).sort().map(([type, data]) => [type, data.count, (data.domains || []).join(', '), (data.task_ids || []).join(', ')]);
      return table(['failure_type', 'count', 'domains', 'task_ids'], rows);
    }

    function filteredMatrix() {
      const q = $('searchInput').value.toLowerCase();
      const suite = $('suiteFilter').value;
      const status = $('statusFilter').value;
      return (current.test_matrix || []).filter(item => {
        const haystack = [item.suite, item.id, item.name, item.failure].join(' ').toLowerCase();
        const itemStatus = statusLabel(item.passed);
        return (!q || haystack.includes(q)) && (!suite || item.suite === suite) && (!status || itemStatus === status);
      });
    }

    function matrixTable(rows) {
      return table(['suite', 'id', 'name', 'status', 'failure'], rows.map(item => [item.suite, item.id, item.name, statusLabel(item.passed), item.failure || '']));
    }

    function artifactTable(artifacts) {
      const q = $('searchInput').value.toLowerCase();
      const root = current._server?.result_root || current.result_root || '';
      const rows = artifacts.filter(item => !q || [item.name, item.type, item.path].join(' ').toLowerCase().includes(q)).map(item => {
        const path = String(item.path || '');
        const link = path.startsWith(root)
          ? `<a href="/artifact/${encodeURIComponent(current._server.id)}?path=${encodeURIComponent(path)}" target="_blank">${esc(path)}</a>`
          : `<span class="muted">${esc(path)}（root 外，未暴露）</span>`;
        return [item.name, item.type, link];
      });
      if (!rows.length) return '<p class="muted">无数据</p>';
      return `<table><thead><tr><th>name</th><th>type</th><th>path</th></tr></thead><tbody>${rows.map(row => `<tr><td>${esc(row[0])}</td><td>${esc(row[1])}</td><td>${row[2]}</td></tr>`).join('')}</tbody></table>`;
    }

    init().catch(error => {
      $('content').innerHTML = `<section><h2>加载失败</h2><pre>${esc(error.stack || error)}</pre></section>`;
    });
  </script>
</body>
</html>
"""


def run_server(args: argparse.Namespace) -> int:
    refs = discover_reports(args)
    ReportServer.refs = {ref.id: ref for ref in refs}
    server = ThreadingHTTPServer((args.host, args.port), ReportServer)
    url = f"http://{args.host}:{server.server_port}/"
    print(f"reports: {len(refs)}")
    for ref in refs:
        print(f"- {ref.id}: {ref.report_path}")
    print(f"serving: {url}")
    print("mode: read-only")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nserver stopped")
    finally:
        server.server_close()
    return 0


def main() -> int:
    args = config()
    return run_server(args)


if __name__ == "__main__":
    raise SystemExit(main())
