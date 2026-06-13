# Note Schemas

这些模板用于中间 notes。写作时可以压缩表格，但字段不能丢。

## section-reading.md

```markdown
# Section Reading

## Section X: <title>

### Paragraph / Block X.Y

- 位置：Section / page / MinerU item / Figure / Table
- 原文短摘：不超过 25 个英文词；更长内容只做转述
- 原文要点转述：
- 作者在说什么：
- 论证作用：背景铺垫 / 问题定义 / 方法机制 / 实验证据 / 局限承认
- 隐含假设：
- 我是否相信：
- 证据强度：强 / 中 / 弱
- 存疑：无 / 作者未讲清楚 / 证据不足 / 解析不足 / 需要外部资料
- 存疑说明：
- 追问：
- 可进入正文的洞察：
```

## HTML reading card

最终 HTML 的“原文对照精读”中使用可折叠结构。summary 显示位置、短摘和一句主旨；展开后首先给“原文对照展开”，再给完整转述、论证作用、分析思考、证据联动、存疑和追问。不要把整段原文搬进 HTML；原文区必须放 2-4 条关键短摘片段和对应中文译述，让读者看到原文措辞和中文理解如何对齐。每条英文短摘只取最短必要短句，避免整段搬运。

```html
<details class="reading-card" open>
  <summary>Section 3.2 · Eq. 5 · Short source excerpt</summary>
  <div class="source-locator">Section 3.2 · Eq. 5 · MinerU item 59</div>
  <blockquote>Short source excerpt, no long verbatim paragraph.</blockquote>
  <div class="source-expanded">
    <p><strong>原文对照展开：</strong>用 2-4 条短摘 + 中文译述呈现这段原文的完整意思。</p>
    <ul>
      <li><strong>原文短句 A：</strong>最短必要短句；<strong>中文译述 A：</strong>逐句译述其技术含义，不要只总结。</li>
      <li><strong>原文短句 B：</strong>最短必要短句；<strong>中文译述 B：</strong>解释作者的限定条件、机制动词或结论边界。</li>
      <li><strong>原文短句 C：</strong>可选；<strong>中文译述 C：</strong>补足该逻辑块的证据或限制。</li>
    </ul>
  </div>
  <p><strong>原文要点转述：</strong>...</p>
  <p><strong>论证作用：</strong>...</p>
  <p><strong>分析思考：</strong>...</p>
  <p><strong>证据联动：</strong>连接 Figure/Table/公式/代码证据，说明它支撑什么、不支撑什么。</p>
  <div class="evidence-embed">
    <p><strong>证据对照：</strong>这张图/表在原论文中显示 ...</p>
    <figure>
      <img src="../mineru/raw/images/xxx.jpg" alt="Figure/Table evidence">
      <figcaption>Figure/Table X：不要只写编号，要复制本地图片或重建关键表格，并解释读法。</figcaption>
    </figure>
  </div>
  <p><strong>存疑：</strong>...</p>
  <p><strong>追问：</strong>...</p>
</details>
```

每张 card 必须回答：这段在整篇论文论证链中承担什么作用？它支撑了什么结论？还没有证明什么？如果提到 Figure/Table，不要只写一句摘要，必须在 card 附近嵌入本地图片、重建核心表格，或给出可读的数字摘录表。
如果没有存疑，写“暂无”；如果有，必须说明是作者未交代、证据不足、公式跳步、实验设置不清，还是当前解析材料不足。

硬校验要求：

- 所有 reading card 都必须是 `<details class="reading-card">`，不允许混入 `<section class="reading-card">` 或 `<div class="reading-card">`。
- 每张 card 必须有 `<summary>`、`source-locator`、`source-expanded`、原文对照展开、原文要点转述、论证作用、分析思考、存疑、追问。
- `source-expanded` 必须至少包含 2 个“原文短句/短摘”和对应“中文译述/翻译/转述”，不能只有一句中文摘要。
- 每张 card 必须有“证据联动”，并指向 Figure/Table/公式/代码中的至少一种证据。没有图表时，也要说明可查证的公式、代码路径或实验数字。
- 每张 card 展开内容有效长度按 `analysis_profile` 执行：`short` 约 180 字、`standard` 约 220 字、`long` 约 250 字；不要用一句话糊弄。
- 折叠/展开控制的是“原文对照展开 + 分析”，不是只隐藏一条短摘。summary 可以短，展开区必须让读者理解原文段落的完整意思。

