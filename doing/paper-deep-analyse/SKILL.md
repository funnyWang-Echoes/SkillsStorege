---
name: paper-deep-analyse
description: |
  对学术论文进行逐段精读、论证链重建、实验与代码审计、相关论文发散，并生成高技术含量 HTML 深度报告。适用于组会精读、复现前评估、研究选题、review-style 批判分析、需要“边读边分析思考”的论文深读任务。内置 MinerU 解析、论文目录管理、代码搜索、KaTeX/Mermaid HTML 模板、综合 report.md 母稿流程和基础论文分析硬指标，并进一步强化原文对照、存疑标注、作者贡献判别、证据链、相关工作和迁移启发。
---

# Paper Deep Analyse

目标：把一篇论文读成“原文对照精读 + 技术报告 + 审稿式批判 + 研究脉络图”。不要只总结论文；要逐段拆解作者如何论证、证据能支持什么、不能支持什么，以及这篇工作能如何迁移或启发新研究。

这个 skill 必须可独立使用：不要把执行说明写成依赖其他 skill。所有必要流程都以内置脚本、内置参考文档和本文件规则为准；即使用户只触发 `paper-deep-analyse`，也必须能完成论文获取、MinerU 解析、目录管理、代码搜索、深度报告写作、HTML 生成和自检。

内置资源：

- `scripts/mineru_parse.py`：内置 MinerU 精解析脚本，用于上传、轮询、下载、解压和规范化 PDF 解析包。
- `scripts/extract_paper_info.py`、`scripts/generate_html.py`、`scripts/check_html_render.py`、`scripts/collect_report_counts.py`、`scripts/validate_deep_report_check.py`：内置论文信息抽取、HTML 生成、浏览器侧渲染检查、客观计数字段收集和最终自检 JSON 校验脚本。
- `references/mineru-api-notes.md`：MinerU API 调用细节。
- `references/paper-analyzer-foundation.md`：内化后的基础论文分析规则，包括目录、HTML、公式、图表、代码硬指标。
- `schemas/deep-report-check.schema.json`：最终 HTML 自检结果结构。

资源使用规则：

- 必须调用或等价执行本 skill 的 `scripts/mineru_parse.py` 完成 PDF 精解析，除非已有 `mineru/manifest.json` 且 `state=done`。
- 必须使用 `extract_paper_info.py` 或等价逻辑抽取标题、作者、arXiv/DOI/URL、代码链接和 slug；结果写入 `source/source.md`。
- `generate_html.py` 只能在 `notes/report.md` 已经完成后使用；最终 HTML 必须忠实来自综合 report md，并补齐 KaTeX、Mermaid、reading-card、figure/table、code 样式。
- `generate_html.py` 只接受 `notes/report.md`，并按 `analysis_profile` 自适应检查必要章节、可折叠 reading-card、每张卡片字段/证据联动/最小长度、作者 claim 贡献条目、「存疑」内容、图表证据类型配额、方法机制 block 深度和公式源/渲染污染；缺 `markdown` 依赖时必须失败，不能用简陋 fallback 生成降级 HTML。
- `check_html_render.py` 用于生成后浏览器侧检查 KaTeX、Mermaid、reading-card 和 evidence block；缺 Playwright 时必须用 Browser/chrome-devtools 做等价检查，并在自检 JSON 中记录 `render_check_method`。
- 生成 `deep-report-check.json` 前先运行 `collect_report_counts.py notes/report.md output/<paper-slug>-deep-report.html --output notes/deep-report-check.draft.json`，把可客观统计的 reading-card、图表、公式、渲染残留和章节长度字段合并进自检 JSON；人工只补充 profile reason、贡献 claim、诊断门、subagent review 等无法由脚本可靠判断的字段。
- `collect_report_counts.py` 生成的是草稿，不是最终验收文件。草稿会带 `manual_fields_required`；最终 `notes/deep-report-check.json` 必须移除或清空该字段，并把所有 `TODO` 手工补成真实结论，否则 schema 不应通过。浏览器运行后得到的 `katex_rendered_nodes`、`mermaid_svg_nodes` 和 `render_check_method` 以 `check_html_render.py` 或 Browser/chrome-devtools 的结果为准，不要把静态 HTML 字符串计数当成渲染结果。
- 最终必须生成 `notes/deep-report-check.json`，字段符合 `schemas/deep-report-check.schema.json`，并在最终说明中报告关键计数。最终 JSON 不得包含 `TODO`、`待补`、`占位`、`placeholder` 等占位文本；schema 会拒绝这些壳值。
- 交付前必须运行 `python skills/paper-deep-analyse/scripts/validate_deep_report_check.py notes/deep-report-check.json`。该脚本会同时做 schema 校验和反占位符校验，防止 draft 冒充 final。
- `notes/deep-report-check.json` 中 `contribution_claims` 必须是逐条 claim 数组，不是只有汇总计数；`contribution_summary` 只作为统计补充。

