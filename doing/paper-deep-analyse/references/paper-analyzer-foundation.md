# Paper Analyzer Foundation

`paper-deep-analyse` 内置并继承这些基础规则，不能因为 deep report 更重而丢掉。

## 工作目录

每篇论文必须有独立目录，所有 PDF、MinerU、代码、notes、HTML 都落在 `papers/<paper-slug>/` 内。HTML、notes 和证据引用不得继续指向 `tmp/` 临时目录。

## 代码搜索

1. 从论文主页、arXiv HTML、PDF 页脚、README badge 中提取官方代码。
2. 没有明确仓库时，用论文标题、方法名、作者名搜索 GitHub。
3. 代码放在 `papers/<paper-slug>/code/`。
4. 阅读顺序：README -> install/quickstart -> 核心源码 -> train/eval/config -> scripts/tests。
5. 正文代码段不超过 30 行，并标注文件路径和行号。

## HTML 基础模板要求

最终 HTML 必须包含：

- UTF-8、viewport、可读正文宽度、移动端响应式样式。
- KaTeX CSS/JS 和 auto-render。
- Mermaid 初始化。
- 表格、代码块、blockquote、figure、reading-card 样式。
- 本地图片使用相对路径，且生成后检查路径存在。

## Academic 基础硬指标

`paper-deep-analyse` 的指标应高于普通 academic 输出：

- 公式/算法片段按 `analysis_profile` 执行，并解释变量和直觉。
- Figure/Table 引用和嵌入按 `analysis_profile` 执行。
- 实验数据表和自制分析表数量按 `analysis_profile` 执行；短论文至少能读懂主结果，长论文要有足够表格支撑实验审计。
- 有公开代码时代码/配置片段数量按 `analysis_profile` 执行。
- 局限或威胁分析按 `analysis_profile` 执行；至少同时考虑作者自述/实验边界和独立判断，不要只写泛泛风险。
- 明确代码状态：已发布 / 待发布 / 无公开代码 / 替代实现。

## 禁止退化

- 不能只把 notes 写深，而 HTML 正文变短。
- 不能丢掉公式编号、Figure/Table 编号、代码路径。
- 不能只复述摘要、Introduction 或 README。
- 不能把相关论文写成无分类的链接清单。
