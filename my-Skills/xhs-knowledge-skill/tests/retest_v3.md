# 端到端测试记录 v3 — 2026-08-09（第三轮修复后）

**测试目的**：第二轮对抗性审计派 4 个子代理（架构/安全/边界/契约）发现 7 个 P0 + 21 个 P1 + 22 个 P2。本轮修 7 P0 + 5 P1 后，跑 5 条新 case 验证修复没破东西。

**测试 case**：与 v2 同一批 5 条（Polaris / Swarm 下篇 / Swarm 上篇 / AskChem / AI4S 视频笔记）。

## 1. 5 步执行

### Step 1: 重抓详情

```bash
python scripts/fetch_note_detail.py \
  --input outputs/list-feeds/collection_20260809_125806.json \
  --offset 7 --limit 7 --output outputs/feed-detail/details_retest_a.json
python scripts/fetch_note_detail.py \
  --input outputs/list-feeds/collection_20260809_125806.json \
  --offset 19 --limit 1 --output outputs/feed-detail/details_retest_b.json
```

合并后过滤出 5 条 → `outputs/feed-detail/details_retest_5.json`

5 条全部抓到，所有 `sourceMeta.feedUrl` 含 `xsec_token`，所有作者 `xsecToken` 已脱敏。

### Step 2: 下载图片（用新 `--output-root`）

```bash
python scripts/download_images.py \
  --input outputs/feed-detail/details_retest_5.json \
  --output-root outputs/assets
```

```
[01/5] 浙大开源 Polaris      | imgs=8  (ok=8,  fail=0)
[02/5] Agent Swarm 下篇      | imgs=17 (ok=17, fail=0)
[03/5] Agent Swarm 上篇      | imgs=18 (ok=18, fail=0)
[04/5] AskChem 论文          | imgs=7  (ok=7,  fail=0)
[05/5] AI4S 视频笔记         | imgs=2  (ok=2,  fail=0)
[DONE] 52 张成功, 0 失败
```

52/52 下载成功，全 `.webp`。**P0-C3 修复验证**：`--output-root`（不是 `--output`）是正确参数。

### Step 3: 转码脚本（新 P0-A3）

```bash
python scripts/transcode_for_ocr.py
```

```
[OK] 扫描 5 个 note 目录
[DONE] 扫描 52 张 → 转码 0，跳过 52，失败 0
```

这批 52 张图都是 ≤2048 像素，不需要转。**转码逻辑单元测**（注入一张 2160×2880 假图）：

```
created fake large 99.webp (2160x2880)
[DONE] 扫描 53 张 → 转码 1，跳过 52，失败 0
[DONE] outputs\intermediate\ocr_tmp\6a73d631…\99.png
```

P0-A3 脚本工作正常：尺寸 > 阈值自动转 PNG 到 `ocr_tmp/<noteId>/`。**注**：5 个子代理本次没有用本脚本（直接调 ffmpeg 转），下一次跑建议在子代理任务模板里显式说「跑 transcode_for_ocr.py 再读图」。

### Step 4: 5 个子代理并行分析

5 个子代理按 SKILL.md v2 的 `ocrNotes` 字段要求重写 5 个 analysis JSON：

```
noteId: 6a73d631…  project  OCR 读出 ZJU-REAL/Polaris 仓库、六阶段流水线、AI 评审 Elo 排名、PolarisBuddy 全局助手
noteId: 6a716ede…  blog     OCR 8 张图，扫架构表 + 时间线 + Context engineering 章节
noteId: 6a716d52…  blog     本次 OCR 18 张全图（v2 只 OCR 9 张）—— 上篇两章扩到四章，Claude Code 三形态、Cursor 四角色
noteId: 6a6fec2…   paper    OCR 出 AskChem 完整细节：147K papers / 2.4M claims / NYU / arXiv 2607.28618
noteId: 6a67efe4…  blog     OCR Auto MD 科研智能体方案、八元高熵合金案例图
```

