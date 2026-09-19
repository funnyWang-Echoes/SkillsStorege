# 2026-09-19 harness 安装副本同步（Codex 侧 4 个过期 Skill）

- **日期**：2026-09-19
- **触发原因**：核验 `grill-me` 来源时发现 `C:\Users\c\.codex\skills\` 是**实体副本**（不是指向仓库的符号链接），其中 4 个 Skill 停在 2026-08-26 刷新前的版本；用户确认执行同步
- **会话**：main session
- **结论**：4 个过期副本已重同步为与仓库逐字节一致（`diff -rq` 0 差异），同步前做了完整备份；**Codex 侧副本无任何本地独有内容**，覆盖未丢失数据

## 1. 本机安装拓扑（本次核验事实）

| 路径 | 形态 | 与仓库的关系 |
|---|---|---|
| `C:\Users\c\.zcode\skills\*` | 除 2 个例外全是**符号链接** | 直接指向 `E:\SkillsStorege\{my-Skills,other-Skills}\<name>`，仓库内容即安装内容，改动立即生效 |
| `C:\Users\c\.zcode\skills\archify` | 实体目录 | npm 安装的产物（`npx skills add`），与仓库无关，见 [source-verify-archify-2026-09-19.md](source-verify-archify-2026-09-19.md) |
| `C:\Users\c\.zcode\skills\grill-me` | 符号链接 | 指向 `C:\Users\c\.codex\skills\grill-me`（跨 harness 链接），见 [source-verify-grill-me-2026-09-19.md](source-verify-grill-me-2026-09-19.md) |
| `C:\Users\c\.codex\skills\*` | **实体副本** | 与仓库无链接关系，**仓库更新后不会自动刷新**，必须手动重同步 |

**由此纠正一个错误结论**：2026-09-19 早前用 `diff -rq 仓库目录 ~/.zcode/skills/<name>` 得到"21 个 Skill 逐字节一致"，该比对因为 `~/.zcode/skills/*` 本身是指向仓库的符号链接而**恒等成立，不构成证据**。真正需要比对的是 Codex 侧的实体副本。

## 2. 同步前的过期清单

| Skill | Codex 侧（同步前） | 仓库（v 当前） | 差异条目 | 落后内容 |
|---|---|---|---|---|
| `aihot` | 1 文件 | 10 文件 | 8 | 2026-08-26 的 v1.5.4 刷新（`install.sh`、`manifest.sha256`、`references/{api,errors,sync}.md`、`agents/openai.yaml` 等） |
| `neat-freak` | 3 文件 | 94 文件 | 7 | 2026-08-26 的 v3.0 刷新（`evals/` 11 个 fixture、`references/{governance,verification}.md`、`scripts/audit-inventory.sh`） |
| `web-design-engineer` | 33 文件 | 39 文件 | 10 | 2026-08-26 的 v1.3.0 刷新（manifest 1.2.2 → 1.3.0、`references/` 5 个新文档） |
| `ppt-master` | 5,279 文件 | 12,925 文件 | 1,810 | 2026-08-26 的 v5.0.0 架构级同步（v2 串行 pipeline → v5 路由式） |

其余 14 个 Codex 侧 Skill 与仓库 `diff -rq` 0 差异，无需同步。

## 3. 覆盖前的安全核查（确认无本地独有内容）

对每个 Skill 先算「仅存在于 Codex 侧」的文件集合：

- `aihot`、`neat-freak`、`web-design-engineer`：**0 个**独有文件，镜像覆盖无损。
- `ppt-master`：173 个独有文件（142 个普通文件 + 31 个缓存文件），逐个判定：
  - **31 个缓存**：3 个 `__pycache__` 目录（`scripts/`、`scripts/svg_finalize/`、`scripts/svg_to_pptx/`）与 `.pyc`，属运行产物，不保留。
  - **142 个普通文件**：逐个执行 `git -c core.quotepath=false log --all --oneline -- other-Skills/ppt-master/<rel>`，**全部命中仓库历史** → 均为 2026-06-14 初次入库（`089f648`）带入、被 v5 同步 `7d5eeda` 删除或重组的 v2 时代上游文件（`scripts/svg_to_pptx/drawingml_*.py`、`pptx_*.py`、`templates/charts/*.svg`、`templates/brands/{anthropic,google}/*`、`templates/decks/<公司>/*` 等）。
  - **结论**：**0 个文件是 Codex 侧独有内容**，镜像覆盖不会丢失任何用户数据。自定义观感很强的中文企业模板（中国电信、中国电建、招商银行、重庆大学、中汽研）也是**上游自带**文件，不是本地创作——首次加入记录均为 `089f648`（2026-06-14 上游导入），不是用户提交。

**方法论修正（供后续复查复用）**：第一次判定用 `git log --diff-filter=D --pretty=format: 7d5eeda -1` 取删除集合再匹配，得到 87 个"无法解释"文件（含中文路径），属**误报**。改为逐路径 `git log --all -- <path>` 才是可靠判据——它同时覆盖"被删除"和"被重组移动"两种情况，且不受路径引号转义影响。

## 4. 备份

```text
C:\Users\c\.codex\skills-backup-2026-09-19\
  aihot\  neat-freak\  web-design-engineer\  ppt-master\
```

- 体积 65 MB，覆盖前用 `cp -a` 创建，文件数逐项校验一致（`aihot` 1 / `neat-freak` 3 / `web-design-engineer` 33 / `ppt-master` 5,279）。
- 确认同步结果无误后即可删除；若需要 v2 时代的品牌模板（见下），删前先从备份取出。

## 5. 同步后验证

```text
aihot: diff条目=0  文件数=10   ✅
neat-freak: diff条目=0  文件数=94   ✅
web-design-engineer: diff条目=0  文件数=39   ✅
ppt-master: diff条目=0  文件数=12925   ✅
```

对 Codex 侧全部 18 个 Skill 重跑 `diff -rq`：除不在仓库的 `grill-me` / `grilling` 外，**全部 0 差异**。同步后检查 `__pycache__`、`*.pyc`、`.env`：**无**（仓库本身不含这些，镜像同步不会引入）。

## 6. 残留风险与下一步

- **没有自动化**：Codex 侧是实体副本，仓库每次更新 `other-Skills/` 后都要手动重同步；本次是首次系统性处理，之前没有任何机制保证一致。是否要写一个同步脚本由用户决定。
- **v5 上游删掉的 v2 品牌模板**：`招商银行`、`重庆大学`、`中国电建_常规`、`中国电建_现代`、`中汽研_商务`、`中汽研_现代` 等 v2 布局模板在 v5 中不再提供（v5 只保留 `中国电信`、`中国电建`、`中汽研`，且改为 `templates/brands/<公司>/templates/` 布局）。这些文件现存于本次备份与仓库 git 历史（`git show 089f648:other-Skills/ppt-master/templates/decks/<公司>/...` 可取回）。若实际在用这几套模板，需另行决定是否保留为本地扩展。
- **Codex 侧未安装的仓库 Skill**：`autoresearch`、`research-progress`、`video-shotcraft`、`xhs-knowledge-skill`、`xiaohongshu-skills` 在 `~/.codex/skills/` 中不存在（ZCode 侧有）。是否有意为之未知，本次未处理。
- **`ppt-master` 体积**：Codex 侧副本同步后为 12,925 文件 / 约 95 MB；若 Codex 有启动扫描开销，需自行评估。
