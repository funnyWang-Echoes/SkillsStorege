---
name: sim-agent-research
description: >
  仿真软件 Agent 生态调研技能。对任意仿真软件进行全维度 Agent 化可行性调研，
  包含接口、MCP Server、Skill、Agent 项目、学术论文、接入难度评估，
  输出带优先级排序的结构化 Markdown 报告。含初稿调研、增强审核、
  MCP/Skill 可用性深度复核三阶段流程。
  触发词：仿真软件调研、Agent生态调研、MCP调研、仿真软件agent化、
  simulation agent research、调研[软件名]
metadata:
  type: project
  version: 3.2.0
  created: 2026-06-04
  updated: 2026-06-06
  templates:
    - reference/VASP_Agent生态调研报告.md
---

# 仿真软件 Agent 生态调研 Skill

## 概述

本 Skill 用于对任意仿真软件进行**全维度 Agent 化可行性调研**。分三阶段执行：

- **阶段一（初稿调研）**：4 路子代理并行侦察，生成结构化报告
- **阶段二（增强审核）**：对报告进行论文/MCP/Skill 三维增强，补充缺失链接，修复格式问题
- **阶段三（可用性深度复核）**：对报告中调研到的每个 MCP / Skill 逐项源码级核验——判定"是否软件专用"、工具数量、来源性质、闭环执行能力（能否提交自动仿真，还是只能生成输入/解析输出，执行靠人工还是其他工具），结果**追加到该软件报告末尾**

## 触发条件

用户提到以下关键词组合时自动触发：
- "调研" + 仿真软件名称
- "Agent 生态" + 软件名
- "MCP" + "仿真"
- "Agent 化" + 软件名
- "/sim-agent-research"

---

## 阶段一：初稿调研

### 核心架构：4 路子代理并行侦察

每个软件同时派出 4 个 Explore 子代理，各自覆盖不重叠的信息域：

```
              ┌─ Agent-A: 官网/文档/接口侦察
              │   → 版本、License、API/SDK/CLI 清单、官方文档 URL
              │
              ├─ Agent-B: GitHub/Agent 生态侦察
软件名 ───────┤   → MCP Server、Skill、Agent 项目、LangChain/LlamaIndex Tool、
              │     IDE 插件（Cursor/Cline/Copilot）、Community 项目
              │
              ├─ Agent-C: 学术论文侦察
              │   → arXiv/Google Scholar/Semantic Scholar/ACM/IEEE/SpringerLink
              │     关键词：软件名 + LLM/GPT/Agent/Code Generation/Tool Use/MCP
              │
              └─ Agent-D: 实操可行性侦察
                  → Docker/PyPI/Conda/Maven、Python 控制方案对比、
                    Headless 能力、启动开销、工程痛点
                                    │
                                    ▼
                          主代理：去重 + 交叉验证 + 优先级排序 + 难度评分 + 写报告
```

### 信息源清单

| 子代理 | 必扫源 |
|---|---|
| A 官网 | 官方 docs / Developer Portal / GitHub Releases / 价格页 / License 页 |
| B 生态 | github.com、modelcontextprotocol/servers、punkpeye/awesome-mcp-servers、smithery.ai、glama.ai/mcp、pulsemcp.com、mcp.so、lobehub.com/mcp、mcpmarket.com、Anthropic Skills 仓库、LangChain Hub、LlamaIndex Hub |
| C 学术 | arXiv（cs.AI + cs.MA + cs.SE + cs.CL）、Google Scholar、Semantic Scholar、IEEE Xplore、ACM DL |
| D 实操 | Docker Hub、PyPI、conda-forge、Maven Central/npm、官方 GitHub examples |

### 数据源访问 fallback 机制（强制）

**当 WebFetch / WebSearch 因网络/SSL/防火墙失败时，必须升级为本地克隆/下载读取**，不允许仅凭页面摘要或主代理推测下结论。具体顺序：

1. **首选 WebFetch**——直接抓 README / 官方文档页 / GitHub Pages
2. **WebFetch 失败时改用 GitHub API + raw.githubusercontent.com**——绕过 HTML 渲染，直接拉 JSON 元数据和原始文件：
   - `curl -sL https://api.github.com/repos/<org>/<repo>` 取 stars/license/最近 commit
   - `curl -sL https://raw.githubusercontent.com/<org>/<repo>/<branch>/README.md` 取 README
   - `curl -sL https://api.github.com/repos/<org>/<repo>/contents/<dir>` 列目录
3. **API 也失败或需要看源码细节时，git clone 到临时目录阅读**：
   ```bash
   git clone --depth 1 https://github.com/<org>/<repo>.git "$CLAUDE_JOB_DIR/tmp/<repo>"
   ```
   - 必须使用 `$CLAUDE_JOB_DIR/tmp`（已存在、自动清理），不要用 `/tmp` 或仓库工作目录
   - `--depth 1` 浅克隆，节省带宽
   - 克隆后用 Read/Grep/Glob 工具阅读，**禁止用 Bash cat/head/tail 读源码**
4. **触发本地克隆的典型场景**：
   - MCP Server 的 Tool 函数清单需逐一确认（必须看源码 `tools/` 或装饰器）
   - 判断耦合度档位时（🟢DRIVE / 🟡GEN-IN）从 README 看不出来
   - 论文项目核实"是否真的开源 + 哪些模块开源"
   - License 文件实际内容与仓库元数据不一致时
5. **结论必须可溯源**：本地阅读后引用具体文件路径与行号（`<repo>/path/file.ext:LN`）写入报告，而不只是仓库根 URL

### 性能优化策略（强制）

WebFetch 是调研流程中最大的延迟瓶颈——单次 5–15s，一个子代理累计可达 1–3 分钟。以下策略**强制执行**，不可省略。

#### P1：GitHub 仓库一律走 API + raw，禁止 WebFetch

GitHub 仓库 HTML 页面极重（commits/contributors/CI 等大量无关内容），WebFetch 转换一次 8–15s。所有 GitHub 仓库元数据获取**必须用**：

```bash
# 元数据（stars/license/最近 commit）— 1 次 curl ≈ 1s
curl -sL https://api.github.com/repos/<org>/<repo>

# README — 1 次 curl ≈ 1s
curl -sL https://raw.githubusercontent.com/<org>/<repo>/<branch>/README.md

# 目录列表 — 1 次 curl ≈ 1s
curl -sL https://api.github.com/repos/<org>/<repo>/contents/<dir>
```

两次 API 调用 **2s** vs WebFetch **12s**，省 10s/个。**仅当 API 返回内容不足以判断耦合度/Tool 清单时**，才升级为 `git clone --depth 1`。

