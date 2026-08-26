# SkillsStorege

这个仓库用来管理可复用的 Agent Skill 与 MCP server。目录分成几类：

- `my-Skills/`：我自己维护或深度改造的 Skill。
- `other-Skills/`：从他人 GitHub 或外部来源整理来的 Skill，只保留可直接使用的 Skill 本体。
- `other-MCPs/`：从他人 GitHub 或外部来源整理来的 MCP server，只保留可直接运行/安装的 MCP 本体（源码、包清单、测试、README、License）。
- `doing/`：正在优化中的 Skill 工作副本，优化完成后再替换回 `my-Skills/` 或 `other-Skills/`。
- `myAgentsMD/`：我自己的跨设备 Agent 指令文件，用于迁移和同步个人协作偏好；它不是 Skill 目录，不要求包含 `SKILL.md`。

整理原则见 [AGENTS.md](AGENTS.md)。核心规则是：外部仓库下载后先分析来源，再剥离外层，只保留包含 `SKILL.md` 的真实 Skill 目录（或等价的 MCP 本体）；来源、作用、可用程度统一记录在本文件。

## 当前结构

```text
my-Skills/
  agent-trajectory-analysis/
  paper-close-reading/
  paper-deep-analyse/
  research-progress/
  sim-agent-research/
  workspace-bootstrap/
  xhs-knowledge-skill/
doing/
  paper-deep-analyse/          # paper-deep-analyse 优化工作副本
myAgentsMD/
  AGENTS.md
other-MCPs/
  slepp-ssh-mcp/
other-Skills/
  aihot/
  autoresearch/
  beautiful-article/
  gpt-image-2/
  hv-analysis/
  kb-retriever/
  khazix-writer/
  neat-freak/
  ppt-master/
  storage-analyzer/
  web-design-engineer/
  web-video-presentation/
  video-shotcraft/
  xiaohongshu-skills/
```

## 个人 Agent 指令

`myAgentsMD/` 用来保存我自己的 Agent 协作规则，当前包含 `AGENTS.md`。这个目录的目标是方便换设备时迁移和持续更新个人默认指令，不作为可安装 Skill 管理，因此不适用“每个 Skill 目录必须直接包含 `SKILL.md`”的检查规则。

## 我自己的 Skills

| Skill | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `paper-deep-analyse` | 对论文做逐段精读、论证链重建、实验/代码审计、相关工作发散，并生成 HTML 深度报告。 | 自有维护版本 | 可用；已完成 A-F 优化（单一阈值源、合并 references、修脚本 bug、阶段化工作流、解耦 subagent、SKILL.md 减负）。当前优化副本在 `doing/paper-deep-analyse/`。 |
| `paper-close-reading` | 带注释的论文逐段双语精读。一边读一边分析——每段先给中文翻译，再给即时分析（这段在论证什么、怎么连接前段、有没有问题），疑问有 ID 追踪并在被回答时显式标记呼应。代码对照放文末附录，图表从 MinerU 解析结果嵌入。 | 自有维护版本 | 可用；已通过 3 篇论文测试（Aurora CVPR2025 有代码 / MacTok CVPR2026 无代码 / DeCo CVPR2026 有代码+Table 全重建）。3 个 reference case 在 `references/example-cases/`。 |
| `sim-agent-research` | 调研仿真软件的 Agent 化生态，包括接口、MCP、Skill、论文、接入难度和可用性复核。 | 自有维护版本 | 较可用；适合系统性调研，但执行成本较高，依赖联网检索质量。 |
| `agent-trajectory-analysis` | 分析 Agent 实验轨迹日志，按阶段复盘工具调用、关键结果、失败点和改进方向。 | 自有维护版本 | 可用；偏分析模板型，适合 JSON/JSONL 轨迹复盘。 |
| `workspace-bootstrap` | 快速创建或整理开发、科研、混合型工作空间，生成项目级 `AGENTS.md`、标准目录和可持久化任务状态系统。 | 自有维护版本 | 草稿可用；当前为 0.4.1 测试版，已完成 `testing/PaperReadingProject` 现有项目、空科研 workspace 和空开发 workspace 生成测试；默认生成中文 `AGENTS.md`/README/任务文档，重点强化 `.gitignore`、Do Not Touch 边界、任务真源复用、嵌套 AGENTS 和空项目命令诚实性。 |
| `research-progress` | 中文版「科研进展 / 工作进展」写作助手：把碎片化实验记录 / 周工作流水整理成结构完整、数据驱动、低 AI 味的进展文档。覆盖探索性实验小结、科研月报（导师/委员会）、文献分析、综合 Benchmark 报告、工作周报、项目进展汇报六类。 | 自有维护版本（科研写法借鉴 `E:\WSL and SSH remote download\geo_project` 高质量范文 + LobeHub `progress-report` 结构；周报写法借鉴现有进展类 Skill 与成熟周报 Prompt） | 可用（v0.2.0）；零外部依赖，纯提示词 + 模板驱动。已实测：周报删除「能力成长」节、下周计划为纯任务条目（无周次/可交付物/数字）、本周进展支持数据统计密集型子节、价值按科研/产业场景分类。待补：HTML/Word 导出。 |
| `xhs-knowledge-skill` | xhs-knowledge：把小红书收藏页笔记批量采集并整理成可直接拖入 Obsidian / Typora / VS Code / Logseq / Joplin 的结构化 MD 文档。支持图文 + 视频笔记（视频不下载，但 MD 保留源链接）；图片下载到本地并以标准 Markdown 语法引用；4 类模板（paper / skill / project / blog）由子代理读图 OCR 后分类渲染。 | 自有维护版本（`chrome_launcher.py` / `cdp_publish.py` / `feed_explorer.py` 衍生自 `Angin/Post-to-xhs`；业务脚本 export_collection / fetch_note_detail / download_images / render_markdown / transcode_for_ocr 为本仓库自研）。SKILL.md frontmatter `metadata.source` 自述为「本仓库自研（基于 Angin/Post-to-xhs CDP 流程裁剪）」。 | 较可用；已在多轮 retest（v3/v4/v5 + `retest_2026-08-09`）中验证导出、详情抓取、图片下载、OCR 转码、4 类渲染均工作。**风控风险**：自动化抓取可能被限流/封号，建议只用测试号、慢节奏（≥1.5s/条）；视频不下载（sign 时效），评论不抓。需 Python 3.10+、Chrome、CDP 9222；可选 `python-magic-bin`（Windows fallback）。 |

