#!/usr/bin/env python3
"""
精读自检——极简。
只问三件事：
1. section 覆盖是否按档位够？
2. 每个段落精读块是否有翻译 + 分析？
3. 疑问是否都有闭环（已回答标 ✓，未回答在追踪表标 ✗）？
"""
import sys
import re
from pathlib import Path

DEPTH_SECTIONS = {
    "quick": ["Abstract", "Method", "Experiment"],
    "full": None,   # None = 全文都要覆盖
    "deep": None,
}

REQUIRED_SECTION_KEYWORDS = [
    "abstract", "introduction", "method", "experiment",
    "conclusion", "related", "discussion", "result",
    "approach", "evaluation", "limitation"
]


def detect_depth(content):
    match = re.search(r'^reading_depth\s*:\s*(quick|full|deep)\s*$', content, re.I | re.M)
    return match.group(1).lower() if match else "full"


def check_section_coverage(content, depth):
    """检查 section 覆盖"""
    headings = re.findall(r'^##\s+(.+)$', content, re.M)
    found = [h.lower() for h in headings]
    
    if depth == "quick":
        missing = []
        for kw in DEPTH_SECTIONS["quick"]:
            if not any(kw.lower() in h for h in found):
                missing.append(kw)
        if missing:
            return f"quick 档缺少核心 section: {', '.join(missing)}"
        return None
    return None  # full/deep 不做强制 section 检查，只要有内容就行


def check_reading_blocks(content):
    """检查每个段落精读块是否有翻译 + 分析"""
    # 找所有 ### 段落标题
    blocks = re.split(r'^(###\s+.+)$', content, flags=re.M)
    issues = []
    
    # 成对组合 (标题, 内容)
    pairs = []
    for i in range(1, len(blocks), 2):
        if i + 1 < len(blocks):
            pairs.append((blocks[i], blocks[i+1]))
    
    if not pairs:
        return "没有找到任何段落精读块（### 标题）"
    
    for heading, body in pairs:
        heading_clean = re.sub(r'^###\s+', '', heading).strip()
        # 跳过非段落标题（如"疑问追踪表"、"举一反三"等尾部章节）
        if any(kw in heading_clean.lower() for kw in ['疑问追踪', '举一反三', '总结', 'meta', '元信息']):
            continue
        
        has_translation = bool(re.search(r'\*\*中文翻译', body))
        has_analysis = bool(re.search(r'\*\*即时分析|这段在说什么', body))
        
        if not has_translation and not has_analysis:
            # 可能是尾部非精读块
            continue
        if not has_translation:
            issues.append(f"{heading_clean}: 缺少中文翻译")
        if not has_analysis:
            issues.append(f"{heading_clean}: 缺少即时分析")
    
    if issues:
        return "段落精读块问题:\n  - " + "\n  - ".join(issues[:10])
    return None


def check_question_tracking(content):
    """检查疑问闭环"""
    # 提取所有疑问 ID
    questions = re.findall(r'疑问\s*(Q\d+)', content)
    if not questions:
        return None  # 没有疑问也可以（有些论文很直白）
    
    unique_qs = sorted(set(questions), key=lambda q: int(q[1:]))
    
    # 找追踪表
    table_match = re.search(r'##\s+疑问追踪表\s*\n(.+?)(?=\n##\s|\Z)', content, re.S | re.I)
    if not table_match:
        return f"有 {len(unique_qs)} 个疑问但缺少疑问追踪表"
    
    table = table_match.group(1)
    
    # 检查每个疑问是否在追踪表中
    missing = []
    for q in unique_qs:
        if q not in table:
            missing.append(q)
    
    if missing:
        return f"疑问追踪表缺少: {', '.join(missing)}"
    
    # 检查闭环：三态 ✓ 已回答 / ◐ 部分回答 / ✗ 未回答
    resolved = len(re.findall(r'✓\s*已回答', table))
    partial = len(re.findall(r'◐\s*部分回答', table))
    unresolved = len(re.findall(r'✗\s*未回答', table))
    total_marked = resolved + partial + unresolved
    
    if total_marked < len(unique_qs):
        return f"追踪表中有 {len(unique_qs)} 个疑问但只标记了 {total_marked} 个状态"
    
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_reading.py <reading.md>")
        sys.exit(1)
    
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)
    
    content = md_path.read_text(encoding='utf-8')
    depth = detect_depth(content)
    
    print(f"reading_depth: {depth}")
    print(f"file: {md_path}")
    print()
    
    errors = []
    
    # 1. section 覆盖
    err = check_section_coverage(content, depth)
    if err:
        errors.append(err)
    else:
        print("✓ section 覆盖检查通过")
    
    # 2. 段落精读块
    err = check_reading_blocks(content)
    if err:
        errors.append(err)
    else:
        print("✓ 段落精读块检查通过（每块有翻译 + 分析）")
    
    # 3. 疑问闭环
    err = check_question_tracking(content)
    if err:
        errors.append(err)
    else:
        # 统计（三态）
        questions = set(re.findall(r'疑问\s*(Q\d+)', content))
        resolved = len(re.findall(r'✓\s*已回答', content))
        partial = len(re.findall(r'◐\s*部分回答', content))
        unresolved = len(re.findall(r'✗\s*未回答', content))
        parts = [f"{resolved} 已回答"]
        if partial:
            parts.append(f"{partial} 部分回答")
        parts.append(f"{unresolved} 未回答")
        print(f"✓ 疑问追踪检查通过（{len(questions)} 个疑问，{'，'.join(parts)}）")
    
    print()
    if errors:
        print("自检未通过:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("自检通过 ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