**禁止** `WebFetch("https://github.com/org/repo")` 这种直接 fetch 仓库页的用法。

#### P2：8 个 MCP 公共目录——先 WebSearch 筛，只 Fetch 有命中的

当前痛点：8 个 MCP 目录每个都 WebFetch 一次（8–10s），但 90% 返回 0 命中，合计浪费 50–60s。

**优化流程**：

```
步骤 1（快，3s/个）：WebSearch 定向搜索
  "VASP MCP" site:smithery.ai
  "VASP MCP" site:glama.ai/mcp
  "VASP MCP" site:pulsemcp.com
  "VASP" site:mcp.so
  ...（8 个目录各搜一次）

步骤 2（仅对有命中的目录）：WebFetch 抓取详情页确认项目名/描述
  → 命中 0 个：记"已检索，0 命中"，跳过 Fetch
  → 命中 1+：Fetch 详情页确认
```

**GitHub 上的两个目录**（modelcontextprotocol/servers、awesome-mcp-servers）不走 WebSearch，直接用 GitHub API 搜索：
```bash
# GitHub 代码搜索 — ≈ 2s
curl -sL "https://api.github.com/search/code?q=VASP+repo:modelcontextprotocol/servers"
```

**预估节省**：Agent-B 省 40–50s（从 ~55s 降到 ~10s）。

#### P3：arXiv 论文页一次 Fetch 够用，不二次搜 Scholar 确认

arXiv abs 页已包含：完整标题、全部作者、提交日期、摘要、DOI 链接、期刊引用。

```
正确流程：
  1. WebSearch 发现论文标题 → 拿到 arXiv ID
  2. WebFetch("https://arxiv.org/abs/XXXX.XXXXX") → 一次拿到全部元数据 ✅

错误流程：
  1. WebFetch arXiv 页
  2. 又 WebSearch Google Scholar 确认发表状态  ← 多余，arXiv 页已有
  3. 又 WebFetch Semantic Scholar 页          ← 多余
```

**例外**：仅当需要确认"该论文是否已被顶会/期刊正式录用"且 arXiv 页未标注时，才用 WebSearch `"论文标题" site:ieee.org OR site:acm.org OR site:nature.com` 快速确认。

**预估节省**：每篇论文省 5–8s，15 篇论文省 75–120s。

#### P4：WebFetch 超时意识——慢成功时主动切换

当 WebFetch 对某个 URL 响应缓慢但尚未超时时（体感 > 10s），子代理应**主动放弃并重试用替代方案**（API/raw/git clone），而不是等到超时。判断标准：

| URL 类型 | 替代方案 |
|---|---|
| GitHub 仓库/文件 | GitHub API + raw（P1） |
| MCP 目录网站 | WebSearch 确认有无命中（P2） |
| PyPI/Docker Hub | `curl -sL https://pypi.org/pypi/<pkg>/json`（≈ 1s） |
| 官方文档页 | WebFetch 是唯一选项（文档站无 API），容忍慢 |

#### 性能优化总览

| 场景 | 旧方案（慢） | 新方案（快） | 单次节省 |
|---|---|---|---|
| GitHub 仓库元数据 | WebFetch 仓库页（8–15s） | API + raw（2s） | **6–13s** |
| 8 个 MCP 目录扫描 | 每个 WebFetch（55s 总计） | WebSearch 筛 + 只 Fetch 命中（10s） | **~45s** |
| 论文元数据 | arXiv Fetch + Scholar 再确认（13s/篇） | arXiv Fetch 一次够（5s/篇） | **8s/篇** |
| PyPI 包信息 | WebFetch pypi.org（6s） | pypi.org API json（1s） | **5s** |

---

## 阶段一交付物结构（固定模板）

### 文档头部：总览表

| 软件名称 | 一级标签 | 二级标签 | 开源/闭源/License | 接口 | Skill | MCP | 论文 | 接入难度 | 备注 |
|---|---|---|---|---|---|---|---|---|---|

禁止留空。无内容填"无"或"未发现（已检索xxx来源）"。

**MCP / 接口 / Skill 字段必须按耦合度档位写明**，例如：

- 接口列：`Cloud Python SDK 🟢DRIVE、qeschema 🟠PARSE-OUT、CLI 🟢DRIVE`
- MCP 列：`2 个社区 MCP（1 🟢DRIVE：kishorkukreja/anylogic-mcp-server；1 🟡GEN-IN：umbaman/anylogicPLE-mcp）`
- Skill 列：`无正式 Skill（已检索 N 个来源）；Skill 化候选 1 个（xxx 🟡GEN-IN）`

四档定义见阶段二增强维度二（🟢DRIVE 直接驱动执行 / 🟡GEN-IN 仅生成输入 / 🟠PARSE-OUT 仅解析输出 / ⚪PERIPHERAL 周边/元数据）。

### Skill 的严格定义（全文统一适用）

> **Skill 是指带有 `SKILL.md` 文件的、可被 Claude Code 直接加载的技能定义。**
>
> 以下类型**不是 Skill**，在阶段一 4.3 表中应排除或标注为"Skill 化候选"：
>
> | 类型 | 示例 | 应记录位置 |
> |---|---|---|
> | **SDK / Library** | Alpyne (Python SDK)、pyNetLogo | 三、接口清单 |
> | **软件扩展原语** | NetLogoGptExtension（NetLogo 内部扩展） | 4.2 LLM 扩展/Agent 项目表 |
> | **研究配套代码** | swarm_gpt（.nlogo 模型文件） | 4.2 LLM 扩展/Agent 项目表 |
> | **MCP Server** | NetLogo-MCP、anylogic-mcp-server | 4.1 MCP Server 表 |
> | **Skill 化候选** | 无 SKILL.md 但有 Skill 潜力的参考书/模板集 | 4.2 或 4.3（标注"候选"） |
>
> **只有确认带有 `SKILL.md` 的项目才能计入"正式 Skill"。** 无法确认的标注为"Skill 化候选"，并在阶段三 B 表中按非 Skill 处理。
>
> 如果明确报告"未发现任何 Skill"，总览表 Skill 列写 `无正式 Skill（已检索 N 个来源）`，4.3 表写明反向证据。

### 一、软件简介
- 开发方、用途、典型用户
- 最新版本号与发布日期
- GitHub 仓库 URL + Stars（如有）
- 官方网站 + 社区论坛

### 二、License 与可获取性
- 开源/闭源、具体协议
- 商业使用限制
- 是否有付费版本/试用版/Docker 镜像
- 对 Agent 化（MCP/Skill）的法律影响评估

### 三、接口清单（含优先级排序）

