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
  --text:#1a1a2e; --muted:#6b7280; --border:#e5e7eb;
  --panel:#fafaf7; --soft:#f5f5f0; --accent:#1e3a5f;
  --warn:#92400e; --resolved:#065f46; --unresolved:#9b1c1c; --partial:#92400e;
  --translation-bg:#f8f6f0; --translation-border:#c9b890;
  --analysis-bg:#f6f8fb; --analysis-border:#6b8caf;
  --code-bg:#1e1e2e; --code-text:#cdd6f4;
  --question-bg:#fef3c7; --question-text:#78350f;
  --echo-color:#1e6b52; --doubt-color:#92400e;
  --serif:"Noto Serif SC","Source Han Serif SC",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",Roboto,sans-serif;
  --mono:"JetBrains Mono","Fira Code",Consolas,monospace;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0; background:#e8e6df; color:var(--text);
  font-family:var(--sans); font-size:16px; line-height:1.85;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}}
main {{
  max-width:920px; margin:0 auto; padding:48px 40px 80px;
  background:var(--panel); min-height:100vh;
  box-shadow:0 0 40px rgba(0,0,0,.04);
}}
h1 {{
  margin:0 0 1.5rem; padding-bottom:1.2rem;
  border-bottom:2px solid var(--accent);
  font-family:var(--serif); font-size:clamp(1.6rem,3.5vw,2.2rem);
  line-height:1.3; color:var(--accent); font-weight:700;
  letter-spacing:-.01em;
}}
h2 {{
  margin-top:3rem; margin-bottom:1rem; padding:.6rem 0 .6rem 1rem;
  border-left:4px solid var(--accent);
  font-family:var(--serif); font-size:1.5rem; color:var(--accent);
  font-weight:600; line-height:1.3;
  background:linear-gradient(90deg, rgba(30,58,95,.04) 0%, transparent 60%);
}}
h3 {{
  margin-top:2rem; margin-bottom:.8rem;
  font-family:var(--sans); font-size:1.15rem; color:#2d3748;
  font-weight:600; line-height:1.4;
  padding-bottom:.3rem; border-bottom:1px dashed var(--border);
}}
h4 {{ margin-top:1.5rem; color:#4a5568; font-size:1rem; font-weight:600; }}
p {{ margin:.8rem 0; }}
a {{ color:var(--accent); text-decoration:none; border-bottom:1px solid transparent; transition:border-color .15s; }}
a:hover {{ border-bottom-color:var(--accent); }}
strong {{ color:#1a202c; font-weight:600; }}
em {{ color:#4a5568; }}

/* 段落精读块 */
h3 + p, h3 + div {{ margin-top:0; }}

/* 翻译区 */
.translation {{
  background:var(--translation-bg);
  border-left:3px solid var(--translation-border);
  padding:1rem 1.4rem; margin:1rem 0 1.2rem;
  border-radius:0 8px 8px 0;
  font-family:var(--serif); font-size:1.02rem; line-height:1.9;
  color:#2d3748;
  position:relative;
}}
.translation::before {{
  content:"译"; position:absolute; top:.6rem; right:.9rem;
  font-family:var(--sans); font-size:.7rem; font-weight:700;
  color:var(--translation-border); opacity:.6;
  letter-spacing:.05em;
}}

/* 分析区 */
.analysis {{
  background:var(--analysis-bg);
  border-left:3px solid var(--analysis-border);
  padding:.8rem 1.2rem; margin:.6rem 0 1.2rem;
  border-radius:0 6px 6px 0;
}}
.analysis ul {{ margin:.4rem 0; padding-left:1.4rem; list-style:none; }}
.analysis li {{ margin:.35rem 0; padding-left:.2rem; position:relative; }}
.analysis li::before {{ content:"▸"; position:absolute; left:-1rem; color:var(--analysis-border); font-size:.85em; }}

/* 疑问 pill */
.question-pill {{
  display:inline-block;
  background:var(--question-bg); color:var(--question-text);
  padding:.2rem .7rem; border-radius:12px;
  font-size:.88rem; font-weight:500;
  margin:.3rem 0;
}}

/* 代码 */
code {{
  font-family:var(--mono); font-size:.88em;
  background:#eef2f7; color:#1e3a5f;
  padding:.12rem .35rem; border-radius:3px;
}}
pre {{
  background:var(--code-bg); color:var(--code-text);
  padding:1.2rem 1.4rem; overflow-x:auto;
  border-radius:8px; font-family:var(--mono);
  font-size:.85rem; line-height:1.6;
  margin:1rem 0;
}}
pre code {{ background:transparent; color:inherit; padding:0; font-size:inherit; }}

/* 引用 */
blockquote {{
  border-left:3px solid var(--border);
  margin:1rem 0; padding:.5rem 0 .5rem 1.2rem;
  color:#4a5568; background:transparent;
  font-style:italic;
}}

/* 表格 */
table {{
  border-collapse:collapse; width:100%; margin:1.5rem 0;
  font-size:.92rem; display:block; overflow-x:auto;
  border-radius:6px; overflow:hidden;
}}
th,td {{ border:1px solid var(--border); padding:.6rem .9rem; text-align:left; vertical-align:top; }}
th {{ background:var(--accent); color:#fff; font-weight:600; font-size:.85rem; letter-spacing:.02em; }}
tbody tr:nth-child(even) {{ background:var(--soft); }}
tbody tr:hover {{ background:#eef2f7; }}

/* 图片 */
img {{
  max-width:100%; height:auto; display:block;
  margin:1.5rem auto; border-radius:8px;
  box-shadow:0 4px 16px rgba(0,0,0,.08);
  background:#fff;
}}
figure {{ margin:2rem 0; text-align:center; }}
figcaption,.img-caption {{
  color:var(--muted); font-size:.88rem; text-align:center;
  margin-top:.6rem; font-style:italic; line-height:1.5;
  max-width:80%; margin-left:auto; margin-right:auto;
}}

/* 元信息盒 */
.meta-box {{
  background:var(--soft); border:1px solid var(--border);
  border-radius:10px; padding:1.2rem 1.6rem; margin:1.5rem 0;
}}
.meta-box table {{ margin:0; }}
.meta-box th,.meta-box td {{ border:none; padding:.25rem .8rem; }}

/* 代码附录 */
.code-appendix {{
  background:#f8f9fb; border:1px solid var(--border);
  border-radius:10px; padding:.5rem 1.4rem 1.4rem; margin:2rem 0;
}}
.code-appendix h3 {{
  border-bottom:2px solid var(--accent);
  padding-bottom:.6rem; margin-top:1rem;
}}

/* 分隔线 */
hr {{ border:none; border-top:1px solid var(--border); margin:3rem 0; }}

@media (max-width:720px) {{
  main {{ padding:28px 18px 50px; }}
  h1 {{ font-size:1.4rem; }}
  h2 {{ font-size:1.25rem; }}
  .translation,.analysis {{ padding:.7rem .9rem; font-size:.95rem; }}
  th,td {{ min-width:100px; padding:.4rem .5rem; font-size:.85rem; }}
  pre {{ padding:.8rem; font-size:.78rem; }}
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


def post_process_reading_blocks(html):
    """把 **中文翻译：** 和 **即时分析：** 标记转成带 class 的 div，让 CSS 能精确匹配"""
    # 把 <p><strong>中文翻译：</strong>...</p> 转成 <div class="translation"><strong>中文翻译：</strong>...</div>
    html = re.sub(
        r'<p><strong>(中文翻译[：:].*?)</strong>(.*?)</p>',
        lambda m: f'<div class="translation"><strong>{m.group(1)}</strong>{m.group(2)}</div>',
        html, flags=re.S
    )
    # 多段翻译：把连续的翻译段合并
    html = re.sub(
        r'(</div>)\s*<p><strong>(中文翻译（段)',
        r'\1\n<div class="translation"><strong>\2',
        html
    )

    # 即时分析
    html = re.sub(
        r'<p><strong>(即时分析[：:].*?)</strong>(.*?)</p>',
        lambda m: f'<div class="analysis"><strong>{m.group(1)}</strong>{m.group(2)}</div>',
        html, flags=re.S
    )
    # 多段分析
    html = re.sub(
        r'(</div>)\s*<p><strong>(即时分析（段)',
        r'\1\n<div class="analysis"><strong>\2',
        html
    )

    # 疑问标记转 pill
    html = re.sub(
        r'<p><strong>(疑问\s*Q\d+[：:].*?)</strong>(.*?)</p>',
        lambda m: f'<div class="question-pill"><strong>{m.group(1)}</strong>{m.group(2)}</div>',
        html, flags=re.S
    )

    # 图注（斜体段落在图片后）
    html = re.sub(
        r'<p><em>(\*?.*?图\s*\d+.*?)</em></p>',
        lambda m: f'<p class="img-caption">{m.group(1).strip("*")}</p>',
        html, flags=re.S
    )

    return html


def md_to_html(md, base_dir):
    if not markdown:
        raise RuntimeError("Missing dependency: markdown. pip install markdown")
    md = process_mermaid(md)
    md = process_images(md, base_dir)
    protected, blocks = protect_math(md)
    html = markdown.markdown(protected, extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html'])
    html = restore_math(html, blocks)
    html = post_process_reading_blocks(html)
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
