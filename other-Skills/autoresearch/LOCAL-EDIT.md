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
