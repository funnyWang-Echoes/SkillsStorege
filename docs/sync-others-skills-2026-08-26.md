# 2026-08-26 other-Skills 上游同步记录

- **日期**：2026-08-26
- **触发原因**：[docs/others-skills-version-check-2026-08-26.md](others-skills-version-check-2026-08-26.md) 建议按优先级刷新 4 个 Skill
- **会话**：`sess_8b59d054-14ac-4ea7-a2b4-b067880d640f`（main session）
- **代理用户授权**：用户已选 doing/ 工作副本模式 + 每 Skill 一个 commit
- **结果**：4 个 Skill 已同步到上游 HEAD，4 个独立 commit + 1 个 Readme/docs 收尾 commit

## 总览

| Skill | 上游 commit | 版本 | 本地 → 新（文件数 / 体积） | 同步类型 | commit SHA |
|---|---|---|---|---|---|
| `neat-freak` | khazix-skills `7a5c493` | v3.0.0 | 3 文件 / 28K → 94 文件 / 192K | 全目录覆盖 | `047de35` |
| `web-design-engineer` | garden-skills `aaf9a82` | v1.3.0 | 33 文件 / 257K → 39 文件 / 313K | 全目录覆盖（新增 6 个） | `78b2d6c` |
| `aihot` | khazix-skills `7a5c493` | v1.5.4 | 1 文件 / 24K → 10 文件 / 71K | 全目录覆盖（新增 9 个） | `b671c7b` |
| `video-shotcraft` | video-shotcraft `d9ffa6d3` | upstream HEAD | 660 文件 / 49M → 889 文件 / 53M | 全目录覆盖（新增 258 个，**排除上游 `.git/` 184M**） | `e898ed8` |
| `ppt-master` | hugohe3/ppt-master `ebd74d1f` | v5.0.0 | 12,131 文件 / 76M → 12,925 文件 / 95M | 全目录覆盖（**架构级重写**） | `7d5eeda` |

## 工作流

每个 Skill 都遵循仓库 `AGENTS.md` L53-58 doing 规则：

1. `mkdir -p doing/<name>` + `cp -a other-Skills/<name>/. doing/<name>/` 建工作副本
2. `diff -rq doing/<name>/ /tmp/upstream-check/.../<name>/` 完整目录比对
3. 记录三类差异：本地独有、上游独有、内容差异
4. `rm -rf doing/<name>/` + `cp -a /tmp/upstream-check/.../<name>/. doing/<name>/` 应用同步
5. doing 内体检：`test -f doing/<name>/SKILL.md`、无 `__pycache__`、无 `.pyc`、无运行时 `.env`
6. `rm -rf other-Skills/<name>` + `mv doing/<name> other-Skills/<name>` 替换正式目录
7. `git commit` 单 Skill 提交

无任何 Skill 在入库时有 `LOCAL-EDIT.md`/`LOCAL-REVIEW.md`（autoresearch 唯一有 LOCAL-EDIT 但不在本次范围），所以未保留 legacy。

## neat-freak

- **上游 commit**：`7a5c4934be4106ac740ffdb95280bb81b3f4b83c`（khazix-skills HEAD）
- **关键 commit message**：`2b4a645 neat-freak v3.0: middle-tier triggers, light path for small projects, generic platform fallback`
- **变化**：SKILL.md 描述改为 "Knowledge and governance closeout"；新增 `evals/` 完整评测套件（11 fixture projects：routine-dev-sync、memory-conflict、cold-start、cross-project、governance、scope-boundary、release-terminal、generated-memory、vibe-project、unknown-platform 等）；新增 `references/governance.md` 与 `references/verification.md`；新增 `scripts/audit-inventory.sh`。
- **注意**：`evals/fixtures/eval-3-cold-start/workspace/analytics_dashboard/.env` 与 `evals/fixtures/eval-5-governance/workspace/pdf-tools/.env` 是**上游评测套件中的 fixture 文件**（模拟需要清理的项目），不是 Skill 自身的运行时配置。这是上游设计的一部分，入库时保留。

