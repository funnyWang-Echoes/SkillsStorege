---
name: paper-close-reading
description: |
  带注释的论文逐段双语精读。一边读一边分析——每段先给中文翻译（保留原文意思），再给即时分析（这段在论证什么、怎么连接前段、有没有问题），疑问有 ID 追踪并在被回答时显式标记呼应。代码对照、实验审计、相关论文比较内嵌在阅读中，读到哪里查到哪里。举一反三从阅读连接中涌现，不是硬加的独立章节。
---

# Paper Close Reading

这个 skill 做的事很简单：像坐在懂行的同事旁边读论文，逐段翻译 + 即时分析 + 追问追踪。最终产物就是这份精读文档本身——不是一个"读完再写"的技术报告。

## 核心理念

- **阅读即分析**。不是先读完（孤立卡片），再分析（独立轮次），最后拼报告。每段读完就分析，分析长在段落旁边。
- **前后呼应**。每段分析显式指回前面的段落（"这里回应了 §2.1 的疑问 Q3"），疑问有 ID 追踪，被回答时标记闭环。
- **最大化保留原文**。每段先给完整中文翻译（不是 ≤25 词短摘），再给分析。读者能对照原文意思理解。
- **举一反三从阅读中涌现**。不是独立章节，而是从"这段机制能怎么迁移"的思考中自然长出来。

## 阅读深度

| 档位 | 适用 | 覆盖 |
|---|---|---|
| `quick` | 快速读核心 | Abstract + Method + Experiments |
| `full` | 默认 | 全文逐段 |
| `deep` | 重度精读 | 全文逐段 + 代码逐函数对照 + 相关论文逐篇比较 |

用户不指定时默认 `full`。`deep` 档在读 Method 时逐函数对照源码，读 Related Work 时逐篇比较差异。

## 输出目录

```text
papers/<paper-slug>/
├── source/paper.pdf, source.md
├── mineru/manifest.json, full.md, content_list.json, raw/
├── code/                    # 有公开代码时克隆
└── output/
    └── <paper-slug>-reading.html   # 唯一最终产物
```

没有 12 个中间 notes 文件。精读文档就是产物，HTML 就是精读文档。

## 工作流

### 1. 获取论文

- arXiv URL：读取 `abs`、`html`，下载 PDF
- 运行 MinerU 解析（除非已有 `mineru/manifest.json` 且 `state=done`）
- MinerU 失败时用 arXiv HTML（ar5iv）作为替代阅读材料

```bash
python scripts/mineru_parse.py papers/<paper-slug>/source/paper.pdf --env .env --output papers/<paper-slug>/mineru
```

MinerU token 自动探测 `minerU_APIKEY` / `minerU_API`。下载含 3 次重试 + Node.js fallback。扫描版用 `--ocr`。

### 2. 逐段精读

这是核心步骤，也是唯一的内容生产步骤。读 `mineru/full.md` 或 arXiv HTML，**按论文原文顺序逐段**生成精读文档。

**默认一段原文 = 一个精读块。** 如果 2-3 段原文逻辑紧密（同一机制的连续描述、同一实验的设置+结果），可以合并成一个精读块，标题标注 `段落 N-M（合并）`。

精读块标题格式：`### §X.Y 段落 N`（可选括号摘要 ≤10 字，不要长标题）。

每段精读块包含：

#### 2.1 中文翻译

把这段原文完整翻成中文。不是摘要，不是短摘——是让读者能对照原文理解这段在说什么的完整翻译。**翻译区只放翻译，不混入分析/批评/审计。** 版权安全：翻译是再创作，不复制原文。

#### 2.2 即时分析

这段在论证链里承担什么角色？回答三个问题：
- **这段在说什么**：一句话概括作者这一段要干什么
- **怎么连接前段**：这段和前面哪段呼应？回应了哪个疑问？还是开了新话题？（显式写 `【呼应 §X.Y】` 或 `【新话题】`）
- **有没有问题**：逻辑跳步、证据不足、定义含糊、实验设置可疑——**审计和批评只放这里，不混入翻译区**

#### 2.3 疑问追踪

这段引出的疑问给它一个 ID（Q1, Q2, ...）。格式：
```
**疑问 Q3：** router 怎么决定选哪个 expert？
```

当后面的段落回答了这个疑问时，在对应段落的即时分析里写：
```
**【回应 Q3】** 这里解释了 router 输入 = 特征点 + 全局潜码。Q3 已回答 ✓
```

读完最后一段后，回顾所有疑问，生成疑问追踪表：
```markdown
| Q# | 提出位置 | 内容 | 状态 | 回答位置 |
|---|---|---|---|---|
| Q1 | §1.1 | GAN 怎么 scale up？ | ✓ 已回答 | §3.1 |
| Q2 | §1.2 | MoE 的 sparse activation 具体怎么做？ | ✓ 已回答 | §3.2 |
| Q3 | §3.2 | router 怎么选 expert？ | ✓ 已回答 | §3.3 |
| Q4 | §4.1 | baseline 是否公平？ | ✗ 未回答 | — |
```

