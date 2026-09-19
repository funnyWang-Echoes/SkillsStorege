# 2026-09-19 grill-me / grilling 来源核验（结果：来源待确认）

- **日期**：2026-09-19
- **触发原因**：用户要求把 `grill-me` 按 `archify` 的方式只做文档登记；登记需要准确来源
- **会话**：main session
- **结论**：**来源待确认**（未定位到公开上游）。本机副本位置已确认，但由于查不到上游，无法登记拉取命令；已在根 `Readme.md`「登记未入库的 Skill → 来源待确认」一节标记为来源待确认，不假写链接

## 1. 本机副本的真实位置

```text
C:\Users\c\.zcode\skills\grill-me  ->  symlink  ->  C:\Users\c\.codex\skills\grill-me
```

`ls -la /c/Users/c/.zcode/skills/` 输出：

```text
lrwxrwxrwx 1 c 197121 33 Aug 24 23:00 grill-me -> /c/Users/c/.codex/skills/grill-me
```

即 `grill-me` 不是从外部下载进 ZCode 的，而是 Codex 侧 skill 目录的符号链接。`~/.codex/skills/` 下两个目标均为**实体目录**（非链接）：

| 路径 | 文件 | 大小 | 时间戳 |
|---|---|---|---|
| `C:\Users\c\.codex\skills\grill-me` | `SKILL.md`、`agents/openai.yaml` | 159 B / 137 B | 2026-07-27 14:49 |
| `C:\Users\c\.codex\skills\grilling` | `SKILL.md`、`agents/openai.yaml` | 843 B / 105 B | 2026-07-27 14:49 |

两个目录时间戳相同，判断为同一次安装/创建动作产生的一对 Skill：`grill-me` 是入口（正文仅一句 `Run a \`/grilling\` session.`），`grilling` 承载实际逻辑。

`grilling/SKILL.md` 正文（843 B，全文）：

```text
---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.
```

`grill-me/agents/openai.yaml` 含 `policy.allow_implicit_invocation: false`（只允许显式调用），说明它是被设计成显式触发的入口 Skill。

## 2. 为什么判为「来源待确认」

1. **文件本身没有来源信息**：两个 `SKILL.md` 的 frontmatter 只有 `name` 与 `description`，没有 `license`、`metadata.author`、`metadata.source`、`version` 等字段（对比同机的 `archify` 有完整来源字段、`aihot` 有 `metadata.version`）。
2. **公开检索未命中同文本**：
   - GitHub 仓库搜索 `grill-me skill`（`total_count` 136）、`grilling agent skill`（`total_count` 110），逐条查看前列候选。
   - 逐一比对候选仓库的 SKILL.md 文本：`RobMitt/grill-me-skill` 的 SKILL.md 要求使用 `AskUserQuestion` 工具并给出 2–4 个多选项、以「a concise summary of all decisions made」收尾，与本机 843 B 文本**不同**；`joshuawheelock/grill-me` 的 `skills/grill-me/SKILL.md`（4,054 B）体量与本机文本不符，且该仓库以 Go 二进制 `pick-quiz-file` 为核心，形态不同。
   - 严格来说这只能证明"前列候选不是来源"，不能证明上游不存在；因此结论写为**待确认**而不是"无上游"。
3. **两种可能性都无法排除**：可能是自用/自写的两个 Skill，也可能是从某个未检索到的来源安装的。本机文件不含可区分的证据。

**未采用的判定手段**：没有可用凭证的 GitHub 代码搜索（code search API 需要认证，本机无 `gh`），也没有按文本做全站搜索的第三方索引可用；`grep.app` 请求在当前网络下 TLS 握手失败。若后续需要，可在有 GitHub token 的环境用 `GET /search/code?q="Interview me relentlessly about every aspect"` 复核。

## 3. 连带发现：ZCode 侧 `/grilling` 是悬空引用

`~/.zcode/skills/` 只链接了 `grill-me`，**没有** `grilling`：

```text
$ ls -1 /c/Users/c/.zcode/skills/ | grep -i grill
grill-me
```

因此在本会话（ZCode）里，`grill-me` 的正文 `Run a /grilling session.` 指向的 `/grilling` 没有对应 Skill 可加载；Codex 侧两个都存在。这不是失败证据，但它是"跨 harness 链接不完整"的事实，登记时一并记录。

## 4. 残留风险与下一步

- **本机副本是唯一副本**：`C:\Users\c\.codex\skills\{grill-me,grilling}` 未纳入任何版本管理；若该目录被清理，两个 Skill 即不可恢复。这是当前最实际的风险。
- **处置选项**（已在根 Readme 待办登记）：
  1. 定位公开上游后，改为「按需拉取」登记（与 `archify` 同处理）；
  2. 确认属自用后移入 `my-Skills/`，由本仓库托管，并去掉对 `~/.codex/skills/` 的依赖；
  3. 同时补齐 ZCode 侧 `grilling` 链接，消除悬空引用。
- **登记会过期**：若后续定位到上游或改为入库，需更新根 `Readme.md` 对应条目并同步本文件的"结论"一节。
