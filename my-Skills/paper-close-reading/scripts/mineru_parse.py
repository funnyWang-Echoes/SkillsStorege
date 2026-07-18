#!/usr/bin/env python3
# MinerU 精准解析脚本：上传本地论文文件，轮询结果并规范化输出。
from __future__ import annotations

import argparse
import http.client
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
import zipfile
from pathlib import Path
from typing import Any


API_BASE = "https://mineru.net/api/v4"
IN_PROGRESS_STATES = {"waiting-file", "pending", "running", "converting"}


def load_env_file(path: Path) -> dict[str, str]:
    """读取简单 .env 文件，返回键值对；不会打印任何敏感值。"""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_token(env_path: Path, token_env: str) -> str:
    """从进程环境或 .env 文件读取 MinerU API token，自动探测常见 key 名。"""
    candidate_keys = [token_env, "minerU_APIKEY", "minerU_API", "MINERU_API", "MINERU_APIKEY"]
    for key in candidate_keys:
        token = os.environ.get(key)
        if token:
            return token
    env_values = load_env_file(env_path)
    for key in candidate_keys:
        token = env_values.get(key, "")
        if token:
            return token
    raise RuntimeError(
        f"MinerU token not found. Tried: {', '.join(candidate_keys)}. "
        f"Set one of them in the environment or .env file at {env_path}."
    )


def request_json(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """发送 JSON API 请求并检查 MinerU 返回码。"""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {token}",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {method} {url}: {body}") from exc
    result = json.loads(body)
    if result.get("code") != 0:
        raise RuntimeError(f"MinerU API error {result.get('code')}: {result.get('msg')}")
    return result


def upload_file(upload_url: str, file_path: Path) -> None:
    """把本地文件字节上传到 MinerU 返回的预签名 URL。"""
    data = file_path.read_bytes()
    parsed = urllib.parse.urlsplit(upload_url)
    path = urllib.parse.urlunsplit(("", "", parsed.path, parsed.query, ""))
    connection_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    connection = connection_cls(parsed.netloc, timeout=180)
    try:
        # 预签名 OSS URL 的签名包含 Content-Type；这里必须不发送 Content-Type。
        connection.putrequest("PUT", path, skip_host=False, skip_accept_encoding=True)
        connection.putheader("Content-Length", str(len(data)))
        connection.endheaders(data)
        response = connection.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"Upload failed with HTTP {response.status}: {body}")
    finally:
        connection.close()


def poll_batch(token: str, batch_id: str, file_name: str, interval: float, timeout_seconds: int) -> dict[str, Any]:
    """轮询批量任务，直到目标文件完成或失败。"""
    deadline = time.time() + timeout_seconds
    url = f"{API_BASE}/extract-results/batch/{batch_id}"
    last_state = ""
    while time.time() < deadline:
        result = request_json("GET", url, token)
        entries = result.get("data", {}).get("extract_result", [])
        target = next((entry for entry in entries if entry.get("file_name") == file_name), None)
        if target is None and entries:
            target = entries[0]
        if target:
            state = target.get("state", "")
            if state != last_state:
                progress = target.get("extract_progress") or {}
                page_text = ""
                if progress:
                    page_text = f" pages={progress.get('extracted_pages')}/{progress.get('total_pages')}"
                print(f"state={state}{page_text}", flush=True)
                last_state = state
            if state == "done":
                if not target.get("full_zip_url"):
                    raise RuntimeError("MinerU task done but full_zip_url is missing")
                return target
            if state == "failed":
                raise RuntimeError(f"MinerU task failed: {target.get('err_msg', '')}")
            if state not in IN_PROGRESS_STATES:
                raise RuntimeError(f"Unexpected MinerU state: {state}")
        time.sleep(interval)
    raise TimeoutError(f"Timed out waiting for MinerU batch {batch_id}")