## 自适应分析档位

不要用同一套刚性阈值套所有论文。Round 1-2 后先判断 `analysis_profile`，并在 `notes/report.md` 和 `notes/deep-report-check.json` 中显式记录：

| profile | 适用论文 | reading cards | evidence points | 相关论文 | 公式/算法 | evidence embeds | 方法机制 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `short` | 4-6 页 workshop、短技术报告、信息密度低的 demo paper | >=4 | >=6 | >=2 | >=1 | >=2 | >=1 block，方法节 >=900 字 |
| `standard` | 常规 8-14 页会议论文 | >=6 | >=9 | >=4 | >=3 | >=3 | >=2 blocks，方法节 >=1500 字 |
| `long` | 长论文、期刊、附录丰富或用户明确要重度精读 | >=8 | >=12 | >=6 | >=5 | >=4 | >=3 blocks，方法节 >=2200 字 |

档位是下限，不是凑数目标。短论文不要硬凑空洞卡片；长论文不能借 `standard` 降低深度。若论文核心机制复杂、实验多或用户要求复现评估，即使篇幅短也应升级档位。

每张 reading card 的最小厚度也随档位变化：`short` 约 180 字、`standard` 约 220 字、`long` 约 250 字。关键方法/实验卡片仍应写透“支撑了什么、没支撑什么、和哪项证据互相印证”。

## 适用场景

- 用户要求“逐段读”“深度分析”“组会精读”“技术报告”“审稿式分析”“举一反三”“发散相关论文”。
- 用户已经有 MinerU 解析包、PDF、arXiv URL、论文 HTML、代码仓库或论文文本。
- 用户想判断一篇论文是否值得复现、跟进、写 related work 或做研究选题。

## 输出目录

每篇论文使用独立目录：

```text
papers/<paper-slug>/
├── source/
│   └── paper.pdf
│   └── source.md          # URL、arXiv HTML、下载时间、来源说明
├── mineru/
│   ├── manifest.json
│   ├── full.md
│   ├── content_list.json
│   └── raw/
├── code/
├── related/
│   └── papers.md
├── notes/
│   ├── section-reading.md
│   ├── argument-map.md
│   ├── assumption-ledger.md
│   ├── evidence-matrix.md
│   ├── experiment-audit.md
│   ├── code-audit.md
│   ├── related-work-map.md
│   ├── transfer-ideas.md
│   ├── report-plan.md
│   └── report.md           # 最终 HTML 的唯一内容母稿
└── output/
    └── <paper-slug>-deep-report.html
```

禁止在论文产物目录 `papers/<paper-slug>/` 下创建 `references/` 目录；`references/` 只属于 skill 根目录。相关论文资料统一放入 `related/`，证据和审计材料统一放入 `notes/`。

也不要把 skill 级别的 `scripts/`、`schemas/`、`references/` 复制到论文目录。论文目录只保存该论文的 source、MinerU 解析、代码、相关论文、notes 和 output；可复用脚本和 schema 始终从 skill 根目录读取。

## 强制工作流

### Round 1: 获取与校验全文

- arXiv URL：同时读取 `abs`、`html`，并下载 PDF 到 `source/paper.pdf`。
- PDF：优先生成 MinerU 解析包；若已有 `mineru/manifest.json` 且 `state=done`，直接复用。
- MinerU 包：读取 `manifest.json`、`full.md`、`content_list.json`，主阅读材料用 `full.md`。
- 文本：保存来源说明，仍建立完整论文目录。

