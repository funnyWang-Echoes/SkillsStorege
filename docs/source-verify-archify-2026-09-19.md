# 2026-09-19 archify 来源核验与按需拉取登记

- **日期**：2026-09-19
- **触发原因**：用户询问本地仓库 Skill 与远程同步状态、`archify` 是否已入库；随后决定 `archify` 只做文档登记、不复制本体入库，之后按需通过 URL 从上游拉取
- **会话**：main session
- **结论**：来源核验**通过**（仓库真实、公开、MIT、main HEAD 可定位）；按用户决策**本体不入库**，仅在根 `Readme.md`「按需拉取的外部 Skills（登记未入库）」与本文件登记来源、拉取方式与漂移证据

## 1. 上游元数据（GitHub REST API 实测）

```bash
curl -sS https://api.github.com/repos/tt-a1i/archify
curl -sS https://api.github.com/repos/tt-a1i/archify/branches/main
```

| 字段 | 值 |
|---|---|
| `full_name` | `tt-a1i/archify` |
| `html_url` | <https://github.com/tt-a1i/archify> |
| `homepage` | <https://tt-a1i.github.io/archify/> |
| `description` | Agent skill for beautiful, verifiable architecture, workflow, sequence, data-flow, and lifecycle diagrams—self-contained HTML with motion and crisp export. |
| `license` | MIT |
| `default_branch` | `main` |
| `main` HEAD | `72c750bb070d95171dbb2244e5b62b1b7da69c12`（2026-09-16T15:04:47Z，`fix(deps): unstick the fast-uri override from a version that is itself vulnerable (#347)`） |
| `created_at` / `pushed_at` | 2026-04-15 / 2026-09-19 |
| `stargazers_count` / `forks_count` / `open_issues_count` | 66,939 / 4,464 / 137 |
| `size` | 229,124 KB（≈224 MB，含全部非 Skill 内容） |
| `archived` | false |

上游版本的二次证据来自本机已装副本里的 `archify/skill-release.json`：

```json
{
  "schemaVersion": 1,
  "skillId": "archify",
  "channel": "development",
  "version": "2.17.0-dev.1",
  "source": { "repository": "https://github.com/tt-a1i/archify" },
  "updateManifestUrl": "https://tt-a1i.github.io/archify/skill-updates/archify/stable.json"
}
```

## 2. 真实 Skill 本体位置

仓库根（`GET /contents`）包含 `.agents/`、`.github/`、`archify/`、`benchmarks/`、`docs/`、`examples/`、`experiments/`、`generated/`、`integrations/`、`scripts/`、`viewer/`，以及 `archify.zip`、`README.md`/`README_EN.md`/`README_ZH.md`、`CHANGELOG.md`、`DESIGN.md`、`PRODUCT.md`、`ROADMAP.md` 等文档。

按仓库 `AGENTS.md` 的判定标准（是否直接包含 `SKILL.md`），**真实本体 = `archify/` 子目录**：

| 内容 | 说明 |
|---|---|
| `SKILL.md` | 16,396 B（HEAD）；frontmatter：`name: archify`、`license: MIT`、`metadata.version: "2.17"`、`metadata.author: tt-a1i`、`metadata.based_on: Cocoon-AI/architecture-diagram-generator (MIT, v1.0)` |
| `LICENSE` / `THIRD_PARTY_NOTICES.md` | MIT + 第三方品牌矢量数据声明（Simple Icons 16.28.0 / CC0） |
| `package.json` / `package-lock.json` / `skill-release.json` | Node 包清单（`engines.node >= 18`、`private: true`）与自更新清单 |
| `bin/` | `archify.mjs`、`open-artifact.mjs`、`preview.mjs`、`visual-check.mjs` |
| `schemas/`、`renderers/`、`delta/`、`migrations/`、`scripts/` | 五类图（architecture / workflow / sequence / dataflow / lifecycle）的 renderer 与校验器 |
| `references/` | `authoring-contract.md`、`delivery-contract.md`、`brand-marks.md`、`viewer-runtime.md` |
| `recipes/`、`examples/`、`brand-marks/`、`assets/` | 场景配方、示例 JSON/HTML、品牌矢量、模板 |
| `test/` | 136 个测试文件 |

## 3. 本机已装副本与上游 HEAD 的逐文件比对

**方法**（可复现）：用 GitHub Trees API 取 HEAD 下 `archify/` 全部 blob 的 git SHA，再对本机每个文件计算 git blob 哈希（`sha1("blob <len>\0" + content)`）后逐个比对。

