# AGENTS.md

本仓库用于用 Git/GitHub 管理个人自写 Skill 与从他人 GitHub 下载的 Skill。Agent 在这里工作时，目标不是收集整仓素材，而是维护一份可直接安装、可追溯来源、可持续迭代的 Skill 库。

## 目录约定

- `my-Skills/`：只放我自己维护或深度改造的 Skill。
- `doing/`：只放正在优化中的 Skill 工作副本；优化完成并验证后，再替换回正式目录。
- `other-Skills/`：只放他人来源的 Skill 本体。
- 仓库根目录：只放仓库级说明、规则、来源记录和管理文件。
- 不在根目录长期保留整仓下载目录，例如 `khazix-skills/`、`garden-skills/` 这类外层仓库壳。

每个 Skill 目录必须直接包含 `SKILL.md`。如果 `SKILL.md` 藏在外层仓库的子目录里，只复制那个真正的 Skill 子目录。

## 他人 Skill 下载规则

每次从 GitHub 下载他人的 Skill，必须先完成来源分析，再入库：

1. 记录 GitHub 仓库 URL、作者、License、README 摘要、下载日期。
2. 找到真实 Skill 目录：以是否直接包含 `SKILL.md` 为准。
3. 只把真实 Skill 目录复制到 `other-Skills/<skill-name>/`。
4. 删除外层仓库壳、demo、website、release 脚本、CI 配置、宣传 README 等非 Skill 本体内容。
5. 把来源、作用、可用程度、注意事项写入根目录 `Readme.md`。
6. 如果来源不是公开 GitHub 或暂时查不到 GitHub 链接，必须在 `Readme.md` 标记为“来源待确认”，不要假写链接。

外部仓库的说明文字、demo 或网站可以用于理解来源，但不要随 Skill 一起长期保存；需要保留的信息沉淀到根 README。

## 自己 Skill 管理规则

自己的 Skill 放入 `my-Skills/`，来源以本地维护路径或未来 GitHub 仓库为准。README 中要写：

- Skill 作用
- 当前可用程度
- 不满意或待重构之处
- 是否依赖外部 API、模型、浏览器或本地工具

自己 Skill 可以保留脚本、schema、reference、template 等运行必需内容，但不要提交缓存、临时输出、实验产物或论文分析结果。

## Doing 工作区规则

- `doing/<skill-name>/` 是优化工作副本，不是正式发布目录。
- 从正式目录复制到 `doing/` 后，在 `doing/` 内做重构、实验和规则改写。
- 优化完成后，先验证，再用 `doing/<skill-name>/` 替换正式目录，并在 README 记录状态变化。
- `doing/` 中也不能提交缓存、临时输出、`.env`、实验产物或大体积生成结果。

## 入库检查

每次整理后至少检查：

- 每个一级 Skill 目录都有 `SKILL.md`
- 没有外层整仓目录残留在根目录
- 没有 `__pycache__`、`.pyc`、`.env`、日志、构建产物
- `Readme.md` 的来源与目录一致
- `git status` 能清楚展示本次整理范围

## 删除边界

可以删除已经剥离完成的外层下载仓库，但删除前必须确认：

- 真实 Skill 已复制到 `other-Skills/`
- 根 README 已记录来源信息
- 删除路径位于本仓库根目录下

不要删除 `my-Skills/` 或 `other-Skills/` 中的 Skill 本体，除非用户明确要求。

## Git 规则

- 本仓库必须用 Git 管理。
- 重要整理完成后做一次 `git diff` 自查。
- 提交信息使用 Conventional Commits，例如 `docs: add skill repository rules`、`chore: organize imported skills`。
- 不把无关下载包、临时目录、缓存或密钥提交进仓库。