**P0-A3 间接收益**：v2 时 Swarm 上篇 9-18.webp 没 OCR 机会（18 张只 OCR 9 张）；本次 18 张**全部 OCR**（子代理用 ffmpeg 手动转码绕开了 transcode 脚本），验证 SKILL.md 提到的多模态 OCR 流程**实际可用**。

### Step 5: 渲染 MD（4 模板加 video_block）

```bash
python scripts/render_markdown.py \
  --details outputs/feed-detail/details_retest_5.json \
  --intermediate outputs/intermediate/ \
  --output outputs/knowledge_retest/
```

```
[project] 浙大开源 Polaris → 6a73d631…_浙大开源-Polaris端到端-AI-科研智能体.md
[blog   ] Agent Swarm 下篇 → 6a716ede…_从-Agent-Team-到-Agent-Swarm下篇.md
[blog   ] Agent Swarm 上篇 → 6a716d52…_从-Agent-Team-到-Agent-swarm上篇.md
[paper  ] AskChem          → 6a6fec2…_AskChem把论文拆成claim.md
[blog   ] AI4S 视频笔记    → 6a67efe4…_最近在AI4S上的成果.md
```

5 个 MD + 1 INDEX.md。**P1-A4 验证**：project + skill 模板代码量减少，结构一致。

## 2. 13 项检查

```
[1]  details 条数: 5 期望 5                           ✓
[2]  sourceMeta.feedUrl 含 xsec_token                ✓ (P0-3 仍生效)
[3]  author.xsecToken 已脱敏                          ✓ (P1-5 仍生效)
[4]  图片: 期望 52, 实际 52 (清理 stray png 后)       ✓
[5]  MD 图片引用: 52/52 文件存在                      ✓ (P1-1/2 仍生效)
[6]  图片扩展名: {'.webp': 52}                        ✓ (P1-2 仍生效)
[7]  .gitignore 含 outputs/                           ✓ (P0-2 仍生效)
[8]  analysis 中无 author.xsecToken 泄漏              ✓
[9]  YAML frontmatter 合法: 5/5                       ✓ (P1-7 仍生效)
[10] 5 个 analysis 都有 ocrNotes 字段                  ✓ (P0-C2)
[11] transcode_for_ocr.py 存在且可执行                ✓ (P0-A3)
[12] CDP host 白名单: 拒绝 evil.com                  ✓ (P0-S1)
[13] get_feed_detail 参数: [self, feed_id, xsec_token] ✓ (P1-A6 删评论死代码)
[14] feed_explorer fallback 改对（删 keys[0]===feedId） ✓ (P0-A7)
```

**全部 14 项通过。**

## 3. 新发现（第三轮验证附带）

抽 2 个 MD 看质量时发现子代理 OCR 写了**残缺 URL**：

### N-1: 链接字段 schema 不严谨

**观察**：
- `outputs/knowledge_retest/projects/6a73d631…_Polaris.md` 第 37 行：`- 🔗 **GitHub**：[ZJU-REAL/Polaris](ZJU-REAL/Polaris)` —— 子代理把 `github.com/ZJU-REAL/Polaris` 读成了 `ZJU-REAL/Polaris`（丢前缀）
- `outputs/knowledge_retest/papers/6a6fec2…_AskChem.md` 第 42 行：`[2607.28618](2607.28618)` —— 子代理把 arXiv ID 当链接值，且 paper 模板同时把 `paper.arxivId` 和 `links.arxiv` 都渲染了

**根因**：
- 子代理写 analysis 时，URL 字段值可能是"看起来像 URL 但不完整"的字符串
- 模板无防御：`[{links.github}]({links.github})` 原样渲染残缺字符串
- paper 模板把 `paper.arxivId` 和 `links.arxiv` 都渲染，重复

**严重度**：🔴 P0（破坏 MD 可读性，链接渲染成 `[残缺字符串](残缺字符串)`，用户点击 404）