MinerU 内置调用规则：

```bash
python skills/paper-deep-analyse/scripts/mineru_parse.py papers/<paper-slug>/source/paper.pdf --env .env --output papers/<paper-slug>/mineru
```

- 默认从 `.env` 读取 `minerU_API`，不要打印或保存 token。
- 扫描版或图片型 PDF 使用 `--ocr`。
- 解析失败时记录状态、`err_msg` 和退回读取方式；不能静默跳过。
- 保留 `mineru/raw/`、`result.zip`、`full.md`、`content_list.json`。

自检：全文是否完整？图片、表格、公式、caption 是否能定位？所有路径是否在当前论文目录内？

### Round 2: 原文对照逐段精读

阅读 `full.md` 和 `content_list.json`，生成 `notes/section-reading.md`。

- 必须覆盖 Abstract、Introduction、Method、Experiments、Limitations/Discussion、Conclusion。
- 方法与实验部分必须逐段或逐逻辑块分析；过长附录可按命题分块，但不能跳过关键证明、算法、表格和消融。
- 每个段落/逻辑块记录：原文位置、短摘、转述、作者在说什么、论证作用、隐含假设、可信度、追问。
- 对没读懂、证据不足、定义含糊、公式跳步、实验设置不明的地方，必须单独标注「存疑」，不要用泛泛总结糊弄过去。存疑项要写清：疑点是什么、是作者没讲清楚还是当前解析/阅读证据不足、需要什么材料才能消解。
- 最终 HTML 必须包含“原文对照精读”小节，reading cards 数量按 `analysis_profile` 执行，覆盖 Abstract/Introduction/Method/Experiments/Conclusion 中的关键段落或逻辑块。
- 原文对照不要整段复制，但也不能只放一句短摘。每个 card 用 `<details class="reading-card">`：summary 放位置、总短摘和一句主旨；展开后必须先给 `<div class="source-expanded">`，再给原文要点转述、论证作用、分析思考、证据联动、存疑、追问。
- “原文对照展开”才是折叠/展开的核心内容：用 2-4 条“原文短句/短摘 + 对应中文译述”覆盖该段落/逻辑块的完整意思，而不是只重复 summary 的一句短摘。短摘必须控制在版权安全范围内：每条只取最短关键短句，避免整句群/整段搬运；更长内容用中文译述或转述。
- `source-expanded` 必须显式包含至少 2 个短摘标记和对应中文译述，例如“原文短句 A / 中文译述 A”。如果原文只有一句核心句，也要拆成术语短语、机制短语和限制短语来对照解释。
- “证据联动”不能空泛，必须指向 Figure/Table/公式/代码/实验数字中的至少一种，并说明这项证据支撑什么、不支撑什么。
- 每个 card 展开后要像 close reading，不要只有一句话。有效长度按 `analysis_profile` 执行；方法/实验关键卡片必须说明“这段支撑了什么、没支撑什么、和哪张图/表/公式/代码相互印证”。
- `notes/deep-report-check.json` 必须记录 reading card 数量、最长短摘词数、是否存在长段复制风险；最长短摘不得超过 25 个英文词。

模板见 `references/note-schemas.md`。

### Round 3: 论证链与证据矩阵

生成：

- `notes/argument-map.md`：主张、子主张、证据、缺口、替代解释。
- `notes/assumption-ledger.md`：关键假设、依赖证据、失败后果。
- `notes/evidence-matrix.md`：证据点数量按 `analysis_profile` 执行，覆盖 Figure、Table、公式、实验数字、消融、局限、代码路径。
- `notes/contribution-claims.md`：作者自称的主要贡献逐条列出，并判定“真创新 / 工程改进 / 应用整合 / 实验验证 / 表述包装 / 存疑”。

硬要求：

