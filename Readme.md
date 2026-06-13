# SkillsStorege

这个仓库用来管理可复用的 Agent Skill。目录分成两类：

- `my-Skills/`：我自己维护或深度改造的 Skill。
- `other-Skills/`：从他人 GitHub 或外部来源整理来的 Skill，只保留可直接使用的 Skill 本体。
- `doing/`：正在优化中的 Skill 工作副本，优化完成后再替换回 `my-Skills/` 或 `other-Skills/`。

整理原则见 [AGENTS.md](AGENTS.md)。核心规则是：外部仓库下载后先分析来源，再剥离外层，只保留包含 `SKILL.md` 的真实 Skill 目录；来源、作用、可用程度统一记录在本文件。

## 当前结构

```text
my-Skills/
  agent-trajectory-analysis/
  paper-deep-analyse/
  sim-agent-research/
doing/
  paper-deep-analyse/
other-Skills/
  aihot/
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

## 我自己的 Skills

| Skill | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `paper-deep-analyse` | 对论文做逐段精读、论证链重建、实验/代码审计、相关工作发散，并生成 HTML 深度报告。 | 自有维护版本 | 可用但仍不够满意；当前规则很重，后续需要继续打磨报告质量、流程负担和自检体验。当前优化副本在 `doing/paper-deep-analyse/`。 |
| `sim-agent-research` | 调研仿真软件的 Agent 化生态，包括接口、MCP、Skill、论文、接入难度和可用性复核。 | 自有维护版本 | 较可用；适合系统性调研，但执行成本较高，依赖联网检索质量。 |
| `agent-trajectory-analysis` | 分析 Agent 实验轨迹日志，按阶段复盘工具调用、关键结果、失败点和改进方向。 | 自有维护版本 | 可用；偏分析模板型，适合 JSON/JSONL 轨迹复盘。 |

## 他人 / 外部 Skills

| Skill | 作用 | 来源 | 可用程度 |
|---|---|---|---|
| `aihot` | 查询 AI HOT 中文 AI 资讯、日报、精选条目和关键词动态。 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | 外部可用，依赖 `aihot.virxact.com` 公共接口。 |
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

## 后续待办

- 后续每新增一个外部 Skill，都先记录来源再删除外层仓库壳。
- 在 `doing/paper-deep-analyse/` 中继续优化 `paper-deep-analyse`，满意后再替换正式目录。
- 持续评估 `paper-deep-analyse` 的满意度，尤其是报告质量、执行成本和自检流程。
