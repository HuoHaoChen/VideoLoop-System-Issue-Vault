---
id: C-20260902-065705
type: change
title: Phase B Gate 增加 expected-actual binding 与 required-not-applicable 条件
domain: 待分类
problems: [P-20260902-065654]
status: 本地验证完成待独立校准
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 本地验证通过，待第二裁判确认
calibrated: false
calibration_ref: 
process_captured: true
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-09-02
tags: [change]
---

# 🔵 Phase B Gate 增加 expected-actual binding 与 required-not-applicable 条件

> [!question] 一句话
> 用 Phase A normalized facts 的 baseline/revision snapshot 做 expected-vs-actual identity 比较，并以显式条件判定 authority required 或 N/A。

---

> [!danger] 改动
> **改前**：非空字段可通过；缺失 authority ref 可被跳过。
> **改后**：owned required fact 必须语义绑定；required authority 缺失 BLOCK；只有明确 NO_DISPUTE/previous admission/local integrity 才 N/A。

---

## ✅ 怎么做

- [x] 修复 G1 state/checkpoint binding 与 G2 identity baseline comparison。
- [x] 修复 G3 adjudicator/history/external attester conditional requirement。
- [x] 增加 ownership、非全局 finding blocker 和 composition-boundary 测试。

---

> [!success] 预测
> 消除 presence-check false-pass 与 missing-authority skip，同时不让 G1-G3 重算 facts_digest 或吸收 G4-G6 职责。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 
> 
> **赌的假设**
> 
> 
> **标尺**
> [[]]