- “主要贡献”必须先引用作者自己的 claim，再给独立判断；不要把 agent 自己总结的亮点冒充作者贡献。
- 每条贡献都要回答：相对哪条已有路线新增？新颖性来自问题、机制、数据、训练/推理流程、系统工程还是实验组织？证据在哪里？仍未证明什么？
- 区分“论文证明了什么”和“论文没有证明什么”。
- 反事实问题数量按档位执行：`short` >=2、`standard` >=3、`long` >=5；例如去掉模块、替换 baseline、改变数据/工具/奖励会怎样。
- 每个强结论必须链接到证据位置；不能只有抽象判断。
- 所有「存疑」项要在论证链或证据矩阵中落位；如果作者没有讲清楚，明确写“作者未充分交代”，不要替作者补完。

### Round 3.5: 诊断门与返工

Round 3 后必须停下来做一次诊断，而不是无条件瀑布式进入后续轮次。生成或更新 `notes/report-plan.md` 中的“诊断门”小节，并在 `deep-report-check.json.diagnostic_gate` 记录结果。

诊断问题：

- 核心主张是否已经被证据支撑？如果没有，后续 Round 4-5 要围绕缺口检索相关论文或审计代码，而不是继续写常规综述。
- 是否发现致命缺陷、baseline 不公平、公式定义不清、实验设置不可复现？若有，先把报告主线改成“问题定位/证据不足型分析”。
- 当前 `analysis_profile` 是否合适？短论文但机制复杂则升级；长论文但用户只需快速复现评估时可维持 standard，但必须说明取舍。
- 哪些段落没有读懂？不要补故事，标为「存疑」，并指定需要作者附录、代码、数据或相关论文来消解。

诊断门决策只能是：`continue`、`refocus`、`downgrade-profile`、`upgrade-profile`、`block-and-repair`。若选择 `refocus` 或 `block-and-repair`，必须回到 Round 2/3 补 notes 后再继续。

### Round 4: 相关论文发散

必须联网检索近期和经典相关工作，优先使用 arXiv、OpenReview、ACL Anthology、NeurIPS/ICLR/ICML/CVPR 官方页、Semantic Scholar、Papers with Code、官方 GitHub。

生成：

- `related/papers.md`：检索到的候选论文、链接、年份、来源。
- `notes/related-work-map.md`：按问题分类的研究脉络，而不是论文列表。
- `notes/transfer-ideas.md`：可迁移想法、可复现方向、可改进点。

检索策略见 `references/related-work.md`。

### Round 5: 实验与代码审计

生成：

- `notes/experiment-audit.md`：claim、supporting evidence、baseline 公平性、metric 合理性、confounder、可信度评级。
- `notes/code-audit.md`：论文机制到源码模块/函数/配置的对应关系；没有公开代码时说明搜索过程和替代实现。

有公开代码时必须阅读 README、核心源码、训练/评估配置；不能只引用 README。“论文概念 ↔ 源码位置”对应点按档位执行：`short` >=3、`standard` >=5、`long` >=8。

代码搜索内置规则：

- 从论文、README、项目页、arXiv HTML 中提取官方仓库；没有则用论文标题、方法名、作者名搜索 GitHub。
- 克隆到 `papers/<paper-slug>/code/`，不要使用临时目录作为最终引用。
- 阅读顺序：README -> install/quickstart -> 核心模块 -> train/eval/config -> scripts/tests。
- 正文中代码段每段不超过 30 行，必须标注当前论文目录内的文件路径和行号。

### Round 6: 报告计划

生成 `notes/report-plan.md`，包含：

- 报告主线：读者看完应理解什么。
- 核心图表：至少 1 个 Mermaid 机制图、2 张证据表。
- 必须进入正文的段落精读点、证据点、相关论文、代码审计点。
- Reviewer-style 追问按档位执行：`short` >=3、`standard` >=5、`long` >=8。

### Round 7: 生成综合 Report Markdown

先生成 `notes/report.md`，再生成 HTML。`report.md` 是最终 HTML 的唯一内容母稿，HTML 不再临场重新发挥。

`report.md` 顶部必须显式写入分析档位元数据，且该值会被 `generate_html.py` 强制解析；不要依赖默认档位：