接口全景表必含列（按此顺序）：
**优先级★ | 接口名称（含官方文档超链接） | 调用方式（🟢DRIVE/🟡GEN-IN/🟠PARSE-OUT/⚪PERIPHERAL） | 类型 | 官方/社区 | Python 可用性 | 维护状态**

- 接口名称直接是 markdown 链接，禁止"名称列+链接列"分离
- 调用方式必须填写四档之一，让读者一眼看出该接口能否驱动软件运行
- 核心接口给出代码示例
- 优先级规则：Python 优先 > 功能完整 > 使用人数多 > 最近维护 > 真正可用

### 四、现有 Agent 生态盘点（含优先级排序）

**4.1 MCP Server 表**必含列：
**优先级★ | 项目名（含 GitHub 超链接） | 调用方式 | 维护状态 | License | 最后 commit | Tool 函数清单 | 是否嵌套依赖**

**4.2 LLM 扩展 / Agent 项目表**必含列：
**优先级★ | 项目名（含超链接） | 调用方式 | 能力类型（参考书型/工具调用型/混合） | 输入→输出 | License | 维护状态 | 依赖链**

**4.3 Skill 项目表**必含列：
**优先级★ | 项目名（含超链接） | 调用方式 | 能力类型（参考书型/工具调用型/混合） | 输入→输出 | License | 维护状态 | 依赖链**

- 仅填入**确认带有 `SKILL.md`** 的项目（定义见"Skill 的严格定义"节）
- 无 SKILL.md 但有 Skill 潜力的项目标为"Skill 化候选"，或放入 4.2 Agent 表
- 如果未发现任何 Skill，写明"已检索 N 个来源未发现带有 SKILL.md 的 [软件名] 项目"

**去重规则**：同一项目同时具备 Agent 属性和 Skill 属性时，在 **4.3 Skill 表主记**（完整字段），4.2 Agent 表中**仅保留一行交叉引用**（如"详见 4.3"），避免信息重复。

**4.4 MCP 公共目录检索清单**：
- 必含 8 个 MCP 目录逐一列出的检索结果（来源、检索关键词、命中数、命中项目、URL）
- 8 个来源：modelcontextprotocol/servers、awesome-mcp-servers、smithery.ai、glama.ai/mcp、pulsemcp.com、mcp.so、lobehub.com/mcp、mcpmarket.com

**4.5 IDE 插件集成**：
- IDE 插件集成（Cursor/Cline/Continue/Copilot）单独列表

**4.6 反向证据**：
- 未发现的集成给出反向证据 + 检索 URL（含 LangChain Hub、LlamaIndex Hub、Anthropic Skills 仓库）

### 五、学术研究（含优先级排序）

论文总览表必含列（按此顺序）：
**优先级★ | 论文标题（含 arXiv 超链接） | 3 句话摘要 | 核心贡献（≤30字） | 作者+机构 | 发布时间 | 论文状态 | 代码 | 价值打分**

- 论文标题必须**完整**（不允许缩写）
- 标题超链接**优先 arXiv**，DOI 作为副链接放备注列
- **3 句话摘要为强制列**：① 问题/动机 ② 方法/创新 ③ 结果/数据
- 高相关论文（★★★★以上）单独详解段，再展开 3 句话摘要为完整段落
- 检索关键词记录（含未命中关键词）必须保留

### 六、接入难度分析
- 综合评分（1–5 ★）
- 6–10 个维度逐项打分
- 关键痛点列表
- 风险与缓解措施表

### 七、快速接入路径建议
- 2–3 条技术路径（含架构图、周期估算、现成参考）
- 路径对比表

### 八、验收自检清单

### 九、推荐优先级总排序
- 第一梯队（立即可用，1–3 天）
- 第二梯队（需适配，1–2 周）
- 第三梯队（长期布局，2–4 周+）

### 十、总结

---

## 阶段二：增强审核

初稿完成后，对每份报告执行以下增强。增强代理**直接修改原文件**，不创建新文件。增强前先备份。

### 增强维度零：通用格式规范（所有表格强制）

**0.1 标题自带超链接，禁止"标题列+链接列"分离**

❌ 错误示范（论文/项目/MCP/Skill 等所有表格通用，禁止 4 列分离）：

```
| 标题 | 作者 | 链接 | 仓库 |
|---|---|---|---|
| GENIUS | KIT | https://... | https://... |
```

✅ 正确示范（标题/项目名直接是 markdown 链接，论文同时附 arXiv 与 GitHub）：

```
| 优先级 | 论文标题 | 作者 | 代码 |
|---|---|---|---|
| ★★★★★ | [GENIUS: an agentic AI framework for autonomous design and execution of simulation protocols](https://arxiv.org/abs/2512.06404) | Soleymanibrojeni et al. | [GitHub](https://github.com/KIT-Workflows/agentic-workflow-framework) |
```

**0.2 论文标题必须完整，不允许缩写**

- 表格中论文一律使用**完整标题**（与发表/预印本一致），副标题用冒号分隔保留
- "GENIUS"、"VASPilot"、"DREAMS" 等只是项目代号，不能作为论文表的标题字段；可放在"作者/项目名"附注里
- ✅ "Towards the Autonomous Optimization of Urban Logistics: Training Generative AI with Scientific Tools via Agentic Digital Twins and Model Context Protocol"
- ❌ "Xu 2025 — AnyLogic+MCP+LLM"

**0.3 论文链接优先级：arXiv > DOI > 出版商页面**

- 同一论文同时有 arXiv 和 DOI 时，标题超链接**统一指向 arXiv**（无墙、稳定、可下载 PDF）
- DOI/期刊页面作为副链接放在备注列
- 仅有 DOI 无 arXiv 时才使用 DOI 链接

### 增强维度一：论文字段增强

每篇论文必须在论文表中包含以下字段（按列顺序）：

| 列名 | 要求 | 示例 |
|---|---|---|
| **优先级** | ★ × 1–5 | ★★★★★ |
| **论文标题（含超链接）** | 完整标题，超链接 arXiv 优先 | `[完整标题](https://arxiv.org/abs/...)` |
| **3 句话摘要** | 必须 3 句：① 问题/动机 ② 方法/创新 ③ 结果/数据。**严禁省略为单句**，每句独立信息量 | 见下方示例 |
| **核心贡献（一句话，≤30字）** | 最关键贡献，不是方法描述 | "首次将 MCP 协议用于 DFT 仿真编排" |
| **作者+机构** | 第一作者 + 所属大学/实验室全称 | Soleymanibrojeni et al., KIT |
| **发布时间** | 精确到月份；arXiv 用提交日期，期刊用录用日期 | 2025-12 (arXiv) / 2026-01 (Nature) |
| **论文状态** | 预印本 / 已录用 / 已发表（期刊名+卷期） / 博士论文 / 会议报告 | 已发表（Nature Comms Materials, 7:115） |
| **代码** | GitHub 链接或"否" | `[GitHub](https://...)` 或 否 |
| **价值打分** | 对该软件 Agent 化/Skill 化的参考价值 ★ × 1–5 | ★★★★★ = 核心引用 / ★☆☆☆☆ = 边缘参考 |

