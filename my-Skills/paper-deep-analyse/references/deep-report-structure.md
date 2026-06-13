# Deep Report Structure

最终 HTML 要像技术报告，不像摘要卡片。

HTML 必须由 `notes/report.md` 生成或与其同步。`report.md` 是可审计母稿，HTML 是发布形态；不要在 HTML 阶段新增未回写的观点、证据或表格。

## 硬指标

先读取 `analysis_profile`：`short`、`standard`、`long`。硬指标按档位执行，不要把长论文阈值硬套给短论文，也不要让长论文借低档位偷薄。

- 中文正文建议 6000-10000 字；复杂论文可更长。
- 至少 10 个二级章节或等价结构。
- 原文对照 reading cards 数量按档位执行：`short` >=4、`standard` >=6、`long` >=8。必须使用可折叠 `<details class="reading-card">`：summary 只放位置、总短摘和一句主旨，展开后先给“原文对照展开”，再给完整转述、论证作用、分析、证据联动、存疑、追问；不要整段复制原文。“证据联动”必须指向 Figure/Table/公式/代码中的至少一种。
- “原文对照展开”要让读者理解原文段落的完整意思：使用 2-4 条版权安全原文短句 + 对应中文译述，而不是只重复 summary 的一句短摘。短句摘录只取最短必要技术短语，长内容用中文译述。
- 所有 reading cards 都必须是 details，不允许只有部分可折叠；每张展开后有效长度按档位执行：`short` 约 180 字、`standard` 约 220 字、`long` 约 250 字。
- 必须有“主要贡献判别”表：作者 claim、独立分类、创新性判断、证据、保留意见。
- 必须有“存疑清单”：没有读懂、作者未讲清楚、证据不足、实验设置不明、公式跳步等问题集中列出。
- 公式或算法片段按档位执行：`short` >=1、`standard` >=3、`long` >=5，并配变量逐项解释、直觉读法、设计动机、边界/副作用和证据连接；优先保留论文公式编号。公式块必须在 HTML 中无 `<em>`、`<strong>`、`<span>` 污染。
- Figure/Table 证据嵌入按档位执行：`short` >=2、`standard` >=3、`long` >=4，不只是文字引用。`long` 至少 2 个本地 MinerU 图片和 2 个重建论文关键表格/数字；`standard` 至少各 1 个；`short` 至少 1 个重建表格/关键数字。
- 自制分析表按档位执行：`short` >=2、`standard` >=3、`long` >=4；证据矩阵摘要、实验可信度评级、相关论文对比、代码审计表任选。
- 至少 1 个 Mermaid 图，展示方法机制、论证链或研究脉络。
- 有公开代码时，代码或配置片段按档位执行：`short` >=1、`standard` >=3、`long` >=5；每段不超过 30 行。
- 相关论文进入正文比较的数量按档位执行：`short` >=2、`standard` >=4、`long` >=6，并提供链接。
- 必须包含 reviewer-style critique 和 transfer ideas。

## 推荐章节

```text
1. Executive Summary
   - 贡献、可信度、适用边界、是否值得复现。

2. Contribution Claims
   - 作者自己 claim 的贡献。
   - 独立判断：真创新、工程改进、应用整合、实验验证、表述包装或存疑。

3. Research Context
   - 这个问题从哪里来。
   - 直接前作、替代路线、本文新增变量。

4. Section-by-Section Reading
   - 不是全文翻译，也不是只写总述。
   - 使用可折叠 reading cards 做原文对照：summary 扫读，展开深读。
   - 至少覆盖 Abstract、Introduction、Method、Experiments、Conclusion。
   - 每张卡片展开后要像一段小型 close reading，不是一句摘要。

5. Doubt Ledger
   - 单独列出「存疑」：作者没讲清楚、证据不足、公式跳步、解析不完整或需要外部资料。
   - 每条存疑都给出下一步查证路径。

6. Mechanism Dissection
   - 公式、架构图、算法流程。
   - 每个机制解释为什么设计成这样。
   - 每个机制至少包含：定义、设计动机、解决的失败模式、边界/副作用、和证据或代码的连接。
   - mechanism block 数量和长度按档位执行：`short` >=1 且约 220 字、`standard` >=2 且约 280 字、`long` >=3 且约 320 字。

7. Argument and Evidence
   - claim -> evidence -> gap。
   - 证明了什么 / 没证明什么。

8. Experiment Audit
   - 主结果、消融、行为分析、公平性、威胁。

9. Code Audit
   - 概念到源码。
   - 实现差异和复现风险。

10. Related Work Expansion
   - 相关论文对照和发散。

11. Reviewer-style Critique
   - 强项、弱项、关键追问。

12. Transfer Ideas
   - 可迁移任务、可改进方向、可落地实验。
```

