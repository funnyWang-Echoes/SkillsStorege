#!/usr/bin/env python3
"""
从综合 report.md 生成 paper-deep-analyse HTML 技术报告。
"""

import sys
import base64
import re
from pathlib import Path

try:
    import markdown
except ImportError:
    markdown = None


REQUIRED_SECTIONS = [
    "执行摘要",
    "主要贡献判别",
    "研究脉络",
    "原文对照逐段精读",
    "存疑清单",
    "方法机制",
    "论证链",
    "实验审计",
    "代码审计",
    "相关论文发散",
    "Reviewer-style Critique",
    "可迁移启发",
]

PROFILE_RULES = {
    "short": {
        "reading_cards": 4,
        "reading_card_chars": 180,
        "reading_section_chars": 1200,
        "method_section_chars": 900,
        "mechanism_blocks": 1,
        "mechanism_block_chars": 220,
        "evidence_total": 2,
        "mineru_images": 0,
        "table_evidence": 1,
    },
    "standard": {
        "reading_cards": 6,
        "reading_card_chars": 220,
        "reading_section_chars": 2200,
        "method_section_chars": 1500,
        "mechanism_blocks": 2,
        "mechanism_block_chars": 280,
        "evidence_total": 3,
        "mineru_images": 1,
        "table_evidence": 1,
    },
    "long": {
        "reading_cards": 8,
        "reading_card_chars": 250,
        "reading_section_chars": 3200,
        "method_section_chars": 2200,
        "mechanism_blocks": 3,
        "mechanism_block_chars": 320,
        "evidence_total": 4,
        "mineru_images": 2,
        "table_evidence": 2,
    },
}


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
            --text:#202124;
            --muted:#667085;
            --border:#d9dee7;
            --panel:#ffffff;
            --soft:#f6f8fb;
            --accent:#2457a6;
            --warn:#b45309;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: #eef2f7;
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
            line-height: 1.78;
        }}
        main {{
            max-width: 1080px;
            margin: 0 auto;
            padding: 32px 24px 56px;
            background: var(--panel);
            min-height: 100vh;
        }}
        h1 {{
            margin: 0 0 1rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #111827;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.18;
        }}
        h2 {{
            margin-top: 2.4rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            color: #111827;
        }}
        h3 {{ margin-top: 1.6rem; color: #1f2937; }}
        a {{ color: var(--accent); }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.25rem auto;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: #fff;
        }}
        figure {{ margin: 1.4rem 0; }}
        figcaption {{ color: var(--muted); font-size: .92rem; text-align: center; }}
        pre {{
            background: #111827;
            color: #f9fafb;
            padding: 1rem;
            overflow-x: auto;
            border-radius: 6px;
        }}
        code {{
            background: #eef2ff;
            color: #1e3a8a;
            padding: .12rem .35rem;
            border-radius: 4px;
        }}
        pre code {{ background: transparent; color: inherit; padding: 0; }}
        blockquote {{
            border-left: 4px solid var(--border);
            margin: .8rem 0;
            padding: .5rem 0 .5rem 1rem;
            color: #374151;
            background: #fafafa;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.2rem 0;
            display: block;
            overflow-x: auto;
        }}
        th, td {{ border: 1px solid var(--border); padding: .6rem .75rem; text-align: left; vertical-align: top; }}
        th {{ background: var(--soft); font-weight: 700; }}
        .reading-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 1.2rem 0;
            background: #fff;
            box-shadow: 0 1px 2px rgba(15,23,42,.05);
        }}
        details.reading-card > summary {{
            cursor: pointer;
            font-weight: 700;
            color: #111827;
            list-style: none;
        }}
        details.reading-card > summary::-webkit-details-marker {{ display: none; }}
        details.reading-card > summary::before {{
            content: "展开";
            display: inline-block;
            margin-right: .55rem;
            padding: .08rem .45rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            color: var(--accent);
            font-size: .78rem;
            font-weight: 650;
        }}
        details.reading-card[open] > summary::before {{ content: "收起"; }}
        .source-locator {{ font-size: .86rem; color: var(--muted); margin-bottom: .4rem; }}
        .reading-card blockquote {{ margin: .5rem 0 1rem; }}
        .evidence-embed {{
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: .85rem;
            margin: 1.1rem 0;
            background: #fbfdff;
        }}
        .math-block {{
            overflow-x: auto;
            padding: .5rem 0;
        }}
        .doubt {{
            border-left: 4px solid var(--warn);
            background: #fff7ed;
            padding: .85rem 1rem;
            margin: 1rem 0;
        }}
        .claim-table td:nth-child(4), .claim-table td:nth-child(5) {{ font-weight: 650; }}
        .mermaid {{ margin: 1.3rem 0; background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }}
        @media (max-width: 720px) {{
            main {{ padding: 22px 14px 44px; }}
            h1 {{ font-size: 2rem; }}
            th, td {{ min-width: 140px; }}
        }}
    </style>
    <script>
      window.addEventListener('DOMContentLoaded', function() {{
        if (window.renderMathInElement) {{
          renderMathInElement(document.body, {{
            delimiters: [
              {{left: '$$', right: '$$', display: true}},
              {{left: '$', right: '$', display: false}},
              {{left: '\\\\(', right: '\\\\)', display: false}},
              {{left: '\\\\[', right: '\\\\]', display: true}}
            ],
            throwOnError: false
          }});
        }}
        if (window.mermaid) {{
          mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
        }}
      }});
    </script>
