#!/usr/bin/env python3
"""
从 report.md 和 HTML 中生成 deep-report-check 草稿。

脚本只自动填写可客观统计的字段；贡献 claim、诊断门、子代理结论等仍需人工补齐。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from thresholds import all_profiles as _all_profiles

PROFILE_RULES = _all_profiles()


def plain_length(text: str) -> int:
    """去掉标签和空白后估算字符数"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def detect_profile(text: str) -> str:
    """强制读取显式 analysis_profile"""
    match = re.search(r"^analysis_profile\s*:\s*(short|standard|long)\s*$", text, flags=re.I | re.M)
    if not match:
        raise ValueError("report.md must contain explicit analysis_profile: short|standard|long")
    return match.group(1).lower()


def detect_profile_reason(text: str) -> str:
    """读取 profile_reason，缺失时返回待补提示"""
    match = re.search(r"^profile_reason\s*:\s*(.+?)\s*$", text, flags=re.I | re.M)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return "TODO: explain why this analysis_profile is appropriate for this paper."


def extract_section(text: str, heading: str) -> str:
    """抽取二级标题章节，容忍标题含前缀/后缀修饰词"""
    match = re.search(rf"^##\s+.*{re.escape(heading)}.*\s*$", text, flags=re.M)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", text[match.end():], flags=re.M)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end():end]


def find_paper_root(report_path: Path) -> Path:
    """从 notes/report.md 反推出论文根目录"""
    if report_path.parent.name.lower() == "notes":
        return report_path.parent.parent
    return report_path.parent


def relative_path(path: Path, root: Path) -> str:
    """尽量输出相对路径，失败时输出原路径"""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def count_reconstructed_table_evidence(text: str) -> int:
    """统计重建表格/关键数字 evidence block"""
    blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>(.*?)</div>', text, flags=re.S)
    count = 0
    for block in blocks:
        has_table = "<table" in block or re.search(r"^\s*\|.+\|\s*$", block, flags=re.M)
        has_numeric_label = any(label in block for label in ["关键数字", "数字摘录", "重建表格", "Reconstructed", "Numeric evidence"])
        numeric_values = re.findall(r"\d+(?:\.\d+)?", block)
        if has_table or (has_numeric_label and len(numeric_values) >= 3):
            count += 1
    return count


def count_math_blocks(text: str) -> int:
    """统计 Markdown/HTML 中的公式或算法片段"""
    display_dollar = len(re.findall(r"\$\$.*?\$\$", text, flags=re.S))
    display_bracket = len(re.findall(r"\\\[.*?\\\]", text, flags=re.S))
    inline_paren = len(re.findall(r"\\\(.*?\\\)", text, flags=re.S))
    inline_dollar = len(re.findall(r"(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)", text))
    return display_dollar + display_bracket + inline_paren + inline_dollar


def count_max_excerpt_words(cards: list[str]) -> int:
    """估算 reading card 中 blockquote 短摘的最长英文词数"""
    max_words = 0
    for card in cards:
        quotes = re.findall(r"<blockquote>(.*?)</blockquote>", card, flags=re.S)
        for quote in quotes:
            words = re.findall(r"[A-Za-z][A-Za-z0-9'-]*", re.sub(r"<[^>]+>", " ", quote))
            max_words = max(max_words, len(words))
    return max_words


def count_related_papers(section: str) -> int:
    """估算进入正文比较的相关论文数量"""
    links = re.findall(r"https?://[^\s)>\"]+", section)
    titled_rows = re.findall(r"^\s*\|.*?(?:arXiv|ICLR|NeurIPS|ICML|ACL|CVPR|EMNLP|AAAI|OpenReview|Papers with Code).*?\|", section, flags=re.I | re.M)
    paper_like_bullets = re.findall(r"^\s*[-*]\s+.*?(?:\(\d{4}\)|20\d{2}|arXiv|OpenReview|NeurIPS|ICLR|ICML|ACL|CVPR)", section, flags=re.I | re.M)
    return max(len(links), len(titled_rows), len(paper_like_bullets))


def has_translation_pairs(card: str) -> bool:
    """判断 reading card 是否包含多条原文短句和中文译述"""
    source_expanded = re.search(r'<div\b[^>]*class=["\'][^"\']*source-expanded[^"\']*["\'][^>]*>(.*?)</div>', card, flags=re.S)
    if not source_expanded:
        return False
    expanded = source_expanded.group(1)
    snippet_count = len(re.findall(r"(短摘|原文短句|source snippet|excerpt)", expanded, flags=re.I))
    has_translation = re.search(r"(中文译述|对应翻译|转述|译文)", expanded) is not None
    return snippet_count >= 2 and has_translation