## 写作风格

- 像组会主讲人：讲清楚，也敢判断。
- 每个强判断后面给证据，不要只写“显著”“有效”“重要”。
- 明确标注不确定性：可能、尚未证明、依赖假设。
- 没读懂的地方要写成「存疑」，并说明疑点来源；不要用“整体而言”“可能有效”等话术绕过去。
- 贡献判断要先尊重作者 claim，再独立分类，不能把工程整合强行写成真创新。
- 不回避负面结论：baseline 不公平、成本未报告、代码未对齐，都要写。
- 避免长段公式堆叠；公式后必须解释变量和直觉。
- 不允许“公式 + 一句人话解释”就结束。方法机制节必须有连续技术说明，读者应能据此复现机制的大致数据流和训练逻辑。
- 图表引用要就地可读：把本地图片或核心表格复制/重建到报告中，并解释读图/读表方式、关键元素、关键数字、支撑的 claim、不能推出的结论和可能误读。

## HTML 验收

- HTML 完整闭合，可浏览器打开。
- KaTeX 和 Mermaid 初始化存在。
- 公式块中不得出现 Markdown 污染后的 `<em>`、`<strong>` 等标签；发现后必须修 `report.md` 的公式写法再生成。
- 公式源 Markdown 也要预检：`\tag{}` 公式必须位于 display math；带下划线和花括号的 group 表达式要用 LaTeX 转义，不要写成会被 Markdown 识别的裸文本。
- 生成后必须做浏览器侧 KaTeX 检查：优先运行 `scripts/check_html_render.py`；若没有 Playwright，就用 Browser/chrome-devtools 等价检查 `.katex-error`、`.katex` 节点和 Mermaid SVG。
- Reading cards 必须是可折叠 details；如果只是普通 section/card，视为不通过。
- 本地图片相对路径正确。
- evidence block 内的图片必须渲染为 `<img>`，表格必须渲染为 `<table>`；页面中不得出现可见的 `![alt]`、`(data:image...)` 或 Markdown 管道表格文本。
- 表格移动端不溢出；长代码块可横向滚动。
- 生成后做一次静态检查：段落数、reading cards、表格数、图片路径、公式数量、相关论文链接数量、代码段数量。

## Minimal CSS additions

HTML 模板除保留 KaTeX、Mermaid、表格、代码块样式外，应加入 reading card 样式：

```css
.reading-card{border:1px solid var(--border);border-radius:8px;padding:1rem 1.1rem;margin:1.2rem 0;background:#fff}
details.reading-card>summary{cursor:pointer;font-weight:700}
.source-locator{font-size:.86rem;color:var(--muted);margin-bottom:.4rem}
.reading-card blockquote{margin:.5rem 0 1rem}
.evidence-embed{border:1px solid var(--border);border-radius:8px;padding:.85rem;margin:1.1rem 0;background:#fbfdff}
.math-block{overflow-x:auto;padding:.5rem 0}
.mechanism-block{border-left:3px solid var(--accent);padding:.2rem 0 .2rem 1rem;margin:1.2rem 0}
.doubt{border-left:4px solid #b45309;background:#fff7ed;padding:.85rem 1rem;margin:1rem 0}
.claim-table td:nth-child(4){font-weight:650}
```