**3 句话摘要示范**：
> ① 当前 LLM 直接生成 Quantum ESPRESSO 输入文件零样本成功率仅 14.2%，参数复杂且依赖专家经验。② 作者构建 247 节点 + 330 边的 QE 知识图谱，配合分层 LLM（Mixtral → Claude 3.5）和有限状态自动机错误恢复机制。③ 在 295 个多样化提示上达到 ~80% 成功率，76.3% 的失败可被自动恢复，推理成本相比纯强模型方案减半。

### 增强维度二：MCP/接口/Skill 通用字段——**调用方式（耦合度）**

**这是最关键的新增字段。不允许把"生成输入文件的工具"和"能驱动软件运行的工具"混在一张表里不区分。**

每个接口/MCP Server/Skill/Agent 项目都必须打上以下四档之一：

| 耦合度档位 | 标记 | 含义 | 示例 |
|---|---|---|---|
| **A 直接驱动执行** | 🟢 **DRIVE** | 可远程驱动软件运行（start/step/stop/get_results），全链路闭环 | AnyLogic Cloud Python Client、Alpyne、AiiDA + aiida-quantumespresso |
| **B 仅生成输入** | 🟡 **GEN-IN** | 只能生成软件输入文件/参数，需用户自行运行软件 | umbaman/anylogicPLE-mcp（生成 .alp 后需用户用 PLE 打开）、Goldilocks（生成 QE 输入） |
| **C 仅解析输出** | 🟠 **PARSE-OUT** | 只能解析软件已产生的输出文件，不参与运行 | qeschema、PyProcar、pymatgen.io.pwscf.PWOutput |
| **D 周边/元数据** | ⚪ **PERIPHERAL** | 与软件相关的数据库/资源/工具链，与软件二进制本身无直接交互 | Materials Project MCP、OPTIMADE MCP、AnyLogic 客户列表查询 |

**强制要求**：
- MCP Server 表：第二列固定为"调用方式"
- 接口表：第二列固定为"调用方式"
- 总览表的 "MCP" 字段必须按耦合度分组写，例如："2 个 MCP Server（1 🟢DRIVE：xxx；1 🟡GEN-IN：yyy）"
- 同一项目同时具备多档能力时，列出主档并用 `+` 标注次档（如 🟢DRIVE+🟠PARSE-OUT）

### 增强维度三：MCP Server 详细字段

对每个 MCP Server，除耦合度外还需：

| 字段 | 要求 |
|---|---|
| **维护状态** | 🟢活跃（最后 commit ≤3 月）/ 🟡低维护（3-12 月）/ 🔴已废弃（>12 月或 archived），**标注最后 commit 日期** |
| **MCP Tool 函数清单** | 完整列出所有 tool 函数名，按类别分组（I/O、构建、运行、检查、模板等）。如无法从文档获取全部，标注"推断"。**直接看出该 MCP 能做什么、不能做什么** |
| **是否嵌套/依赖其他 MCP** | 该 MCP 是否内部调用其他 MCP？列出依赖。无依赖写"独立，无嵌套" |
| **底层调用方式** | 通过 REST API / subprocess / Python SDK / 文件读写 / 其他。配合耦合度字段说明"如何"实现该耦合 |

### 增强维度四：Skill / Agent 项目详细字段

对每个 Skill 或 Agent 项目，除耦合度外还需：

| 字段 | 要求 |
|---|---|
| **能力类型** | **参考书型**（提供知识/模板/教程，告诉 Agent "怎么做"，不带工具）/ **工具调用型**（封装 API/CLI 让 Agent "能做"）/ **混合型** |
| **输入/输出类型** | 明确数据流：输入（自然语言/文件路径/参数 JSON），输出（代码/数据表格/图表/报告/.alp 文件等） |
| **是否依赖其他 MCP 或 Skill** | 完整依赖链（如 Skill → MCP → pyNetLogo → NetLogo 二进制） |

### 增强维度五：审核与修复

- 修复所有 `> ` blockquote 前缀出现在表格前的情况（阻断 Markdown 表格渲染）
- 修复表格分隔符列数与表头列数不一致
- **审查所有"标题列+链接列"分离的表格，合并为标题自带超链接**
- **审查所有论文标题缩写，替换为完整标题**
- **审查所有论文链接，arXiv 优先（同时有 arXiv 与 DOI 时用 arXiv）**
- **审查所有 MCP/接口/Skill/Agent 项目，必须打上耦合度档位**
- **审查所有论文必须有 3 句话摘要**（不允许只有一句）
- 检查所有 URL 格式有效
- 检查所有"未找到"条目是否附有检索来源说明
- 交叉验证关键事实（License、版本号、MCP 特性）≥2 个独立来源
- 修正明显的事实错误

---

## 阶段三：MCP / Skill 可用性深度复核

阶段二完成后，对报告中调研到的**每一个 MCP Server 和每一个 Skill**逐项做一次源码级"可用性深度复核"，回答四个核心问题，然后把复核结果**追加到该软件报告的末尾**（不创建独立新文件——独立的跨软件汇总表 `MCP复核汇总表.md` / `Skill复核汇总表.md` 另行维护，与本节互不冲突）。

### 阶段三要回答的四个核心问题

1. **相关性**：这个 MCP/Skill 是**专为该仿真软件做的**，还是**通用工具恰好其中某个功能可以参与到仿真流程**里？（决定能不能计为"该软件专用"）
2. **工具数量 / 来源 / 备注**：实际注册多少个 tool（源码计数）？来源性质（官方/学术/第三方/社区，License）？关键备注（已归档、stars、口径修正等）。
3. **闭环执行能力**：能**提交自动仿真执行**（start→run→get_results 闭环），还是**只能生成分析输入**、**只能解析输出**？
4. **执行依靠谁**：执行环节由 **MCP/Skill 自身**完成、还是依靠**人工**手动运行软件、还是依靠**其他工具**（HPC/Slurm、其他 MCP、本地二进制、Cloud API）提交？

### 复核判定口径（复用阶段二四档 + 映射）

阶段三**复用阶段二的四档耦合度**作为相关性主轴，并映射到复核口径表述，保证前后一致、可交叉验证：

