---
id: C-20261002-183723
type: change
title: TEST07 TRANSFORM_TARGET 多目标聚合改为 ALL_CHANGED 并补 mutation
domain: 测试与价值判定
problems: [P-20261002-181318]
status: 已实施
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 机械验证通过；待 NEW CLEAN Claude Code 独立审计
calibrated: false
calibration_ref: 
process_captured: true
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-10-02
tags: [change]
---

# 🔵 TEST07 TRANSFORM_TARGET 多目标聚合改为 ALL_CHANGED 并补 mutation

> [!question] 一句话
> 将多目标 `TARGET_MUST_CHANGE` 从 ANY 聚合改为 ALL 聚合，并用四组合回归与反向 mutation 固定合同语义。

---

> [!danger] 改动
> **改前**：`bool(changed)`；任一 target 变化即 `POSITIVE`。
> **改后**：`len(changed) == len(targets)`；只有全部 target 变化才 `POSITIVE`。

---

## ✅ 怎么做

- [x] 复现 A变/B不变与 A不变/B变的 false positive。
- [x] 保留 `VALUE_EVIDENCE.TARGETS == ACTION_TARGETS` 集合完全一致门。
- [x] 新增四个最小回归。
- [x] 新增 ALL_CHANGED→ANY_CHANGED mutation。
- [x] 完整 suite 265/265 PASS；mutation 32/32 killed。
- [x] 冻结五项哈希并确认 live pollution=NO、source quiescent。
- [ ] NEW CLEAN Claude Code 独立只读审计。

---

> [!success] 预测
> 两条部分变化路径稳定派生 NEGATIVE；专用 mutant 只由这两条检查击杀。当前结论只到施工方机械验证，不自评为独立审计 PASS。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 合同正文已经明确 ALL 语义，根因仅是一条聚合表达式；修改合同或重构价值模块都会扩大范围。
> 
> **赌的假设**
> `VALUE_EVIDENCE.TARGETS` 与 baseline 集合完全一致门继续先于方向聚合执行；完整旧 suite 与 mutation 用来验证该假设未被破坏。
> 
> **标尺**
> `R3_3_1_TRANSFORM_AGGREGATION_FREEZE_V1.json`：suite 265/265、mutation 32/32、live 四件工件哈希不变。`calibrated=false`，等待第二裁判。
