# SkillsStorege

这个仓库用来管理可复用的 Agent Skill。目录分成两类：

- `my-Skills/`：我自己维护或深度改造的 Skill。
- `other-Skills/`：从他人 GitHub 或外部来源整理来的 Skill，只保留可直接使用的 Skill 本体。
- `doing/`：正在优化中的 Skill 工作副本，优化完成后再替换回 `my-Skills/` 或 `other-Skills/`。
- `myAgentsMD/`：我自己的跨设备 Agent 指令文件，用于迁移和同步个人协作偏好；它不是 Skill 目录，不要求包含 `SKILL.md`。

整理原则见 [AGENTS.md](AGENTS.md)。核心规则是：外部仓库下载后先分析来源，再剥离外层，只保留包含 `SKILL.md` 的真实 Skill 目录；来源、作用、可用程度统一记录在本文件。

## 当前结构

```text
my-Skills/
  agent-trajectory-analysis/
  paper-close-reading/
  paper-deep-analyse/
  research-progress/
  sim-agent-research/
  workspace-bootstrap/
doing/
  paper-deep-analyse/          # paper-deep-analyse 优化工作副本
myAgentsMD/
  AGENTS.md
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

## 他人 / 外部 Skills

| Skill | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `aihot` | 查询 AI HOT 中文 AI 资讯、日报、精选条目和关键词动态。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，依赖 `aihot.virxact.com` 公共接口。 |
| `autoresearch` | 自主实验研究循环：agent 反复「改一个变量 → commit → 跑 → 读指标 → keep/discard → advance/reset」，直到预算耗尽或达标。适用于有单一自动指标、可自动运行、可 git 版本化的多轮优化任务（模型评测、仿真调参、超参/架构搜索）。 | **来源待确认**：用户提供 [letsgetai/agent-skills](https://github.com/letsgetai/agent-skills)（`skills/autoresearch/`，2026-07-24 入库），但该仓库 GitHub 当前返回 404，作者与 License 无法核验；SKILL.md 声明泛化自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)。 | 外部可用（未实测）；要求项目内有可自动测量的单一指标和可 git 化的代码。**已本地化**：删除原 SKILL.md 对 `experiment-hygiene`、`eval-harness` 配套 skill 的引用（本库暂无，检查项已由 Setup 节覆盖），修改记录见 `other-Skills/autoresearch/LOCAL-EDIT.md`。 |
| `hv-analysis` | 横纵分析法深度研究，用纵向历史和横向竞品/同类对比生成系统性研究报告。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，偏长报告工作流。 |
| `khazix-writer` | 按“数字生命卡兹克”公众号风格写长文。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，风格强，不适合通用写作。 |
| `neat-freak` | 会话结束后对项目文档、AGENTS/CLAUDE 规则和记忆做同步清理。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，适合阶段收尾。 |
| `storage-analyzer` | macOS/Windows 只读存储扫描，生成可操作的 HTML 清理报告。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用；涉及删除建议时需要人工确认。 |
| `beautiful-article` | 把 URL/PDF/DOCX/Markdown/纯文本等素材编辑设计成可离线分享的单文件 HTML 网页文章。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；流程含多次确认和审阅，适合长文网页化。 |
| `gpt-image-2` | GPT Image 2 图像生成/编辑提示与本地调用工作流。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；依赖图像模型/API 或宿主生图能力。 |
| `kb-retriever` | 本地知识库渐进式检索与问答，支持 PDF/Excel 等文件处理规则。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；效果依赖知识库索引质量。 |
| `web-design-engineer` | 生成高质量网页、仪表盘、原型、交互演示和数据可视化。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；适合视觉前端产物。 |
| `web-video-presentation` | 把文章/口播稿做成点击驱动的 16:9 网页演示，可用于录屏视频。 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 外部可用；适合视频化演示，流程较重。 |
| `ppt-master` | 多角色协作式 PPT 生成系统，把 PDF/DOCX/URL/Markdown 转为 SVG 页面并导出 PPTX。 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，实际 Skill 位于 `skills/ppt-master/`。 | 外部可用；能力完整但体量较大，使用前应按其依赖和流程做实测。 |

## 已剥离的外层来源

- `hugohe3/ppt-master`：来源为 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，只保留 `skills/ppt-master/` 到 `other-Skills/ppt-master/`。
- `khazix-skills/`：来源为 [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)，只保留其中 `aihot`、`hv-analysis`、`khazix-writer`、`neat-freak`、`storage-analyzer` 到 `other-Skills/`。
- `garden-skills/`：来源为 [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills)，只保留其中 `beautiful-article`、`gpt-image-2`、`kb-retriever`、`web-design-engineer`、`web-video-presentation` 到 `other-Skills/`。

## 外部来源刷新记录

| 日期 | 来源 | 拉取 commit | 入库内容 |
|---|---|---|---|
| 2026-06-14 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | `a0d6243` | `ppt-master` |
| 2026-06-14 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | `9c315d7` | `aihot`、`hv-analysis`、`khazix-writer`、`neat-freak`、`storage-analyzer` |
| 2026-06-14 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | `fbd6453` | `beautiful-article`、`gpt-image-2`、`kb-retriever`、`web-design-engineer`、`web-video-presentation` |
| 2026-07-24 | 来源待确认（[letsgetai/agent-skills](https://github.com/letsgetai/agent-skills)，入库时 GitHub 返回 404） | 无法核验 | `autoresearch` |

## 后续待办

- 后续每新增一个外部 Skill，都先记录来源再删除外层仓库壳。
- 在 `doing/paper-deep-analyse/` 中继续优化 `paper-deep-analyse`，满意后再替换正式目录。
- 持续评估 `paper-deep-analyse` 的满意度，尤其是报告质量、执行成本和自检流程。