```markdown
analysis_profile: long
profile_reason: 常规会议论文且方法、实验、代码和相关工作都需要完整审计。
```

`report.md` 必须包含：

- 标题、论文元信息、来源、代码状态。
- 执行摘要：贡献、可信度、适用边界、是否值得复现。
- 主要贡献判别表：作者 claim、独立分类、创新性判断、证据、保留意见。
- 原文对照精读卡片：数量按 `analysis_profile` 执行，包含位置、短摘、转述、分析、追问、存疑状态。
- 「存疑」专栏：集中列出未读懂/未交代清楚/证据不足之处，并标注下一步查证路径。
- 研究脉络、方法机制、论证链、实验审计、代码审计、相关论文发散、reviewer-style critique、transfer ideas。
- 所有进入 HTML 的公式、图表、代码、Mermaid、相关论文链接和本地图片引用。
- 所有关键 Figure/Table 证据必须就地可读：优先嵌入 MinerU 本地图片；表格可以重建核心数字；不要只写“见 Table/Figure”。`evidence-embed` 或本地图表证据块数量按 `analysis_profile` 执行。
- 每个图表 evidence block 不能只有一句“这图说明了什么”。必须至少写清：读图方式、关键元素、支撑的结论、不支持/不能推出的结论、边界或可能误读。对系统图要解释箭头、模块、状态流；对实验表要解释行列含义、关键差值、baseline 公平性和替代解释。
- 图表证据配额按档位执行。`long` 档至少 2 个 MinerU 本地图片和 2 个重建论文表格/关键数字块；`standard` 档至少 1 个 MinerU 本地图片和 1 个重建表格/关键数字块；`short` 档允许没有 MinerU 图片，但至少 1 个重建表格/关键数字块。若论文本身没有图/表，必须解释并改用公式、算法或实验数字证据。
- 重建表格/关键数字块必须包含 `<table>` / Markdown 表格，或明确写“关键数字/数字摘录/重建表格”并至少列出 3 个关键数值；普通年份、编号不能算作重建数字证据。
- 图表 evidence block 必须在最终 HTML 中正确渲染：图片必须是 `<img>`，表格必须是 `<table>`；不得出现可见的 `![alt]`、`(data:image...)` 或 Markdown 管道表格文本。
- 方法机制节必须是连续技术说明，不是“公式 + 一句人话解释”。`mechanism-block` 数量和长度按 `analysis_profile` 执行；每个关键机制至少解释定义、变量/符号、直觉、设计动机、解决的失败模式、边界/副作用，并连接实验或代码证据。
- 每个重要公式后必须有 `formula-analysis` 或等价段落，说明变量逐项含义、公式在算法中的位置、直觉读法、为什么这样设计、边界/副作用、和图表/代码/实验的证据连接。
- 公式必须用独立 `$$ ... $$` / `\[...\]` 或 inline `\(...\)` / `$...$`；`\tag{}` 公式必须是 display math。生成 HTML 后公式块里不得出现 `<em>`、`<strong>` 等 Markdown 污染标签。发现污染时必须先修 `report.md`，不能交付。

生成 `report.md` 后先自读一遍：如果读起来只是摘要堆叠，而不是逐段阅读后的技术判断，必须回到 notes 补证据再改。

### Round 8: 从 Report Markdown 生成 HTML 技术报告

输出 `output/<paper-slug>-deep-report.html`。报告不是论文摘要，而是技术报告。

推荐结构：

1. 执行摘要：贡献、可信度、适用边界。
2. 主要贡献判别：作者 claim -> 独立分类 -> 证据 -> 保留意见。
3. 研究脉络：本文解决什么历史问题，和相关论文如何连接。
4. 逐段精读：按 Section 展开关键段落与分析思考。
5. 存疑清单：作者没讲清楚、证据不足或需要进一步查证的地方。
6. 方法机制：公式、架构、流程、设计选择。
7. 论证链：claim -> evidence -> gap。
8. 实验审计：主结果、消融、公平性、威胁。
9. 代码审计：论文机制与实现差异。
10. 相关论文发散：替代路线、并行工作、后续机会。
11. Reviewer-style critique：强项、弱项、追问。
12. 可迁移启发：能复用到哪里，不能复用到哪里。

