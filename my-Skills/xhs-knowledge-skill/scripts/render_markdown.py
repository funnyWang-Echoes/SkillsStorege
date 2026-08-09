"""
按 analysis.type 渲染 4 类 MD 文档到 outputs/knowledge/<type>/

Usage:
    python render_markdown.py \
      --details ../outputs/feed-detail/details_full_20.json \
      --intermediate ../outputs/intermediate/ \
      --output ../outputs/knowledge/

Outputs:
    outputs/knowledge/projects/<noteId>_<slug>.md
    outputs/knowledge/blogs/<noteId>_<slug>.md
    outputs/knowledge/skills/<noteId>_<slug>.md
    outputs/knowledge/papers/<noteId>_<slug>.md
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# ---------- 工具 ----------

def slugify(text: str, max_len: int = 50) -> str:
    """生成文件名安全的 slug：保留中英文数字 + 短横线

    第五轮 P2 fix：CJK 扩展 A (`\\u3400-\\u4dbf`) + 兼容汉字 (`\\uf900-\\ufaff`)。
    扩展 B (`\\U00020000-\\U0002a6df`) 需要 surrogate pair，超出基本平面，
    Python str 长度统计会爆 —— 不在默认范围，需要时单独处理。
    """
    if not text:
        return "untitled"
    text = re.sub(r'[^\w\s\-\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = text.lstrip('-')
    return text[:max_len].lstrip('-') or "untitled"


def ts_to_date(ms: int | None) -> str:
    """毫秒时间戳 → YYYY-MM-DD"""
    if not ms:
        return ""
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def frontmatter_yaml(note: dict, analysis: dict, type_label: str) -> str:
    """生成 Obsidian 友好的 YAML frontmatter"""
    fm = {
        "noteId": note.get("noteId"),
        "type": type_label,
        "title": analysis.get("title") or note.get("title"),
        "author": (note.get("author") or {}).get("nickname"),
        "source": note.get("sourceMeta", {}).get("feedUrl") or f'https://www.xiaohongshu.com/explore/{note.get("noteId")}',
        "tags": analysis.get("tags") or note.get("tags") or [],
        "created": datetime.now().strftime("%Y-%m-%d"),
    }
    # 互动数据
    interact = note.get("interact") or {}
    if interact:
        fm["interact"] = {
            k: v for k, v in interact.items() if v is not None
        }
    # 时间
    pub_date = ts_to_date(note.get("time"))
    if pub_date:
        fm["published"] = pub_date
    ip = note.get("ipLocation")
    if ip:
        fm["ipLocation"] = ip

    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {yaml_escape(item)}")
        elif isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {yaml_escape(vv)}")
        else:
            lines.append(f"{k}: {yaml_escape(v)}")
    lines.append("---")
    return "\n".join(lines)


def yaml_escape(v) -> str:
    """YAML 字符串/布尔/数字通用序列化（兼容所有 YAML 解析器）

    第五轮 P2 fix：补 `!`（YAML 显式类型标签）和控制字符（\\n \\t \\x00）。
    """
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v) if v is not None else ""
    special_chars = [":", "#", "&", "*", "!", "[", "]", "{", "}", "|", ">", "'", chr(34), "%", "@", "`"]
    needs_quote = (
        any(c in s for c in special_chars)
        or s.startswith("-")
        or s.startswith("?")
        or any(ord(c) < 0x20 for c in s)  # 控制字符（\n \t \x00 等）
    )
    if needs_quote:
        return "'" + s.replace("'", "''") + "'"
    return s


def sanitize_url(value: str, key: str = "url") -> str:
    """第三轮 N-1 P0 fix：URL 字段白名单校验。

    子代理 OCR 出来的 `links.github` 可能是 `ZJU-REAL/Polaris`（丢 `github.com/`），
    `links.arxiv` 可能是 `2607.28618`（丢 `https://arxiv.org/abs/`）。
    原模板原样渲染成 `[残缺字符串](残缺字符串)`，用户点开 404。

    这里做严格白名单：URL 必须以 `http://` 或 `https://` 开头，否则当成不可信。
    """
    if not value or not isinstance(value, str):
        return ""
    v = value.strip()
    if not v:
        return ""
    if not (v.startswith("http://") or v.startswith("https://")):
        return ""
    # 防 xsec_token 等敏感串被渲染到 MD
    if "xsec_token" in v or "xsecToken" in v:
        return ""
    return v


def sanitize_links(links: dict) -> dict:
    """对整个 links 字典跑 sanitize_url，过滤掉所有不合格字段。"""
    if not isinstance(links, dict):
        return {}
    return {k: sanitize_url(v, k) for k, v in links.items() if sanitize_url(v, k)}


def _render_links_detailed(links: dict) -> str:
    """第五轮 P2 fix：project/skill/paper 模板的详细链接区块（带 emoji + 加粗）。

    4 模板共用，文案统一。
    """
    link_lines = []
    items = [
        ("github", "🔗 **GitHub**"),
        ("homepage", "🌐 **官网**"),
        ("arxiv", "📄 **论文**"),
        ("demo", "🎯 **Demo**"),
    ]
    for key, label in items:
        url = sanitize_url(links.get(key), key)
        if url:
            link_lines.append(f"- {label}：[{url}]({url})")
    return "\n".join(link_lines) if link_lines else ""


def _render_links_simple(links: dict) -> str:
    """第五轮 P2 fix：blog 模板的简洁链接区块（无 emoji）。

    4 模板共用，文案统一。
    """
    link_lines = []
    items = [
        ("github", "GitHub"),
        ("homepage", "官网"),
        ("arxiv", "论文"),
        ("demo", "Demo"),
    ]
    for key, label in items:
        url = sanitize_url(links.get(key), key)
        if url:
            link_lines.append(f"- {label}：[{url}]({url})")
    return "\n".join(link_lines) if link_lines else ""


def clean_desc(desc: str) -> str:
    """第三轮 N-2 P2 fix：把 desc 里的连续空白（\\n\\t 等）压成单个空格。

    小红书 desc 含大量 `\\n\\t`（笔记段落标记），直接渲染到 MD 会出现满屏空行。
    """
    if not desc:
        return ""
    import re
    # 把所有空白字符（含全角空格 \u3000）压成单个半角空格
    return re.sub(r"[\s\u3000]+", " ", desc).strip()


# 敏感 token 标记（出现这些子串的字段值会被替换成空字符串）
_SENSITIVE_TOKENS = ("xsec_token=", "xsecToken=")


def redact_sensitive(obj):
    """递归遍历 dict/list/str，把含敏感 token 的字符串值清空。

    第三轮 N-3 P2 fix：子代理 OCR 时如果把 `sourceMeta.feedUrl` 里的 token
    粘到 `links.*` 或 `keyPoints` 等字段，渲染 MD 会泄露。统一在 main() 入口
    对 analysis JSON 跑一次脱敏。

    注意：details JSON 的 `sourceMeta.feedUrl` 是合法的（用于回链），不要动；
    只清 analysis JSON 里冒出来的敏感串。
    """
    if isinstance(obj, dict):
        return {k: redact_sensitive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_sensitive(v) for v in obj]
    if isinstance(obj, str):
        for tok in _SENSITIVE_TOKENS:
            if tok in obj:
                return ""  # 含敏感 token 整段清空
        return obj
    return obj


def images_block(note_id: str, image_count: int, assets_root: str = "", md_dir: str = "") -> str:
    """生成标准 Markdown 图片引用（兼容所有 MD 软件）

    Args:
        note_id: 笔记 ID
        image_count: 该笔记图片数
        assets_root: assets 根目录（默认 SCRIPT_DIR/../outputs/assets）
        md_dir: MD 文件所在目录（用于计算相对路径）

    Returns:
        Markdown 图片引用块（多行）

    修复点（P1-1, P1-2）：
    - 用真实文件扫描获取扩展名（不硬编码 .webp）
    - 用 os.path.relpath 计算 MD 到图片的相对路径（不假设固定目录结构）
    """
    if image_count == 0:
        return "_（无配图）_"

    if not assets_root:
        assets_root = os.path.join(SCRIPT_DIR, "..", "outputs", "assets")

    note_dir = os.path.join(assets_root, note_id)

    lines = []
    for i in range(1, image_count + 1):
        # 扫描真实文件拿到扩展名（P1-2 fix: 不硬编码 .webp）
        ext = ".webp"  # fallback
        if os.path.isdir(note_dir):
            for f in os.listdir(note_dir):
                if f.startswith(f"{i:02d}."):
                    ext = os.path.splitext(f)[1].lower() or ext
                    break
        # 计算相对路径（P1-1 fix: 不硬编码 ../../assets/...）
        if md_dir:
            img_abs = os.path.join(note_dir, f"{i:02d}{ext}")
            try:
                rel = os.path.relpath(img_abs, md_dir).replace("\\", "/")
            except ValueError:
                rel = f"../../assets/{note_id}/{i:02d}{ext}"
        else:
            # fallback：假设 assets/ 与 knowledge/ 平级（默认 outputs/ 目录结构）
            rel = f"../../assets/{note_id}/{i:02d}{ext}"
        lines.append(f"![{i:02d}{ext}]({rel})")
    return "\n".join(lines)


# ---------- 4 类模板 ----------


def video_block(note: dict) -> str:
    """视频笔记的视频链接区块。

    第二轮 P0-C1 fix：之前文档承诺「视频笔记不下载，仅记录链接」，
    但 4 个模板都没渲染 video.masterUrl/coverUrl，导致视频回链丢失。
    现在统一在 4 个模板的 `## 配图` 前插入本块（仅 type=video 时有内容）。
    """
    video = note.get("video")
    if not video:
        return ""
    master = video.get("masterUrl")
    cover = video.get("coverUrl")
    duration = video.get("duration")
    if not (master or cover):
        return ""

    parts = []
    if duration:
        try:
            parts.append(f"时长 {int(duration)} 秒")
        except (TypeError, ValueError):
            pass
    if master:
        parts.append(f"[视频源文件]({master})")
    if cover:
        parts.append(f"[封面图]({cover})")
    desc = " · ".join(parts)
    return f"\n## 视频\n\n> 🎬 本笔记为视频笔记。{desc}（视频文件未下载，仅记录链接）\n"


def _render_simple_template(
    note: dict,
    analysis: dict,
    md_dir: str,
    type_label: str,
    heading_overview: str,
    heading_links: str,
    extra_section: tuple[str, str] | None = None,
) -> str:
    """project 与 skill 共用模板。

    第二轮 P1-A4 fix：原本 project 和 skill 两个函数 90% 重复（frontmatter、
    链接区块、要点区块、配图区块都相同），抽成单一渲染函数，差异通过
    `type_label`/`heading_overview`/`heading_links`/`extra_section` 参数注入。

    Args:
        note: 笔记 dict
        analysis: analysis JSON
        md_dir: MD 文件所在目录（用于计算图片相对路径）
        type_label: "project" 或 "skill"，写入 YAML frontmatter
        heading_overview: 「项目概述」/「Skill 概述」之类的小节标题
        heading_links: 「项目链接」/「链接」之类
        extra_section: 可选的额外 (heading, content) 二元组，skill 用它加「使用方式」
    """
    fm = frontmatter_yaml(note, analysis, type_label)
    title = analysis.get("title") or note.get("title")
    summary = analysis.get("summary", "")
    key_points = analysis.get("keyPoints", [])
    links = analysis.get("links") or {}

    author = (note.get("author") or {}).get("nickname", "未知")
    source_url = note.get("sourceMeta", {}).get("feedUrl") or \
        f'https://www.xiaohongshu.com/explore/{note.get("noteId")}'
    note_id = note.get("noteId")
    images = note.get("images") or []

    link_block = _render_links_detailed(links) or "_（无外部链接）_"

    key_block = "\n".join(f"- {p}" for p in key_points) if key_points else "_（无）_"

    img_block = images_block(note_id, len(images), md_dir=md_dir)
    vid_block = video_block(note)

    extra = ""
    if extra_section:
        extra = f"\n## {extra_section[0]}\n\n{extra_section[1]}\n"

    return f"""{fm}

