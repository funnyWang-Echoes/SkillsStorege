# Report Specification

最终 HTML 要像技术报告，不像摘要卡片。这是 reading card、evidence embed、mechanism block、公式、图表和自检 JSON 的唯一规格来源。`SKILL.md` 只管工作流，不重复这些细节。

## 阈值单一来源

所有 `short`/`standard`/`long` 档位阈值定义在 `schemas/thresholds.json`。三个脚本通过 `scripts/thresholds.py` 读取同一份。修改阈值只需改一个文件。

## Reading Card 规格

每张 card 必须是 `<details class="reading-card">`，展开后包含：

1. `<summary>`：位置 + 短摘 + 一句主旨
2. `<div class="source-locator">`：Section / page / MinerU item / Figure / Table
3. `<div class="source-expanded">`：2-4 条版权安全原文短句 + 对应中文译述（每条短句 ≤25 英文词）
4. 原文要点转述
5. 论证作用：背景铺垫 / 问题定义 / 方法机制 / 实验证据 / 局限承认
6. 分析思考
7. 证据联动：指向 Figure/Table/公式/代码中的至少一种，说明支撑什么、不支撑什么
8. 存疑：无 / 作者未讲清楚 / 证据不足 / 解析不足 / 需要外部资料
9. 追问

source-expanded 中"原文短句"和"中文译述"是字段关键词，写同义词（如"原文摘录"/"原文片段"）会被脚本漏数。统一用"原文短句 A / 中文译述 A"格式。

模板：

```html
<details class="reading-card">
  <summary>Section 3.2 · Eq. 5 · Short source excerpt</summary>
  <div class="source-locator">Section 3.2 · Eq. 5 · MinerU item 59</div>
  <div class="source-expanded">
    <p><strong>原文对照展开：</strong>用 2-4 条短摘 + 中文译述呈现这段原文的完整意思。</p>
    <ul>
      <li><strong>原文短句 A：</strong>最短必要短句；<strong>中文译述 A：</strong>逐句译述其技术含义。</li>
      <li><strong>原文短句 B：</strong>最短必要短句；<strong>中文译述 B：</strong>解释作者的限定条件或结论边界。</li>
    </ul>
  </div>
  <p><strong>原文要点转述：</strong>...</p>
  <p><strong>论证作用：</strong>...</p>
  <p><strong>分析思考：</strong>...</p>
  <p><strong>证据联动：</strong>连接 Figure/Table/公式/代码证据。</p>
  <p><strong>存疑：</strong>...</p>
  <p><strong>追问：</strong>...</p>
</details>
```

## Evidence Embed 规格

图表证据必须进入 `report.md`，再进入 HTML。不要只写"见 Table 1 / Fig. 2"。

```html
<div class="evidence-embed">
  <p><strong>证据：</strong>Table 3 对比 frozen / SFT / Flow-GRPO。</p>
  <table>
    <thead><tr><th>Setting</th><th>Average</th><th>Interpretation</th></tr></thead>
    <tbody><tr><td>Flow-GRPO</td><td>...</td><td>...</td></tr></tbody>
  </table>
  <p><strong>读图/读表方式：</strong>先看行列含义，再看关键差值。</p>
  <p><strong>关键元素：</strong>列出图中的模块、箭头、变量或表格中的核心列。</p>
  <p><strong>支撑：</strong>它能支持哪条 claim。</p>
  <p><strong>不支持：</strong>它不能推出什么，哪些替代解释仍然存在。</p>
  <p><strong>边界：</strong>样本、任务、baseline、成本或实现条件的限制。</p>
</div>
```

必填字段关键词：读图、关键元素、支撑、不支持、边界。写同义词会被脚本漏数。

MinerU 图片路径必须包含 `mineru`，例如 `../mineru/raw/images/...`。

## Mechanism Block 规格

方法机制节必须是连续技术说明，不能是"公式 + 一句人话解释"。

```html
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
```

必填字段关键词：定义、设计动机、失败模式、边界、证据。

## 公式规格

- 独立公式用 `$$ ... $$` 或 `\[...\]`；inline 用 `\(...\)` 或 `$...$`
- `\tag{}` 公式必须位于 display math
- 带下标花括号的表达式（如 `\{r_j\}`）要用 LaTeX 转义，不要写裸 `{r_j}`
- 生成 HTML 后公式块里不得出现 `<em>`、`<strong>`、`<span>` 等 Markdown 污染标签
- 每个重要公式后必须有 formula-analysis：变量逐项含义、直觉读法、设计动机、边界/副作用、与证据的连接

## 贡献判别规格

先列作者自己的 claim，再做独立判断。

| ID | Author-claimed contribution | Source location | Independent category | Novelty judgment | Evidence | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | | Abstract / Intro | 真创新 / 工程改进 / 应用整合 / 实验验证 / 表述包装 / 存疑 | | | |

分类口径：
- 真创新：问题设定、机制、理论、训练/推理范式或数据构造有清晰新增
- 工程改进：主要价值来自系统组合、流程优化、规模化
- 应用整合：把已有方法迁移到新任务/场景
- 实验验证：主要贡献是更系统的 benchmark、ablation、analysis 或负结果
- 表述包装：claim 听起来新，但证据显示更像已有路线的换名
- 存疑：无法从论文证据确认新颖性

## HTML 推荐章节

```text
1. Executive Summary — 贡献、可信度、适用边界、是否值得复现
2. Contribution Claims — 作者 claim → 独立分类 → 证据 → 保留意见
3. Research Context — 问题从哪里来，本文新增变量
4. Section-by-Section Reading — 可折叠 reading cards
5. Doubt Ledger — 存疑集中列出，每条给查证路径
6. Mechanism Dissection — 公式、架构、设计选择
7. Argument and Evidence — claim → evidence → gap
8. Experiment Audit — 主结果、消融、公平性、威胁
9. Code Audit — 概念到源码，实现差异和复现风险
10. Related Work Expansion — 分类比较，不是链接清单
11. Reviewer-style Critique — 强项、弱项、追问
12. Transfer Ideas — 可迁移任务、可改进方向
```

## 写作风格

- 像组会主讲人：讲清楚，也敢判断
- 每个强判断后面给证据
- 明确标注不确定性：可能、尚未证明、依赖假设
- 没读懂的地方写「存疑」，说明疑点来源
- 不回避负面结论：baseline 不公平、成本未报告、代码未对齐，都要写
- 避免长段公式堆叠；公式后必须解释变量和直觉

## CSS

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

## HTML 基础模板

最终 HTML 必须包含：
- UTF-8、viewport、可读正文宽度、移动端响应式样式
- KaTeX CSS/JS 和 auto-render
- Mermaid 初始化
- 表格、代码块、blockquote、figure、reading-card 样式
- 本地图片使用相对路径（默认不 base64 内嵌，除非 `--embed-images` 传入）

## 禁止退化

- 不能只把 notes 写深，而 HTML 正文变短
- 不能丢掉公式编号、Figure/Table 编号、代码路径
- 不能只复述摘要、Introduction 或 README
- 不能把相关论文写成无分类的链接清单