HTML 内置硬指标：

- 正文应明显长于常规论文摘要式输出，`short` 档也必须是技术报告而非摘要；不能因为增加 notes 而压缩正文。
- 可折叠原文对照 reading cards 数量按 `analysis_profile` 执行：位置、短摘、原文对照展开、转述、论证作用、分析、证据联动、存疑、追问。
- 所有 reading cards 都必须是 `<details class="reading-card">`，不能混用普通 section/card。
- 公式/算法片段、Figure/Table 证据嵌入、方法机制 blocks、逐段精读长度和方法节长度都按 `analysis_profile` 执行；低于对应档位通常说明只写了摘要，没有深读透。
- 自制分析表按档位执行：`short` >=2、`standard` >=3、`long` >=4；证据矩阵摘要、实验可信度评级、相关论文对比、代码审计表任选。
- 至少 1 个 Mermaid 图。
- 有公开代码时，代码/配置片段按档位执行：`short` >=1、`standard` >=3、`long` >=5；每段不超过 30 行。
- 相关论文进入正文比较的数量按 `analysis_profile` 执行，并提供链接。
- 必须从 `notes/report.md` 渲染生成；若手工改 HTML，必须同步回 `report.md`，保持 MD 是可复审母稿。
- 生成后必须运行 `python skills/paper-deep-analyse/scripts/check_html_render.py output/<paper-slug>-deep-report.html <analysis_profile> --json-output notes/render-check.json`；`<analysis_profile>` 必须显式传入，不允许脚本自行猜测。如果缺 Playwright，则用 Browser/chrome-devtools 打开 HTML 做等价检查，确认 `.katex-error=0`、`.katex` 节点数量达到对应档位、Mermaid SVG 存在，并把同等计数手工写入 `notes/render-check.json`。

HTML 规格见 `references/deep-report-structure.md`。

基础 HTML、公式、图表、代码约束还必须读取并遵守 `references/paper-analyzer-foundation.md`。

### Round 9: 自检与修订

输出前逐项检查：

- 是否真的逐段读了核心 Section，而不是按摘要改写？
- HTML 是否真的展示了可折叠原文对照 reading cards，而不只是 notes 里有逐段笔记？
- 每个 reading card 展开后是否有完整分析，而不是一句转述/一句评价？
- 每个 reading card 的 `source-expanded` 是否有多条原文短句与对应中文译述，而不是只有一句短摘？
- 方法机制是否有足够连续技术说明，而不是“公式 + 一句人话解释”？
- 方法机制是否逐 block 包含定义、设计动机、失败模式、边界/副作用和证据？
- 关键图表是否在 `report.md` 和 HTML 中就地嵌入或重建，而不是只写 Table/Figure 摘要？
- 每个图表证据是否写清读图方式、关键元素、支撑什么、不支持什么、边界/可能误读？
- 图表证据是否满足当前 `analysis_profile` 的 MinerU 本地图片和重建表格/关键数字配额？
- 图表证据是否真的渲染成 `<img>` 和 `<table>`，而不是露出 Markdown 图片语法、base64 文本或管道表格文本？
- 公式渲染是否检查过？公式块中是否没有 `<em>`、`<strong>`、异常 HTML 标签污染？
- 是否做过浏览器侧 KaTeX 检查，并在 `deep-report-check.json` 写入 `render_check_method` 和实际渲染节点数？
- 是否包含当前 `analysis_profile` 要求的 evidence-matrix 证据点？
- 是否有相关论文发散，并在正文中比较当前 `analysis_profile` 要求数量的相关工作？
- 是否包含“论文证明了什么 / 没证明什么”？
- 是否列出作者 claim 的主要贡献，并区分真创新、工程改进、应用整合和存疑贡献？
- `deep-report-check.json` 是否用 `contribution_claims[]` 逐条记录作者 claim，而不是只写数量？
- 是否把没读懂或作者没讲清楚的地方标为「存疑」，而不是用模糊话术带过？
- `notes/report.md` 是否存在，且 HTML 是否由它生成/同步？
- 是否包含假设链、反事实推理和 reviewer 追问？
- 是否有实验可信度评级表？
- 有代码时，源码对应点是否达到当前 `analysis_profile` 要求，并指出实现差异或复现风险？
- 是否有 KaTeX 公式、Mermaid 图、本地 Figure/Table 引用和完整 HTML 技术报告模板？
- 本地图片路径是否存在？HTML 是否能浏览器打开？
- 是否生成 `notes/deep-report-check.json`，并符合 `schemas/deep-report-check.schema.json`？
- `deep-report-check.json` 是否记录 `analysis_profile`、`profile_reason`、`thresholds_used` 和 `diagnostic_gate`？
- `deep-report-check.json` 中的 details card 数、证据联动 card 数、未渲染 Markdown 图片/表格数是否来自实际检查，而不是主观布尔自述？
- `deep-report-check.json` 是否记录 `source_expanded_cards`、`reading_cards_with_translation_pairs`、`rich_evidence_blocks`，并达到当前 `analysis_profile` 要求？
- `papers/<paper-slug>/` 下是否没有错误创建 `references/` 目录？