# {title}

> 📌 来源：小红书 @{author} · [原帖]({source_url})

## {heading_overview}

{summary}

## {heading_links}

{link_block}

## 核心要点

{key_block}
{extra}
{vid_block}
## 配图

{img_block}

---

*收藏时间：{ts_to_date(note.get("time"))} | IP：{note.get("ipLocation", "")}*
"""


# ---------- 4 类模板 ----------

def render_project(note: dict, analysis: dict, md_dir: str = "") -> str:
    """第二轮 P1-A4 fix：薄壳，调用 _render_simple_template。"""
    return _render_simple_template(
        note, analysis, md_dir,
        type_label="project",
        heading_overview="项目概述",
        heading_links="项目链接",
        extra_section=None,
    )


def render_skill(note: dict, analysis: dict, md_dir: str = "") -> str:
    """第二轮 P1-A4 fix：薄壳。skill 与 project 同模板，额外加「使用方式」占位段。"""
    return _render_simple_template(
        note, analysis, md_dir,
        type_label="skill",
        heading_overview="Skill 概述",
        heading_links="链接",
        extra_section=("使用方式", "_（从原帖截图提取安装/调用方式，见下方配图）_"),
    )


def render_blog(note: dict, analysis: dict, md_dir: str = "") -> str:
    fm = frontmatter_yaml(note, analysis, "blog")
    title = analysis.get("title") or note.get("title")
    summary = analysis.get("summary", "")
    key_points = analysis.get("keyPoints", [])
    desc = note.get("desc", "").strip()
    links = analysis.get("links") or {}

    author = (note.get("author") or {}).get("nickname", "未知")
    source_url = note.get("sourceMeta", {}).get("feedUrl") or \
        f'https://www.xiaohongshu.com/explore/{note.get("noteId")}'
    note_id = note.get("noteId")
    images = note.get("images") or []

    key_block = "\n".join(f"- {p}" for p in key_points) if key_points else "_（无）_"
    desc_block = clean_desc(desc) if desc else "_（原文无文字）_"
    img_block = images_block(note_id, len(images), md_dir=md_dir)
    vid_block = video_block(note)

    link_block = _render_links_simple(links)

    extra_links = f"\n## 相关链接\n\n{link_block}\n" if link_block else ""

    return f"""{fm}

