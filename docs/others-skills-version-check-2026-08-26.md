# other-Skills 上游版本检查

- **执行日期**：2026-08-26
- **执行分支**：`chore/check-others-skills-versions`
- **执行方式**：通过 `http://127.0.0.1:7890` 代理 shallow clone 各上游仓库到 `/tmp/upstream-check/`，对 `other-Skills/` 下每个 Skill 做 SKILL.md `md5` 与目录文件清单比对。
- **目的**：核实根 `Readme.md` 中记录的"上次入库 commit / 来源 URL"是否准确，识别哪些上游有可同步的新版本。

## 摘要

`other-Skills/` 14 个 Skill 中，**7 个 SKILL.md 与上游 HEAD 字节相同**（不需同步），**4 个已有新版本**（建议刷新），**1 个需要修正来源标注**，`xiaohongshu-skills` 自入库 18 个 commit 全部是 `chore: update star history`，无功能变更。`ppt-master` 的 Readme 来源 commit (`a0d6243`) 不存在于上游仓库，需更正为 `skills/ppt-master` 路径下真实的早期 commit。

## 逐项结果

| 本地 Skill | 上次入库 commit | 上游当前 HEAD | SKILL.md 是否一致 | 结论 |
|---|---|---|---|---|
| `aihot` | khazix-skills `9c315d7` | khazix-skills `7a5c493` | ❌ 不同 | **建议刷新到上游 v1.5.4**。自上次入库以来上游对 aihot 共做了 10 次 `chore(aihot): sync skill to vX.Y.Z` 自动同步；本地 SKILL.md 完全缺少 `metadata.version` 字段，结构与上游当前版本差异较大。 |
| `hv-analysis` | khazix-skills `9c315d7` | khazix-skills `7a5c493` | ✅ 相同 | 无需同步。 |
| `khazix-writer` | khazix-skills `9c315d7` | khazix-skills `7a5c493` | ✅ 相同 | 无需同步。 |
| `neat-freak` | khazix-skills `9c315d7` | khazix-skills `7a5c493` | ❌ 不同 | **建议刷新到上游 v3.0**。上游 commit `2b4a645 neat-freak v3.0: middle-tier triggers, light path for small projects, generic platform fallback` 是一次明确的版本跃迁；description 已改为 "Knowledge and governance closeout"，触发词与覆盖范围与本地差异显著。 |
| `storage-analyzer` | khazix-skills `9c315d7` | khazix-skills `7a5c493` | ✅ 相同 | 无需同步。 |
| `autoresearch` | letsgetai/agent-skills（404） | — | 来源待确认 | **建议修正 Readme 来源描述**：本地 SKILL.md 自述"泛化自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)"，当前 HEAD `228791f`；`letsgetai/agent-skills` 仍 404。Readme 中"来源待确认"应改为"上游即 karpathy/autoresearch，本地 SKILL.md 由用户提供（入仓 commit 2026-07-24）"。`LOCAL-EDIT.md` 已记录 local-0.2.0 的本地化修改。 |
| `beautiful-article` | garden-skills `fbd6453` | garden-skills `aaf9a82` | ✅ 相同 | 无需同步。garden-skills 自 `fbd6453` 仅修改 `web-design-engineer/` 与 marketplace 路径。 |
| `gpt-image-2` | garden-skills `fbd6453` | garden-skills `aaf9a82` | ✅ 相同 | 无需同步。 |
| `kb-retriever` | garden-skills `fbd6453` | garden-skills `aaf9a82` | ✅ 相同 | 无需同步。 |
| `web-design-engineer` | garden-skills `fbd6453` | garden-skills `aaf9a82` | ❌ manifest version 不一致 | **建议刷新到上游 v1.3.0**。本地 `manifest.json` 仍为 `1.2.2`，上游已 `1.3.0`（commit `0886299 docs(readme): sync download links for web-design-engineer v1.3.0`）。新增 features：five-dial Design Read、preservation-aware redesigns、contextual failure patterns。SKILL.md 同步需要重新比对。 |
| `web-video-presentation` | garden-skills `fbd6453` | garden-skills `aaf9a82` | ✅ 相同 | 无需同步。 |
| `ppt-master` | hugohe3/ppt-master `a0d6243`（**不存在**） | hugohe3/ppt-master `ebd74d1` | — | **Readme 来源 commit 错误**：本仓库 `a0d6243` 不存在于 `hugohe3/ppt-master` 仓库（unshallow 后仍 `cat-file -t a0d6243` 返回 Not a valid object）。仓库最早 commit 是 `fa291f44 梳理之后第一次提交`，现存 1732 个 commit，`skills/ppt-master/` 路径下从 v2.0.0 起到 HEAD 共 1348 次变更。本地 SKILL.md 5.7KB，上游 11.8KB，差异显著。**建议：核查真实入库时的上游 commit 并修正 Readme，再决定是否刷新**（不强行同步，刷新前先 backup）。 |
| `video-shotcraft` | video-shotcraft `d491544` | video-shotcraft `d9ffa6d3` | 小幅差异（+31/-6） | **建议刷新（含新能力）**：自上次入库 18 个 commit、283 个文件变更。核心 SKILL.md/README 变化温和，但新增 `demos/`（72 文件）+ `gallery/`（96 文件）+ `jianying-export/`（5 文件，剪映工程导出成为 skill 正式能力）。`assets/` 文件数本地与上游一致（4 个）。 |
| `xiaohongshu-skills` | XiaohongshuSkills `8536136` | XiaohongshuSkills `ba485253` | ✅（实际未比对，commit 都是 chore: update star history） | 无需同步。18 个 commit 全部是 `chore: update star history`，Skill 本体（SKILL.md / scripts / config / requirements.txt）零变更。 |