```bash
curl -sS "https://api.github.com/repos/tt-a1i/archify/git/trees/72c750bb070d95171dbb2244e5b62b1b7da69c12?recursive=1"
# 本机：C:\Users\c\.zcode\skills\archify，逐文件算 git blob 哈希后与上面的 SHA 对齐
```

| 指标 | 值 |
|---|---|
| 上游 `archify/` blob 总数 | 218 |
| 本机文件总数 | 79 |
| 字节一致 | 63 |
| 本机缺失 | 139（`test/` 136、`scripts/` 2、`package-lock.json` 1） |
| 本机多出 | 0 |
| **内容不同** | **16** |

内容不同的 16 个文件：

```text
assets/template.html
bin/archify.mjs
delta/architecture-delta.mjs
examples/dataflow-product-analytics.html
examples/lifecycle-agent-run.html
examples/sequence-cache-miss-request.html
examples/web-app-rendered.html
examples/workflow-agent-tool-call-rendered.html
package.json
references/authoring-contract.md
references/delivery-contract.md
renderers/shared/cli.mjs
renderers/shared/diagnostics.mjs
renderers/shared/repository-evidence.mjs
renderers/workflow/workflow-compiler.mjs
scripts/check-render-output.mjs
```

抽样 diff（`上游 → 本机`，即本机缺哪些上游新增内容）：

- `bin/archify.mjs`：上游 78,627 B / 本机 76,056 B。上游新增 `recoveryFiles` 追踪、"Recovery directory retained at ${stagingDirectory}" 提示，以及按备份路径逐条生成的 `supportedFixes`；本机为旧版单行 `supportedFixes`。
- `references/authoring-contract.md`：上游 14,192 B / 本机 13,962 B。上游新增"校验忽略本地 Git replacement refs（含 `GIT_REPLACE_REF_BASE`），始终按 pinned SHA 读取原始对象"的说明。
- `package.json`：本机缺 `scripts` 与 `devDependencies`（发行裁剪），且 `overrides.fast-uri` 仍为 `3.1.5`；上游 HEAD 为 `^3.1.7`（上游 commit `72c750bb` 记录 3.1.5 已被 4 条 advisory 覆盖、`npm audit` 报 2 个 high）。

**结论**：本机副本是**发行裁剪产物**（去掉 `scripts`/`devDependencies`/`test/`/`package-lock.json`），且**内容整体落后于上游 `main` HEAD**；其中 `SKILL.md` 与 `skill-release.json` 与 HEAD 字节一致，因此"版本号相同"不能作为"内容一致"的依据。

## 4. 不入库本体的理由

1. **自更新通道**：`skill-release.json` 带 `updateManifestUrl`，本体由上游更新流程维护；任何入库快照都会随上游更新持续漂移，本仓库无法保证它代表"当前版本"。
2. **体积与结构**：真实本体在上游子目录，仓库根另有 `docs/`、`viewer/`、`benchmarks/`、`experiments/`、`integrations/`、`scripts/`、`generated/` 等非 Skill 内容，整仓 ≈224 MB；整仓入库违反本仓库"只保留 Skill 本体"的原则。
3. **可替代**：上游提供官方安装命令与离线 ZIP，按需拉取的成本低于长期维护一份必然过期的副本。

## 5. 按需拉取方式（来自上游 README）

```bash
# 全局安装
npx skills add tt-a1i/archify -g

# 非交互安装到指定 agent
npx -y skills add tt-a1i/archify --skill archify --agent cursor --global --copy --yes

# 免安装试用
npx skills use tt-a1i/archify@archify --agent codex
```

离线路径：从仓库根取 `archify.zip` 解压到目标 skills 目录，得到 `<目标目录>/archify`。运行要求：Node.js >= 18。

## 6. 残留风险与下一步

- **本机副本落后**：`C:\Users\c\.zcode\skills\archify` 有 16 个共有文件落后于 HEAD。把它当"当前版本"会拿到旧实现；需要当前版本时重跑第 5 节命令。
- **`fast-uri` pin 差异未实测影响面**：本机副本 `package.json` 写 `3.1.5`，上游 HEAD 为 `^3.1.7`。本机副本的 `devDependencies` 已被裁剪，`ajv`/`fast-uri` 是否实际安装并进入运行路径**未实测**，因此未判定为可利用漏洞。
- **登记会过期**：上游处于 development 通道且版本号不一定随内容更新而变化；本文件的比对结论对应 `main` HEAD `72c750bb`（2026-09-16）。若上游有新提交，需重新核验后再更新根 `Readme.md`。
- **下一步**：需要 `archify` 时按第 5 节拉取；若后续决定改为入库本体，须先在 `doing/` 建工作副本、按发行版裁剪规则确认保留范围，再替换正式目录并补 `other-Skills/` 的 Readme 记录。