| 阶段二耦合度 | 阶段三相关性口径 | 含义 | 闭环执行能力 | 执行依靠 |
|---|---|---|---|---|
| 🟢 **DRIVE** | **直接控制** | MCP/Skill 实际调用目标软件本体 / 目标软件 Cloud API / Python 接口，或提交目标软件计算任务 | **可提交自动执行**（全闭环或有条件闭环） | 自身驱动；可能再委托 HPC/Slurm/Cloud |
| 🟡 **GEN-IN** | **文件格式级 / 仅生成输入** | 生成、读取或修改目标软件兼容文件/参数，但**不启动或控制软件本体** | **仅生成输入**，不提交 | **依靠人工**在软件中打开运行，或委托其他工具 |
| 🟠 **PARSE-OUT** | **仅解析输出** | 只解析目标软件已产生的输出文件，不参与运行 | **仅解析输出** | 运行环节由人工/其他工具先完成 |
| ⚪ **PERIPHERAL** | **通用/周边 / 领域辅助** | 能力可参与仿真流程，但**并非针对该软件实现**（数据库检索、k-point 推荐、结构查询等），不应计为该软件专用 | 不驱动软件本体 | 不涉及软件执行 |

> 注意：阶段三必须显式回答"是否软件专用"。⚪PERIPHERAL 与"恰好能参与的通用工具"= **不计为该软件专用 MCP/Skill**，必须在复核结论里点明（如"应归为通用仿真 MCP，含 1 个该软件转换工具，不能称为完整 XXX MCP"）。

### 工具数 / 执行能力——硬事实核验强度（强制 git clone）

工具数量、闭环执行能力属于**硬事实，禁止沿用旧报告的推断值**。核验顺序与阶段一 fallback 一致，但**计数与执行判定必须落到源码**：

1. **工具数量**必须按**当前 GitHub 仓库实际注册的 MCP tools / Skill 步骤**计数，标注**核验等级**：
   - **源码确认**：已 `git clone --depth 1` 后用 Grep 数 `@mcp.tool` / `@tool` / `server.add_tool` / `tools=[...]` 注册点（注明主入口文件名，如 `fastmcp_anylogic_server_v2.py`）
   - **文档确认**：仓库 README 明确列出且与版本一致
   - **报告记录**：本轮未取得完整源码或原报告未给可核验仓库（必须标注为"待调研/口径不一致"，不得当作确定值）
2. **闭环执行能力**必须看源码判定，**不能从 README 猜**：
   - MCP：看 `tools/` 目录、`server.py`、`@tool` 装饰器函数体——是 `subprocess.run([binary, ...])` / REST 调用 Cloud API / 提交 Slurm（=可执行），还是只 `open(file, 'w')` 写输入文件（=仅生成）
   - Skill：看 `SKILL.md` 是否声明 `allowed-tools: Bash` 并在正文给出 `$LMP -in input.lmp` / `mpirun pw.x` 这类真实运行命令（=可执行），还是明确写"不提交 jobs / 需交给提交 Skill"（=仅生成）
3. **一个项目被多个 MCP 目录收录时，不能重复计数**——按唯一 GitHub 仓库去重。
4. 结论引用具体文件路径与行号（`<repo>/path/file.ext:LN`）。

### 阶段三交付物：追加到报告末尾的固定结构

在该软件报告末尾追加一节，标题统一为 **`## 附录：MCP / Skill 可用性深度复核（阶段三）`**，含三张表 + 修正记录：

**附录头部**写明：复核日期、核验等级说明（源码确认/文档确认/报告记录）。

**A. MCP 可用性复核表**必含列（按此顺序）：

| 列 | 要求 |
|---|---|
| **MCP / 项目（含 GitHub 超链接）** | 项目名直接是 markdown 链接 |
| **与软件本体关系** | 直接控制🟢 / 文件格式级🟡 / 仅解析输出🟠 / 通用周边⚪（映射阶段二耦合度，须一致） |
| **是否软件专用** | 是 / 否（通用工具恰好可参与，不计专用） |
| **工具数（核验等级）** | 如 `8（源码确认）` / `2（文档确认）` / `约21（报告记录，口径不一致）` |
| **来源性质** | 官方 / 学术 / 第三方 / 社区 + License（如 第三方 GitHub，MIT；已归档） |
| **可否提交自动执行** | 可提交执行 / 仅生成输入 / 仅解析输出 / 不驱动本体 |
| **执行依靠** | 自身（subprocess/REST/SDK） / 人工运行软件 / 其他工具（HPC/Slurm/其他 MCP/Cloud） |
| **底层调用方式** | REST API / subprocess / Python SDK / 文件读写 |
| **复核结论 / 备注** | 一句话结论 + 关键修正（如"原报告记 12 tools，当前源码 23 tools"） |

**B. Skill 可用性复核表**必含列（按此顺序）：

| 列 | 要求 |
|---|---|
| **Skill / 资源（含仓库超链接）** | 名称直接是 markdown 链接 |
| **当前类型** | 正式 Skill（有 `SKILL.md`）/ Skill 化候选 / 非 Skill |
| **是否官方推出** | 软件官方 / 非官方（学术/个人/社区/第三方公司即使质量高也标非官方） |
| **与软件本体关系** | 直接相关🟢 / 文件格式级🟡 / 领域辅助⚪（映射耦合度） |
| **是否软件专用** | 是 / 否 |
| **执行能力** | 可执行/可提交 / 仅生成输入工作流 / 仅知识模板 / 候选 |
| **执行依靠** | 自身调用 Bash/二进制/HPC / 人工 / 其他工具或 MCP |
| **是否依赖其他 MCP** | 是（列出）/ 否（仅统计 MCP Server/Tool 层依赖；普通 Python/CLI/HPC/API 不算） |
| **输入 → 输出** | 输入类型 → 输出类型 |
| **复核结论 / 备注** | 一句话结论 |

> **⚠️ 重要：Skill 的严格定义（与阶段一交付物开头定义一致，此处重申以供复核）**
>
> **Skill 是指带有 `SKILL.md` 文件的、可被 Claude Code 直接加载的技能定义**。以下类型**不是 Skill**，不应出现在 B 表中：
>
> | 类型 | 示例 | 应记录位置 |
> |---|---|---|
> | **SDK / Library** | Alpyne (Python SDK)、pyNetLogo | 阶段一 → 三、接口清单 |
> | **软件扩展原语** | NetLogoGptExtension（NetLogo 内部扩展） | 阶段一 → 4.2 LLM 扩展/Agent 项目表 |
> | **研究配套代码** | swarm_gpt（.nlogo 模型文件） | 阶段一 → 4.2 LLM 扩展/Agent 项目表 |
> | **MCP Server** | NetLogo-MCP、anylogic-mcp-server | 阶段三 → A. MCP 可用性复核表 |
>
> **如果阶段一二明确报告"未发现任何 Skill"，则阶段三 B 表应为空**，写明：
> ```
> **已检索 N 个来源，未发现任何 [软件名] 专用 Skill**：
>
> | 来源 | 检索结果 |
> |---|---|
> | Anthropic Skills / Claude Skills | ❌ 未发现 |
> | LangChain Hub | ❌ 未发现 |
> | LlamaIndex Hub | ❌ 未发现 |
> | GitHub 搜索 | ❌ 未发现带有 SKILL.md 的项目 |
> ```
>
> **禁止将 SDK/库/扩展原语/研究代码错误地填入 B 表**。

