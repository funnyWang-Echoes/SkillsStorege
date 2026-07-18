---
name: paper-deep-analyse
description: |
  对学术论文进行逐段精读、论证链重建、实验与代码审计、相关论文发散，并生成高技术含量 HTML 深度报告。适用于组会精读、复现前评估、研究选题、review-style 批判分析。内置 MinerU 解析、阈值自检、KaTeX/Mermaid HTML 生成。阈值单一来源在 schemas/thresholds.json，报告规格在 references/report-spec.md。
---

# Paper Deep Analyse

把一篇论文读成"原文对照精读 + 技术报告 + 审稿式批判 + 研究脉络图"。不只总结论文——逐段拆解作者如何论证、证据能支持什么、不能支持什么，以及这篇工作能如何迁移或启发新研究。

这个 skill 必须可独立使用。所有必要流程都以内置脚本、内置参考文档和本文件规则为准。

## 内置资源

| 资源 | 用途 |
|---|---|
| `scripts/mineru_parse.py` | MinerU 精解析：上传 PDF、轮询、下载（含重试和 Node.js fallback） |
| `scripts/extract_paper_info.py` | 论文元数据抽取 |
| `scripts/generate_html.py` | 从 report.md 生成 HTML（含 KaTeX/Mermaid/reading-card 校验） |
| `scripts/check_html_render.py` | 浏览器侧渲染检查 |
| `scripts/collect_report_counts.py` | 客观计数字段收集 |
| `scripts/validate_deep_report_check.py` | 最终自检 JSON 校验（schema + 反占位符） |
| `scripts/thresholds.py` | 阈值单一来源加载器（读 `schemas/thresholds.json`） |
| `references/report-spec.md` | reading card、evidence embed、mechanism block、公式、图表、自检 JSON 的唯一规格 |
| `references/related-work.md` | 相关论文检索与发散规则 |
| `references/mineru-api-notes.md` | MinerU API 调用细节 |
| `schemas/thresholds.json` | short/standard/long 档位阈值（唯一来源，脚本和 schema 共同引用） |
| `schemas/deep-report-check.schema.json` | 最终自检 JSON schema |

## 自适应分析档位

根据论文类型选择 `analysis_profile`：

| profile | 适用 | reading cards | evidence | 相关论文 | 公式 | evidence embeds | mechanism blocks |
|---|---|---:|---:|---:|---:|---:|---:|
| `short` | 4-6 页 workshop/demo | ≥4 | ≥6 | ≥2 | ≥1 | ≥2 | ≥1 |
| `standard` | 8-14 页会议论文 | ≥6 | ≥9 | ≥4 | ≥3 | ≥3 | ≥2 |
| `long` | 长论文/期刊/重度精读 | ≥8 | ≥12 | ≥6 | ≥5 | ≥4 | ≥3 |

完整阈值见 `schemas/thresholds.json`。档位是下限，不是凑数目标。短论文不要硬凑空洞卡片；长论文不能借 `standard` 降低深度。若论文核心机制复杂、实验多或用户要求复现评估，即使篇幅短也应升级档位。

## 输出目录

```text
papers/<paper-slug>/
├── source/paper.pdf, source.md
├── mineru/manifest.json, full.md, content_list.json, raw/
├── code/
├── related/papers.md
├── notes/  section-reading.md, argument-map.md, assumption-ledger.md,
│           evidence-matrix.md, contribution-claims.md, experiment-audit.md,
│           code-audit.md, related-work-map.md, transfer-ideas.md,
│           report-plan.md, report.md, deep-report-check.json
└── output/<paper-slug>-deep-report.html
```

禁止在论文目录下创建 `references/` 目录（它只属于 skill 根）。不要把 skill 的 `scripts/`、`schemas/` 复制到论文目录。

## 工作流（阶段化，非线性瀑布）

### 入口选择

| 入口 | 适用 | 跳过 |
|---|---|---|
| `quick` | 用户要快速读一遍 | 代码审计、相关论文发散、子 agent 校验 |
| `full` | 默认 | 无 |
| `re-audit` | 已有 report.md，只重新审计某个部分 | 按 request 跳过 |

### 阶段 1: 获取与校验全文

- arXiv URL：同时读取 `abs`、`html`，下载 PDF 到 `source/paper.pdf`
- PDF：运行 MinerU 解析（除非已有 `mineru/manifest.json` 且 `state=done`）
- MinerU 包：读取 `manifest.json`、`full.md`、`content_list.json`

**MinerU 调用**（token 自动探测 `minerU_APIKEY` / `minerU_API` / 环境变量）：

```bash
python scripts/mineru_parse.py papers/<paper-slug>/source/paper.pdf --env .env --output papers/<paper-slug>/mineru
```

**MinerU 失败 fallback**：
- 下载失败：脚本已内置 3 次重试 + Node.js fallback
- 解析超时/服务不可用：改用 arXiv HTML（ar5iv）或 PyMuPDF 本地解析
- 扫描版 PDF：加 `--ocr`

自检：全文是否完整？图片、表格、公式、caption 是否能定位？

### 阶段 2: 原文对照逐段精读

生成 `notes/section-reading.md`。覆盖 Abstract、Introduction、Method、Experiments、Limitations/Discussion、Conclusion。每段记录：位置、短摘、转述、论证作用、隐含假设、可信度、追问。

对没读懂、证据不足、定义含糊、公式跳步的地方标注「存疑」。存疑项写清：疑点是什么、是作者没讲清楚还是证据不足、需要什么材料消解。

Reading card 格式和字段见 `references/report-spec.md`。

### 阶段 3: 论证链与证据矩阵