## evidence embeds

图表证据必须进入 `report.md`，再进入 HTML。不要只写“见 Table 1 / Fig. 2”。

```html
<div class="evidence-embed">
  <p><strong>证据：</strong>Table 3 对比 frozen / SFT / Flow-GRPO。这里要写清楚读表方式和关键数字。</p>
  <table>
    <thead><tr><th>Setting</th><th>Average</th><th>Interpretation</th></tr></thead>
    <tbody><tr><td>Flow-GRPO</td><td>...</td><td>...</td></tr></tbody>
  </table>
  <p><strong>读图/读表方式：</strong>先看行列含义，再看关键差值和实验设置是否公平。</p>
  <p><strong>关键元素：</strong>列出图中的模块、箭头、变量或表格中的核心列。</p>
  <p><strong>支撑：</strong>它能支持哪条 claim。</p>
  <p><strong>不支持：</strong>它不能推出什么，哪些替代解释仍然存在。</p>
  <p><strong>边界：</strong>样本、任务、baseline、成本或实现条件的限制。</p>
</div>
```

最低要求按 `analysis_profile` 执行：`short` 至少 2 个 `evidence-embed` 或本地图片证据块，且至少 1 个重建表格/关键数字；`standard` 至少 3 个 evidence blocks，且至少 1 个 MinerU 本地图片和 1 个重建表格/关键数字；`long` 至少 4 个 evidence blocks，且至少 2 个 MinerU 本地图片和 2 个重建表格/关键数字。每个 evidence block 后必须有“读图/读表方式、关键元素、支撑什么、不支持什么、边界/可能误读”的解释。

MinerU 图片路径中应显式包含 `mineru`，例如 `../mineru/raw/images/...`。重建表格证据必须包含 `<table>` 或 Markdown 表格；如果不用表格，则必须明确写“关键数字/数字摘录/重建表格”等标签，并至少列出 3 个关键数值，避免把普通年份或编号误当证据。生成器会阻断 evidence block 中残留的 `![...](...)` 图片语法或未渲染 Markdown 表格。

## contribution-claims.md

先列作者自己的贡献 claim，再做独立判断。不要把自己的总结替换成作者 claim。

```markdown
# Contribution Claims

| ID | Author-claimed contribution | Source location | Independent category | Novelty judgment | Evidence | Caveat / 存疑 |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | | Abstract / Intro / Contribution paragraph | 真创新 / 工程改进 / 应用整合 / 实验验证 / 表述包装 / 存疑 | | Fig/Table/Eq/Related work | |
```

判断口径：

- 真创新：问题设定、机制、理论、训练/推理范式或数据构造有清晰新增，并能相对具体前作定位差异。
- 工程改进：主要价值来自系统组合、流程优化、规模化、工具链打通或实现细节。
- 应用整合：把已有方法迁移到新任务/场景，贡献主要在场景定义或落地验证。
- 实验验证：主要贡献是更系统的 benchmark、ablation、analysis 或负结果。
- 表述包装：claim 听起来新，但证据显示更像已有路线的换名或重组。
- 存疑：无法从论文证据确认新颖性或作者没有讲清楚差异。

## argument-map.md

```markdown
# Argument Map

## Main Claim

- 作者主张：
- 这篇论文真正想说服读者相信：

## Claim Table

| Claim | Evidence | Gap | Alternative explanation | Report use |
| --- | --- | --- | --- | --- |
| | Figure/Table/Eq/Code | | | |
```

## assumption-ledger.md

```markdown
# Assumption Ledger

| Assumption | Why needed | Evidence | Failure mode | Affected conclusion |
| --- | --- | --- | --- | --- |
| | | | | |
```

## evidence-matrix.md

每个证据点必须能回到论文或代码。

```markdown
# Evidence Matrix

| ID | Location | Raw fact | Supports | Does not support | Confidence |
| --- | --- | --- | --- | --- | --- |
| E01 | Fig. 1 / Table 1 / Eq. 3 / code path | | | | |
```

覆盖规则按 `analysis_profile` 执行。`long` 档尽量覆盖：公式、Figure、Table/实验数字、消融/行为分析、局限/威胁、代码路径各不少于 2 个；`standard` 档每类至少有代表性证据；`short` 档优先覆盖主张成立所需的核心证据，不为凑类别制造空洞条目。

