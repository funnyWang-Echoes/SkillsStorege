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