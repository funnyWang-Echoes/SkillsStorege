---
name: xhs-knowledge
description: |
  把小红书收藏页里的笔记批量采集并整理成可导入 Obsidian / Typora / VS Code 的结构化 MD 文档。
  适用场景：批量备份收藏笔记、技术博客/论文/项目分类整理、本地离线保存。
  支持图文 + 视频笔记（视频不下载，仅记录链接）；图片自动下载到本地并以标准 Markdown 语法引用。
metadata:
  trigger: 整理小红书收藏 / 备份收藏笔记 / 收藏转 Obsidian
  source: 本仓库自研（基于 Angin/Post-to-xhs CDP 流程裁剪）
---

# xhs-knowledge — 小红书收藏 → 结构化知识库

## 你要做什么

把用户在 Chrome 里已经打开的小红书收藏页，转化为可直接拖入 Obsidian / Typora / VS Code / Logseq / Joplin 的独立 MD 文档。

## 不适用场景

- ❌ 发布笔记（用其他 xhs Skill）
- ❌ 评论、点赞、互动
- ❌ 实时浏览 / 搜索笔记
- ❌ 下载视频文件（sign 临时有效，不在范围）。**但 MD 里会保留视频源链接**（`masterUrl`、`coverUrl`）和时长，第二轮 P0-C1 修复后 4 个模板都会渲染 `## 视频` 区块。
- ❌ 多账号隔离（默认单账号已够用）

## 风险提示

按小红书平台规则，自动化抓取存在被风控、限流、封号风险：

- 建议在**测试号**上跑
- **小流量**、**慢节奏**（每条间隔 ≥ 1.5 秒）
- **不要**在主账号上跑大批量

## 凭证保护

`outputs/` 目录里包含 `xsec_token`、`userId` 等敏感凭据。本仓库的 `.gitignore` 已经自动忽略 `outputs/`、`logs/`、`*.err`，但其他位置请勿再手动保存这些字段。

`fetch_note_detail.py` 不会把作者的 `xsecToken` 写进 details JSON；`sourceMeta.feedUrl` 中的 token 仅用于 MD 回链，不会扩散到其他字段。

子代理分析时建议用文件路径传 details JSON，而不是把全文贴到聊天上下文。

## 默认工作流（5 步）

### 前置：用户操作

1. 在 Chrome 手动打开收藏页：
   `https://www.xiaohongshu.com/user/profile/{your_uid}?tab=fav&subTab=note`
2. 等笔记卡片在 DOM 里渲染出来
3. **之后不要操作 Chrome**

### Step 1: 采集收藏列表

```bash
cd scripts
python export_collection.py --max 40
# → outputs/list-feeds/collection_NNN.json
```

实现要点：
- 纯 JS DOM 探查，零导航，不打开新页面
- 默认 `--reuse-existing-tab`，复用用户在 Chrome 已打开的 fav tab
- boolean 检查用了 `if not fav:` 而不是 `if fav is None`，避免 `fav=None` 时崩溃

### Step 2: 抓取详情（可批量）

```bash
python fetch_note_detail.py \
  --input ../outputs/list-feeds/collection_NNN.json \
  --limit 20 --offset 0 \
  --output ../outputs/feed-detail/details_NNN.json
```

实现要点：
- 每条 note 的 `sourceMeta` 写入 `feedUrl`（含 `xsec_token`），保证 MD 里 `source:` 字段可点回小红书
- 作者的 `xsecToken` 不会被持久化（避免泄露）
- stdout 末尾打印真换行（不是字面 `\n`），下游脚本能正常截取

### Step 3: 下载图片

```bash
python download_images.py \
  --input ../outputs/feed-detail/details_NNN.json
# → outputs/assets/<noteId>/<NN>.{webp,jpg,png}
```

实现要点：
- 优先 `file --mime-type`（Git Bash / WSL 自带）
- Windows fallback：`python-magic-bin`
- 仅在 MIME 以 `image/` 开头时信任结果，否则保留服务端给出的扩展名
- 小红书服务端经常把 WebP 标成 JPG，实际扩展名以文件内容为准

### Step 4: 分析（派子代理或自己分析）

主代理（你，ZCode）作为 LLM，对每条笔记输出 analysis JSON：

- 分类：paper / skill / project / blog
- 摘要、要点、链接

写到 `outputs/intermediate/<noteId>.analysis.json`

**派发密度**：每条 note 派 1 个子代理并行（20 条 → 20 个子代理一次性派完）。

> 注：之前文档写「每 4 条派 1 个子代理」是误述，实际 retest 5 条都是 1 note 1 agent。多图笔记（>10 张）独立成 1 个 agent 是因为图片 OCR 会吃上下文预算，混在一起容易 OOM。

**子代理的多模态能力**：可以直接读 `outputs/assets/<noteId>/01.webp` 等图片，OCR 出图里的 GitHub URL、项目名、论文标题，写到 analysis 的 `links.github` / `links.homepage` / `links.arxiv` / `paper.title` 等字段。这是这个 Skill 最有价值的提取能力之一，不要跳过。

**URL 字段必须完整或留空**（第四轮 N-1 fix）：子代理写 `links.github` / `links.homepage` / `links.arxiv` / `links.demo` 时：

- **必须**以 `http://` 或 `https://` 开头（如 `https://github.com/ZJU-REAL/Polaris`）
- 不完整的残缺字符串（`ZJU-REAL/Polaris`、`arxiv.org/...`、`2607.28618`）**直接留空**，不要写
- 渲染器会做白名单校验，不合规的值会被丢弃，不会渲染成 404 链接