## experiment-audit.md

```markdown
# Experiment Audit

| Claim | Evidence | Baseline fairness | Metric fit | Confounder | Credibility |
| --- | --- | --- | --- | --- | --- |
| | | same backbone/tool/budget? | | | Strong/Medium/Weak |
```

必须额外写：

- 评价协议是否稳定。
- judge/reward 是否可能偏置。
- 工具、数据、缓存、时间变化是否影响复现。
- 成本和延迟是否与 baseline 公平比较。

## code-audit.md

```markdown
# Code Audit

| Paper concept | Code location | Match level | Implementation note | Repro risk |
| --- | --- | --- | --- | --- |
| | file:line / function / config | Exact / Partial / Missing | | |
```

必须指出至少 1 个：

- 论文描述与工程实现粒度不同之处。
- 默认配置与论文实验设置可能不同之处。
- 复现需要额外 API、数据、模型或硬件的地方。

## report-plan.md

```markdown
# Report Plan

- 主线：
- 读者画像：
- 关键结论：
- 必进正文证据：
- 必进正文相关论文：
- 必进正文代码点：
- Mermaid 图：
- Reviewer questions:
  1. ...
```

## report.md

最终 HTML 必须由这个 Markdown 母稿生成或同步。它不是零散 notes，而是一份可直接审阅的综合技术报告。

```markdown
# <Paper Title> 深度精读报告

analysis_profile: long
profile_reason: 常规会议论文且方法、实验、代码和相关工作都需要完整审计。

## 论文元信息

## 执行摘要

## 主要贡献判别

## 研究脉络

## 原文对照逐段精读

## 存疑清单

## 方法机制

<div class="mechanism-block">
  <h3>机制名</h3>
  <p><strong>定义：</strong>...</p>
  <p><strong>变量/符号：</strong>...</p>
  <p><strong>直觉：</strong>...</p>
  <p><strong>设计动机：</strong>...</p>
  <p><strong>解决的失败模式：</strong>...</p>
  <p><strong>边界/副作用：</strong>...</p>
  <p><strong>证据：</strong>连接公式、Figure/Table 或代码位置。</p>
</div>

## 论证链与证据矩阵

## 实验审计

## 代码审计

## 相关论文发散

## Reviewer-style Critique

## 可迁移启发
```

`report.md` 必须包含所有将进入 HTML 的 reading cards、公式/算法片段、Mermaid、表格、图片引用、代码片段和相关论文链接。HTML 如果有新增内容，必须回写到 `report.md`。

深度要求：

- “原文对照逐段精读”不能每卡只有一句分析。每个 card 展开内容应达到当前 `analysis_profile` 的厚度要求，至少包含转述、论证作用、分析、证据联动、存疑/无存疑、追问。
- “方法机制”不能是“公式 + 一句人话解释”。每个关键机制至少写 3 层：数学/流程定义、为什么这样设计、它解决了什么失败模式、它还会带来什么副作用或边界。
- “方法机制”必须达到当前 `analysis_profile` 的 mechanism-block 数量和厚度要求；每个 block 至少包含定义、变量/符号、直觉、设计动机、失败模式、边界/副作用、证据。
- 重要公式必须有 `formula-analysis` 或等价段落：变量逐项解释、公式在算法中的位置、直觉读法、设计动机、边界/副作用、与图表/代码/实验的证据连接。
- 公式块优先用独立 `$$ ... $$` 或 `\[...\]`，inline 公式用 `\(...\)` 或 `$...$`。不要让下划线、花括号、尖括号被 Markdown 当成强调或 HTML。所有 `\tag{...}` 都必须位于 display math。生成 HTML 后若公式块里出现 `<em>`、`<strong>` 等标签，必须回到 `report.md` 修公式。
- 生成 HTML 后必须做浏览器侧 KaTeX 检查：优先运行 `scripts/check_html_render.py output/<slug>-deep-report.html`；若缺 Playwright，使用 Browser/chrome-devtools 打开 HTML 并检查 `.katex-error` 为 0、`.katex` 节点不少于公式数量、`.mermaid svg` 存在。
- 图表证据必须复制到 `report.md`：优先嵌入 MinerU 本地图片；表格可重建核心数字，不要只在正文中说“Table/Figure 说明了 ...”。

## deep-report-check.json

最终必须生成 `notes/deep-report-check.json`，并符合 `schemas/deep-report-check.schema.json`。示例：