未回答的疑问 = 这篇论文的局限或存疑点，在最后的"举一反三"里讨论。

#### 2.4 论文图表嵌入

MinerU 解析后的图片在 `mineru/raw/` 目录下。当段落原文引用了 Figure/Table 时，精读块**必须**嵌入对应图片，不能只有文字。格式：

```markdown
![Figure 2: Router 架构图](../mineru/raw/images/figure_2.jpg)

*图 2：Router 接收特征点和全局潜码，输出 expert 选择概率。*
```

每张图下面必须有图注（斜体），说明这张图在读什么。HTML 生成器会把本地图片转成 base64 内嵌，保证单文件可分享。

#### 2.5 代码引用（正文只引，不贴）

读到 Method 的关键机制时，在即时分析里只写一句引用：

```
**代码：** router 实现在 `text_generator.py:1655`，详见文末代码附录。
```

**正文不贴代码**——代码集中放在文末"核心代码附录"，整段贴出核心实现并附讲解。这样读者读正文时不被代码打断。

#### 2.6 实验即时审计（读到 Experiments 时）

读到实验段落时，当场审计：baseline 是否公平？metric 是否合理？有没有 confounder？不要把实验审计做成独立轮次。

#### 2.7 相关论文即时比较（读到 Related Work 时，`deep` 档逐篇）

读到 Related Work 时，当场比较：这篇前作和本文的关系是什么？本文新增了什么？不要把相关论文做成独立的"发散"章节。

### 3. 精读尾部

读完最后一段后：

#### 3.1 疑问追踪表

把所有 Q1-Qn 集中列出来，三态标注：✓ 已回答 / ◐ 部分回答 / ✗ 未回答。未回答和部分回答的 = 存疑点。

#### 3.2 举一反三

从阅读中涌现的连接出发，写 2-4 条迁移启发。每条必须：
- 指明来源段落
- 给出具体迁移路径（迁移到什么任务/场景、为什么能迁移）
- 给出最小验证实验（怎么做最小实验来验证迁移可行性）

不要写"这个思路理论上可以迁移到 X"这种无法操作的抽象建议。

#### 3.3 一句话总结

这篇论文到底在干什么、做得怎么样、值不值得跟。三句话说清楚。

#### 3.4 核心代码附录

有公开代码时，在文档末尾放"核心代码附录"章节。正文里只引用了 `文件名:行号`，这里整段贴出核心代码并附讲解：

```markdown
## 核心代码附录

代码来源：https://github.com/zhujiapeng/Aurora

### 代码块 1: Router 实现

**对应论文：** §3.2 Router Design
**文件：** `models/text_generator.py:1655-1690`

```python
class Router(nn.Module):
    ...
```

**讲解：**
- `self.gate` 对应论文的 router 线性层
- 代码用了 `top_k=2`，论文写的是完全稀疏——实现差异
- `global_w` 就是论文说的"文本集成的全局潜码"
```

规则：每块标注对应论文章节+文件行号，代码后必须有讲解，每段不超过 40 行，只贴核心代码。

### 4. 生成 HTML

精读文档写完后，生成带样式的 HTML（KaTeX 公式、Mermaid 图、可折叠段落、疑问高亮）。

```bash
python scripts/generate_reading_html.py papers/<paper-slug>/output/<paper-slug>-reading.md papers/<paper-slug>/output/<paper-slug>-reading.html
```

### 5. 自检

```bash
python scripts/validate_reading.py papers/<paper-slug>/output/<paper-slug>-reading.md
```

自检只问三件事：
1. 全文 section 是否都覆盖了？（按档位：`quick` 只查核心 3 节，`full`/`deep` 查全节）
2. 每段精读块是否有翻译 + 分析？（不能只有翻译没分析，也不能只有分析没翻译）
3. 疑问是否都有闭环？（已回答的标 ✓，未回答的在追踪表里标 ✗）

不检查 reading card 数量、evidence embed 配额、mechanism block 字数这些。那些是旧 skill 的"凑指标"思路。新 skill 的质量由阅读深度本身决定，不是由计数器决定。

## 精读文档格式

详细格式和字段见 `references/close-reading-spec.md`。

## 内置资源

| 资源 | 用途 |
|---|---|
| `scripts/mineru_parse.py` | MinerU 精解析（复用自 paper-deep-analyse） |
| `scripts/extract_paper_info.py` | 论文元数据抽取（复用） |
| `scripts/generate_reading_html.py` | 从精读 md 生成 HTML（新写） |
| `scripts/validate_reading.py` | 精读自检（新写，极简） |
| `references/close-reading-spec.md` | 段落精读块格式规格 |
| `references/mineru-api-notes.md` | MinerU API 调用细节（复用） |

## 适用场景

- 用户要求"逐段读""精读""翻译着读""一边读一边分析"
- 用户想真正理解一篇论文在干什么，而不是要一份"技术报告"
- 组会精读、复现前理解、写 related work 前的深度阅读