**`ocrNotes` 字段**：子代理在 analysis JSON 里新增一个 `ocrNotes` 字段（字符串），记录每张图读到了什么（论文标题、公司名、URL、关键数字）。这个字段不是给 MD 渲染用的，是给后续 Agent 追溯用的。如果某张图读不到（如 webp 太大被 Read 工具拒绝），写明原因，例如：

```json
"ocrNotes": "01 封面：浙大 Polaris 海报；02 时间线表，未见 URL；03 LangGraph 6 形态架构；04 LangGraph 文档链接..."
```

**大图自动转码**（OCR 前必做，第四轮 N-2 fix）：

```bash
python scripts/transcode_for_ocr.py
```

把 `outputs/assets/<noteId>/` 里尺寸超过 2048 像素的 webp 转成 PNG 到 `outputs/intermediate/ocr_tmp/<noteId>/`。子代理**只读** `outputs/intermediate/ocr_tmp/<noteId>/*.png`，**不要**自己调 ffmpeg 直接写 `outputs/assets/`（会污染 download_images 的输出目录）。

如果重跑 download_images 时担心子代理残留 png，加 `--clean` 自动删 stray png：

```bash
python scripts/download_images.py --input ... --output-root outputs/assets --clean
```

### Step 5: 渲染 MD

```bash
python render_markdown.py \
  --details ../outputs/feed-detail/details_NNN.json \
  --intermediate ../outputs/intermediate/ \
  --output ../outputs/knowledge/
# → outputs/knowledge/{projects,skills,papers,blogs}/*.md
# → outputs/knowledge/INDEX.md
```

实现要点：
- 图片路径用 `os.path.relpath(img, md_dir)` 动态计算，不假设固定目录结构
- 真实扩展名扫描：MD 引用的扩展名是真实文件扫描结果，不是硬编码 `.webp`
- `slugify` 去掉首字符 `-`，避免 shell/URL 把文件名当选项
- YAML frontmatter 用 `yaml_escape`，布尔值输出小写 `true`/`false`

## 4 类笔记模板

| 类型 | 模板字段 |
|---|---|
| **paper** | 论文元信息 + AI 总结 + 收藏者笔记 + 配图 |
| **skill** | Skill 描述 + GitHub 链接 + 安装方式 + 配图 |
| **project** | 项目概述 + 链接 + 核心要点 + 配图 |
| **blog** | 文章摘要 + 关键要点 + 全文 + 配图 |

分类优先级：**paper > skill > project > blog**（命中关键词即归类）

## MD 输出规范

- **标准 Markdown 语法** `![alt](path)`，Obsidian / Typora / VS Code / Logseq / Joplin 都能打开
- **相对路径**（动态计算），默认 `../../assets/<noteId>/<NN>.<ext>`，目录调整时仍正确
- **YAML frontmatter**，标准 YAML 语法，小写布尔
- **图片扩展名真实**（WebP / JPG / PNG 自适应）

## 失败处理

- **登录失败**：提示用户重新扫码登录
- **笔记不可访问**（已删除 / 私密）：自动跳过
- **图片下载失败**：保留 MD 引用，缺失文件标注
- **Skill stdout 被日志污染**：用 brace matching 提取 JSON（已内置在 fetch_note_detail.py）
- **SPA 误抓**：`feed_explorer` 严格校验 `noteDetailMap` key 与 feedId 一致

## 已知限制

- 不下载视频（占空间 + sign 临时有效）
- 收藏页 desc 为空的笔记：AI 摘要依据标题推断（不准确，但配合图片 OCR 仍可还原大部分信息）
- 不抓评论（量大优先级低）
- `cdp_publish.py` 的 `_send` 用 `recv(timeout=...)`，高并发下可能假超时
- 子代理读图 OCR 准确率取决于图片清晰度；图小、字小、截图截断都可能漏掉链接
- 子代理读大尺寸 webp（>2K 像素）会被 Read 工具拒绝；遇到这种情况需要在 OCR 前用 ffmpeg/ImageMagick 转成 PNG（参考 `tests/retest_2026-08-09.md` 的 Step 3.5）

## 输出目录结构

```
xhs-knowledge-skill/
├── .gitignore              ← 凭证保护（outputs/logs 自动忽略）
├── SKILL.md                ← 本文件
├── README.md
├── requirements.txt
├── scripts/
│   ├── chrome_launcher.py  ← 启动/重启 Chrome CDP
│   ├── cdp_publish.py      ← CDP 客户端（精简版）
│   ├── feed_explorer.py    ← noteDetailMap 提取
│   ├── export_collection.py ← fav tab 纯 JS 探查
│   ├── fetch_note_detail.py ← subprocess 调 get-feed-detail
│   ├── download_images.py  ← 图片下载 + 真实类型检测
│   ├── render_markdown.py  ← 4 类模板渲染
│   ├── fix_image_extensions.py ← 一次性修复扩展名
│   └── fix_md_image_syntax.py  ← 一次性修复 Obsidian 双链
└── outputs/                ← （gitignored）所有运行产物
    ├── list-feeds/         ← 收藏列表
    ├── feed-detail/        ← 笔记详情
    ├── assets/<noteId>/    ← 本地图片（子代理可读）
    ├── intermediate/       ← 子代理分析产物
    └── knowledge/          ← 最终 MD（拖入 Obsidian）
        ├── INDEX.md
        ├── projects/
        ├── skills/
        ├── papers/
        └── blogs/
```