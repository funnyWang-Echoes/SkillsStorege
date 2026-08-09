# xhs-knowledge Skill

把小红书收藏转成可导入 Obsidian / Typora / VS Code 的 Markdown 文档。

## 依赖

- Python 3.10+
- Google Chrome（Windows / macOS / Linux）
- `pip install -r requirements.txt` 装 `requests` + `websockets`；Windows 还要装 `python-magic-bin`（Git Bash 自带 `file` 命令就跳过）

## 安装

1. 把 `xhs-knowledge-skill/` 整个目录放到你的 Skill 目录（例如 `~/.zcode/skills/` 或 `D:\SkillsStorege\`）
2. `pip install -r requirements.txt`
3. 在 Chrome 里手动打开收藏页并登录
4. 按 `SKILL.md` 的工作流跑

## 完整流程（CLI）

```bash
# 1. 启动 Chrome（带 CDP 9222）
python scripts/chrome_launcher.py

# 2. 采集收藏列表（用户在 Chrome 已打开收藏页）
python scripts/export_collection.py --max 40 --output outputs/list-feeds/

# 3. 抓详情
python scripts/fetch_note_detail.py \
  --input outputs/list-feeds/collection_*.json \
  --output outputs/feed-detail/

# 4. 下载图片
python scripts/download_images.py \
  --input outputs/feed-detail/details_*.json

# 5. 分析（派子代理读图片 OCR 链接 — 这一步在主代理层做）

# 6. 渲染 MD
python scripts/render_markdown.py \
  --details outputs/feed-detail/details_*.json \
  --intermediate outputs/intermediate/ \
  --output outputs/knowledge/

# 7. 复制到 Obsidian vault
cp -r outputs/knowledge/ <你的 vault>/knowledge/
cp -r outputs/assets/ <你的 vault>/assets/
```

## 脚本说明

### Chrome 启动和 CDP（精简自 xhs skill）

| 脚本 | 行数 | 作用 |
|---|---|---|
| `chrome_launcher.py` | 337 | 启动 / 停止 / 重启 Chrome CDP |
| `cdp_publish.py` | 374 | CDP 客户端，只留 `get-feed-detail` |
| `feed_explorer.py` | 117 | 只留 `noteDetailMap` 提取（带严格 key 校验防 SPA 误抓） |

### 业务脚本（本仓库自研）

| 脚本 | 行数 | 作用 |
|---|---|---|
| `export_collection.py` | 183 | fav tab 纯 JS 探查，零导航 |
| `fetch_note_detail.py` | 295 | subprocess 调 get-feed-detail + 规范化三类笔记 |
| `download_images.py` | 230 | 下载图片 + 自动检测 WebP/JPG/PNG 真实类型 |
| `render_markdown.py` | 489 | 4 类模板渲染 MD + INDEX 索引 |
| `fix_image_extensions.py` | 104 | 一次性修复扩展名错配（保留供调试） |
| `fix_md_image_syntax.py` | 47 | 一次性修复 Obsidian 双链语法（保留供调试） |

## 与原 xhs Skill 的对比

| 维度 | 原 Angin/Post-to-xhs | 本 Skill |
|---|---|---|
| 总行数 | ~5900 | ~2200（9 个脚本） |
| 功能范围 | 发布 + 评论 + 搜索 + 多账号 | 只读采集 |
| 外部依赖 | account_manager / image_downloader / publish_pipeline | 零 |
| 视频下载 | 支持 | 不支持 |
| Skill 自包含 | 否（依赖 SkillStorege 安装） | 是 |
| 兼容 MD 软件 | Obsidian 双链 | 标准 Markdown，多软件兼容 |

## 架构图

```
Chrome (CDP :9222)
        ↓
chrome_launcher (启动)
        ↓
export_collection ─→ collection.json ─→ fetch_note_detail
                                              ↓
                                       (subprocess cdp_publish)
                                              ↓
                                       details.json
                                              ↓
                              download_images → assets/*.webp
                                              ↓
                          [主代理派子代理] analysis/*.json
                              子代理可读图 OCR 链接
                                              ↓
                                       render_markdown
                                              ↓
                                       knowledge/*.md
                                              ↓
                                       Obsidian vault
```

## 风险与边界

- 风控：见 SKILL.md 风险提示
- 法律：仅个人收藏备份，不要传播
- 视频：sign 时效，不在范围
- 评论：量大优先级低

## 进阶用法

### 全量 403 篇批量

```bash
# 1. 滚动加载全部
python scripts/export_collection.py --max 500 --scroll-rounds 13

# 2. 分批抓详情（每批 20 条）
python scripts/fetch_note_detail.py --limit 20 --offset 0
python scripts/fetch_note_detail.py --limit 20 --offset 20
...

# 3. 子代理每 4 条 1 个（100 条 → 25 个子代理）
# 主代理分批派：每批 5 个子代理 × 20 条 = 100 条

# 4. 一次性渲染
python scripts/render_markdown.py --input outputs/feed-detail/details_full.json
```

### 多账号（如果你需要）

本 Skill 单账号已够用。如需多账号隔离：
- 用 `chrome_launcher.launch_chrome(port=9223, account="work")` 启动第二个实例
- 不同端口 → 不同 Chrome user-data-dir → 不同账号 cookie

### 调试

```bash
# 看 raw noteData
python scripts/cdp_publish.py --reuse-existing-tab \
  get-feed-detail --feed-id NOTE_ID --xsec-token TOKEN | jq .

# 看 Chrome 状态
python scripts/chrome_launcher.py
```

## 已知问题

- `cdp_publish.py` 的 `_send` 用 `recv(timeout=...)`，高并发下可能假超时
- `export_collection.py` 假定 fav tab 在 Chrome 里已渲染完成
- `download_images.py` 用 `file --mime-type` 检测图片类型，依赖 Git Bash / WSL（Windows fallback 是 `python-magic-bin`）
- 子代理 OCR 准确率取决于图片清晰度

## License

本仓库自研代码 MIT。`chrome_launcher.py` 衍生自 Angin/Post-to-xhs（按上游协议）。