---
name: workspace-bootstrap
description: |
  快速创建或整理开发、科研、混合型工作空间。用于初始化项目目录、生成项目级 AGENTS.md、建立 README/docs/tasks/runs/outputs 等工作区契约，或诊断“目录很乱”的现有项目。用户提到搭建 workspace、初始化科研项目、整理项目结构、补项目级 AGENTS、任务追踪目录、todo/done 阶段管理、开发/论文/实验工作区时应触发。整理现有项目时必须先只读扫描并给出迁移计划，确认后再编辑，不自动移动或删除用户文件。
metadata:
  type: project
  version: 0.4.1
  created: 2026-07-05
  updated: 2026-07-05
  references:
    - references/project-agents-template.md
    - references/workspace-profiles.md
    - references/task-system.md
---

# Workspace Bootstrap

目标：把一个新目录或已有混乱目录变成可持续使用的开发/科研工作空间。这个 skill 的核心产物不是“很多文件夹”，而是**项目级工作契约**：路径边界清楚、任务状态可恢复、生成输出有去处、后续 Agent 知道该读什么、能改什么、不能碰什么。

## 适用场景

- 用户要新建开发、科研、论文阅读、数据分析、仿真、Web/App 或混合型 workspace。
- 用户说“这个项目目录很乱”“帮我整理项目结构”“给项目补 AGENTS.md”。
- 用户想建立 `todo1/todo2/已完成1/已完成2` 这类阶段化任务系统。
- 用户要把个人 Agent 协作规则落到项目级 `AGENTS.md`。

不要用于：只想问某个文件内容、只要普通代码 review、已经有明确工程任务且不涉及工作区结构或项目规则。

## 基本原则

- 新项目可以直接创建骨架；已有项目先只读诊断，再让用户确认改动。
- 默认用中文生成项目级 `AGENTS.md`、`README.md`、任务说明和 docs 入口；只有用户明确要求英文，或项目已有英文协作/开源语境时，才生成英文。
- 项目级 `AGENTS.md` 写项目契约，不整包复制个人全局偏好。
- 目录设计要少而稳定。不要在根目录平铺 `todo1/`、`todo2/`、`done1/` 这类弱语义目录。
- 原始数据、论文、用户材料、运行数据和生成输出必须有明确边界。
- 不删除、不移动、不覆盖已有文件，除非用户明确确认具体路径和动作。
- 生成输出默认写入当前 workspace 的 `outputs/` 或 `runs/`，不要写入已安装 Skill 目录或工具源码目录。

## 参考文件

执行前按任务需要读取：

- `references/project-agents-template.md`：项目级 `AGENTS.md` 模板和下沉规则。
- `references/workspace-profiles.md`：`dev`、`research`、`hybrid`、`skill`、`mcp` 等目录 profile。
- `references/task-system.md`：`tasks/` 状态机、任务文件模板和 registry 规则。

## 工作流

### 1. 判断模式

先判断用户意图属于哪一类：

| 模式 | 触发信号 | 默认动作 |
|---|---|---|
| 新建 workspace | “创建/初始化/搭建一个项目目录” | 询问或推断 profile，创建最小骨架 |
| 整理现有 workspace | “目录很乱/帮我整理/补 AGENTS.md” + 现有路径 | 只读扫描，输出诊断和计划 |
| 只生成规则 | “生成项目级 AGENTS.md/任务系统” | 读取项目事实后生成对应文档 |
| 任务系统设计 | “todo1/todo2/已完成怎么设计” | 使用 `tasks/` 状态机方案 |

如果路径不明确，先确认目标路径。Windows 路径要特别小心，不要因为目录名相似就操作错误项目。

### 2. 只读扫描现有项目

整理现有项目时，先收集事实，不做编辑：

- `git status --short`，确认是否是 git 仓库和是否有未提交改动。
- 根目录文件和一级/二级目录，排除 `.git`、`node_modules`、`.next`、`dist`、`build`、`coverage`、`logs`、`tmp`、`.smoke`、runtime store、大体积运行数据和已知依赖缓存。
- `README.md`、`.gitignore`、已有 `AGENTS.md`/`CLAUDE.md`/`TODO.md`，并检查子目录是否已有局部 Agent 指令文件。
- `package.json`、`pyproject.toml`、`Cargo.toml`、`Makefile`、`docker-compose.yml` 等入口文件。
- `docs/`、`data/`、`outputs/`、`runs/`、`experiments/`、`notebooks/` 等既有约定。
- 大目录和大文件分布只做浅层统计，用于判断原始数据、运行数据、依赖缓存和生成产物；不要递归读取 PDF、模型权重、日志、`.env*`、`*.log`、`*.tsbuildinfo`、`pw_args.json` 或 runtime store 内容。
- 使用 `.gitignore` 判断本地数据、runtime data、测试样例和生成产物；被忽略的内容默认进入 `Do Not Touch By Default`，除非项目文档明确说明它们可再生成且用户要求清理。

诊断时把内容分类为：source code、docs/planning、raw input data、processed data、runtime data、generated outputs、experiments、dependencies/cache、ambiguous。

### 3. 选择 profile

根据项目事实选择一个或多个 profile：

- `dev`：普通软件开发项目。
- `research`：论文、数据、实验、报告为主。
- `hybrid`：同时有软件系统和科研/论文/数据工作流。
- `skill`：ZCode/Agent Skill 开发。
- `mcp`：MCP server 或长任务工具。
- `simulation`：仿真软件、作业运行、结果分析。