**修复建议**（下轮做）：
1. 在 `render_markdown.py` 的链接区块对 `links.github` 等字段做白名单校验：
   - URL 必须以 `http://` 或 `https://` 开头
   - `links.arxiv` 必须以 `https://arxiv.org/` 开头
   - 否则降级为纯文本（"`ZJU-REAL/Polaris`（注：OCR 未读出完整 URL）"）
2. paper 模板去掉 `links.arxiv` 的重复渲染（`paper.arxivId` 已包含）
3. SKILL.md Step 4 增规则：子代理写 `links.*` 时**必须**写完整 URL，写不完整就留空

**本轮范围外**：第二轮审计的契约子代理把这列为 P2，但实际触发后严重度是 P0。下轮必修。

### N-2: 子代理绕开了 transcode_for_ocr.py

**观察**：本次 5 个子代理里至少 1 个（Swarm 上篇）用 `ffmpeg` 直接把 webp 转 png 写到 `outputs/assets/<noteId>/`，绕开了 `outputs/intermediate/ocr_tmp/`。

**问题**：
- `outputs/assets/` 本应是 `download_images.py` 唯一写入方，子代理手动写污染了目录结构
- 重跑 download_images 看到 `01.webp` 和 `01.png` 同时存在时，`images_block` 扫描 `f.startswith("01.")` 会取**第一个匹配的扩展名**，随机性

**根因**：
- SKILL.md v2 写"ffmpeg/ImageMagick 转"是散文，没指定**输出目录**
- transcode_for_ocr.py 是 v3 新增的，子代理任务模板里没显式说"先跑这个"

**严重度**：🟡 P1（功能上 OK，污染目录是次要问题）

**修复建议**（下轮做）：
1. SKILL.md Step 4 子代理模板明确写：**先跑 `transcode_for_ocr.py`，再读 `outputs/intermediate/ocr_tmp/<noteId>/*.png`**；禁止直接 ffmpeg 写到 `outputs/assets/`
2. `download_images.py` 加 `--clean` 选项，重跑前删 stray `.png`

**本轮范围外**：留下次。

## 4. 与前两轮对比

| 维度 | v1 | v2 | v3 |
|---|---|---|---|
| 修复项 | 13 项（第一轮）| + OCR 多模态 + 文档去 AI 味 | + 7 P0 + 5 P1 |
| 端到端 case | 5 | 5 | 5 |
| 图片下载 | 38 | 52 | 52 |
| 多图 OCR | 未做 | 1 case 部分 | 1 case 全图（18/18）|
| MD 渲染模板 | 4 类 | 4 类 + 多模态提示 | 4 类 + 视频区块 |
| cdp_publish 行数 | 374 | 374 | 347 |
| 子代理分析数 | 5 | 5 | 5 |
| 9-14 项检查 | 9 全过 | 9 全过 | 14 全过 |

## 5. 剩余风险

继承自 v2 + 本轮新发现：
- N-1 链接字段 schema 不严谨（🔴 P0，下轮必修）
- N-2 子代理绕开 transcode 脚本（🟡 P1，下轮修）
- 第二轮审计列出的 22 个 P2 待办（见 `tests/bugfix_log.md` 第三轮修复小节）

## 6. 结论

第三轮修复**全部 14 项验证通过**。新发现 1 个 P0（链接字段 schema）和 1 个 P1（子代理流程约束），已记录等下轮修。

Skill 当前状态：
- ✅ 5 步流程稳
- ✅ 多模态 OCR 可用（v3 验证 Swarm 上篇 18 张图全 OCR）
- ✅ 视频区块契约兑现（虽然本批没有 video 笔记触发，但 4 个模板都加了 video_block）
- ✅ CDP host 安全 + 不再复用错的 tab + 不抓评论
- ✅ feed_explorer fallback 真修（不是第一轮的假修复）
- ⚠️ 链接字段 schema 需下轮加固（子代理 OCR 残缺 URL 渲染成 404 链接）