def count_rich_evidence_blocks(report: str) -> int:
    """统计包含完整图表解释字段的 evidence block"""
    blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*evidence-embed[^"\']*["\'][^>]*>(.*?)</div>', report, flags=re.S)
    required = ["读图", "关键元素", "支撑", "不支持", "边界"]
    return sum(1 for block in blocks if all(field in block for field in required))


def count_evidence_points(report: str, paper_root: Path) -> int:
    """优先从 evidence-matrix.md 统计证据点，退回正文证据标记"""
    matrix_path = paper_root / "notes" / "evidence-matrix.md"
    if matrix_path.exists():
        matrix = matrix_path.read_text(encoding="utf-8")
        ids = re.findall(r"\bE\d{2,}\b", matrix)
        if ids:
            return len(set(ids))
        rows = [line for line in matrix.splitlines() if line.strip().startswith("|") and "---" not in line]
        return max(0, len(rows) - 1)
    ids = re.findall(r"\bE\d{2,}\b", report)
    if ids:
        return len(set(ids))
    return len(re.findall(r"(Figure|Fig\.|Table|Eq\.|公式|表格|图|代码|消融|局限|威胁)", report))


def missing_image_paths(report: str, report_path: Path) -> list[str]:
    """检查 report.md 中本地图片路径是否存在"""
    missing: list[str] = []
    image_paths = re.findall(r'(?:!\[[^\]]*\]\(|<img\b[^>]*src=["\'])([^)"\']+)', report)
    for raw_path in image_paths:
        if raw_path.startswith(("http://", "https://", "data:")):
            continue
        candidate = (report_path.parent / raw_path).resolve()
        if not candidate.exists():
            missing.append(raw_path)
    return missing