## web-design-engineer

- **上游 commit**：`aaf9a82f5efd73e87cc0998edc398e75bfc35901`（garden-skills HEAD）
- **关键 commit message**：`0886299 docs(readme): sync download links for web-design-engineer v1.3.0` / `ea45dc5 docs(readme): update web-design-engineer skill documentation with new features, including five-dial Design Read, preservation-aware redesigns, and contextual failure patterns`
- **变化**：manifest.json `1.2.2 → 1.3.0`；新增 5 个 references（block-library、browser-acceptance、design-calibration、failure-patterns、redesign-protocol）；新增 `agents/openai.yaml`；SKILL.md/README.md/README.zh-CN.md 全部刷新。
- **aaf9a82 本身**：`fix(marketplace): update skill source paths for ...`，` 是 marketplace 路径修复（`web-design-engineer/` → `skills/web-design-engineer/`），不涉及 Skill 内容的实质变化。Skill 内容主要由前两次 commit 提供。

## aihot

- **上游 commit**：`7a5c4934be4106ac740ffdb95280bb81b3f4b83c`（khazix-skills HEAD）
- **关键 commit messages**（自 `9c315d7` 以来）：10 次 `chore(aihot): sync skill to vX.Y.Z`（从 v0.3.6 一路升至 v1.5.4）+ `d0534c3 fix(aihot): repair the install command`
- **变化**：SKILL.md frontmatter 现在声明 `metadata.version: "1.5.4"`、`license: MIT`、`author: Virxact`；新增「安全边界」「用途许可边界」两节；新增 `README.md`、`LICENSE`、`agents/openai.yaml`、`install.sh`、`manifest.sha256`、`references/{api,errors,sync}.md`。

## video-shotcraft

- **上游 commit**：`d9ffa6d30c227b76f24fa5728fbc55f34b741d82`（video-shotcraft HEAD）
- **关键 commit messages**（自 `d491544` 以来，18 commits）：
  - `0d6f0b5 feat: 剪映工程导出成为 skill 正式能力（Mac 11.2 实测验收）` —— 新增 `jianying-export/`
  - `ec3cbd1 feat(assets/lib): ClipCard — wrap external video clips as card heroes`
  - `8b56005 demos: 补 shot-transitions 卡 B/C/D 三式转场参考实现`
  - `80b3f5d demos: 为 9 张依赖 template 场景的镜头卡补独立参考实现`
  - `c05d484 feat: motion-lab 48 个定稿动效模板`
  - 其他 docs/test/CI commit
- **变化**：新增 `jianying-export/`（剪映工程导出：aifl_promo.py、mac_draft.py、windows_draft.py、smoke_test.py）；新增 `package.json`/`package-lock.json`（Node/Remotion 依赖）；新增 `assets/lib/ClipCard.tsx`、`assets/scripts/smoke-render-demos.py`、`assets/lib/helpers/__tests__/helpers.test.ts`；`demos/` 大量新镜头参考实现（72 文件）；`gallery/` 大量海报与源码（96 文件）；`references/shots/` 镜头配方文档（50 文件）。
- **重要排除**：上游仓库根 `.git/`（184MB）必须排除 —— 本仓库 AGENTS.md L58 禁止 git 历史入库，`.git/` 是上游 git 元数据，不应 vendoring。Plan 阶段预估仓库体积 +187M 全部来自这一项，实际内容增量很小。

## 残留风险与下一步

- **未触发 skill 实际运行测试**：4 个 Skill 都没有本地实测先例（Readme 标注"外部可用（未实测）"），同步后未运行 eval/手动验证。
- **`ppt-master` 入库 commit 待重核**：仓库 Readme 历史记录的 `a0d6243` 在上游不存在，下次刷新 `ppt-master` 前需用 `git log --reverse -- skills/ppt-master/SKILL.md` 找到 `skills/ppt-master/` 路径首次出现的真实 commit。
- **`doing/.env` 违规**：用户已选择本轮不处理，AGENTS.md L58 仍规定 doing/ 中不得提交 `.env`。
- **`neat-freak` evals fixture .env**：上游评测套件内的 `.env` 不是 Skill 运行时配置，但如果未来要在仓库内运行 evals，需注意这些 fixture 的 `.env` 不应被任何 agent 当成真实环境变量加载。
- **video-shotcraft 体积**：`assets/audio/AUDITION-2026-07-27.md`、`assets/brand/BRAND.md` 等媒体资产授权状态本次未做合规复审，仅做版本同步。如需商用，应单独审查音频与品牌素材授权。
- **`other-Skills/` 剩余 10 个 Skill**：hv-analysis / khazix-writer / storage-analyzer / beautiful-article / gpt-image-2 / kb-retriever / web-video-presentation / autoresearch / xiaohongshu-skills / ppt-master 在本次检查中与上游 HEAD 字节相同或来源已核验，无需同步。后续若有上游大版本发布再走本流程。

## 验证证据

- **commit log**：`git log --oneline -6` 显示 4 个 Skill commit + 2 个 docs commit 全部在同一分支 `chore/check-others-skills-versions`
- **字节一致性**：每个 Skill 替换后 `md5sum other-Skills/<name>/SKILL.md /tmp/upstream-check/.../SKILL.md` 完全一致
- **未入库 `.git/`**：`ls other-Skills/video-shotcraft/.git` 返回 No such file or directory
- **未入库 `.env`（运行时）**：`find other-Skills/<name> -type f -name .env` 仅返回 neat-freak evals fixture（说明如上）

---

## ppt-master（补遗，commit `7d5eeda` + docs commit）

### 上游身份与首次入库 commit

| 项 | 数据 |
|---|---|
| 仓库 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) |
| License | MIT |
| 作者 | Hugo He（hugohe3） |
| 真实 Skill 路径 | `skills/ppt-master/SKILL.md`（不在仓库根；本仓库是 monorepo，只取 Skill 子目录） |
| 当前 HEAD | `ebd74d1f`（2026-08-25，`fix(roundtrip): preserve PPTX fidelity through SVG conversion`） |
| 当前版本 | **v5.0.0**（frontmatter `metadata.version: "5.0.0"`，2026-08-24 bump by `e469064b chore(release): bump version fields to 5.0.0`） |
| **真实首次入库 commit** | **`4e57f2f7`**（2026-03-20，`refactor: migrate to skill-based architecture with multi-platform adapter generation`） |
| Readme 错误 commit | `a0d6243` —— 不存在上游（`git cat-file -t a0d6243` → Not a valid object），仓库最早 commit 为 `fa291f44 梳理之后第一次提交` |

`4e57f2f7` 的关键作用：把上游项目从 `tools/` + `roles/` + `docs/` 旧布局迁移到 Skill-based 架构：`tools/ → skills/ppt-master/scripts/`、`templates/ → skills/ppt-master/templates/`、把 13 个 references 从 `roles/` 与 `docs/` 合并入 `skills/ppt-master/references/`（93KB vs 203KB，54% 体积减少）。本仓库 2026-06-14 入库时记录的 `a0d6243` 是记录错误，现已修正。

### 自上次入库（2026-06-14）以来变化规模

- **910 commits** 涉及 `skills/ppt-master/`
- **1,884 unique files** changed
- 现行 v5.0.0（2026-08-24 release）相比 v2.x 入库版本是**架构级重写**

### 同步详情

仅拷贝上游仓库的 `skills/ppt-master/` 子目录（不拷仓库根的 `.github/`、`AGENTS.md`、`docs/`、`index.html`、`projects/`、根 `requirements.txt` 等 CI/分发元数据）。SKILL.md 从 41,757 B / 542 行（v2 串行 pipeline "Step 1..N" + Main Pipeline Scripts 14 项 + 8 项全局确认）改为 5,700 B / 79 行（v5 路由式：Global Execution Discipline + Mandatory Load Order + Global Communication Rules，主流程由 `workflows/routing.md` + `workflows/profiles/*.md` + `workflows/stages/*.md` 驱动）。

**新增**（564 项）：

- `scripts/attribution_guard.py` —— SKILL.md 第 2 步硬性 gate，必须随同步带入
- 15 个 references：`artifact-ownership`、`executor-{chart,image,notes,structure,structured,table,visualization,web-image}`、`native-{data-interface,formula,hyperlinks,shape-authoring}`、`pptx-structure-interface`、`preset-shape-vocabulary`、`semantic-svg`、`shared-standards-core`、`strategist-{image,template}`、`topology-assembly`、`video-design`
- 51 个 scripts（`prompt_audit`、`project_specs`、`mirror_template_materialize`、`chart_recall`、`narration_sync`、`slide_roster`、`sound_sync`、`video_*`、`native_enhance_pptx`、`pptx_intake`、`pptx_delivery_check` 等）+ 4 个 scripts 子目录（`confirm_ui/`、`pptx_shapes/`、`project_management/`、`svg_quality/`）+ 数据文件（`pptx_animation_presets.json` 561KB、`prompt_audit_manifest.json`）
- `workflows/{governance/, profiles/, stages/}` 三个子目录 + `workflows/{generate-pptx, native-enhance-pptx, routing, index}.md`
- 5 类 templates 新增：`styles/`（12 风格）、`decks/中国电信`、`decks/中汽研`、`scaffolds/`、`schemas/`、`sounds/`、`VISUALIZATION_TEMPLATE_AUTHORING.md`
- 6 个 brands：`alibaba`、`aws`、`bain`、`bcg`、`deloitte`、`huawei`、`jpmorgan`、`mckinsey`、`nvidia`、`pwc`、`tencent`、`xiaomi`（实际新增 6 个，总数 12 → 18）
- 大量 chart/layout/icon 资源（chart SVG 新增 donut / dual_axis_line / dumbbell / funnel / gantt / gauge / grouped_bar / heatmap 等）

**丢弃**（v2 时代不再适用，100 项本地独有文件）：

- `workflows/{create-brand, customize-animations, generate-audio, live-preview, resume-execute, topic-research, verify-charts, visual-review}.md` —— v5 路由表替代
- `scripts/svg_to_pptx/*.py`（13 文件）—— 上游改用 `native_enhance_pptx`
- 本地部分老品牌模板（`anthropic/`、`google/`、`brands/README.md`、`charts_index`、`brands_index`） —— 上游 v5 重新整理

### 残留风险

- **最大风险**：v5.0.0 是**架构级**变化（routing + profiles + stages），不是简单的版本号升级。Agent 在调用本 Skill 时的执行流程会显著变化 —— 任何下游 agent 流程文档（如 skill 内置 example）需要重新对照
- **次风险**：仓库大小显著增加（76M → 95M，+19M）
- **未做实测**：v5 路由式工作流未实际跑过生成 PPT 的完整流程
- **未保留 v2 workflows**：本地无 LOCAL-EDIT.md 记录 v2 workflows 的迁移意图；如需保留，可在 future commit 单独 backport

### 验证

- `md5sum other-Skills/ppt-master/SKILL.md /tmp/upstream-check/ppt-master/skills/ppt-master/SKILL.md` 一致（`b5e24473...`）
- `test -f other-Skills/ppt-master/scripts/attribution_guard.py` 通过
- `find other-Skills/ppt-master -type d -name __pycache__` 为空
- `find other-Skills/ppt-master -type f -name .env` 为空
- `ls other-Skills/ppt-master/.git` → No such file or directory
- `grep '^version:' other-Skills/ppt-master/SKILL.md` 返回 `version: "5.0.0"`
- `find other-Skills/ppt-master -type f | wc -l` = 12,925