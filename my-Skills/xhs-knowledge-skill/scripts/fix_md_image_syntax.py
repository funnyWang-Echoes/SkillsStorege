"""
把 Obsidian 双链 ![[assets/...]] 转换为标准 Markdown ![](./...)

兼容策略：
- Obsidian 也能解析标准语法 ![](path)
- Typora / VS Code / Logseq / Notion 都支持标准语法
- 相对路径基于 MD 文件所在目录计算
"""
import os
import re
from pathlib import Path


def main():
    md_root = Path(__file__).resolve().parent.parent / "outputs" / "knowledge"

    # Obsidian 双链 -> 标准 markdown
    obsidian_pattern = re.compile(r"!\[\[assets/([^/]+)/(\d+\.\w+)\]\]")

    md_changes = 0
    ref_changes = 0

    for md_file in md_root.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")

        def replace_obsidian(m):
            nonlocal ref_changes
            note_id = m.group(1)
            fname = m.group(2)
            # 相对路径：从 md_file 出发
            # md_file 在 .../knowledge/<type>/xxx.md
            # 目标在 .../assets/<noteId>/<fname>
            # 相对路径 = ../../assets/<noteId>/<fname>
            rel = f"../../assets/{note_id}/{fname}"
            ref_changes += 1
            return f"![{fname}]({rel})"

        new_text = obsidian_pattern.sub(replace_obsidian, text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            md_changes += 1
            print(f"  [OK] {md_file.name}")

    print(f"\n[DONE] Updated {md_changes} MD files, {ref_changes} image refs converted")


if __name__ == "__main__":
    main()