读取 `references/workspace-profiles.md` 后生成最小必要结构。不要一律创建所有目录。

### 4. 生成计划

对新项目，给出将创建的目录和文件。

对现有项目，给出：

- 当前目录事实摘要。
- 推荐保留的既有约定。
- 缺失的工作区契约，例如根 `AGENTS.md`、docs 入口、输出边界或任务真源说明。
- 现有 planning source of truth，例如 `docs/TODO.md`、OpenSpec、GitHub Issues、roadmap；如果已经成熟，默认引用它，不创建并行任务系统。
- `Do Not Touch By Default` 清单，列出原始数据、运行数据、迁移源、大体积输入、缓存和用户材料。
- 建议新增文件和目录，按“必要”和“可选”区分。
- 可选迁移动作，明确每个源路径、目标路径、风险和是否需要用户确认。

只有新增空目录、创建新文档、追加明确说明这类低风险动作可在用户确认整体计划后执行。移动、删除、覆盖和改名必须单独列出并等待确认。

### 5. 创建或更新文件

新建项目可以生成完整骨架：

```text
AGENTS.md
README.md
.gitignore
docs/index.md
docs/contracts/workspace-contract.md
tasks/README.md
tasks/registry.md
tasks/todo/01-intake/
tasks/todo/02-planned/
tasks/todo/03-ready/
tasks/active/01-doing/
tasks/active/02-review/
tasks/active/03-verify/
tasks/blocked/
tasks/done/01-implemented/
tasks/done/02-verified/
tasks/done/03-delivered/
runs/
outputs/
```

新建 workspace 必须生成 `.gitignore`，除非用户明确要求不要。`.gitignore` 要覆盖 `.env*`、credentials/secrets、logs/temp、cache、依赖、构建产物，以及该 profile 下默认不应提交的大体积 raw data、runtime data 和 generated outputs。`.gitignore` 的保护范围必须和 `AGENTS.md` 的 Path Boundaries / Do Not Touch 规则一致。

已有项目默认走最小契约：优先创建或更新根 `AGENTS.md`，必要时补 `docs/index.md` 或 `tasks/README.md` 指向现有任务真源。不要默认创建完整 `tasks/` 状态机、`docs/contracts/`、`runs/`、`outputs/`，除非用户明确要本地任务状态机或输出边界目录。

对已有项目，不要覆盖已有 README、AGENTS、TODO 或 registry。若文件已存在，先读取并提出补丁式更新。新增或重写 `AGENTS.md`、`README.md`、`tasks/README.md`、任务文件和 docs 入口时默认使用中文；若已有文件主体为英文，则沿用项目现有语言并说明原因。

### 6. 验证

完成后至少检查：

- 目标路径仍在用户指定 workspace 内。
- 新增目录和文件符合计划。
- `AGENTS.md` 中写明 source、docs、data、outputs、runs、cache 的边界。
- `tasks/registry.md` 与实际任务目录一致。
- `.gitignore` 覆盖缓存、密钥、依赖、构建产物、本地测试样例和不应提交的大体积数据。
- `git status --short` 能清楚展示本次变更范围；如果存在本地测试副本，例如 `testing/`，应确认它被忽略或明确不纳入提交。

最终汇报要说明：改了什么、关键文件、未执行的迁移动作、验证结果、剩余风险。

## 项目级 AGENTS.md 生成规则

项目级 `AGENTS.md` 应短而具体，至少包含：

- Project Goal
- Path Boundaries
- Agent Workflow
- Persistent Task Tracking
- Documentation Contract
- Git Rules
- Verification
- Project-specific Notes

从个人全局规则中下沉“路径、证据、任务追踪、文档契约、git、验证、实现偏好”；不要下沉个人画像、通用沟通风格或与本项目无关的 MCP/Skill/仿真专项规则。

## 任务状态系统

默认使用 `tasks/{todo,active,blocked,done}/数字阶段/任务文件.md`，不要使用根目录 `todo1/`、`todo2/`、`已完成1/`。

状态语义：

```text
todo/01-intake       刚收进来的想法，还没梳理
todo/02-planned      已经拆解，有计划
todo/03-ready        条件具备，可以开工
active/01-doing      正在做
active/02-review     等待审查
active/03-verify     等待验证
blocked/             被外部条件卡住
done/01-implemented  已实现，但验证不完整
done/02-verified     已验证，有测试或检查记录
done/03-delivered    已交付，文档、总结、commit 状态已处理
```

任务文件和 registry 规范见 `references/task-system.md`。

## 输出格式

整理现有项目时，先输出：

````markdown
## Workspace Diagnosis

| Area | Finding | Evidence | Action |
|---|---|---|---|

## Existing Planning Source Of Truth

- <docs/TODO.md, OpenSpec, GitHub Issues, roadmap, or none>

## Do Not Touch By Default

- <raw data, runtime data, migration sources, large inputs, caches, user materials>

## Observed Structure And Minimal Contract

```text
<existing structure with only necessary contract additions, not a forced target tree>
```

## Proposed Changes

| Action | Path | Risk | Confirmation Scope |
|---|---|---|---|

## AGENTS.md Draft Outline

...
````

新建项目时，先输出：

```markdown
## Workspace Plan

Profile: dev/research/hybrid/...
Root: <path>

## Files And Directories To Create

...

## Initial Project Contract

...
```