**C. 软件级复核结论表**（收口）：

| 列 |
|---|
| **可计为直接控制软件/平台的 MCP/Skill** |
| **文件格式级 / 局部辅助 MCP/Skill** |
| **不应计为该软件专用的（通用/周边）** |
| **自动执行能力总判断**（哪些可提交执行、哪些仅生成、执行靠什么） |

**D. 主要修正记录表**（对比阶段一/二原表述）：

| 原报告表述 | 复核后修正 |
|---|---|

### 子代理 Prompt 模板（阶段三）

```
请对 **[软件名]** 报告（[报告文件路径]）中**已列出的每个 MCP Server 和每个 Skill** 做一次"可用性深度复核"。
对每一项，逐一回答并填表：

1. 相关性：是 [软件名] 专用，还是通用工具的某个功能恰好能参与 [软件名] 流程？
   映射阶段二耦合度四档：🟢DRIVE 直接控制 / 🟡GEN-IN 文件格式级·仅生成输入 /
   🟠PARSE-OUT 仅解析输出 / ⚪PERIPHERAL 通用周边·不计专用。
2. 工具数量 / 来源 / 备注：实际注册多少 tool？来源性质 + License？关键备注？
3. 闭环执行：能提交自动仿真执行，还是只生成输入 / 只解析输出？
4. 执行依靠：自身（subprocess/REST/SDK）、人工运行软件、还是其他工具（HPC/Slurm/其他 MCP/Cloud）？

**硬事实核验强度（强制，禁止沿用旧报告推断值）**：
- 工具数量必须 `git clone --depth 1 <repo> $CLAUDE_JOB_DIR/tmp/<repo>` 后用 Grep 数
  `@mcp.tool`/`@tool`/`add_tool`/`tools=[...]` 注册点，标注"源码确认/文档确认/报告记录"，注明主入口文件。
- 闭环执行能力必须看源码：subprocess 调二进制 / REST 调 Cloud / 提交 Slurm = 可执行；
  只 open(file,'w') 写输入 = 仅生成；Skill 看是否声明 allowed-tools: Bash 且给出真实运行命令。
- 一个项目被多个 MCP 目录收录，按唯一 GitHub 仓库去重，不重复计数。
- 结论引用具体文件路径与行号（<repo>/path/file.ext:LN）。

WebFetch 失败时升级 GitHub API + raw.githubusercontent.com；仍不够判定时必须 git clone 读源码。

输出 4 张表，结构见 SKILL「阶段三交付物」：
A. MCP 可用性复核表  B. Skill 可用性复核表  C. 软件级复核结论表  D. 主要修正记录表
全部用「项目名（带超链接）」列，禁止"名称列+链接列"分离。
```

### 阶段三交付动作（强制）

- 复核结果以 `## 附录：MCP / Skill 可用性深度复核（阶段三）` 为标题，**追加（append）到该软件报告文件末尾**，不新建文件、不覆盖正文。
- 追加前先备份报告文件。
- 若某软件报告中 MCP / Skill 均为"未发现"，附录仍要写明"已检索 N 个来源未发现可计为该软件专用的 MCP/Skill"，并列出反向证据来源。

---

## 优先级排序规则

所有列表（接口、MCP、Agent 项目、Skill、论文）必须按以下维度打分排序，不能平铺：

### 接口/MCP/Agent 权重（Python 优先导向）

```
总分 = Python原生(+3) + 功能完整(+2) + 活跃维护(+2) + 使用人数(+1) + 有文档(+1) + 可跑通(+1)
```

### Skill 权重

```
总分 = 正式Skill有SKILL.md(+3) + 工具调用型(+2) + 活跃维护(+2) + 可执行闭环(+2) + 使用人数(+1) + 有文档(+1)
```

> 参考书型 Skill 无 `+2` 工具调用加分；Skill 化候选无 `+3` 正式 Skill 加分。

### 论文权重

```
总分 = 直接相关(+3) + 开源代码(+2) + 顶会(+2) + 近3年(+1) + 方法可复现(+1)
```

---

## 子代理 Prompt 模板

### Agent-A：官网/文档/接口侦察

```
请对 **[软件名]** 仿真软件的**官方文档与接口情况**进行很彻底的全网搜索调研。

必须查证并给出 URL：
1. 基本面：开发方、用途、典型用户、最新版本号与发布日期
2. License：开源/闭源、具体协议、商业使用限制、付费版本
3. 可被程序调用的接口清单（逐一列出，附官方文档链接）
4. CLI 命令能力
5. Web 版 API 情况（如有）
6. 最新版本新特性（特别是与 AI/LLM 相关的）

输出结构化 markdown，所有结论带 URL。未找到写"已检索xxx未找到"，禁止留空。
```

### Agent-B：GitHub/Agent 生态侦察

```
请对 **[软件名]** 与 LLM Agent 的现有集成生态进行很彻底的全网搜索调研。

必须扫描：
1. GitHub 全网搜索 MCP、LLM、GPT、Claude、Agent、LangChain
2. MCP 服务器目录（8 个来源逐一检查）
3. Anthropic Skills / Claude Skills
4. LangChain Hub / LlamaIndex Hub
5. Cursor/Cline/Continue/Copilot IDE 插件
6. 官方仓库 issues/PR 中的 AI/LLM 关键词
7. 社区论坛中 LLM/AI 相关讨论

每个项目必须记录以下字段（缺一不可）：
- 仓库 URL、Stars、License、最近 commit 日期、维护状态
- **调用方式（耦合度档位）**——必须明确判断并标注四档之一：
  - 🟢 DRIVE：可远程驱动软件运行（start/step/stop/get_results）
  - 🟡 GEN-IN：仅生成软件输入文件/参数，需用户手动运行软件
  - 🟠 PARSE-OUT：仅解析软件已产生的输出文件，不参与运行
  - ⚪ PERIPHERAL：周边/元数据/数据库，与软件二进制无直接交互
- **Tool 函数清单**（MCP）或 **能力类型**（Skill：参考书型/工具调用型/混合型）
- **底层调用方式**：REST API / subprocess / Python SDK / 文件读写
- **依赖链**：是否依赖其他 MCP/Skill/Python 库/软件

**数据获取 fallback（强制）**：
WebFetch 失败时升级到 GitHub API + raw.githubusercontent.com 拉元数据和 README；
仍不够判断耦合度/Tool 清单/许可证时，必须 `git clone --depth 1 <repo> $CLAUDE_JOB_DIR/tmp/<repo>` 后用 Read/Grep 阅读源码。
特别是判断 🟢DRIVE vs 🟡GEN-IN 时从 README 通常看不出来，必须看 `tools/`、`server.py`、`@tool` 装饰器或主入口的子进程调用代码。
结论引用具体文件路径与行号（`<repo>/path/file.ext:LN`），不只是仓库根 URL。

**⚡ 性能策略（强制，不可省略）**：
- **GitHub 仓库**：一律用 `curl` GitHub API + raw（P1 规则），**禁止 WebFetch 仓库页**
- **8 个 MCP 目录**：先 WebSearch `"[软件名] MCP" site:<domain>` 筛，**只 Fetch 有命中的**（P2 规则），0 命中的目录直接记"已检索，0 命中"
- **PyPI 包**：用 `curl -sL https://pypi.org/pypi/<pkg>/json`，不 Fetch HTML

