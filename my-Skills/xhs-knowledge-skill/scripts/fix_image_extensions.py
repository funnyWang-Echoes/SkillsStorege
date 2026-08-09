"""
修复脚本：把错的 .jpg 重命名为正确的扩展名（WebP），并修改 MD 中的引用
- 用 file --mime-type 检测真实类型
- 重命名文件
- 同步 MD 中 ![[assets/<noteId>/NN.jpg]] → ![[assets/<noteId>/NN.webp]]
"""
import re
import subprocess
from pathlib import Path


EXT_MAP = {
    "webp": ".webp",
    "jpeg": ".jpg",
    "jpg":  ".jpg",
    "png":  ".png",
    "gif":  ".gif",
}


def real_mime(path: Path) -> str:
    try:
        out = subprocess.run(
            ["file", "--mime-type", "-b", str(path)],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        return out.split("/")[-1]
    except Exception:
        return ""


def main():
    base = Path(__file__).resolve().parent.parent / "outputs"
    assets_root = base / "assets"
    md_root = base / "knowledge"

    # 1) 检测并重命名文件
    rename_log = []
    for note_dir in sorted(assets_root.iterdir()):
        if not note_dir.is_dir():
            continue
        for f in sorted(note_dir.iterdir()):
            if not f.is_file():
                continue
            mime = real_mime(f)
            new_ext = EXT_MAP.get(mime)
            if not new_ext:
                continue
            cur_ext = f.suffix.lower()
            if cur_ext == new_ext:
                continue
            new_path = f.parent / (f.stem + new_ext)
            if new_path.exists():
                new_path.unlink()
            f.rename(new_path)
            rename_log.append((note_dir.name, f.name, new_path.name))

    print(f"[OK] Renamed {len(rename_log)} files")
    for n, old, new in rename_log[:3]:
        print(f"     {n}: {old} -> {new}")
    if len(rename_log) > 3:
        print(f"     ... and {len(rename_log) - 3} more")

    # 2) 同步 MD 引用
    md_pattern = re.compile(r"!\[\[assets/([^/]+)/(\d+)\.jpg\]\]")
    md_changes = []
    for md_file in md_root.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        new_text = text
        # 用 dict 缓存查找结果
        lookup_cache = {}

        def lookup(note_id, idx):
            key = (note_id, idx)
            if key in lookup_cache:
                return lookup_cache[key]
            d = assets_root / note_id
            ext = ".jpg"  # fallback
            if d.exists():
                for f in d.iterdir():
                    if f.stem == idx:
                        ext = f.suffix.lower()
                        break
            lookup_cache[key] = ext
            return ext

        def replace_ref(m):
            note_id = m.group(1)
            idx = m.group(2)
            ext = lookup(note_id, idx)
            return f"![[assets/{note_id}/{idx}{ext}]]"

        new_text = md_pattern.sub(replace_ref, text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            old_count = len(md_pattern.findall(text))
            md_changes.append((md_file.name, old_count))

    print(f"[OK] Updated {len(md_changes)} MD files")
    for name, n in md_changes[:5]:
        print(f"     {name}: {n} refs")


if __name__ == "__main__":
    main()