# {title}

> 📌 来源：小红书 @{author} · [原帖]({source_url})

## 文章摘要

{summary}

## 关键要点

{key_block}

## 全文

{desc_block}
{extra_links}
{vid_block}
## 配图

{img_block}

---

*收藏时间：{ts_to_date(note.get("time"))} | IP：{note.get("ipLocation", "")}*
"""


def render_paper(note: dict, analysis: dict, md_dir: str = "") -> str:
    fm = frontmatter_yaml(note, analysis, "paper")
    title = analysis.get("title") or note.get("title")
    summary = analysis.get("summary", "")
    key_points = analysis.get("keyPoints", [])
    desc = note.get("desc", "").strip()
    links = analysis.get("links") or {}
    paper = analysis.get("paper") or {}

    author = (note.get("author") or {}).get("nickname", "未知")
    source_url = note.get("sourceMeta", {}).get("feedUrl") or \
        f'https://www.xiaohongshu.com/explore/{note.get("noteId")}'
    note_id = note.get("noteId")
    images = note.get("images") or []

    paper_lines = []
    if paper.get("title"):
        paper_lines.append(f"- **标题**：{paper['title']}")
    if paper.get("authors"):
        paper_lines.append(f"- **作者**：{paper['authors']}")
    if paper.get("affiliations"):
        paper_lines.append(f"- **机构**：{paper['affiliations']}")
    if paper.get("venue"):
        paper_lines.append(f"- **发表**：{paper['venue']} {paper.get('year', '')}".strip())
    if paper.get("arxivId"):
        arxiv_url = f"https://arxiv.org/abs/{paper['arxivId']}"
        paper_lines.append(f"- **arXiv**：[{paper['arxivId']}]({arxiv_url})")
    # 第三轮 N-1 P0 fix：去掉 links.arxiv 的重复渲染（paper.arxivId 已含），
    # 第五轮 fix：paper 模板里 github 用详细文案（与其他 3 模板一致）
    gh = sanitize_url(links.get("github"), "github")
    if gh:
        paper_lines.append(f"- 🔗 **GitHub**：[{gh}]({gh})")
    paper_block = "\n".join(paper_lines) if paper_lines else "_（未从笔记中提取到论文元信息，见下方收藏者笔记）_"

    collector_note = clean_desc(desc) if desc else "_（笔记 desc 为空，论文解读主要在下方配图中）_"

    key_block = "\n".join(f"- {p}" for p in key_points) if key_points else "_（无）_"

    img_block = images_block(note_id, len(images), md_dir=md_dir)
    vid_block = video_block(note)

    return f"""{fm}

