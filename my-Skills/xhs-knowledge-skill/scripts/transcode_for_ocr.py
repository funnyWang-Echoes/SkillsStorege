"""
把 outputs/assets/<noteId>/ 下尺寸过大的 webp 转成 PNG，给子代理 OCR 用。

第二轮 P0-A3 fix：SKILL.md 吹了多模态 OCR，但 Read 工具拒绝 >2K 像素的 webp；
之前 retest 18 张图里只有 7 张被 OCR（被人工/子代理手动 ffmpeg 转 PNG），
其余 11 张（10-18.webp + 1.webp）没任何机制让子代理去读。

本脚本：
- 扫 outputs/assets/<noteId>/*.webp
- 对宽>2048 或高>2048 的图用 Pillow 转 PNG
- 输出到 outputs/intermediate/ocr_tmp/<noteId>/<NN>.png
- 跳过已经存在的 PNG（幂等）
- 跳过 <2K 像素的图（让子代理直接读 webp）

Usage:
    python transcode_for_ocr.py [--assets-root outputs/assets] [--ocr-root outputs/intermediate/ocr_tmp] [--threshold 2048]
"""
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("[ERR] Pillow 未装。先跑: pip install Pillow", file=sys.stderr)
    sys.exit(2)


def transcode_one(src: str, dst: str) -> bool:
    """转一张图。返回 True 表示成功。"""
    try:
        with Image.open(src) as im:
            im.save(dst, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"  [WARN] {os.path.basename(src)} 失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-root", default=os.path.join("outputs", "assets"))
    parser.add_argument("--ocr-root", default=os.path.join("outputs", "intermediate", "ocr_tmp"))
    parser.add_argument("--threshold", type=int, default=2048,
                        help="宽或高超过此值才转 PNG，默认 2048")
    args = parser.parse_args()

    if not os.path.isdir(args.assets_root):
        print(f"[ERR] assets 目录不存在: {args.assets_root}")
        sys.exit(1)

    os.makedirs(args.ocr_root, exist_ok=True)

    notes = sorted(d for d in os.listdir(args.assets_root)
                   if os.path.isdir(os.path.join(args.assets_root, d)))

    print(f"[OK] 扫描 {len(notes)} 个 note 目录")

    total_in = 0
    total_out = 0
    total_skip = 0
    total_fail = 0

    for note_id in notes:
        src_dir = os.path.join(args.assets_root, note_id)
        dst_dir = os.path.join(args.ocr_root, note_id)
        os.makedirs(dst_dir, exist_ok=True)

        for fname in sorted(os.listdir(src_dir)):
            if not fname.lower().endswith((".webp", ".jpg", ".jpeg", ".png")):
                continue
            total_in += 1
            src = os.path.join(src_dir, fname)
            base, _ = os.path.splitext(fname)
            dst = os.path.join(dst_dir, f"{base}.png")

            # 幂等：目标已存在则跳过
            if os.path.exists(dst):
                total_skip += 1
                continue

            # 检查尺寸
            try:
                with Image.open(src) as im:
                    w, h = im.size
            except Exception:
                total_fail += 1
                continue

            if max(w, h) <= args.threshold:
                # 尺寸小，子代理可直接读原图，不需要转码
                total_skip += 1
                continue

            if transcode_one(src, dst):
                total_out += 1
            else:
                total_fail += 1

    print(f"[DONE] 扫描 {total_in} 张 → 转码 {total_out}，跳过 {total_skip}，失败 {total_fail}")
    print(f"       输出: {args.ocr_root}")


if __name__ == "__main__":
    main()