### Round 10: 子 agent 校验（环境支持时必须）

如果当前环境支持子 agent / multi-agent 工具，必须在主 agent 自检之后启动固定 review 子 agent，而不是只靠主 agent 判断。

推荐配置：

- model: `gpt-5.4-mini`
- reasoning: `medium`
- role: `paper-deep-report-reviewer`
- 输入：`notes/report.md`、最终 HTML 路径、notes 目录、`schemas/deep-report-check.schema.json`、最多 12 条关键证据摘要。
- 不要把主 agent 的自评结论作为提示泄露给 reviewer。

子 agent 检查重点：

- HTML 是否真正呈现原文对照 reading cards。
- reading cards 是否可折叠展开，并且展开后有足够详细的 close reading。
- 关键 Figure/Table 是否就地可读：本地图片或重建表格是否进入 HTML。
- 公式是否全部可渲染，尤其检查 Markdown 污染、`\tag{}`、下划线和花括号。
- 是否有浏览器侧 KaTeX 结果，而不是只做静态字符串检查？
- 方法机制和逐段精读是否存在“一处只有一句话”的薄弱段落。
- `report.md` 与 HTML 是否一致，HTML 是否存在未回写 MD 的临场内容。
- 是否列出作者 claim 的贡献，并合理区分真创新、工程改进、应用整合和存疑。
- 是否把没读懂/作者没讲清楚之处明确标为「存疑」。
- 是否丢失基础论文分析硬指标：公式编号、Figure/Table、代码段、KaTeX/Mermaid。
- 相关论文发散是否有分类比较，而非链接堆砌。
- 论证链是否区分“证明了什么 / 没证明什么”。
- 实验/代码审计是否指出威胁和复现风险。

如果当前环境不支持子 agent，必须在最终说明和 `notes/report-plan.md` 或自检摘要中写明：`subagent_review.supported=false`，并由主 agent 做等价检查。

验收约束：

- `subagent_review.supported=true` 时，`attempted` 必须为 `true`，`result` 必须包含 reviewer 的明确通过/不通过结论和至少 3 条发现；不能填空壳文本。
- `subagent_review.supported=true` 时，`model` 必须是 `gpt-5.4-mini`，`verdict` 必须是 `pass` / `fail` / `pass-with-issues`，`findings_count` 必须至少为 3；`supported=false` 时 `verdict=unsupported`。
- reviewer 提出阻断问题时，必须修订 HTML 或 notes 后再次自检；不能只在最终说明里解释。

## 参考模板

- `references/note-schemas.md`：逐段阅读、论证链、证据矩阵、审计笔记模板。
- `references/related-work.md`：相关论文检索与发散规则。
- `references/deep-report-structure.md`：HTML 技术报告结构、硬指标和写作要求。
- `references/mineru-api-notes.md`：MinerU API 调用链路和常见错误。
- `references/paper-analyzer-foundation.md`：内化后的基础论文分析规则。
- `schemas/deep-report-check.schema.json`：最终自检摘要 schema。