# {title}

> 📌 来源：小红书 @{author} · [原帖]({source_url})

## 论文信息

{paper_block}

## 论文核心要点（AI 总结）

{key_block}

## 收藏者笔记（原作者解读）

{collector_note}
{vid_block}
## 配图（论文截图/示意图）

{img_block}

---

*收藏时间：{ts_to_date(note.get("time"))} | IP：{note.get("ipLocation", "")}*
"""


TEMPLATE_MAP = {
    "project": render_project,
    "skill": render_skill,
    "paper": render_paper,
    "blog": render_blog,
}

OUTPUT_TYPE_DIR = {
    "project": "projects",
    "skill": "skills",
    "paper": "papers",
    "blog": "blogs",
}


# ---------- 主流程 ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", required=True)
    parser.add_argument("--intermediate", required=True, help="analysis JSON 目录")
    parser.add_argument("--output", required=True, help="knowledge 输出根目录")
    args = parser.parse_args()

    with open(args.details, encoding="utf-8") as f:
        data = json.load(f)
    notes = data.get("notes", [])
    print(f"[OK] {len(notes)} 条笔记")

    summary = {"total": 0, "by_type": {}, "files": []}

    for note in notes:
        note_id = note["noteId"]
        analysis_path = os.path.join(args.intermediate, f"{note_id}.analysis.json")
        if not os.path.exists(analysis_path):
            print(f"  [SKIP] {note_id[:12]}…: no analysis file")
            continue

        with open(analysis_path, encoding="utf-8") as f:
            analysis = json.load(f)

        # 第三轮 N-3 fix：渲染前对 analysis 跑一次敏感 token 脱敏
        analysis = redact_sensitive(analysis)

        type_label = analysis.get("type", "blog")
        if type_label not in TEMPLATE_MAP:
            print(f"  [WARN] {note_id[:12]}…: unknown type {type_label}, fallback to blog")
            type_label = "blog"

        renderer = TEMPLATE_MAP[type_label]
        type_dir = OUTPUT_TYPE_DIR[type_label]
        out_dir = os.path.join(args.output, type_dir)
        os.makedirs(out_dir, exist_ok=True)

        slug = slugify(note.get("title", "untitled"))
        out_path = os.path.join(out_dir, f"{note_id}_{slug}.md")
        md_dir = os.path.dirname(out_path)

        md_content = renderer(note, analysis, md_dir=md_dir)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        summary["total"] += 1
        summary["by_type"][type_label] = summary["by_type"].get(type_label, 0) + 1
        summary["files"].append({
            "noteId": note_id,
            "type": type_label,
            "path": out_path,
            "size": os.path.getsize(out_path),
        })
        print(f"  [{type_label:8}] {note.get('title','')[:35]:35} → {os.path.basename(out_path)}")

    # 索引文件
    index_path = os.path.join(args.output, "INDEX.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# 收藏笔记知识库索引\n\n")
        # 第五轮 P2 fix：顶部加 generated 时间戳，让多份 INDEX 共存时可区分
        f.write(f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"共 {summary['total']} 条笔记\n\n")
        for t, n in summary["by_type"].items():
            f.write(f"- **{t}**：{n} 条\n")
        f.write("\n## 全部笔记\n\n")
        for item in summary["files"]:
            rel = os.path.relpath(item["path"], args.output).replace("\\", "/")
            f.write(f"- [{item['noteId'][:16]}…]({rel}) `{item['type']}`\n")

    print()
    print(f"[DONE] 生成 {summary['total']} 个 MD → {args.output}")
    print(f"       类型分布: {summary['by_type']}")
    print(f"       索引: {index_path}")


if __name__ == "__main__":
    main()