## 他人 / 外部 Skills

| Skill | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `aihot` | 查询 AI HOT 中文 AI 资讯、日报、精选条目和关键词动态。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，依赖 `aihot.virxact.com` 公共接口。 |
| `autoresearch` | 自主实验研究循环：agent 反复「改一个变量 → commit → 跑 → 读指标 → keep/discard → advance/reset」，直到预算耗尽或达标。适用于有单一自动指标、可自动运行、可 git 版本化的多轮优化任务（模型评测、仿真调参、超参/架构搜索）。 | 本地 SKILL.md 泛化自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)（上游 HEAD `228791f`）。2026-07-24 入库时引用源为 [letsgetai/agent-skills](https://github.com/letsgetai/agent-skills)，但该仓库 GitHub 当前仍返回 404，作者与 License 无法核验；上游血缘以 `karpathy/autoresearch` 为准。 | 外部可用（未实测）；要求项目内有可自动测量的单一指标和可 git 化的代码。**已本地化（local-0.2.0）**：删除 `experiment-hygiene`、`eval-harness` 等缺失配套 skill 引用，并补 `results/` git 口径、中断恢复协议、baseline 抓取验证、平台执行说明；修改记录见 `other-Skills/autoresearch/LOCAL-EDIT.md`。 |
| `hv-analysis` | 横纵分析法深度研究，用纵向历史和横向竞品/同类对比生成系统性研究报告。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，偏长报告工作流。 |
| `khazix-writer` | 按“数字生命卡兹克”公众号风格写长文。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，风格强，不适合通用写作。 |
| `neat-freak` | 会话结束后对项目文档、AGENTS/CLAUDE 规则和记忆做同步清理。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，适合阶段收尾。 |
| `storage-analyzer` | macOS/Windows 只读存储扫描，生成可操作的 HTML 清理报告。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用；涉及删除建议时需要人工确认。 |
| `beautiful-article` | 把 URL/PDF/DOCX/Markdown/纯文本等素材编辑设计成可离线分享的单文件 HTML 网页文章。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；流程含多次确认和审阅，适合长文网页化。 |
| `gpt-image-2` | GPT Image 2 图像生成/编辑提示与本地调用工作流。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；依赖图像模型/API 或宿主生图能力。 |
| `kb-retriever` | 本地知识库渐进式检索与问答，支持 PDF/Excel 等文件处理规则。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；效果依赖知识库索引质量。 |
| `web-design-engineer` | 生成高质量网页、仪表盘、原型、交互演示和数据可视化。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；适合视觉前端产物。 |
| `web-video-presentation` | 把文章/口播稿做成点击驱动的 16:9 网页演示，可用于录屏视频。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；适合视频化演示，流程较重。 |
| `ppt-master` | 多角色协作式 PPT 生成系统，把 PDF/DOCX/URL/Markdown 转为 SVG 页面并导出 PPTX。 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，实际 Skill 位于 `skills/ppt-master/`；上游 HEAD `ebd74d1`。**入库 commit 待核验**：Readme 历史记录的 `a0d6243` 在上游仓库不存在（`git cat-file -t a0d6243` → Not a valid object），仓库最早 commit 为 `fa291f44 梳理之后第一次提交`，现存 1732 个 commit；建议下次刷新前先 `git log --reverse -- skills/ppt-master/SKILL.md` 找到 `skills/ppt-master/` 路径首次出现的 commit。 | 外部可用；能力完整但体量较大，使用前应按其依赖和流程做实测。 |
| `video-shotcraft` | 用 104 张镜头配方卡、Remotion demo/模板、真实页面截图、2.5D 运镜、节奏卡点和音频素材制作电影感产品/宣传视频。 | 作者 Yihao；[Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)；Apache-2.0。 | 外部可用；入库副本约 49.1 MB/660 个文件，依赖 Node/Remotion/浏览器等运行环境。音频授权和仍需核验的素材见 `assets/audio/ATTRIBUTION.md`。 |
| `xiaohongshu-skills` | RedBookSkills：小红书图文/视频自动发布 + 内容检索与互动（搜索、详情、评论/回复、点赞收藏、主页快照、内容数据看板）。基于 Chrome DevTools Protocol 驱动浏览器。 | [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills)；MIT（Copyright 2026 angiin）；仓库根即 Skill 本体，`SKILL.md` 中 `metadata.name=RedBookSkills` / `metadata.source=Angiin/Post-to-xhs` 与 GitHub 仓库名/作者不一致，实际以 GitHub 仓库为准。 | 外部可用（未实测）；**平台风控风险高**，建议只在测试号、小流量、人工复核标题/正文/素材后再发布；仅在 Windows + Python 3.10+ + Chrome 上验证过。剥离了 `README.md`/`LICENSE`/`AGENTS.md`/`.github`/`docs`/`images`/`public`/`assets`/`todo.md` 等外层仓库壳，只保留 `SKILL.md`、`requirements.txt`、`config/accounts.json.example`、`scripts/`。 |

## 他人 / 外部 MCPs

| MCP | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `slepp-ssh-mcp` | stdio MCP server，包装本机 OpenSSH（ssh/scp/rsync），给 Agent 17 个工具：一次性远程执行（`ssh_exec`）、持久交互会话（PTY + transcript + 可选 tmux 实时旁观，支持 `session_name` 跨调用/跨会话复用）、端口转发（独立工具便于权限门控）、远程文件读/建/改/搜（`ssh_view`/`ssh_create`/`ssh_edit`/`ssh_grep`/`ssh_glob`，对齐本地文件工具语义）。零第三方运行时依赖（纯 Python 标准库实现 JSON-RPC/MCP），直接复用本机 `~/.ssh/config`、密钥、ProxyJump。 | [slepp/ssh-mcp](https://github.com/slepp/ssh-mcp)（作者 Stephen Olesen，加拿大，GitHub 2008 年注册）；MIT；PyPI 包名 `slepp-ssh-mcp`，v0.2.0，拉取 commit `28834a8`。 | 外部可用（已实测）：**仅 POSIX**——在 WSL Ubuntu（Python 3.14）114/114 测试全过 + stdio 握手/`tools/list` 冒烟通过；Windows 原生不可用（会话依赖 `os.openpty`/进程组信号，本机直跑 83 errors + 5 failures），Windows 上须经 WSL 运行。要求 Python 3.10+、本机 `ssh`/`scp`，`rsync` 仅 `ssh_sync` 需要，`tmux` 可选。**已确认安全缺陷**：`extra_ssh_args` 黑名单与 README 声明不符——`ssh -F <恶意config>`（config 内 `ProxyCommand` 可致本机命令执行）与 `scp -S <恶意程序>` 均未被拦截，已在本地复现；利用前提是 Agent 已能控制本机文件/二进制，若 MCP client 只暴露 SSH 工具做权限隔离则该缺口有意义，拟向上游提 issue。其他注意：serve 循环单线程串行（无 timeout 的长 `ssh_exec` 会阻塞其他工具调用，会话本体在后台线程不受影响）；transcript 可能含密码/密钥（0600 权限但不自动清理）；`ssh_edit` 为非原子两次往返读写。完整审查记录（来源核验、实测数据、绕过复现）见 `other-MCPs/slepp-ssh-mcp/LOCAL-REVIEW.md`。入库保留 `README.md`/`LICENSE`/`pyproject.toml`/`src/`/`tests/`，剥离 `.github/` CI 与发布脚本。 |

## 已剥离的外层来源

- `slepp/ssh-mcp`：来源为 [slepp/ssh-mcp](https://github.com/slepp/ssh-mcp)，仓库根即 MCP 本体，只保留 `README.md`/`LICENSE`/`pyproject.toml`/`src/ssh_mcp/`/`tests/` 到 `other-MCPs/slepp-ssh-mcp/`；外层 `.github/`（CI/发布 workflow）与 `.gitignore` 已剥离。

- `hugohe3/ppt-master`：来源为 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，只保留 `skills/ppt-master/` 到 `other-Skills/ppt-master/`。
- `white0dew/XiaohongshuSkills`：来源为 [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills)，仓库根即真实 Skill，只保留 `SKILL.md`/`requirements.txt`/`config/accounts.json.example`/`scripts/` 到 `other-Skills/xiaohongshu-skills/`；外层 `README.md`/`LICENSE`/`AGENTS.md`/`.github`/`docs`/`images`/`public`/`assets`/`todo.md` 已剥离。
- `khazix-skills/`：来源为 [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)，只保留其中 `aihot`、`hv-analysis`、`khazix-writer`、`neat-freak`、`storage-analyzer` 到 `other-Skills/`。
- `garden-skills/`：来源为 [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills)，只保留其中 `beautiful-article`、`gpt-image-2`、`kb-retriever`、`web-design-engineer`、`web-video-presentation` 到 `other-Skills/`。

## 外部来源刷新记录

| 日期 | 来源 | 拉取 commit | 入库内容 |
|---|---|---|---|
| 2026-06-14 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | `a0d6243`（**已核验：上游不存在**，需在下一次刷新前用 `git log --reverse -- skills/ppt-master/SKILL.md` 重核） | `ppt-master` |
| 2026-06-14 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | `9c315d7` | `aihot`、`hv-analysis`、`khazix-writer`、`neat-freak`、`storage-analyzer` |
| 2026-06-14 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | `fbd6453` | `beautiful-article`、`gpt-image-2`、`kb-retriever`、`web-design-engineer`、`web-video-presentation` |
| 2026-07-24 | 来源待确认（[letsgetai/agent-skills](https://github.com/letsgetai/agent-skills)，入库时 GitHub 返回 404） | 无法核验 | `autoresearch` |
| 2026-08-02 | 作者 Yihao；[Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)；Apache-2.0 | `d491544`（2026-07-28） | `video-shotcraft`；仓库根目录即真实 Skill，未保留外层仓库壳 |
| 2026-08-08 | [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills)；MIT（Copyright 2026 angiin） | `8536136`（2026-08-08） | `xiaohongshu-skills`；仓库根即真实 Skill，仅保留 `SKILL.md`/`requirements.txt`/`config/accounts.json.example`/`scripts/` |
| 2026-08-24 | [slepp/ssh-mcp](https://github.com/slepp/ssh-mcp)；MIT；PyPI 名 `slepp-ssh-mcp`（本仓库首个 MCP 入库） | `28834a8`（v0.2.0，2026-07-09） | `slepp-ssh-mcp` 入 `other-MCPs/`；保留 `README.md`/`LICENSE`/`pyproject.toml`/`src/`/`tests/`，剥离 `.github/` |

## 后续待办

- 后续每新增一个外部 Skill/MCP，都先记录来源再删除外层仓库壳。
- `slepp-ssh-mcp` 的 `extra_ssh_args` 黑名单绕过（`ssh -F` / `scp -S`）拟向上游提 issue，提交后在此登记链接。
- 在 `doing/paper-deep-analyse/` 中继续优化 `paper-deep-analyse`，满意后再替换正式目录。
- 持续评估 `paper-deep-analyse` 的满意度，尤其是报告质量、执行成本和自检流程。
- 2026-08-26 上游版本检查（`docs/others-skills-version-check-2026-08-26.md`）：建议按优先级刷新 `neat-freak` (v3.0) → `web-design-engineer` (v1.3.0) → `aihot` (v1.5.4) → `video-shotcraft`（新增 demos/gallery/jianying-export）；7 个 Skill SKILL.md 与上游 HEAD 字节相同，无需同步；`xiaohongshu-skills` 自入库以来无功能变更。