def collect_counts(report_path: Path, html_path: Path, render_method: str) -> dict:
    """收集可自动生成的 deep-report-check 字段"""
    report = report_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    paper_root = find_paper_root(report_path)
    profile = detect_profile(report)
    rules = PROFILE_RULES[profile]
    cards = re.findall(r'<details\b[^>]*class=["\'][^"\']*reading-card[^"\']*["\'][^>]*>.*?</details>', report, flags=re.S)
    all_card_like = re.findall(r'<[a-zA-Z0-9]+\b[^>]*class=["\'][^"\']*reading-card', report)
    evidence_cards = [card for card in cards if re.search(r"(Figure|Fig\.|Table|Eq\.|公式|表格|图|代码|code|evidence-embed)", card)]
    source_expanded_cards = [card for card in cards if re.search(r'<div\b[^>]*class=["\'][^"\']*source-expanded', card)]
    translation_pair_cards = [card for card in cards if has_translation_pairs(card)]
    mechanism_blocks = re.findall(r'<div\b[^>]*class=["\'][^"\']*mechanism-block[^"\']*["\'][^>]*>(.*?)</div>', report, flags=re.S)
    mechanism_lengths = [plain_length(block) for block in mechanism_blocks] or [0]
    card_lengths = [plain_length(card) for card in cards] or [0]
    related_section = extract_section(report, "相关论文发散")

    draft = {
        "paper_slug": paper_root.name,
        "html_path": relative_path(html_path, paper_root),
        "analysis_profile": profile,
        "profile_reason": detect_profile_reason(report),
        "thresholds_used": rules,
        "mineru_used": (paper_root / "mineru" / "manifest.json").exists(),
        "reading_cards": len(cards),
        "details_reading_cards": len(cards),
        "non_details_reading_cards": max(0, len(all_card_like) - len(cards)),
        "reading_cards_with_evidence_linkage": len(evidence_cards),
        "source_expanded_cards": len(source_expanded_cards),
        "reading_cards_with_translation_pairs": len(translation_pair_cards),
        "min_reading_card_chars": min(card_lengths),
        "evidence_points": count_evidence_points(report, paper_root),
        "related_papers_in_body": count_related_papers(related_section),
        "formulas": count_math_blocks(report),
        "figures_or_tables": len(re.findall(r"(<figure\b|<img\b|<table\b|!\[[^\]]*\]\(|\b(?:Figure|Fig\.|Table)\s*\d+)", report, flags=re.I)),
        "evidence_embeds": len(re.findall(r'class=["\'][^"\']*evidence-embed', report)),
        "mineru_local_images": len(re.findall(r'(?:!\[[^\]]*\]\(|<img\b[^>]*src=["\'])([^)"\']*mineru[^)"\']*)', report, flags=re.I)),
        "reconstructed_table_evidence": count_reconstructed_table_evidence(report),
        "rich_evidence_blocks": count_rich_evidence_blocks(report),
        "unrendered_markdown_images": len(re.findall(r'!\[[^\]]*\]\s*(?:\(|$)', html)),
        "unrendered_markdown_tables": len(re.findall(r'^\s*\|.+\|\s*$', html, flags=re.M)),
        "custom_tables": len(re.findall(r"<table\b", html)),
        "code_blocks": len(re.findall(r"```(?:python|bash|shell|yaml|json|javascript|js|c|cpp|rust|go|java|ruby|php|sql|html|css|text|diff)?\s*\n", report, flags=re.I)) + len(re.findall(r"<pre\b", html)),
        "mermaid_svg_nodes": len(re.findall(r'<div\b[^>]*class=["\'][^"\']*mermaid', html)) or len(re.findall(r'```mermaid', report)),
        "katex_rendered_nodes": len(re.findall(r'class="[^"]*katex', html)) or len(re.findall(r'class="[^"]*math-(?:block|inline)', html)),
        "formula_render_errors": re.findall(r'katex-error', html),
        "math_source_checked": True,
        "render_check_method": render_method,
        "method_section_chars": plain_length(extract_section(report, "方法机制")),
        "reading_section_chars": plain_length(extract_section(report, "原文对照逐段精读")),
        "mechanism_blocks": len(mechanism_blocks),
        "min_mechanism_block_chars": min(mechanism_lengths),
        "max_excerpt_words": count_max_excerpt_words(cards),
        "long_quote_risk": count_max_excerpt_words(cards) > 25,
        "paper_references_dir_exists": (paper_root / "references").exists(),
        "report_md_path": relative_path(report_path, paper_root),
        "report_md_generated_first": True,
        "doubt_items": len(re.findall(r"存疑", report)),
        "image_paths_missing": missing_image_paths(report, report_path),
        "manual_fields_required": [
            "render_check_method",
            "katex_rendered_nodes",
            "mermaid_svg_nodes",
            "diagnostic_gate",
            "contribution_claims",
            "contribution_summary",
            "subagent_review",
        ],
        "diagnostic_gate": {
            "performed": True,
            "decision": "continue",
            "iterations": 1,
            "fatal_flaws": [],
            "adjustments": ["TODO: summarize diagnostic gate decision and any refocus/profile changes."],
        },
        "contribution_claims": [
            {
                "id": "C01",
                "author_claim": "TODO: copy/paraphrase one author-claimed contribution from Abstract/Introduction.",
                "source_location": "TODO: source section/page",
                "independent_category": "存疑",
                "novelty_judgment": "TODO: judge whether this is true innovation, engineering improvement, integration, validation, packaging, or uncertain.",
                "evidence": "TODO: link to Figure/Table/Eq/related-work evidence",
                "caveat_or_doubt": "TODO: state caveat or doubt.",
            }
        ],
        "contribution_summary": {
            "total": 1,
            "true_innovation": 0,
            "engineering_improvement": 0,
            "application_integration": 0,
            "experiment_validation": 0,
            "repackaging": 0,
            "uncertain": 1,
        },
        "subagent_review": {
            "attempted": False,
            "supported": False,
            "model": "gpt-5.4-mini",
            "verdict": "unsupported",
            "result": "TODO: replace with fixed reviewer result, or state that subagent review is unsupported and describe equivalent main-agent checks.",
            "findings_count": 0,
        },
    }
    return draft


def parse_args(argv: list[str]) -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Generate an objective deep-report-check draft.")
    parser.add_argument("report_md", help="Path to notes/report.md")
    parser.add_argument("html", help="Path to output deep-report.html")
    parser.add_argument("--render-method", choices=["playwright", "browser", "chrome-devtools"], default="browser")
    parser.add_argument("--output", help="Write draft JSON to this path instead of stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """输出或写入 deep-report-check 草稿"""
    args = parse_args(argv or sys.argv[1:])
    try:
        draft = collect_counts(Path(args.report_md), Path(args.html), args.render_method)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(draft, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote draft: {output_path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