先运行客观计数脚本，再补人工判断字段：

```bash
python skills/paper-deep-analyse/scripts/check_html_render.py papers/example-paper/output/example-paper-deep-report.html long --json-output papers/example-paper/notes/render-check.json
python skills/paper-deep-analyse/scripts/collect_report_counts.py papers/example-paper/notes/report.md papers/example-paper/output/example-paper-deep-report.html --render-method browser --output papers/example-paper/notes/deep-report-check.draft.json
python skills/paper-deep-analyse/scripts/validate_deep_report_check.py papers/example-paper/notes/deep-report-check.json
```

`deep-report-check.draft.json` 不是最终验收文件。它会保留 `manual_fields_required` 并放入若干 `TODO` 占位；最终 `deep-report-check.json` 必须合并 `render-check.json` 的浏览器渲染结果，补齐诊断门、贡献 claim、贡献统计、subagent review 后，移除或清空 `manual_fields_required`。最终文件不得保留 `TODO`、`待补`、`占位`、`placeholder` 等占位文本，schema 会拒绝这些壳值。

```json
{
  "paper_slug": "example-paper",
  "html_path": "papers/example-paper/output/example-paper-deep-report.html",
  "analysis_profile": "long",
  "profile_reason": "常规会议论文且方法、实验和代码审计都需要完整展开。",
  "thresholds_used": {
    "reading_cards": 8,
    "reading_card_chars": 250,
    "evidence_points": 12,
    "related_papers_in_body": 6,
    "formulas": 5,
    "evidence_embeds": 4,
    "mineru_local_images": 2,
    "reconstructed_table_evidence": 2,
    "method_section_chars": 2200,
    "reading_section_chars": 3200,
    "mechanism_blocks": 3,
    "mechanism_block_chars": 320
  },
  "mineru_used": true,
  "reading_cards": 10,
  "details_reading_cards": 10,
  "non_details_reading_cards": 0,
  "reading_cards_with_evidence_linkage": 10,
  "source_expanded_cards": 10,
  "reading_cards_with_translation_pairs": 10,
  "min_reading_card_chars": 280,
  "evidence_points": 18,
  "related_papers_in_body": 8,
  "formulas": 6,
  "figures_or_tables": 5,
  "evidence_embeds": 4,
  "mineru_local_images": 2,
  "reconstructed_table_evidence": 2,
  "rich_evidence_blocks": 4,
  "custom_tables": 4,
  "code_blocks": 3,
  "unrendered_markdown_images": 0,
  "unrendered_markdown_tables": 0,
  "mermaid_svg_nodes": 1,
  "katex_rendered_nodes": 6,
  "formula_render_errors": [],
  "math_source_checked": true,
  "render_check_method": "playwright",
  "method_section_chars": 2200,
  "reading_section_chars": 3600,
  "mechanism_blocks": 3,
  "min_mechanism_block_chars": 350,
  "max_excerpt_words": 22,
  "long_quote_risk": false,
  "paper_references_dir_exists": false,
  "report_md_path": "papers/example-paper/notes/report.md",
  "report_md_generated_first": true,
  "diagnostic_gate": {
    "performed": true,
    "decision": "continue",
    "iterations": 1,
    "fatal_flaws": [],
    "adjustments": ["维持 long 档，后续重点审计实验和代码证据。"]
  },
  "doubt_items": 4,
  "contribution_claims": [
    {
      "id": "C01",
      "author_claim": "The paper claims ...",
      "source_location": "Introduction contribution paragraph",
      "independent_category": "工程改进",
      "novelty_judgment": "主要新意来自系统流程组合和工程化约束，而非全新理论机制。",
      "evidence": "Table 2 / Section 3 / related-work comparison",
      "caveat_or_doubt": "作者没有充分隔离该模块相对已有 agent workflow 的独立增益。"
    }
  ],
  "contribution_summary": {
    "total": 5,
    "true_innovation": 2,
    "engineering_improvement": 2,
    "application_integration": 1,
    "experiment_validation": 0,
    "repackaging": 0,
    "uncertain": 1
  },
  "image_paths_missing": [],
  "subagent_review": {
    "attempted": true,
    "supported": true,
    "model": "gpt-5.4-mini",
    "verdict": "pass-with-issues",
    "result": "pass with minor issues: ...",
    "findings_count": 3
  }
}
```