**输出结构（三张表分开，不可混填）**：
1. **4.1 MCP Server 表**：所有 MCP Server 项目，含 Tool 函数清单列
2. **4.2 LLM 扩展 / Agent 项目表**：Agent 框架、LLM 集成项目、LLM 扩展
3. **4.3 Skill 项目表**：**仅**填入带有 `SKILL.md` 的项目（Skill 定义见阶段一交付物开头）；无 SKILL.md 但有 Skill 潜力的项目标为"Skill 化候选"并说明理由；若无任何 Skill，写明"已检索 N 个来源未发现带有 SKILL.md 的项目"

同一项目同时出现在多个表中时，在所属主表完整记录，另一表仅保留一行交叉引用（"详见 4.x"）。

输出表格必须用"项目名（带超链接）"列，禁止"名称列+链接列"分离。
未找到的写"已检索 N 个来源未发现"，作为反向证据。
```

### Agent-C：学术论文侦察

```
请对 **[软件名] + LLM / Agent / Code Generation / Tool Use** 进行学术论文搜索。

搜索源：arXiv、Google Scholar、Semantic Scholar、ACM DL、IEEE Xplore、SpringerLink

关键词组合（每组合都搜）：
- "[软件名]" + "LLM" / "Large Language Model"
- "[软件名]" + "GPT" / "ChatGPT" / "GPT-4" / "Claude"
- "[软件名]" + "code generation"
- "[软件名]" + "Agent" + "LLM"
- "[软件名]" + "MCP" / "Model Context Protocol"
- "[软件名]" + "natural language" + "generation"

时间范围：2022–2026。每篇必须记录以下字段（缺一不可）：

1. **完整论文标题**（与 arXiv/期刊一致，禁止缩写、禁止用项目代号代替标题）
2. **作者**（第一作者 + 等）
3. **第一作者所属机构**（大学/实验室全称）
4. **发布时间**（精确到月份；arXiv 用提交月份，期刊用录用月份）
5. **论文状态**：预印本(arXiv ID) / 已录用 / 已发表（期刊名+卷期）/ 博士论文 / 会议报告
6. **链接**：arXiv 链接（必有则优先）+ DOI/期刊链接（如有）。同时存在时 arXiv 优先作为主链接
7. **3 句话摘要**（强制 3 句，缺一不可，每句独立信息）：
   - 第 1 句：问题或动机（这篇论文为什么要做这件事？现状有什么问题？）
   - 第 2 句：方法或创新（具体怎么做？关键技术或架构是什么？）
   - 第 3 句：结果或数据（达到什么效果？关键数字、benchmark 分数、对比基线）
8. **核心贡献（一句话，≤30字）**：最关键的贡献，不是方法描述
9. **是否开源**：GitHub 链接 / 否
10. **相关度**：高/中/低（直接涉及软件名+LLM/Agent 为高）
11. **价值打分（★1-5）**：对该软件 Agent 化/Skill 化的参考价值

至少找 5 篇高相关。未命中的关键词也要记录（哪些关键词搜索返回 0 结果）。

**⚡ 性能策略（P3 规则）**：
- arXiv abs 页一次 Fetch 已包含完整摘要、作者、提交日期、DOI，**不再二次搜 Google Scholar / Semantic Scholar 确认**
- 仅当需确认"是否已被顶会/期刊正式录用"且 arXiv 页未标注时，才用 WebSearch 快速确认
- GitHub 仓库（论文配套代码）一律走 API + raw，不 Fetch 仓库页

输出表格中"论文标题"列直接为 markdown 链接（链接到 arXiv 优先），禁止"标题列+链接列"分离。
```

### Agent-D：实操可行性侦察

```
请对 **[软件名]** 的实操可行性（从零做 MCP Server/Skill 的工程难度）进行搜索调研。

查证：
1. Docker 镜像情况
2. PyPI / Conda / Maven / npm 可用性
3. Python 控制方案对比（这是关键路径）
4. Headless 模式能力
5. 状态管理（session 保持、启动开销、checkpoint）
6. 可视化回传
7. 典型工程痛点（GitHub issue/Stack Overflow/博客）

**数据获取 fallback（强制）**：
WebFetch 抓官方文档/教程页失败时改用 GitHub API + raw.githubusercontent.com 取 README/示例代码；
评估"Python 控制方案"时如官方文档不清晰，必须 `git clone --depth 1` 关键 Python 封装库（如 ASE、AiiDA 插件、Alpyne）到 $CLAUDE_JOB_DIR/tmp 后用 Read/Grep 阅读 calculator.py / runner.py / __init__.py 类源码，确认它是否真能驱动软件运行（subprocess/socket/REST），还是只读写输入输出文件。
结论引用具体文件路径与行号。

**⚡ 性能策略**：
- PyPI 包信息：`curl -sL https://pypi.org/pypi/<pkg>/json`（≈ 1s），不 Fetch pypi.org HTML 页
- Docker Hub：`curl -sL https://hub.docker.com/v2/repositories/<org>/<image>`（≈ 1s），不 Fetch 页面
- GitHub 仓库一律走 API + raw（P1 规则）

