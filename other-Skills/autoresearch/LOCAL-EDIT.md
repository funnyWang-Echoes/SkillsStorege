# 本地修改记录（LOCAL-EDIT）

记录本仓库副本相对上游原版所做的修改，便于追溯与对比。上游来源见根目录 `Readme.md`（当前标记为「来源待确认」，声明泛化自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)）。

## 2026-07-24 — 删除配套 skill 引用

- **修改内容**：删除原 `SKILL.md` 中「## 前置：复用两个现有 skill」整节。
- **被删原文**：

  > ## 前置：复用两个现有 skill
  >
  > 可用时先读，不可用则在 setup 里覆盖同样的检查项：
  >
  > - **`experiment-hygiene`**：循环前的纪律检查（工作区干净、专用分支、有 baseline）。
  > - **`eval-harness`**：定义「什么叫改善、什么叫达标」，作为循环的验收标准。

- **修改原因**：本库暂无 `experiment-hygiene`、`eval-harness` 两个配套 skill，避免引用缺失依赖。
- **功能影响**：无实质损失——两 skill 覆盖的检查项（指标定义、预算、可改范围只读、专用分支、结果目录）已由保留的「## Setup：敲定研究配置」一节完整覆盖。
- **保留未动**：`SKILL.md`「何时用 / 不用」中仍提到 `benchmark-optimization-loop`（本库亦无），因其属于「不适用时改用谁」的指引而非前置依赖，暂未删除；如需一并清理可再改。
- **恢复方式**：若日后补入这两个配套 skill，可按上方被删原文恢复该节。

## 2026-07-24（第二轮，local-0.2.0）— 清残留引用 + 实操健壮性 + 平台说明

本轮为本地新增/改写，非上游原文：

- **清理残留缺失依赖引用**（与第一轮同方向，完成收口）：
  - 「何时用 / 不用」中 `benchmark-optimization-loop` → 改为通用表述「不必起循环，按常规工程优化流程处理（改动少、人盯得住）」。
  - 「没想法时」中「用 `search` 或 `deep-research`」→ 改为「主动联网调研」。
  - frontmatter description 中「不用于单次性能优化（用 benchmark-optimization-loop）」→ 删去括号引用。
- **补 `results/` 的 git 口径**（Setup 第 7 条）：文本台账（log.md、调研笔记）commit 进分支；run.log 及大二进制产物按体量 gitignore 或另存，避免仓库膨胀。
- **新增「### 中断恢复（断线 / 重启后续跑）」节**：靠 git 分支 + log.md 续跑——脏改动按 discard 处理、读最新总览行确认 best、从下一轮编号继续，不重头跑。
- **写明 baseline 双重职责**：第一轮兼验证抓取命令，抓不到指标 = 抓取命令写错，先修再进循环，否则每轮都会被误判成 crash。
- **补平台说明**（Setup 第 2 条）：命令按目标环境 shell 写；Windows PowerShell 重定向语义不同（默认 UTF-16、不支持 `&&`），建议统一 bash 或远程 Linux 执行。
- **frontmatter 加 `version: "0.2.0-local"`**：上游无版本号，此为本仓库本地维护版本号（local-0.1.0 = 第一轮删前置节）。
