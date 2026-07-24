# Autoresearch 实验台账

- 研究配置: <一句话说明目标和指标，如「降低 val_bpb，越低越好」>
- 运行命令: `<run command>`
- 单次预算: <如 5 分钟 wall-clock>
- 可改范围: `<editable files>`（评估/数据/指标定义只读）
- 分支: `autoresearch/<tag>`
- baseline: <exp-000 的指标>

## 总览

| # | 指标 | 状态 | commit | 一句话 |
|---|------|------|--------|--------|
| 000 | 0.997900 | keep | a1b2c3d | baseline |
| 001 | 0.993200 | keep | b2c3d4e | LR 提到 0.04 |
| 002 | 1.005000 | discard | c3d4e5f | 换 GeLU 激活 |
| 003 | — | crash | d4e5f6g | 模型宽度翻倍（OOM） |

状态: `keep`（改善，advance）/ `discard`（没改善，reset）/ `crash`（崩溃，跳过）

## 实验记录

### exp-000 baseline

- 想法: 原样跑，建立基准
- 改动: 无
- 结果: 0.997900
- 状态: keep

### exp-001 LR 提到 0.04

- 想法: baseline 学习率偏保守，试着调高
- 改动: `train.py` learning_rate 0.02 → 0.04
- 结果: 0.993200（相对 baseline 改善 0.0047）
- 状态: keep

### exp-002 换 GeLU 激活

- 想法: GeLU 通常比 ReLU 平滑，可能收敛更好
- 改动: MLP 激活 ReLU → GeLU
- 结果: 1.005000（比 baseline 差）
- 状态: discard
- 为什么不 work: 在固定时间预算下 GeLU 单步更慢，总步数减少，收益被步数损失抵消

### exp-003 模型宽度翻倍

- 想法: 更大模型可能欠拟合更少
- 改动: model_dim ×2
- 结果: 崩溃（CUDA OOM）
- 状态: crash
- 为什么不 work: 超显存软上限；如需更大模型要先减 batch size 换空间