每条结论带 URL。最后给出"最优技术路径是什么？为什么？"
```

---

## 接入难度评分标准

| 星级 | 判据 | 示例 |
|---|---|---|
| ★ 极易 | 已有官方/高星 MCP；或有稳定 REST API + 完善 Python SDK | ANSYS PyAnsys、Gazebo + ROS2 |
| ★★ 容易 | 有 Python API 或脚本接口，headless 可用，文档全 | NetLogo + pyNetLogo |
| ★★★ 中等 | 仅 CLI 或 COM/IPC，需自行封装；License 闭源但可批量调用 | Simulink + MATLAB Engine |
| ★★★★ 较难 | GUI-only / 需 license server / 状态机复杂 / 长任务难中断 | AnyLogic（闭源+Java only） |
| ★★★★★ 极难 | 无公开接口、强加密 dongle、Windows-only GUI 自动化 | 老旧工业仿真软件 |

---

## 质量标准

### 阶段一合格标准

- [ ] 总览表 9 个字段全部有内容（无内容写"无"或"未公开"，**禁止留空**）
- [ ] 接口字段至少列出 1 种，并附**官方文档 URL**
- [ ] MCP 字段：找到的写仓库名+stars+最近 commit；找不到要写"已检索 xxx 来源未发现"
- [ ] **Skill 字段**：找到的写项目名+当前类型（正式 Skill / Skill 化候选）+耦合度；找不到要写"已检索 N 个来源未发现带有 SKILL.md 的项目"
- [ ] 论文字段：≥5 篇，每篇有 DOI 或 arXiv 链接
- [ ] **4.4 MCP 目录检索清单**：8 个 MCP 公共目录逐一列出检索结果（命中数+命中项目）
- [ ] **4.6 反向证据**：LangChain Hub / LlamaIndex Hub / Anthropic Skills 仓库 的检索结果已记录
- [ ] 接入难度有理由说明，不是孤立打分
- [ ] 关键事实交叉验证：License、接口可用性等硬事实需 ≥2 个独立来源
- [ ] 所有外部声明带 URL（不接受"据说"/"听说"）
- [ ] 所有列表（接口、MCP、Skill、论文）按优先级排序，不是平铺

### 阶段二增强合格标准

**格式合规**
- [ ] **所有表格的项目名/论文标题/MCP 名直接是 markdown 超链接**——零容忍"标题列+链接列"分离
- [ ] **所有论文标题完整**（与 arXiv/期刊一致），禁止用项目代号代替标题
- [ ] **所有论文链接 arXiv 优先**（同时有 arXiv 与 DOI 时主链接指向 arXiv，DOI 放备注）
- [ ] 无不正确渲染的表格（无 `> ` blockquote 在表格前、无列数不一致）
- [ ] 所有 URL 有效

**论文字段**
- [ ] 每篇论文有：完整标题 + **3 句话摘要（① 问题 ② 方法 ③ 结果，三句独立信息）** + 核心贡献（≤30字） + 发布时间（精确月） + 第一作者机构 + 价值打分★ + 论文状态 + 是否开源
- [ ] 高相关论文（★★★★以上）单独详解段，3 句话摘要展开为完整段落

**调用方式（耦合度）合规**
- [ ] **每个接口/MCP/Skill/Agent 项目都打上四档之一**：🟢DRIVE / 🟡GEN-IN / 🟠PARSE-OUT / ⚪PERIPHERAL
- [ ] 总览表的接口/Skill/MCP 字段按耦合度分组写明
- [ ] 同一表格内不允许把"驱动执行"和"仅生成输入"项目混在不区分

**MCP 字段**
- [ ] 每个 MCP 有：调用方式 + 维护状态🟢🟡🔴（含最后 commit 日期） + Tool 函数清单（按类别分组） + 是否嵌套依赖 + 底层调用方式

**Skill 字段**
- [ ] 每个 Skill/准 Skill 有：调用方式 + 能力类型（参考书型/工具调用型/混合型） + 输入→输出类型 + 完整依赖链

**事实合规**
- [ ] 所有"未找到"有检索来源 URL
- [ ] 关键事实 ≥2 个独立来源交叉验证

### 阶段三可用性复核合格标准

**覆盖度**
- [ ] 报告中**每一个** MCP 和**每一个** Skill 都进入复核表，无遗漏
- [ ] 复核结果以 `## 附录：MCP / Skill 可用性深度复核（阶段三）` **追加到报告末尾**，未覆盖正文

**四个核心问题逐项回答**
- [ ] **相关性**：每项标明"是否软件专用"，区分"专用"与"通用工具恰好可参与"
- [ ] **工具数量**：源码确认计数（标注核验等级 + 主入口文件），禁止沿用旧报告推断值
- [ ] **来源 / 备注**：来源性质 + License + 关键修正备注齐全
- [ ] **闭环执行**：明确"可提交自动执行 / 仅生成输入 / 仅解析输出"之一
- [ ] **执行依靠**：明确"自身 / 人工 / 其他工具（HPC/MCP/Cloud）"

**一致性 / 可溯源**
- [ ] 相关性档位与阶段二耦合度（🟢🟡🟠⚪）映射一致，可交叉验证
- [ ] 硬事实（工具数、执行能力）结论引用具体文件路径与行号
- [ ] 同一仓库被多目录收录时去重，未重复计数
- [ ] 四张表齐全：A MCP 复核表 / B Skill 复核表 / C 软件级结论 / D 主要修正记录

---

## 模板参考

优化后的调研报告模板位于 `reference/` 目录：

| 软件 | 文件 | 领域 | 接入难度 | 阶段覆盖 |
|---|---|---|---|---|
| VASP | [reference/VASP_Agent生态调研报告.md](reference/VASP_Agent生态调研报告.md) | DFT/材料科学 | ★★★☆ | 阶段一 + 阶段二 + **阶段三附录** |

> VASP 报告是当前唯一完整覆盖三阶段流程的范本——正文为阶段一/二产物，末尾 `## 附录：MCP / Skill 可用性深度复核（阶段三）` 即阶段三标准产出，新软件调研应对齐此结构。
>
> 旧版报告（NetLogo / Vensim / Stella / LAMMPS / VASP legacy）已归档至 `reference/legacy/`，仅含阶段一/二、未做阶段三复核，仅保留供历史参考。

后续新软件调研应严格遵循以上报告的章节结构、优先级标注方式和验收清单。

---

## 持续迭代

- 新发现的 MCP/Agent 项目 → 更新对应软件报告
- 新软件调研 → 按此 Skill 三阶段流程执行（初稿 → 增强审核 → 可用性深度复核），报告追加到系列中
- 横向对比总览 → 所有单软件报告完成后合并；跨软件 MCP/Skill 复核可汇总到 `MCP复核汇总表.md` / `Skill复核汇总表.md`
- 增强审核 → 每批次新增报告后可对全系列执行阶段二增强
- 可用性复核 → 每份报告完成阶段二后执行阶段三，复核结果追加到该报告末尾附录
