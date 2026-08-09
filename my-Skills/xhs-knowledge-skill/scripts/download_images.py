"""
批量下载 notes 图片到本地 assets/<noteId>/

Usage:
    python download_images.py --input ../outputs/feed-detail/details_full_20.json

Output:
    outputs/assets/<noteId>/01.jpg
    outputs/assets/<noteId>/02.jpg
    ...
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
from urllib.parse import urlparse, unquote

import requests


REFERER = "https://www.xiaohongshu.com/"
DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 第五轮 P2 fix：列出支持格式（README/SKILL.md 对应）
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def _is_private_host(url: str) -> bool:
    """第五轮 P2 fix：SSRF 防御。检查 URL host 是否是私网 IP / localhost。

    小红书 CDN 是公网，正常情况不会命中；但 details JSON 被污染时
    `images[].urlClean` 可能是 `http://127.0.0.1:9222/...` 之类。
    """
    try:
        from urllib.parse import urlparse
        import ipaddress
        hostname = urlparse(url).hostname or ""
        if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return True
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return False  # hostname 不是 IP，不在私网阻断范围
    except Exception:
        return False  # 出错时放行（避免误杀）


def guess_ext(url: str, content_type: str | None, detected_mime: str | None = None) -> str:
    """
    决定扩展名的优先级：
    1. detected_mime（用 file/magic 检测到的真实类型，最准）
    2. content_type（HTTP 响应头）
    3. URL 路径（最不可靠，小红书 URL 路径常带 .jpg 但实际是 WebP）
    4. 默认 .jpg
    """
    mime_map = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    if detected_mime and detected_mime in mime_map:
        return mime_map[detected_mime]
    if content_type:
        for mime, e in mime_map.items():
            if mime in content_type:
                return e
    # URL 路径（最不可靠，但作为兜底）
    path = urlparse(url).path
    _, ext = os.path.splitext(unquote(path))
    if ext and ext.lower() in ALLOWED_EXTS:
        return ext.lower()
    return ".jpg"


def detect_real_mime(file_path: str) -> str | None:
    """用 file 命令或 magic 检测真实 mime 类型

    P1-8 fix: 只接受 image/* 开头的合法 MIME，否则返回 None
    防止 file 命令报错信息（如 'cannot open ...'）被当成 MIME
    """
    # 优先用 file 命令（Windows 下 Git Bash 自带）
    try:
        out = subprocess.run(
            ["file", "--mime-type", "-b", file_path],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        # P1-8: 严格校验：必须以 image/ 开头
        if out.startswith("image/"):
            return out
    except Exception:
        pass
    # 备用：用 magic 库（python-magic-bin 在 Windows 上可用）
    try:
        import magic
        mime = magic.from_file(file_path, mime=True)
        if mime and mime.startswith("image/"):
            return mime
    except Exception:
        pass
    # 最后备用：用文件头 magic bytes 简易判断
    try:
        with open(file_path, "rb") as f:
            head = f.read(12)
        if head.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if head.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if head[:4] == b"GIF8":
            return "image/gif"
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            return "image/webp"
    except Exception:
        pass
    return None


def download_one(url: str, dst: str, retries: int = 3) -> tuple[bool, str]:
    """下载单张图片，失败重试"""
    # 第五轮 P2 fix：SSRF 防御
    if _is_private_host(url):
        return False, "blocked: private/loopback host"
    headers = {
        "Referer": REFERER,
        "User-Agent": DEFAULT_UA,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    last_err = ""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=30, stream=True)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")
            # 检测是否返回了 HTML（防盗链常见）
            if "text/html" in ct and len(r.content) < 1024:
                last_err = f"got HTML (likely 403), content-type={ct}"
                _cleanup_partial(dst)
                time.sleep(1)
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            size = os.path.getsize(dst)
            if size < 100:
                last_err = f"file too small ({size}B)"
                _cleanup_partial(dst)
                continue
            return True, f"{size}B"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"[:120]
            _cleanup_partial(dst)  # 第三轮 P2-11 fix：retry 失败时也删占位
            time.sleep(1)
    return False, last_err


def _cleanup_partial(dst: str):
    """删除半成品文件（任意大小都删）"""
    try:
        if os.path.exists(dst):
            os.remove(dst)
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="details JSON 路径")
    parser.add_argument(
        "--output-root",
        default=os.path.join(SCRIPT_DIR, "..", "outputs", "assets"),
        help="assets 根目录",
    )
    parser.add_argument("--max-imgs-per-note", type=int, default=20)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="第三轮 N-2 fix：开跑前删除 note 目录下所有非 webp/jpg/png 的 stray 文件 "
             "（如子代理 OCR 时手动 ffmpeg 转出的 .png）。",
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    notes = data.get("notes", [])
    print(f"[OK] {len(notes)} 条笔记")

    # 第三轮 N-2 fix：先清 stray 文件再跑（如果开了 --clean）
    # download_images 默认只产 webp/jpg，stray .png 是子代理 OCR 时手动 ffmpeg 转码写入的。
    if args.clean:
        cleaned = 0
        for note in notes:
            nid = note["noteId"]
            note_dir = os.path.join(args.output_root, nid)
            if not os.path.isdir(note_dir):
                continue
            for f in os.listdir(note_dir):
                if not f.lower().endswith(".png"):
                    continue
                try:
                    os.remove(os.path.join(note_dir, f))
                    cleaned += 1
                except OSError:
                    pass
        print(f"[CLEAN] 删 {cleaned} 个 stray .png（子代理 OCR 残留）")

    summary = {"ok": 0, "fail": 0, "skipped": 0, "by_note": []}

    for i, note in enumerate(notes):
        note_id = note["noteId"]
        title = note["title"][:25]
        images = note.get("images", [])
        if note.get("video"):
            # video 笔记暂不下载（按 plan）
            summary["by_note"].append(
                {"noteId": note_id, "title": title, "skipped": "video"}
            )
            summary["skipped"] += 1
            continue

        note_dir = os.path.join(args.output_root, note_id)
        os.makedirs(note_dir, exist_ok=True)

        note_result = {"noteId": note_id, "title": title, "imgs_ok": 0, "imgs_fail": 0}

        for idx, img in enumerate(images[: args.max_imgs_per_note]):
            url = img.get("urlClean") or img.get("urlWatermarked")
            if not url:
                note_result["imgs_fail"] += 1
                continue
            ext = guess_ext(url, None)
            dst = os.path.join(note_dir, f"{idx + 1:02d}{ext}")
            if args.skip_existing and os.path.exists(dst) and os.path.getsize(dst) > 1024:
                # 第二轮 P1-B7 fix：阈值 100 byte → 1024 byte。
                # 原 100 byte 太低，会把 retry 中途断网留下的几十字节垃圾文件
                # 误判为「已下载成功」，下次跑就跳过了。
                note_result["imgs_ok"] += 1
                continue

            ok, info = download_one(url, dst)
            if ok:
                # 检测真实类型，如果跟扩展名不匹配就改名
                real_mime = detect_real_mime(dst)
                if real_mime:
                    mime_map = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "image/gif": ".gif",
                        "image/webp": ".webp",
                        "image/bmp": ".bmp",
                    }
                    correct_ext = mime_map.get(real_mime, ext)
                    if correct_ext != ext:
                        new_dst = os.path.join(note_dir, f"{idx + 1:02d}{correct_ext}")
                        if os.path.exists(new_dst):
                            os.remove(new_dst)
                        os.rename(dst, new_dst)
                note_result["imgs_ok"] += 1
                summary["ok"] += 1
            else:
                note_result["imgs_fail"] += 1
                summary["fail"] += 1
                print(f"  [{i + 1:02d}/{len(notes)}] {title:25} img{idx+1} FAIL: {info[:60]}")

        summary["by_note"].append(note_result)
        total_imgs = note_result["imgs_ok"] + note_result["imgs_fail"]
        print(
            f"  [{i + 1:02d}/{len(notes)}] {title:30} | imgs={total_imgs} "
            f"(ok={note_result['imgs_ok']}, fail={note_result['imgs_fail']})"
        )

    print()
    print(f"[DONE] 下载完成: {summary['ok']} 张成功, {summary['fail']} 失败, "
          f"{summary['skipped']} 跳过")
    # 保存 summary
    summary_path = os.path.join(args.output_root, "_download_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 摘要: {summary_path}")


if __name__ == "__main__":
    main()