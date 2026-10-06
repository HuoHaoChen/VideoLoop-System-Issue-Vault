---
id: C-20260830-102332
type: change
title: Add required canonical_promotion guard to AN-0 task ticket
domain: 系统
problems: [P-20260830-102323]
status: 已实施
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 有效（技术合同验证通过；待第二裁判／人工校准）
calibrated: false
calibration_ref: 
process_captured: false
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-08-30
tags: [change]
---

# 🔵 Add required canonical_promotion guard to AN-0 task ticket

> [!question] 一句话
> 为 AN-0 票据补齐预提交要求的精确禁止标签 `canonical_promotion`，保持原有 `canonical_or_ssot_promotion`，使语义边界和机器合同一致。

---

> [!danger] 改动
> **改前**：`forbidden_actions` 只有宽泛的 `canonical_or_ssot_promotion`，预提交拒绝。
> **改后**：同时包含精确 `canonical_promotion` 和宽泛标签；票据验证与本地提交均通过。

---

## ✅ 怎么做

- [x] 用 KEDB 查重并建立 P 卡。
- [x] 建立 C 卡，且在 AN-1 Maintenance Ticket 中显式扩展本次 metadata-only 修复范围。
- [x] 为 AN-0 ticket 增加 `canonical_promotion`，不改动其审计范围、资产或结果。
- [x] 运行 `validate_hub` 验证 AN-0 / AN-1，均 PASS。
- [x] 本地提交 `d90a15d` 通过预提交。
- [ ] 

---

> [!success] 预测
> 同一历史票据在包含宽泛保护意图时，也必须含机器合同需要的精确保护标签；修复后不会扩大任何写权或改变业务状态。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 跳过 pre-commit 会破坏 SharedHub 证据链；补一条显式禁止标签是最小、可审计且不改变运行行为的修复。
> 
> **赌的假设**
> 预提交 hook 的精确标签规则仍是有效的长期契约；若未来规则变化，应另建卡而非扩展本次改动。
> 
> **标尺**
> SharedHub `validate_hub.rb` 的票据契约检查与成功的本地 commit `d90a15d`。第二裁判／人工尚未完成校准。