生成：
- `notes/argument-map.md`：主张、子主张、证据、缺口、替代解释
- `notes/assumption-ledger.md`：关键假设、依赖证据、失败后果
- `notes/evidence-matrix.md`：证据点覆盖 Figure、Table、公式、实验数字、消融、局限、代码路径
- `notes/contribution-claims.md`：作者自称贡献逐条列出，判定"真创新 / 工程改进 / 应用整合 / 实验验证 / 表述包装 / 存疑"

硬要求：贡献必须先引用作者 claim，再给独立判断。反事实问题按档位执行：`short` ≥2、`standard` ≥3、`long` ≥5。所有「存疑」项在论证链或证据矩阵中落位。

### 阶段 3.5: 诊断门

阶段 3 后必须做一次诊断：
- 核心主张是否已被证据支撑？
- 是否有致命缺陷（baseline 不公平、公式定义不清、实验不可复现）？
- 当前 `analysis_profile` 是否合适？
- 哪些段落没读懂？

决策：`continue` / `refocus` / `downgrade-profile` / `upgrade-profile` / `block-and-repair`。记录到 `notes/report-plan.md` 和 `deep-report-check.json.diagnostic_gate`。

### 阶段 4: 相关论文发散（`quick` 入口可跳过）

检索策略见 `references/related-work.md`。生成 `related/papers.md` 和 `notes/related-work-map.md`（按问题分类，不是论文列表）。

### 阶段 5: 实验与代码审计（`quick` 入口可跳过代码部分）

- `notes/experiment-audit.md`：claim、supporting evidence、baseline 公平性、metric 合理性、confounder、可信度评级
- `notes/code-audit.md`：论文机制到源码模块/函数/配置的对应关系。没有公开代码时说明搜索过程和替代实现

有公开代码时必须阅读 README、核心源码、训练/评估配置。代码克隆到 `papers/<paper-slug>/code/`。正文代码段每段不超过 30 行，标注文件路径和行号。

### 阶段 6: 报告计划

生成 `notes/report-plan.md`：报告主线、核心图表（≥1 Mermaid、≥2 证据表）、必进正文的内容点、reviewer-style 追问。

### 阶段 7: 生成 report.md

`report.md` 是最终 HTML 的唯一内容母稿。顶部必须写入：

```markdown
analysis_profile: standard
profile_reason: 常规会议论文且方法、实验、代码和相关工作都需要完整审计。
```

report.md 必须包含所有将进入 HTML 的 reading cards、公式、Mermaid、表格、图片引用、代码片段和相关论文链接。报告规格（reading card 字段、evidence embed 字段、mechanism block 字段、公式格式）见 `references/report-spec.md`。

生成后自读一遍：如果只是摘要堆叠，回到 notes 补证据再改。

### 阶段 8: 从 report.md 生成 HTML

```bash
python scripts/generate_html.py papers/<paper-slug>/notes/report.md papers/<paper-slug>/output/<paper-slug>-deep-report.html
```

生成后运行渲染检查：
```bash
python scripts/check_html_render.py papers/<paper-slug>/output/<paper-slug>-deep-report.html <analysis_profile> --json-output papers/<paper-slug>/notes/render-check.json
```

缺 Playwright 时用 Browser/chrome-devtools 等价检查，设 `render_check_method` 为 `"browser"`。

### 阶段 9: 自检与修订

```bash
python scripts/collect_report_counts.py papers/<paper-slug>/notes/report.md papers/<paper-slug>/output/<paper-slug>-deep-report.html --render-method browser --output papers/<paper-slug>/notes/deep-report-check.draft.json
python scripts/validate_deep_report_check.py papers/<paper-slug>/notes/deep-report-check.json
```

`collect_report_counts.py` 生成草稿（含 `manual_fields_required` 和 TODO 占位）。最终 `deep-report-check.json` 必须移除占位字段、补齐人工判断（诊断门、贡献 claim、subagent review），并通过 `validate_deep_report_check.py`。

最终 JSON 不得包含 `TODO:` / `待补:` / `占位:` / `placeholder:` 等占位标记。`contribution_claims` 必须是逐条 claim 数组。

### 阶段 10: 子 agent 校验（环境支持时）

推荐配置：role=`paper-deep-report-reviewer`，输入 report.md + HTML 路径 + notes 目录 + schema。不把主 agent 自评泄露给 reviewer。

reviewer 检查重点：HTML 是否真正呈现 reading cards、公式是否可渲染、方法机制是否有薄弱段落、贡献判别是否合理、存疑是否标注、相关论文是否有分类比较。

环境不支持子 agent 时：设 `subagent_review.supported=false`、`verdict="unsupported"`，由主 agent 做等价检查。`model` 字段填实际使用的模型名（不限定特定模型）。

## MinerU 内置调用规则

```bash
python skills/paper-deep-analyse/scripts/mineru_parse.py papers/<paper-slug>/source/paper.pdf --env .env --output papers/<paper-slug>/mineru
```

- token 自动探测：先查 `minerU_APIKEY`，再查 `minerU_API`，再查环境变量
- 下载含 3 次重试 + Node.js fallback
- 扫描版或图片型 PDF 使用 `--ocr`
- 解析失败时记录状态、`err_msg` 和退回读取方式，不静默跳过

## 适用场景

- 用户要求"逐段读""深度分析""组会精读""技术报告""审稿式分析""举一反三""发散相关论文"
- 用户已经有 MinerU 解析包、PDF、arXiv URL、论文 HTML、代码仓库或论文文本
- 用户想判断一篇论文是否值得复现、跟进、写 related work 或做研究选题
