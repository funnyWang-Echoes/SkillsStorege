#!/usr/bin/env python3
"""
从精读 Markdown 生成带样式的 HTML。
KaTeX 公式、Mermaid 图、论文图片嵌入（base64）、疑问高亮。
"""
import sys
import base64
import re
from pathlib import Path

try:
    import markdown
except ImportError:
    markdown = None

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root {{
  --text:#202124; --muted:#667085; --border:#d9dee7;
  --panel:#ffffff; --soft:#f6f8fb; --accent:#2457a6; --warn:#b45309;
  --resolved:#0F6E56; --unresolved:#993C1D; --partial:#854F0B;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:#eef2f7; color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans SC",sans-serif;
  line-height:1.8;
}}
main {{ max-width:900px; margin:0 auto; padding:32px 24px 56px; background:var(--panel); min-height:100vh; }}
h1 {{ margin:0 0 1rem; padding-bottom:1rem; border-bottom:3px solid #111827; font-size:clamp(1.5rem,3vw,2.4rem); line-height:1.2; }}
h2 {{ margin-top:2.5rem; padding-top:1rem; border-top:1px solid var(--border); color:#111827; }}
h3 {{ margin-top:1.8rem; color:#1f2937; }}
h4 {{ margin-top:1.4rem; color:#374151; }}
a {{ color:var(--accent); }}
code {{ background:#eef2ff; color:#1e3a8a; padding:.1rem .3rem; border-radius:3px; font-size:.9em; }}
pre {{ background:#111827; color:#f9fafb; padding:1rem; overflow-x:auto; border-radius:6px; }}
pre code {{ background:transparent; color:inherit; padding:0; }}
blockquote {{ border-left:4px solid var(--border); margin:.8rem 0; padding:.4rem 0 .4rem 1rem; color:#374151; background:#fafafa; }}
table {{ border-collapse:collapse; width:100%; margin:1.2rem 0; display:block; overflow-x:auto; }}
th,td {{ border:1px solid var(--border); padding:.5rem .7rem; text-align:left; vertical-align:top; }}
th {{ background:var(--soft); font-weight:600; }}
img {{ max-width:100%; height:auto; display:block; margin:1rem auto; border:1px solid var(--border); border-radius:6px; background:#fff; }}
figure {{ margin:1.5rem 0; }}
figcaption,.img-caption {{ color:var(--muted); font-size:.9rem; text-align:center; margin-top:.4rem; font-style:italic; }}
.doubt {{ border-left:4px solid var(--warn); background:#fff7ed; padding:.6rem 1rem; margin:.8rem 0; border-radius:0 6px 6px 0; }}
.translation {{ background:var(--soft); border-left:3px solid var(--accent); padding:.6rem 1rem; margin:.5rem 0 1rem; border-radius:0 6px 6px 0; }}
.analysis {{ margin:.5rem 0; }}
.analysis ul {{ margin:.3rem 0; }}
hr {{ border:none; border-top:1px solid var(--border); margin:2rem 0; }}
.meta-box {{ background:var(--soft); border:1px solid var(--border); border-radius:8px; padding:1rem 1.2rem; margin:1rem 0; }}
.meta-box table {{ margin:0; }}
.meta-box th,.meta-box td {{ border:none; }}
.code-appendix {{ background:#f8f9fb; border:1px solid var(--border); border-radius:8px; padding:.5rem 1rem; margin:2rem 0; }}
.code-appendix h3 {{ border-bottom:1px solid var(--border); padding-bottom:.5rem; }}
@media (max-width:720px) {{
  main {{ padding:20px 14px 40px; }}
  h1 {{ font-size:1.5rem; }}
  th,td {{ min-width:120px; }}
}}
</style>
<script>
window.addEventListener('DOMContentLoaded', function() {{
  if (window.renderMathInElement) {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{left:'$$',right:'$$',display:true}},
        {{left:'$',right:'$',display:false}},
        {{left:'\\\\(',right:'\\\\)',display:false}},
        {{left:'\\\\[',right:'\\\\]',display:true}}
      ],
      throwOnError:false
    }});
  }}
  if (window.mermaid) {{ mermaid.initialize({{startOnLoad:true,securityLevel:'loose'}}); }}
}});
</script>
</head>
<body>
<main>
{content}
</main>
</body>
</html>'''


def get_mime_type(ext):
    types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp'}
    return types.get(ext.lower(), 'image/png')


def embed_image(img_path):
    """把本地图片转成 base64 data URI"""
    data = img_path.read_bytes()
    mime = get_mime_type(img_path.suffix)
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def process_images(content, base_dir):
    """把 Markdown 图片语法中的本地路径转成 base64"""
    def resolve_src(src):
        if src.startswith(("http://", "https://", "data:")):
            return src
        img_path = (base_dir / src).resolve()
        if img_path.exists():
            return embed_image(img_path)
        return src

    def replace_md_img(match):
        alt, src = match.groups()
        return f'![{alt}]({resolve_src(src.strip())})'

    def replace_html_img(match):
        before, src, after = match.groups()
        return f'<img{before}src="{resolve_src(src.strip())}"{after}>'

    # 修复跨行拆断的图片语法
    content = re.sub(r'!\[([^\]]*)\]\s*\n\s*\(([^)]+)\)', replace_md_img, content)
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_img, content)
    content = re.sub(r'<img([^>]*?)src=["\']([^"\']+)["\']([^>]*)>', replace_html_img, content)
    return content


def protect_math(content):
    """保护数学公式不被 Markdown 污染"""
    blocks = []
    def store(text, display):
        wrapper = "div" if display else "span"
        cls = "math-block" if display else "math-inline"
        left, right = ("$$","$$") if display else ("\\(","\\)")
        blocks.append(f'<{wrapper} class="{cls}">{left}\n{text.strip()}\n{right}</{wrapper}>')
        return f"@@MATH_{len(blocks)-1}@@"
    protected = re.sub(r'\$\$\s*\n?(.*?)\n?\s*\$\$', lambda m: store(m.group(1), True), content, flags=re.S)
    protected = re.sub(r'\\\[\s*(.*?)\s*\\\]', lambda m: store(m.group(1), True), protected, flags=re.S)
    protected = re.sub(r'\\\(\s*(.*?)\s*\\\)', lambda m: store(m.group(1), False), protected, flags=re.S)
    protected = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', lambda m: store(m.group(1), False), protected)
    return protected, blocks


def restore_math(content, blocks):
    for i, block in enumerate(blocks):
        content = content.replace(f"<p>@@MATH_{i}@@</p>", block)
        content = content.replace(f"@@MATH_{i}@@", block)
    return content


def process_mermaid(content):
    return re.sub(r'```mermaid\s*\n(.*?)\n```', lambda m: f'<div class="mermaid">\n{m.group(1).strip()}\n</div>', content, flags=re.S)


def md_to_html(md, base_dir):
    if not markdown:
        raise RuntimeError("Missing dependency: markdown. pip install markdown")
    md = process_mermaid(md)
    md = process_images(md, base_dir)
    protected, blocks = protect_math(md)
    html = markdown.markdown(protected, extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html'])
    html = restore_math(html, blocks)
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_reading_html.py <reading.md> [output.html]")
        sys.exit(1)
    md_path = Path(sys.argv[1]).resolve()
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)
    output_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else md_path.with_suffix('.html')

    content = md_path.read_text(encoding='utf-8')
    title_match = re.search(r'^#\s+(.+)$', content, re.M)
    title = title_match.group(1) if title_match else "Paper Reading"

    try:
        html_content = md_to_html(content, md_path.parent)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    html = HTML_TEMPLATE.format(title=title, content=html_content)
    output_path.write_text(html, encoding='utf-8')
    print(f"Generated: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
