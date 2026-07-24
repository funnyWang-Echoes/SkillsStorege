---
name: autoresearch
description: 在当前项目里做自主实验研究循环——agent 反复提出改动、跑实验、读指标、keep/discard、advance/reset，直到预算耗尽或达标。泛化自 karpathy/autoresearch，把训练场景抽成可配置的「项目研究配置」，适用于任何有明确单一指标、可自动运行、可 git 版本化的优化任务（模型评测、仿真调参、算法/超参搜索、性能优化的多轮迭代）。触发词："autoresearch"、"自主研究"、"通宵跑实验"、"自动迭代优化"、"让 agent 自己一直试"、"过夜实验循环"。不用于单次性能优化（用 benchmark-optimization-loop）、没有自动化指标的探索性任务、需要人逐步决策的研究。
---

# Autoresearch：自主实验研究循环

把研究收缩成一个可无人值守的循环：**改一个想法 → commit → 跑 → 读指标 → 改善则 advance，否则 reset → 记录 → 继续**。
泛化自 [karpathy/autoresearch](https://github.com/karpathy/autoresearch)。原版把场景写死为训练 nanochat；本 skill 把写死部分抽成 setup 阶段敲定的「研究配置」。

## 何时用 / 不用

**用：** 有单一可自动测量的指标、单次运行可自动跑完、代码可 git 版本化、要跑很多轮（十几到上百次）自主迭代。典型：模型评测调参、MATLAB/仿真调参、超参/架构搜索、多轮性能优化。

**不用：**
- 单次或少数几次工程性能优化 → 用 `benchmark-optimization-loop`。
- 指标无法自动测量、每轮都要人看输出判断好坏 → 不适合自主循环。
- 需要人逐步做研究决策的开放探索 → 保持人在环。

## Setup：敲定研究配置（每个项目一次性）

和用户敲定下面这份**研究配置**并复述确认。它把原版写死的参数泛化为项目级配置，决定了结果能不能可比、能不能自主判断。有一项不清楚就问，不要自己假设。

1. **指标（metric）**：单一标量，方向明确。例：`val_bpb`（越低越好）、纯度%（越高越好）。写清从输出里抓它的命令（如 `grep`）。

2. **运行命令（run command）**：一条自动跑完并把结果重定向到日志的命令，如 `uv run train.py > run.log 2>&1`。用重定向而非 tee，避免输出灌爆 context。

3. **预算（budget）**：单次运行的固定预算，让结果可比。优先固定 wall-clock 时间；否则固定其他可比条件（数据量、迭代步数）。设 timeout：超预算 N 倍（默认 2）就 kill 当失败。

4. **可改范围（editable scope）**：列出 agent 能改和只读的文件。**评估/数据/指标定义只读**，否则会作弊或改口径。可改范围越窄，diff 越可审。

5. **约束（constraints）**：不装新依赖、资源软上限（如显存）等不可越界条件。

6. **run tag 与分支**：约定 tag（如 `mar5`），从一个不存在的分支开新 run：
   ```bash
   git checkout -b autoresearch/<tag>
   ```

7. **结果目录**：建 `results/` 存产物，把 `assets/log-template.md` 复制为 `results/log.md`，填好顶部研究配置、清空示例行。baseline 第一次跑后记录。

复述配置，用户确认后开始。

## LOOP：实验循环

确认配置后进入循环。**第一轮永远是 baseline：原样跑，不改任何东西，记录基准。**

```
LOOP:
  1. 看 git 状态：当前分支 / commit
  2. 想一个想法，直接改「可改范围」内的文件实现它（一次只改一个变量）
  3. git commit -m "experiment: <描述>"
  4. 跑 run command，输出重定向到日志
  5. 用抓取命令读指标：grep "^metric:" run.log
  6. grep 为空 = 崩溃：tail -n 50 run.log 看栈；typo/缺 import 修了重跑，想法本身崩了就跳过、标 crash、回退
  7. 把本轮产物存进 `results/exp-NNN-<一句词>/`，并向 `results/log.md` 追加总览表一行 + 详细记录一段
  8. 指标改善 → advance（保留 commit，从这里继续）
  9. 指标持平或更差 → git reset 回起点（丢弃这次改动）
```

### 结果与记录格式

**目录结构**：`results/` 下每个实验一个子目录，存该实验相关的产物（run.log、输出文件、配置快照等）；目录名带序号 + 一句词，如 `results/exp-001-lr-0.04/`。`results/log.md` 是总台账。

```
results/
├── log.md                    # 总台账：总览表 + 逐个实验详细记录
├── exp-000-baseline/
│   └── run.log
├── exp-001-lr-0.04/
│   └── run.log
├── research/                 # 没想法时的调研笔记，为新实验提供来源
│   └── 2026-03-05-muon-variants.md
└── ...
```

**`log.md` 格式**（样本见 `assets/log-template.md`）：顶部一张 Markdown 总览表做快速回看，下面接每个实验的详细记录。每跑完一轮追一行总览 + 一段详细。

- 总览表列：序号 / 指标 / 状态 / commit / 一句话
- 详细字段：想法、改动、结果、状态；discard 或 crash 的写上「为什么这个想法不 work」
- status：`keep`（改善，advance）/ `discard`（没改善，reset）/ `crash`（崩溃，跳过）；崩溃时指标栏填 `—`
- 每个实验一个 commit；crash/discard 的代码改动 reset 掉，`results/` 下的记录保留

### 纪律

- **一次只改一个变量**，否则无法归因。
- **Simplicity criterion**：同等效果下更简单更好。0.001 改善 + 20 行 hacky 代码 → 不值；0.001 改善 + 删代码 → 保留；改善约 0 但代码更简洁 → 保留。
- **口径不可变**：循环期间不改评估/数据/依赖；改了口径，之前结果作废。对比 baseline 前先确认口径对齐。
- **Timeout**：超预算 N 倍就 kill，当失败回退。
- **rewind 极少用**：advance 支持持续迭代；只有走进死胡同才 rewind。

### 没想法时

不停下来问人，先从现有材料挖：重读 in-scope 文件找没试过的维度、组合之前的 near-miss、试更激进的结构性改动。

现有材料耗尽时主动调研（用 `search` 或 `deep-research`）找新方向：相关论文、SOTA 做法、开源实现的 trick。把调研结论落盘到 `results/research/<日期>-<主题>.md`（如 `results/research/2026-03-05-muon-variants.md`），记下来源、可试的具体改动、与当前代码的差异。调研得出的想法进入 LOOP 后，在该实验的 `log.md` 记录里注明来源（哪篇调研/哪个来源），形成「调研 → 想法 → 实验」的可追溯链。

### 停止条件

原版是通宵无人值守、永不停。本 skill 保留「循环期间不逐轮问人、自主判断 keep/discard」，但在以下条件停止或产出小结：

- **达到预算 / 达标**：跑满约定轮次或指标达阈值，输出最终小结。
- **每 N 轮进度小结**（默认 N=10 或 1 小时，取先到）：输出当前 best、相对 baseline 改善、有效改动清单、下一步方向，然后继续，不等回复。
- **想法枯竭**：连续多轮无改善时输出小结、说明已试方向，交还给人。

用户明确说「通宵一直跑」时，按原版永不停，只在崩溃无法恢复或预算耗尽时停。

## 最终小结

循环结束时产出：baseline 指标、最终 best 指标及相对改善、保留下来的有效改动列表（附 commit hash 和描述）、观察到的规律、放弃或没试的方向。`results/log.md` 是完整实验轨迹。

## 参照

- 实验台账模板：`assets/log-template.md`（setup 时复制为 `results/log.md`）。
- 需要还原 karpathy 原版意图或对照写死场景的细节时，读 `references/karpathy-program-md.md`。
