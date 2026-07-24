# karpathy/autoresearch 原版 program.md（参照范例）

来源: https://github.com/karpathy/autoresearch （2026-03）

这是本 skill 泛化的原始蓝本。原版把场景写死为「单 GPU 训练 nanochat、指标 val_bpb、固定 5 分钟预算、只改 train.py」。
本 skill 把这些写死的部分抽成 setup 阶段与用户敲定的「项目配置」，其余循环逻辑基本沿用。
需要还原 karpathy 的原始意图或对照细节时读本文件。

## 原版核心设计（四要素）

1. **固定时间预算** → 每次实验跑固定 wall-clock 时间，结果直接可比，不用担心训练时长。
2. **单文件可改范围** → agent 只改 `train.py`，`prepare.py`（数据/评估/常量）只读。diff 可审、scope 可控。
3. **Git 作为记忆** → 每个实验一个 commit，agent 读分支历史规划下一步；改进则 advance，退步则 reset。
4. **二元 keep/discard** → 指标改善就保留 commit，否则 git reset 回退，不需要人判断。

## 原版 Setup 步骤

1. 约定 run tag（如 `mar5`），分支 `autoresearch/<tag>` 必须不存在（全新 run）。
2. `git checkout -b autoresearch/<tag>` 从 master 拉出。
3. 读 in-scope 文件：README、prepare.py（只读）、train.py（可改）。
4. 确认数据存在。
5. 初始化 `results.tsv`，只有表头；baseline 在第一次跑后记录。
6. 确认无误后开始。

## 原版 results.tsv 格式

Tab 分隔，5 列：`commit  val_bpb  memory_gb  status  description`

```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

- status: `keep` / `discard` / `crash`
- 崩溃时指标填 0，status 填 crash
- results.tsv 保持 untracked（不 commit）

## 原版实验循环（LOOP FOREVER）

1. 看 git 状态（当前分支/commit）。
2. 直接改 train.py 试一个想法。
3. git commit。
4. 跑：`uv run train.py > run.log 2>&1`（重定向，别用 tee 灌爆 context）。
5. 读结果：`grep "^val_bpb:\|^peak_vram_mb:" run.log`。
6. grep 空 = 崩溃，`tail -n 50 run.log` 看栈，尝试修；修几次不行就放弃。
7. 记录到 tsv。
8. 指标改善（更低）→ advance，保留 commit。
9. 指标持平或更差 → git reset 回起点。

## 原版关键纪律

- **Simplicity criterion**: 同等效果下更简单更好。0.001 改善 + 20 行 hacky 代码 → 不值；0.001 改善 + 删代码 → 保留；改善约 0 但代码更简洁 → 保留。
- **Timeout**: 单次约预算时间 + 少量开销；超 2 倍预算就 kill，当失败回退。
- **Crashes**: typo/缺 import 这类小问题就修重跑；想法本身崩了就跳过标 crash。
- **First run**: 第一次必须原样跑 baseline，不改任何东西。
- **NEVER STOP**（原版）: 循环启动后不停下问人。人可能在睡觉，期望醒来看到一堆结果。没想法就想更狠的：读代码引用的论文、重读文件找新角度、组合之前的 near-miss、试更激进的架构改动。

本 skill 对 NEVER STOP 做了调整：见 SKILL.md「停止条件」一节。
