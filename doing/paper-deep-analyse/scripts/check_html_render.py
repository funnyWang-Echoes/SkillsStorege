#!/usr/bin/env python3
"""
浏览器侧检查 paper-deep-analyse HTML 的 KaTeX、Mermaid 和公式污染。
"""

import sys
import json
from pathlib import Path

from thresholds import get_rules as _get_profile_rules

PROFILE_RULES = {
    p: {
        "katex_nodes": _get_profile_rules(p).get("katex_nodes", 1),
        "reading_cards": _get_profile_rules(p)["reading_cards"],
        "evidence_blocks": _get_profile_rules(p)["evidence_embeds"],
    }
    for p in ("short", "standard", "long")
}


def main() -> int:
    """用 Playwright 打开 HTML 并检查渲染后的 DOM"""
    if len(sys.argv) not in (3, 5):
        print("Usage: python check_html_render.py <deep-report.html> <short|standard|long> [--json-output <path>]")
        return 1

    html_path = Path(sys.argv[1]).resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}")
        return 1

    profile = sys.argv[2]
    if profile not in PROFILE_RULES:
        print(f"Error: unknown profile {profile}; use short, standard, or long.")
        return 1
    rules = PROFILE_RULES[profile]
    json_output = None
    if len(sys.argv) == 5:
        if sys.argv[3] != "--json-output":
            print("Error: optional argument must be --json-output <path>.")
            return 1
        json_output = Path(sys.argv[4])

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright is not installed; use Browser/chrome-devtools for an equivalent render check.")
        if json_output:
            json_output.parent.mkdir(parents=True, exist_ok=True)
            json_output.write_text(json.dumps({
                "render_check_method": "playwright",
                "analysis_profile": profile,
                "passed": False,
                "unsupported": True,
                "errors": [
                    "playwright is not installed; run Browser/chrome-devtools equivalent check and write browser counts."
                ],
                "katex_errors": None,
                "katex_rendered_nodes": None,
                "mermaid_svg_nodes": None,
                "polluted_math_nodes": None,
                "details_reading_cards": None,
                "evidence_embeds": None,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 2

    url = html_path.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1200)
        katex_errors = page.locator(".katex-error").count()
        katex_nodes = page.locator(".katex").count()
        mermaid_nodes = page.locator(".mermaid svg").count()
        polluted_math = page.locator(".math-block em, .math-block strong, .math-inline em, .math-inline strong").count()
        reading_cards = page.locator("details.reading-card").count()
        evidence_blocks = page.locator(".evidence-embed").count()

        browser.close()

    errors = []
    if katex_errors:
        errors.append(f"katex_errors={katex_errors}")
    if katex_nodes < rules["katex_nodes"]:
        errors.append(f"katex_nodes={katex_nodes} (<{rules['katex_nodes']})")
    if mermaid_nodes < 1:
        errors.append("mermaid_nodes=0")
    if polluted_math:
        errors.append(f"polluted_math_nodes={polluted_math}")
    if reading_cards < rules["reading_cards"]:
        errors.append(f"reading_cards={reading_cards} (<{rules['reading_cards']})")
    if evidence_blocks < rules["evidence_blocks"]:
        errors.append(f"evidence_blocks={evidence_blocks} (<{rules['evidence_blocks']})")

    if errors:
        print("Render check failed: " + "; ".join(errors))
        if json_output:
            json_output.parent.mkdir(parents=True, exist_ok=True)
            json_output.write_text(json.dumps({
                "render_check_method": "playwright",
                "analysis_profile": profile,
                "katex_errors": katex_errors,
                "katex_rendered_nodes": katex_nodes,
                "mermaid_svg_nodes": mermaid_nodes,
                "polluted_math_nodes": polluted_math,
                "details_reading_cards": reading_cards,
                "evidence_embeds": evidence_blocks,
                "passed": False,
                "errors": errors,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 1

    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps({
            "render_check_method": "playwright",
            "analysis_profile": profile,
            "katex_errors": katex_errors,
            "katex_rendered_nodes": katex_nodes,
            "mermaid_svg_nodes": mermaid_nodes,
            "polluted_math_nodes": polluted_math,
            "details_reading_cards": reading_cards,
            "evidence_embeds": evidence_blocks,
            "passed": True,
            "errors": [],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        "Render check passed: "
        f"profile={profile}, katex_nodes={katex_nodes}, mermaid_nodes={mermaid_nodes}, "
        f"reading_cards={reading_cards}, evidence_blocks={evidence_blocks}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