def download_file(url: str, destination: Path, max_retries: int = 3) -> None:
    """下载解析结果 zip，带重试和 Node.js fallback。"""
    last_error = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                destination.write_bytes(response.read())
            return
        except Exception as exc:
            last_error = exc
            print(f"download attempt {attempt + 1}/{max_retries} failed: {exc}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(3)

    print("Python urllib download failed, trying Node.js fallback...", flush=True)
    try:
        import subprocess
        result = subprocess.run(
            ["node", "-e", f"""
const fs = require('fs');
const https = require('https');
const file = fs.createWriteStream({str(destination)!r});
const req = https.get({url!r}, {{rejectUnauthorized: false, timeout: 60000}}, (res) => {{
  if (res.statusCode !== 200) {{ process.exit(1); }}
  res.pipe(file);
  file.on('finish', () => {{ file.close(); }});
}});
req.on('error', () => process.exit(1));
req.on('timeout', () => {{ req.destroy(); process.exit(1); }});
"""],
            capture_output=True,
            timeout=120,
        )
        if result.returncode == 0 and destination.exists() and destination.stat().st_size > 0:
            print(f"Node.js fallback succeeded ({destination.stat().st_size} bytes)", flush=True)
            return
        last_error = RuntimeError(f"Node.js fallback failed: exit code {result.returncode}")
    except FileNotFoundError:
        last_error = RuntimeError("Node.js not found for download fallback")
    except Exception as exc:
        last_error = exc

    raise RuntimeError(f"Download failed after {max_retries} retries and Node.js fallback: {last_error}")


def find_first(root: Path, names: tuple[str, ...], suffix: str | None = None) -> Path | None:
    """在解压目录中查找第一个匹配文件。"""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in names:
            return path
        if suffix and path.name.endswith(suffix):
            return path
    return None


def normalize_outputs(
    output_dir: Path,
    zip_path: Path,
    source: Path,
    batch_id: str,
    result: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    """解压 MinerU zip，并生成稳定文件名和 manifest。"""
    raw_dir = output_dir / "raw"
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(raw_dir)

    md_path = find_first(raw_dir, ("full.md",), ".md")
    content_list_path = find_first(raw_dir, ("content_list.json",), "_content_list.json")
    if md_path:
        shutil.copy2(md_path, output_dir / "full.md")
    if content_list_path:
        shutil.copy2(content_list_path, output_dir / "content_list.json")

    manifest = {
        "source_file": str(source),
        "batch_id": batch_id,
        "file_name": source.name,
        "state": result.get("state"),
        "data_id": result.get("data_id"),
        "err_msg": result.get("err_msg", ""),
        "model_version": args.model_version,
        "language": args.language,
        "is_ocr": args.ocr,
        "enable_formula": not args.disable_formula,
        "enable_table": not args.disable_table,
        "page_ranges": args.page_ranges,
        "extra_formats": args.extra_format,
        "zip_file": str(zip_path),
        "raw_dir": str(raw_dir),
        "normalized": {
            "full_md": str(output_dir / "full.md") if md_path else None,
            "content_list_json": str(output_dir / "content_list.json") if content_list_path else None,
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """构造命令行参数。"""
    parser = argparse.ArgumentParser(description="Parse a local paper with MinerU precise API.")
    parser.add_argument("file", type=Path, help="Local PDF or document path.")
    parser.add_argument("--env", type=Path, default=Path(".env"), help="Path to .env file.")
    parser.add_argument("--token-env", default="minerU_API", help="Environment variable containing MinerU token.")
    parser.add_argument("--output", type=Path, help="Output directory. Defaults to <file_stem>_mineru.")
    parser.add_argument("--model-version", default="vlm", choices=["vlm", "pipeline", "MinerU-HTML"])
    parser.add_argument("--language", default="ch")
    parser.add_argument("--page-ranges", default=None)
    parser.add_argument("--ocr", action="store_true", help="Enable OCR.")
    parser.add_argument("--disable-formula", action="store_true")
    parser.add_argument("--disable-table", action="store_true")
    parser.add_argument("--extra-format", action="append", default=[], choices=["docx", "html", "latex"])
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--data-id", default=None)
    return parser


def main() -> int:
    """执行本地文件 MinerU 解析流程。"""
    args = build_parser().parse_args()
    source = args.file.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    output_dir = (args.output or source.with_name(f"{source.stem}_mineru")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    token = get_token(args.env.resolve(), args.token_env)
    data_id = args.data_id or source.stem.replace(" ", "_")
    file_item: dict[str, Any] = {"name": source.name, "data_id": data_id, "is_ocr": args.ocr}
    if args.page_ranges:
        file_item["page_ranges"] = args.page_ranges
    payload: dict[str, Any] = {
        "files": [file_item],
        "model_version": args.model_version,
        "enable_formula": not args.disable_formula,
        "enable_table": not args.disable_table,
        "language": args.language,
    }
    if args.extra_format:
        payload["extra_formats"] = args.extra_format

    print("requesting_upload_url", flush=True)
    create_result = request_json("POST", f"{API_BASE}/file-urls/batch", token, payload)
    batch_id = create_result["data"]["batch_id"]
    upload_url = create_result["data"]["file_urls"][0]

    print("uploading_file", flush=True)
    upload_file(upload_url, source)

    print(f"polling_batch={batch_id}", flush=True)
    parse_result = poll_batch(token, batch_id, source.name, args.poll_interval, args.timeout_seconds)

    zip_path = output_dir / "result.zip"
    print("downloading_result_zip", flush=True)
    download_file(parse_result["full_zip_url"], zip_path)
    normalize_outputs(output_dir, zip_path, source, batch_id, parse_result, args)
    print(f"done output={output_dir}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
