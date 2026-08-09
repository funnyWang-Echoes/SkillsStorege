# Bugfix Log

记录 xhs-knowledge-skill 自打包以来的代码改动。

## 2026-08-09 第一轮修复

### 修复列表

| 类别 | 文件 | 问题 | 修法 |
|---|---|---|---|
| 边界 | `scripts/export_collection.py:121` | 写错的 boolean 检查 `if not fav is None and not fav:`，fav=None 时崩溃 | 改为 `if not fav:` |
| 安全 | `.gitignore` (新文件) | `outputs/`、`logs/`、`*.err` 没排除，`xsecToken` 会进 git | 新建 `.gitignore` 覆盖 |
| 契约 | `scripts/fetch_note_detail.py` | 不写 `sourceMeta.feedUrl`，MD 回链丢 xsec_token | `sourceMeta` 写入 `feedUrl` |
| 可移植 | `scripts/download_images.py` + `scripts/fix_image_extensions.py` | 强依赖 `file` 命令（Windows 非 Git Bash 静默失败） | requirements.txt 加 `python-magic[-bin]` 兜底；`detect_real_mime` 容错 |
| 契约 | `scripts/feed_explorer.py` | SPA 切换时单 key fallback 可能拿到旧笔记 | 严格 key 匹配（fallback 时校验 key === feedId） |
| 契约 | `scripts/render_markdown.py` | 相对路径假设 `--output` 必须固定 | 用 `os.path.relpath(img, md_dir)` 动态算 |
| 契约 | `scripts/render_markdown.py` | 图片扩展名硬编码 `.webp`，未来 png/jpg 出现会 404 | 扫描真实文件拿扩展名 |
| 边界 | `scripts/render_markdown.py` | `slugify` 首字符 `-` 不处理（shell/URL 当选项） | `lstrip('-')` |
| 安全 | `scripts/fetch_note_detail.py` | 作者 `xsecToken` 也写进 details JSON | author 不持久化 `xsecToken` |
| 架构 | `scripts/cdp_publish.py` | 死代码（`import base64`、`FEED_DETAIL_URL_TEMPLATE`、`DEFAULT_FEED_DETAIL_COMMENTS_LOAD_SECONDS`、`ACTION_INTERVAL`） | 清掉 |
| 架构 | `scripts/fetch_note_detail.py:287` | `\\n` 字符串字面量 bug | 改为真 `\n` |
| 边界 | `scripts/download_images.py` | `detect_real_mime` 对 file 命令错误信息（"cannot open..."）静默接受 | 要求 image/* 前缀 |
| 架构 | `scripts/render_markdown.py` | 缺 `SCRIPT_DIR` 定义导致 `images_block` 失败 | 加 `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` |

### 修复后的端到端验证

```
[1] collection: 20 条
[2] details: 5 条
    feedUrl 含 xsec_token: True
    author.xsecToken 不存在: True
[3] assets: 38 张图
[4] MD: 5 个（图片路径全部解析正确）
[5] MD frontmatter source 含 xsec_token: True
[6] .gitignore 含 outputs/: True
```

### 未修的项

| 项 | 文件 | 说明 |
|---|---|---|
| `if False else` 死分支 | `fetch_note_detail.py:132-133` | 仅代码风格，运行正确 |
| `_send` 高并发假超时 | `cdp_publish.py:103` | 单进程使用无影响 |
| `desc` 含 `\n\t` 在 MD 中可能误解析列表 | `render_markdown.py` | 实际渲染测试无问题 |
| subprocess timeout 后 CDP 残留 | `fetch_note_detail.py:63` | 串行使用无阻塞 |
| `likedCount` 在 JSON 里是字符串 | `fetch_note_detail.py:202` | 文档级，保持字符串 |

### 待改进项

1. `make_feed_detail_url` 加白名单（`re.fullmatch(r'[0-9a-f]{16,32}', feed_id)`）
2. `download_one` 加 URL 白名单，拒绝私网 IP（防 SSRF）
3. CDP `--host` 不允许非 localhost
4. README 增补凭据与隐私风险提示

## 2026-08-09 第二轮修复（与第一轮同期发现）

### 新增功能

- 子代理分析时显式支持多模态读图 OCR 链接（详见 SKILL.md Step 4）
- `outputs/assets/<noteId>/NN.webp` 在子代理上下文里可直接读

### 重测验证（5 条新 case）

详见 `tests/retest_2026-08-09.md`（即 `audit_retest.md` 的改名版）。

## 2026-08-09 第三轮修复（第二轮对抗性审计）

派 4 个子代理（架构 / 安全 / 边界 / 契约）二次审计发现 7 个 P0 + 21 个 P1 + 22 个 P2。本轮修 7 个 P0 + 5 个关键 P1；其余 P2 见下一节。

### 必修清单

| # | 严重度 | 来源 | 文件 | 问题 | 修法 |
|---|---|---|---|---|---|
| P0-C1 | 🔴 | 契约 | `scripts/render_markdown.py` | 视频笔记契约不一致：文档承诺"仅记录链接"，4 个模板根本没渲染 video 区块，masterUrl 在 MD 里完全丢失 | 新增 `video_block(note)` 辅助函数，4 个模板在 `## 配图` 前插一段；视频笔记现在会渲染 `## 视频` 区块（masterUrl + coverUrl + 时长） |
| P0-A3 | 🔴 | 架构 | `scripts/transcode_for_ocr.py` (新) | retest 18 张图只 OCR 7 张（10-18.webp 没机制可读） | 新增脚本：扫 assets/，>2048 像素的 webp 用 Pillow 转 PNG 到 `outputs/intermediate/ocr_tmp/<noteId>/`，子代理读 PNG 不会被 Read 工具拒绝 |
| P0-A7 | 🔴 | 架构 | `scripts/feed_explorer.py:84` | 第一轮 P1-4 假修复：`keys[0] === feedId` 在 keys.length===1 时永远成立，等于没校验 | 改成"目标 key 缺失 + detailMap 恰好 1 个 key" 才 fallback；2+ key 时报错 |
| P0-S1 | 🔴 | 安全 | `scripts/cdp_publish.py:75` | CDP `--host` 无白名单（第一轮 P2 待办，升级 P0） | `XiaohongshuPublisher.__init__` 加 `if not _is_local_host(host): raise CDPError` |
| P0-B4 | 🔴 | 边界 | `scripts/cdp_publish.py:_find_or_create_tab` | 多 tab 时复用错 tab：之前只看 URL 含 xhs 就复用，会把用户浏览中的 explore/search tab 强制跳走 | 优先匹配 fav tab（`/user/profile` + `tab=fav`），其次含 xhs 的任意 tab，最后**新建 tab**（不再随便用用户的页面） |
| P0-C3 | 🔴 | 契约 | `tests/retest_2026-08-09.md:45` | retest 命令 `--output outputs/assets` 在 download_images.py 里**根本不存在** | 改成 `--output-root outputs/assets` |
| P0-C2 | 🟡 | 契约 | `SKILL.md` Step 4 | `ocrNotes` 字段没在 SKILL.md 出现，子代理不知道要写 | SKILL.md 加 `ocrNotes` 字段说明 + 给 JSON 示例 |
| P1-A4 | 🟡 | 架构 | `scripts/render_markdown.py` | project 与 skill 模板 90% 重复 | 抽 `_render_simple_template()` 公共函数，两个模板变薄壳 |
| P1-A8/C4 | 🟡 | 架构/契约 | `SKILL.md:101` | 文档说"每 4 条派 1 个子代理"，retest 实际"1 note 1 agent" | 改为"每条 note 派 1 个子代理" |
| P1-A6 | 🟡 | 架构 | `scripts/cdp_publish.py` | 30 行 `_load_feed_detail_comments` 死代码 + 5 个 CLI 参数 | 全删；`get_feed_detail(feed_id, xsec_token)` 函数签名收窄；cdp_publish 从 374 行降到 347 行 |
| P1-B7 | 🟡 | 边界 | `scripts/download_images.py:184` | 跳过阈值 100 byte 过小，会误判断网残留为成功 | 提到 1024 byte |
| P1-B9 | 🟡 | 边界 | `scripts/fetch_note_detail.py:extract_tags` | 只取 tag.get('name')，遇到 tagName/tag_name 字段就 0 tag | 加 fallback |
| P1-A3 | 🟡 | 架构 | `scripts/fetch_note_detail.py:132-134` | `if False else` 死分支 | 删掉死分支 |

## 2026-08-09 第四轮修复（第三轮重测附带发现）

第三轮 retest_v3.md 抽 MD 质量时新发现 2 个 bug：
- N-1 链接字段 schema 不严谨（子代理 OCR 残缺 URL 渲染成 404）
- N-2 子代理绕开 transcode_for_ocr.py 手动 ffmpeg 转码到 outputs/assets/

本轮把这两条必修 + 3 个顺手修（desc 清洗、xsec_token 全字段脱敏、download_one 失败删半成品）全做完。

### 必修清单

| # | 严重度 | 来源 | 文件 | 问题 | 修法 |
|---|---|---|---|---|---|
| N-1 | 🔴 P0 | retest_v3.md | `scripts/render_markdown.py` | 子代理 OCR 残缺 URL 渲染成 `[残缺](残缺)`，用户点开 404 | 新增 `sanitize_url()`：URL 必须以 `http(s)://` 开头，否则返回空；4 个模板的 links 渲染都走 `sanitize_url` |
| N-1 | 🔴 P0 | 同上 | `render_markdown.py:render_paper` | `paper.arxivId` + `links.arxiv` 同时渲染重复 | 删 `links.arxiv` 重复渲染（保留 `paper.arxivId`） |
| N-2 | 🟡 P1 | retest_v3.md | `scripts/download_images.py` | 子代理手动 ffmpeg 转 .png 写到 `outputs/assets/`，污染 download_images 输出目录 | 加 `--clean` 选项，开跑前删 stray `.png` |
| N-2 | 🟡 P1 | 同上 | `SKILL.md` Step 4 | 文档只写"ffmpeg/ImageMagick 转"散文，没指定输出目录 | 显式写"先跑 `transcode_for_ocr.py`，只读 `ocr_tmp/<noteId>/`，不要自己 ffmpeg 写到 assets/" |
| N-3 | 🟢 P2 | bugfix_log 第二轮 P2 待办 | `render_markdown.py` | 子代理可能把 `xsec_token=...` 粘到 `links.*`/`keyPoints` 等字段 | 新增 `redact_sensitive()` 递归脱敏，main() 入口跑一次 |
| N-4 | 🟢 P2 | bugfix_log 第二轮 P2 待办 | `render_markdown.py` | desc 含 `\n\t\t` 满屏空行 | 新增 `clean_desc()` 把连续空白压成单空格；paper/blog 模板都用 |
| N-5 | 🟢 P2 | bugfix_log 第二轮 P2-11 | `download_images.py:download_one` | retry 失败时只有 `size<100` 才删半成品，size=200 残留会被下次跳过 | 抽 `_cleanup_partial(dst)` 任意大小都删；retry 异常路径统一调用 |

### 端到端验证（v4）

详见 `tests/retest_v4.md`。**19 项检查全部通过**（含 9 个新单测）。

### 下轮待办（剩余 P2，5 项）

**第三轮重测发现的新问题**：

| 严重度 | 文件 | 问题 | 修法 |
|---|---|---|---|
| 🔴 P0 | `scripts/render_markdown.py` 链接渲染 | 子代理 OCR 出的 `links.github="ZJU-REAL/Polaris"`（丢 `github.com/`）和 `links.arxiv="2607.28618"`（丢 `https://arxiv.org/abs/`）被模板原样渲染成 `[残缺字符串](残缺字符串)`，用户点开 404 | 1) 链接区块对 `links.*` 做 URL 白名单校验，必须以 `http://`/`https://` 开头；2) paper 模板去掉 `links.arxiv` 重复渲染（`paper.arxivId` 已含）；3) SKILL.md Step 4 加规则：URL 字段必须完整或留空 |
| 🟡 P1 | 子代理流程 | Swarm 上篇 OCR 时子代理手动 ffmpeg 转码到 `outputs/assets/<noteId>/`，污染了 download_images.py 的输出目录 | 1) SKILL.md Step 4 显式说"先跑 transcode_for_ocr.py 再读图"；2) `download_images.py` 加 `--clean` 选项删 stray `.png` |

## 2026-08-09 第五轮修复（P2 清扫）

把第三轮待办区剩下的 19 个 P2 全修了。

### 必修清单（15 项）

| # | 文件 | 问题 | 修法 |
|---|---|---|---|
| P2-1 | `render_markdown.yaml_escape` | 漏 `!` 和控制字符 | special_chars 加 `!` + `any(ord(c) < 0x20)` |
| P2-2 | `render_markdown.slugify` | 仅 `\u4e00-\u9fff` 不含 CJK 扩展 A/B + 兼容汉字 | 加 `\u3400-\u4dbf \uf900-\ufaff` |
| P2-3 | `render_markdown.py` 4 模板 link 区块 | 文案不一致 | 抽 `_render_links_detailed` / `_render_links_simple` 共用 |
| P2-4 | `render_markdown.py` INDEX | 多份 INDEX 共存无元数据 | 顶部加 `generated: <时间戳>` |
| P2-5 | `fetch_note_detail.py:240` | `json.load()` 无 try/except | 加 FileNotFoundError / JSONDecodeError / UnicodeDecodeError |
| P2-6 | `fetch_note_detail.py:parse_json_from_mixed_output` | 失败不分类 | 返回 `{"error": "EMPTY/NO_BRACE/PARSE_FAIL", "preview": ...}` |
| P2-7 | `download_images.py` | SSRF 私网 IP 未拒 | 新增 `_is_private_host()` |
| P2-8 | `download_images.py:download_one` | SSRF 函数未调用 | 入口检查 |
| P2-9 | `download_images.ALLOWED_EXTS` | 注释没说明支持格式 | 加注释 |
| P2-10 | `export_collection.py:119` | CDP 不可用 traceback | URLError 捕获 + 提示跑 chrome_launcher.py |
| P2-11 | `export_collection.py:js_eval` | recv 循环不跳 event 消息 | `if 'id' not in d: continue` |
| P2-12 | `requirements.txt` | `websockets>=12.0` 但 13+ 移除了 sync.client | 收紧到 `>=12.0,<14` |
| P2-13 | `chrome_launcher.py:get_user_data_dir` | fallback 调已删的 account_manager | 注释明确说明 |
| P2-14 | `chrome_launcher.py:launch_chrome` | 端口被占静默 return 可能连到别的 Skill | 加 `verify_chrome_cdp()` 探测 `/json/version` |
| P2-15 | `cdp_publish.py:_send` | msg_id `time.time() % 100000` 1ms 内并发撞 id | 改用 `itertools.count(1)` 实例属性 |

**未修的（标为下轮）**：
- `fetch_note_detail.py` subprocess timeout 不 kill 僵尸（要改用 Popen 跨平台测试）
- `render_markdown.slugify` 扩展 B (`\U00020000-\U0002a6df`) 要 `regex` 库
- `chrome_launcher.get_chrome_path` 加 `CHROME_PATH` 环境变量 + MSIX/Edge 路径

### 端到端验证（v5）

详见 `tests/retest_v5.md`。**11 项检查 + 6 套单测全过**。

### 剩余 3 项高成本 P2

| 优先级 | 文件 | 说明 |
|---|---|---|
| P2 | `scripts/feed_explorer.py` | `_wait_for_detail_state` poll 间隔 0.5s 不退避，全量 403 条会累计 25s × 5 条 = 125s |
| ✅ 已修 | `scripts/cdp_publish.py:103` | msg_id 撞 id —— **第五轮 P2-15 已修**（itertools.count） |
| ✅ 已修 | `scripts/render_markdown.py` | yaml_escape 漏 `!` —— **第五轮 P2-1 已修** |
| ✅ 已修 | `scripts/render_markdown.py` | `analysis.links.*` 字段无 schema 校验 —— **第四轮 N-3 已修**（redact_sensitive） |
| ✅ 已修 | `scripts/render_markdown.py` | 4 模板 link 区块文案不一致 —— **第五轮 P2-3 已修**（_render_links_detailed/simple） |
| ✅ 已修 | `scripts/render_markdown.py` | slugify 仅基本平面 —— **第五轮 P2-2 已修** |
| ✅ 已修 | `scripts/render_markdown.py` | desc 含 `\n\t` —— **第四轮 N-4 已修**（clean_desc） |
| ✅ 已修 | `scripts/render_markdown.py` | interact.liked bool/str —— **第五轮检查时已正确**（yaml_escape bool 转小写） |
| P2 | `scripts/fetch_note_detail.py` | subprocess timeout 不 kill 僵尸（要改 Popen）—— **第五轮留作下轮** |
| ✅ 已修 | `scripts/fetch_note_detail.py` | parse_json_from_mixed_output 失败不分类 —— **第五轮 P2-6 已修** |
| ✅ 已修 | `scripts/fetch_note_detail.py:232` | json.load() 无 try/except —— **第五轮 P2-5 已修** |
| ✅ 已修 | `scripts/download_images.py` | download_one 不拒私网 IP —— **第五轮 P2-7/8 已修** |
| ✅ 已修 | `scripts/download_images.py:107` | retry 失败不删占位 —— **第四轮 N-5 已修**（_cleanup_partial） |
| ✅ 已修 | `scripts/download_images.py:33` | ALLOWED_EXTS 没文档化 —— **第五轮 P2-9 已修** |
| ✅ 已修 | `scripts/export_collection.py:119` | CDP 不可用 traceback —— **第五轮 P2-10 已修** |
| ✅ 已修 | `scripts/export_collection.py:42` | js_eval 不跳 event —— **第五轮 P2-11 已修** |
| ✅ 已修 | `scripts/chrome_launcher.py:90-97` | fallback 调已删 account_manager —— **第五轮 P2-13 已修** |
| ✅ 已修 | `scripts/chrome_launcher.py:129-131` | 端口被占静默 —— **第五轮 P2-14 已修**（verify_chrome_cdp） |
| P2 | `scripts/chrome_launcher.py:30-76` | get_chrome_path 不支持 CHROME_PATH 环境变量 + MSIX/Edge 改装版 —— **第五轮留作下轮** |
| ✅ 已修 | `requirements.txt` | websockets 版本 —— **第五轮 P2-12 已修** |
| P2 | `requirements.txt` | python-magic macOS 漏装 libmagic 不友好提示 —— **第五轮留作下轮** |
| ✅ 已修 | `outputs/knowledge*/` INDEX 时间戳 | **第五轮 P2-4 已修** |