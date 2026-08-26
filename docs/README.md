# docs/ — 仓库级变更与同步记录

本目录保存与本仓库 Skill / MCP 库相关的**跨设备同步、版本检查、来源核验、计划与决策**等结构化记录。每条记录作为单文件提交到 git，便于事后追溯证据。

## 规则

- 文件名格式：`<event-kind>-<topic>-<YYYY-MM-DD>.md`，其中 `<event-kind>` 在以下枚举中：
  - `sync` — 跨设备/会话的状态或文件同步（如 `AGENTS.md` 同步、prompt 模板同步）
  - `version-check` — 上游版本比对（`other-Skills/` 与上游 HEAD）
  - `source-verify` — 外部 Skill/MCP 来源核验（URL、License、作者、commit 是否真实）
  - `plan` — 长期计划、迁移方案、版本升级路线
  - `decision` — 重大设计决策（与 `decisions/<topic>.md` 类似，但属于仓库级而非 Skill 级）
- 每个文件必须包含：
  - **日期**、**触发原因**、**执行人或 Agent 会话标识**（可写「main session」或自动生成的 session id）
  - **事实证据**：命令输出、URL、commit SHA、文件路径、行号
  - **结论**：明确的"已同步 / 待同步 / 已核验通过 / 已核验失败 / 暂缓"等
  - **残留风险与下一步**
- 一条记录只写一件事，避免把多类事件混在同一文件里。

## 与根目录 Readme.md 的关系

- 根 `Readme.md` 的「外部来源刷新记录」表只列**外部 Skill/MCP 入库**事件（含拉取 commit）。
- 「后续待办」列表只列**当前活跃的待办**与**关键决策指针**。
- `docs/` 内的文件提供**完整证据**与背景，是上面两表的展开版。

## 索引

| 文件 | 类型 | 日期 | 摘要 |
|---|---|---|---|
| [others-skills-version-check-2026-08-26.md](others-skills-version-check-2026-08-26.md) | version-check | 2026-08-26 | `other-Skills/` 14 个 Skill 与上游 HEAD 逐项比对；建议按优先级刷新 `neat-freak` v3.0 → `web-design-engineer` v1.3.0 → `aihot` v1.5.4 → `video-shotcraft`；修正 `autoresearch` 与 `ppt-master` 来源描述。 |
| [sync-others-skills-2026-08-26.md](sync-others-skills-2026-08-26.md) | sync | 2026-08-26 | 4 个 Skill 同步落地记录：每 Skill 一个 commit，doing 工作副本 + `diff -rq` 校验；`video-shotcraft` 同步时排除上游 `.git/` 184M；记录残留风险（`ppt-master` 入库 commit 待重核、`doing/.env` 违规、`neat-freak` evals fixture `.env`）。 |