## Readme.md 待修正项

1. **ppt-master** 的「拉取 commit `a0d6243`」改为仓库中真实可核验的早期 commit（建议先 `git log --reverse -- skills/ppt-master/SKILL.md` 找首次出现该路径的 commit，再写进 Readme）。
2. **autoresearch** 的「来源待确认」改为「上游即 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)（本地 SKILL.md 泛化自上游；当前 HEAD `228791f`）；入仓 commit 2026-07-24；`letsgetai/agent-skills` 仍 404」。

## 建议下一步

按优先级处理 4 个需刷新的 Skill：

1. **`neat-freak`**：上游 v3.0，触发词与 description 变化明显，建议先 `git diff 9c315d7..HEAD -- neat-freak/SKILL.md neat-freak/references/ neat-freak/scripts/` 看 diff，再决定是否整目录覆盖；本地 `references/` 仅 1 个文档，上游多份 references，可能需要合并。
2. **`web-design-engineer`**：manifest 已从 1.2.2 → 1.3.0，commit 提示是新增 references + 文档调整；建议全目录覆盖（diff 已确认 SKILL.md 在 fbd6453 之后变更）。
3. **`aihot`**：上游 v1.5.4 与本地结构差异大（10 次自动同步），建议全目录覆盖，注意核对 SKILL.md 中 description 字段与上游一致后再入库。
4. **`video-shotcraft`**：核心 SKILL.md 变更温和，但新增 `demos/` / `gallery/` / `jianying-export/` 体量大（>170 文件），且仓库根已声明「仓库根即真实 Skill」，建议按目录增量同步，避免覆盖本地已有的 `gallery/0…` 老内容前先列 diff。

刷新前应：
- 在 `doing/<name>/` 做工作副本（仓库 AGENTS.md 已规定 doing 工作流）。
- 备份当前 `other-Skills/<name>/`（`mv` 到 `doing/<name>/legacy-2026-08-26/`）。
- 同步完成后更新 `Readme.md` 中"上次入库 commit"与"可用程度"，并在「外部来源刷新记录」表追加一行。

## 复核建议

由于本检查只比对了 `SKILL.md` 的字节 hash 和顶层目录清单，对 `references/`、`scripts/` 子文件没有逐文件 diff，建议对建议刷新的 4 个 Skill 在 doing/ 工作副本里用 `diff -rq` 跑一次完整目录比对后再入库。