"""Download OSWorld qcow2 zip files from HuggingFace with resume support.

This is a utility script for large files that may fail with plain curl.
It uses HTTP Range requests for resume, and retries on transient errors.

Examples:

  # Windows qcow2 zip
  python scripts/python/download_hf_qcow2.py \
    --url "https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip" \
    --out "docker_vm_data/Windows-10-x64.qcow2.zip"

  # Ubuntu qcow2 zip
  python scripts/python/download_hf_qcow2.py \
    --url "https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu.qcow2.zip" \
    --out "docker_vm_data/Ubuntu.qcow2.zip"

  # Quick verification: download only 1MB
  python scripts/python/download_hf_qcow2.py \
    --url "https://huggingface.co/datasets/xlangai/windows_osworld/resolve/main/Windows-10-x64.qcow2.zip" \
    --out "/tmp/osworld_hf_test1m.zip" \
    --max-bytes 1048576
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Optional

import requests


def _fmt_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024.0 or u == units[-1]:
            if u == "B":
                return f"{int(x)}{u}"
            return f"{x:.2f}{u}"
        x /= 1024.0
    return f"{n}B"


def _fmt_duration(sec: float) -> str:
    if sec < 0 or sec == float("inf"):
        return "?"
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def head_total_size(url: str, timeout: int = 20, retries: int = 5, retry_sleep_sec: float = 2.0) -> int:
    """Best-effort content size detection.

    HuggingFace large files may redirect to a signed URL; transient network errors can happen.
    This function retries and returns 0 if size cannot be determined.
    """

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            r = requests.head(url, allow_redirects=True, timeout=timeout)
            r.raise_for_status()
            return int(r.headers.get("content-length") or 0)
        except Exception as e:
            last_err = e
            time.sleep(retry_sleep_sec * (attempt + 1))

    print("warning: failed to HEAD total size, will download without total size:", type(last_err).__name__, last_err)
    return 0


def download_with_resume(
    url: str,
    out: str,
    max_bytes: Optional[int],
    chunk_mb: int,
    sleep_sec: float,
    retry_sleep_sec: float,
    progress_interval_sec: float,
):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    sess = requests.Session()
    # Some CDNs behave better with an explicit UA.
    sess.headers.update({"User-Agent": "OSWorldUse-downloader/1.0"})

    total = head_total_size(url, retry_sleep_sec=retry_sleep_sec)
    if total:
        print("total_bytes=", total)

    last_report_t = 0.0
    last_report_pos = 0
    started_t = time.time()
    while True:
        pos = os.path.getsize(out) if os.path.exists(out) else 0
        if total and pos >= total:
            print("done, size=", pos)
            return
        if max_bytes is not None and pos >= max_bytes:
            print("reached max_bytes, size=", pos)
            return

        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with sess.get(
                url,
                stream=True,
                allow_redirects=True,
                timeout=(10, 60),
                headers=headers,
            ) as r:
                r.raise_for_status()
                with open(out, "ab" if pos else "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_mb * 1024 * 1024):
                        if not chunk:
                            continue

                        if max_bytes is not None:
                            remaining = max_bytes - f.tell()
                            if remaining <= 0:
                                print("reached max_bytes, size=", f.tell())
                                return
                            if len(chunk) > remaining:
                                f.write(chunk[:remaining])
                                print("reached max_bytes, size=", f.tell())
                                return

                        f.write(chunk)

                        now = time.time()
                        if progress_interval_sec > 0 and (now - last_report_t) >= progress_interval_sec:
                            cur = f.tell()
                            delta_b = cur - last_report_pos
                            delta_t = max(now - (last_report_t or started_t), 1e-6)
                            speed = delta_b / delta_t

                            if total:
                                pct = (cur / total) * 100
                                eta = (total - cur) / speed if speed > 0 else float("inf")
                                msg = (
                                    f"\r{_fmt_bytes(cur)}/{_fmt_bytes(total)} "
                                    f"({pct:5.1f}%) { _fmt_bytes(int(speed)) }/s ETA {_fmt_duration(eta)}"
                                )
                            else:
                                msg = f"\r{_fmt_bytes(cur)} downloaded { _fmt_bytes(int(speed)) }/s"

                            sys.stderr.write(msg)
                            sys.stderr.flush()
                            last_report_t = now
                            last_report_pos = cur

                # Finish the current line
                sys.stderr.write("\n")
                sys.stderr.flush()

            time.sleep(sleep_sec)
        except Exception as e:
            print("error:", type(e).__name__, e)
            time.sleep(retry_sleep_sec)


def main():
    p = argparse.ArgumentParser(description="Download HuggingFace files with resume")
    p.add_argument("--url", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-bytes", type=int, default=None)
    p.add_argument("--chunk-mb", type=int, default=8)
    p.add_argument("--sleep-sec", type=float, default=0.5)
    p.add_argument("--retry-sleep-sec", type=float, default=5.0)
    p.add_argument("--progress-interval-sec", type=float, default=1.0)
    args = p.parse_args()
    download_with_resume(
        url=args.url,
        out=args.out,
        max_bytes=args.max_bytes,
        chunk_mb=args.chunk_mb,
        sleep_sec=args.sleep_sec,
        retry_sleep_sec=args.retry_sleep_sec,
        progress_interval_sec=args.progress_interval_sec,
    )


if __name__ == "__main__":
    main()