</head>
<body>
<main>
{content}
</main>
</body>
</html>'''


def get_mime_type(ext: str) -> str:
    """获取图片 MIME 类型"""
    types = {'.png': 'image/png', '.jpg': 'image/jpeg',
             '.jpeg': 'image/jpeg', '.gif': 'image/gif'}
    return types.get(ext.lower(), 'image/png')


def embed_image(img_path: Path) -> str:
    """将图片转换为 base64"""
    with open(img_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    mime = get_mime_type(img_path.suffix)
    return f"data:{mime};base64,{data}"


def detect_profile(content: str) -> str:
    """读取 report.md 中显式声明的分析档位"""
    patterns = [
        r"^analysis_profile\s*:\s*(short|standard|long)\s*$",
        r"^分析档位\s*[：:]\s*(short|standard|long|短|标准|长)\s*$",
        r"analysis_profile\s*:\s*(short|standard|long)",
    ]
    aliases = {"短": "short", "标准": "standard", "长": "long"}
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.I | re.M)
        if match:
            value = match.group(1).lower()
            return aliases.get(value, value)
    raise ValueError(
        "report.md must explicitly declare analysis_profile: short|standard|long "
        "near the top; do not rely on an implicit default profile."
    )


def process_images(content: str, base_dir: Path) -> str:
    """处理 Markdown/HTML 图片，转换为可直接渲染的 HTML img"""
    def resolve_src(src: str) -> str:
        if src.startswith(("http://", "https://", "data:")):
            return src
        img_path = (base_dir / src).resolve()
        if img_path.exists():
            return embed_image(img_path)
        return src

    def replace_split_img(match):
        alt, src = match.groups()
        return f'<img src="{resolve_src(src.strip())}" alt="{alt}">'

    def replace_markdown_img(match):
        alt, src = match.groups()
        return f'<img src="{resolve_src(src.strip())}" alt="{alt}">'

    def replace_html_img(match):
        before, src, after = match.groups()
        return f'<img{before}src="{resolve_src(src.strip())}"{after}>'

    # 修正错误拆成两行的图片语法：![alt]\n(path)
    content = re.sub(r'!\[([^\]]*)\]\s*\n\s*\(([^)]+)\)', replace_split_img, content)
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_markdown_img, content)
    return re.sub(r'<img([^>]*?)src=["\']([^"\']+)["\']([^>]*)>', replace_html_img, content)


def render_evidence_blocks(content: str) -> str:
    """单独渲染 evidence-embed 内的 Markdown，确保表格和图片不变成纯文本"""
    if not markdown:
        return content

    pattern = re.compile(r'(<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>)(.*?)(</div>)', re.S)

    def replace_block(match):
        start, inner, end = match.groups()
        rendered = markdown.markdown(inner.strip(), extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html'])
        return f"{start}\n{rendered}\n{end}"

    return pattern.sub(replace_block, content)


def process_mermaid(content: str) -> str:
    """将 fenced mermaid 代码块转换为 Mermaid 可渲染节点"""
    pattern = re.compile(r"```mermaid\s*\n(.*?)\n```", re.S)
    return pattern.sub(lambda match: f'<div class="mermaid">\n{match.group(1).strip()}\n</div>', content)


def protect_math(content: str) -> tuple[str, list[str]]:
    """保护数学公式，避免 Markdown 把下划线/星号转换成 HTML 标签"""
    math_blocks: list[str] = []

    def store_math(text: str, display: bool) -> str:
        body = text.strip()
        wrapper = "div" if display else "span"
        cls = "math-block" if display else "math-inline"
        left, right = ("$$", "$$") if display else ("\\(", "\\)")
        math_blocks.append(f'<{wrapper} class="{cls}">{left}\n{body}\n{right}</{wrapper}>')
        return f"@@MATH_BLOCK_{len(math_blocks) - 1}@@"

    def replace_dollar_display(match):
        return store_math(match.group(1), True)

    def replace_bracket_display(match):
        return store_math(match.group(1), True)

    def replace_paren_inline(match):
        return store_math(match.group(1), False)

    def replace_dollar_inline(match):
        return store_math(match.group(1), False)

    protected = re.sub(r"\$\$\s*\n?(.*?)\n?\s*\$\$", replace_dollar_display, content, flags=re.S)
    protected = re.sub(r"\\\[\s*(.*?)\s*\\\]", replace_bracket_display, protected, flags=re.S)
    protected = re.sub(r"\\\(\s*(.*?)\s*\\\)", replace_paren_inline, protected, flags=re.S)
    protected = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", replace_dollar_inline, protected)
    return protected, math_blocks


def restore_math(content: str, math_blocks: list[str]) -> str:
    """恢复被保护的数学公式"""
    for index, block in enumerate(math_blocks):
        placeholder = f"@@MATH_BLOCK_{index}@@"
        content = content.replace(f"<p>{placeholder}</p>", block)
        content = content.replace(placeholder, block)
    return content


def validate_source_math(content: str) -> None:
    """预检源 Markdown 中公式格式，避免已知渲染失败模式"""
    tag_numbers = re.findall(r"\\tag\{([^}]+)\}", content)
    for tag_number in tag_numbers:
        escaped_tag = re.escape(tag_number)
        tag_match = re.search(rf"\$\$.*?\\tag\{{{escaped_tag}\}}.*?\$\$", content, flags=re.S)
        tag_match = tag_match or re.search(rf"\\\[.*?\\tag\{{{escaped_tag}\}}.*?\\\]", content, flags=re.S)
        if not tag_match:
            raise ValueError(f"Formula tag {tag_number} must be in a display math block ($$...$$ or \\[...\\]).")
        tag_source = tag_match.group(0)
        if "{r_j}" in tag_source and "\\{r_j\\}" not in tag_source:
            raise ValueError(
                f"Formula tag {tag_number} appears to use unescaped brace groups; "
                "use \\{r_j\\}_{j=1}^{G}."
            )


def validate_rendered_math(html: str) -> None:
    """阻断明显被 Markdown 污染的公式块"""
    math_fragments = re.findall(r'<(?:div|span) class="math-(?:block|inline)">(.*?)</(?:div|span)>', html, flags=re.S)
    for block in math_fragments:
        if re.search(r"</?(em|strong|a|code|span)\b", block):
            raise ValueError("Rendered math block contains HTML tags; protect or rewrite the formula before export.")
        if "\\tag{4}" in block and ("<em" in block or "</em>" in block):
            raise ValueError("Formula tag 4 appears corrupted by Markdown emphasis.")


def md_to_html(md_content: str) -> str:
    """Markdown 转 HTML"""
    if not markdown:
        raise RuntimeError(
            "Missing dependency: markdown. Install it before generating the deep report HTML; "
            "the fallback converter is intentionally disabled to avoid losing tables, code, "
            "Mermaid, and embedded HTML report structures."
        )
    validate_source_math(md_content)
    protected, math_blocks = protect_math(md_content)
    protected = render_evidence_blocks(protected)
    html = markdown.markdown(
        protected,
        extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html']
    )
    html = restore_math(html, math_blocks)
    validate_rendered_math(html)
    validate_rendered_evidence(html)
    return html


def validate_rendered_evidence(html: str) -> None:
    """阻断 evidence block 中残留未渲染的 Markdown 图片或表格"""
    blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>(.*?)</div>', html, flags=re.S)
    for index, block in enumerate(blocks, start=1):
        if re.search(r'!\[[^\]]*\]\s*(?:\(|$)', block):
            raise ValueError(f"evidence-embed {index} contains unrendered Markdown image syntax.")
        if re.search(r'^\s*\|.+\|\s*$', block, flags=re.M):
            raise ValueError(f"evidence-embed {index} contains an unrendered Markdown table.")


def count_reading_cards(content: str) -> int:
    """统计 HTML 母稿中的原文对照卡片"""
    return len(extract_details_reading_cards(content))


def extract_details_reading_cards(content: str) -> list[str]:
    """抽取所有可折叠 reading card"""
    return re.findall(r'<details\b[^>]*class=["\'][^"\']*reading-card[^"\']*["\'][^>]*>.*?</details>', content, flags=re.S)


def reject_non_collapsible_cards(content: str) -> None:
    """拒绝非 details 的 reading card"""
    non_details = re.findall(r'<(?!details\b)([a-zA-Z0-9]+)\b[^>]*class=["\'][^"\']*reading-card', content)
    if non_details:
        raise ValueError("Every reading-card must use <details class=\"reading-card\">, not section/div cards.")


def validate_reading_cards(content: str, rules: dict) -> None:
    """逐卡检查 close reading 的字段和厚度"""
    reject_non_collapsible_cards(content)
    cards = extract_details_reading_cards(content)
    min_cards = rules["reading_cards"]
    if len(cards) < min_cards:
        raise ValueError(f"report.md must contain at least {min_cards} collapsible reading-card blocks, found {len(cards)}.")
    required = ["<summary", "source-locator", "原文对照展开", "原文要点转述", "论证作用", "分析思考", "证据联动", "存疑", "追问"]
    for index, card in enumerate(cards, start=1):
        missing = [field for field in required if field not in card]
        if missing:
            raise ValueError(f"reading-card {index} is missing fields: {', '.join(missing)}.")
        min_chars = rules["reading_card_chars"]
        if plain_length(card) < min_chars:
            raise ValueError(f"reading-card {index} is too thin; require at least {min_chars} non-space chars.")
        has_evidence_block = "evidence-embed" in card
        has_evidence_reference = re.search(r"(Figure|Fig\.|Table|Eq\.|公式|表格|图|代码|code)", card) is not None
        if not has_evidence_block and not has_evidence_reference:
            raise ValueError(f"reading-card {index} must include evidence linkage to a figure/table/formula/code point.")
        source_expanded = re.search(r'<div\b[^>]*class=["\'][^"\']*source-expanded[^"\']*["\'][^>]*>(.*?)</div>', card, flags=re.S)
        if not source_expanded:
            raise ValueError(f"reading-card {index} must include <div class=\"source-expanded\"> for source-aligned reading.")
        expanded_text = source_expanded.group(1)
        snippet_count = len(re.findall(r"(短摘|原文短句|source snippet|excerpt)", expanded_text, flags=re.I))
        has_translation = re.search(r"(中文译述|对应翻译|转述|译文)", expanded_text) is not None
        if snippet_count < 2 or not has_translation:
            raise ValueError(
                f"reading-card {index} source-expanded must contain at least 2 short source snippets "
                "with Chinese translation/paraphrase, not only one summary sentence."
            )


def validate_evidence_explanations(content: str) -> None:
    """检查图表和公式解释是否足够可读"""
    evidence_blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>(.*?)</div>', content, flags=re.S)
    required_evidence_fields = ["读图", "关键元素", "支撑", "不支持", "边界"]
    for index, block in enumerate(evidence_blocks, start=1):
        if "<img" not in block and "<table" not in block and not re.search(r"^\s*\|.+\|\s*$", block, flags=re.M):
            continue
        missing = [field for field in required_evidence_fields if field not in block]
        if missing:
            raise ValueError(
                f"evidence-embed {index} needs richer figure/table analysis; missing: {', '.join(missing)}."
            )

    formula_like_blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*(?:formula-analysis|mechanism-block)[^"\']*["\'][^>]*>(.*?)</div>', content, flags=re.S)
    formula_blocks = [block for block in formula_like_blocks if re.search(r"(\$\$|\\\[|\\\(|公式|Eq\.)", block)]
    for index, block in enumerate(formula_blocks, start=1):
        required_formula_fields = ["变量", "直觉", "设计动机", "边界"]
        missing = [field for field in required_formula_fields if field not in block]
        if missing:
            raise ValueError(
                f"formula/mechanism analysis block {index} is too thin; missing: {', '.join(missing)}."
            )


def extract_section(content: str, heading: str) -> str:
    """抽取二级标题下的 Markdown 内容"""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", content, flags=re.M)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", content[match.end():], flags=re.M)
    end = match.end() + next_match.start() if next_match else len(content)
    return content[match.end():end]


def plain_length(text: str) -> int:
    """估算去掉标签和空白后的正文长度"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def count_mineru_local_images(content: str) -> int:
    """统计指向 MinerU 本地解析产物的图片"""
    image_paths = re.findall(r'(?:!\[[^\]]*\]\(|<img\b[^>]*src=["\'])([^)"\']+)', content)
    return sum(1 for path in image_paths if "mineru" in path.lower() and not path.startswith(("http://", "https://", "data:")))


def count_reconstructed_table_evidence(content: str) -> int:
    """统计包含重建表格或关键数字的 evidence block"""
    blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>(.*?)</div>', content, flags=re.S)
    count = 0
    for block in blocks:
        has_table = "<table" in block or re.search(r"^\s*\|.+\|\s*$", block, flags=re.M)
        has_numeric_label = any(label in block for label in ["关键数字", "数字摘录", "重建表格", "Reconstructed", "Numeric evidence"])
        numeric_values = re.findall(r"\d+(?:\.\d+)?", block)
        if has_table or (has_numeric_label and len(numeric_values) >= 3):
            count += 1
    return count


def validate_method_mechanisms(content: str, rules: dict) -> None:
    """检查方法机制是否逐机制展开，而不是总长度灌水"""
    method_section = extract_section(content, "方法机制")
    mechanism_blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*mechanism-block[^"\']*["\'][^>]*>(.*?)</div>', method_section, flags=re.S)
    min_blocks = rules["mechanism_blocks"]
    if len(mechanism_blocks) < min_blocks:
        raise ValueError(f"方法机制 must include at least {min_blocks} <div class=\"mechanism-block\"> blocks.")
    required = ["定义", "设计动机", "失败模式", "边界", "证据"]
    for index, block in enumerate(mechanism_blocks, start=1):
        missing = [field for field in required if field not in block]
        if missing:
            raise ValueError(f"mechanism-block {index} is missing fields: {', '.join(missing)}.")
        min_chars = rules["mechanism_block_chars"]
        if plain_length(block) < min_chars:
            raise ValueError(f"mechanism-block {index} is too thin; require at least {min_chars} non-space chars.")


def validate_report_path(md_path: Path) -> None:
    """确保输入是 notes/report.md，避免跳过综合母稿流程"""
    normalized = [part.lower() for part in md_path.parts]
    if md_path.name.lower() != "report.md" or "notes" not in normalized:
        raise ValueError("Input must be the paper's notes/report.md.")


def validate_report_content(content: str) -> None:
    """轻量检查 report.md 是否具备深度报告骨架"""
    profile = detect_profile(content)
    rules = PROFILE_RULES[profile]
    missing = [section for section in REQUIRED_SECTIONS if section not in content]
    if missing:
        raise ValueError("report.md is missing required sections: " + ", ".join(missing))

    validate_reading_cards(content, rules)

    if "Author-claimed" not in content and "作者 claim" not in content and "作者自称" not in content:
        raise ValueError("report.md must include author-claimed contribution entries.")

    if "存疑" not in content:
        raise ValueError("report.md must include a doubt ledger or doubt annotations.")

    method_section = extract_section(content, "方法机制")
    reading_section = extract_section(content, "原文对照逐段精读")
    if plain_length(method_section) < rules["method_section_chars"]:
        raise ValueError(
            f"方法机制 section is too thin for {profile} profile; "
            f"require at least {rules['method_section_chars']} non-space chars."
        )
    if plain_length(reading_section) < rules["reading_section_chars"]:
        raise ValueError(
            f"原文对照逐段精读 section is too thin for {profile} profile; "
            f"require at least {rules['reading_section_chars']} non-space chars."
        )
    validate_method_mechanisms(content, rules)
    validate_evidence_explanations(content)

    evidence_embeds = len(re.findall(r'class=["\'][^"\']*evidence-embed', content))
    local_images = len(re.findall(r'!\[[^\]]*\]\((?!https?://|data:)[^)]+\)', content))
    if evidence_embeds + local_images < rules["evidence_total"]:
        raise ValueError(
            f"report.md must embed at least {rules['evidence_total']} local figure/table evidence blocks "
            f"for {profile} profile, not only mention Figure/Table IDs."
        )
    mineru_images = count_mineru_local_images(content)
    table_evidence = count_reconstructed_table_evidence(content)
    if mineru_images < rules["mineru_images"]:
        raise ValueError(
            f"report.md must include at least {rules['mineru_images']} MinerU local images "
            f"for {profile} profile, found {mineru_images}."
        )
    if table_evidence < rules["table_evidence"]:
        raise ValueError(
            f"report.md must include at least {rules['table_evidence']} reconstructed table/numeric evidence blocks "
            f"for {profile} profile, found {table_evidence}."
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_html.py <report.md> [output.html]")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2] if len(sys.argv) > 2 else "article.html")

    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    try:
        validate_report_path(md_path)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        validate_report_content(content)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    # 保留 report.md 为内容母稿，仅在生成阶段处理图片和 Markdown。
    base_dir = md_path.parent
    content = process_mermaid(content)
    content = process_images(content, base_dir)

    # 转换为 HTML
    try:
        html_content = md_to_html(content)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.M)
    title = title_match.group(1) if title_match else "Article"

    # 生成完整 HTML
    html = HTML_TEMPLATE.format(title=title, content=html_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
