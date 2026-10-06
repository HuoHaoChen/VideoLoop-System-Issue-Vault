---
id: C-20260831-173606
type: change
title: Add canonical_promotion guard to Dashboard UX finding task ticket
domain: 待分类
problems: [P-20260831-173556]
status: 已实施待裁判
baseline_window: "2026-08-31 当前 Dashboard UX Finding 独立本地提交"
minimum_effect: "仅补齐 Task Ticket / Maintenance Ticket 的 canonical_promotion 禁止项，并在 Receipt 记录未发生。"
confounds: "无 Dashboard、Cross-Window 或主线文件变更；最终校准未由第二裁判完成。"
significance: 方向性
borrows_from: 无
verdict: 待校准
calibrated: false
calibration_ref: 
process_captured: false
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-08-31
tags: [change]
---

# 🔵 Add canonical_promotion guard to Dashboard UX finding task ticket

> [!question] 一句话
> 用最小票据护栏修复 pre-commit 合同失败，不扩大 Dashboard UX Finding 的登记范围。

---

> [!danger] 改动
> **改前**：`forbidden_actions` 缺少 `canonical_promotion`，提交钩子拒绝提交。
> **改后**：Maintenance / Task Ticket 均明确禁止 `canonical_promotion`，Receipt 记录 `canonical_promotion: false`。

---

## ✅ 怎么做

- [x] 在 Maintenance Ticket、Task Ticket 与 Receipt 补齐最小治理护栏。
- [x] 重新运行 SharedHub 治理校验、Workspace 资产检查与提交钩子。
- [ ] 

---

> [!success] 预测
> SharedHub pre-commit 将接受该受限登记，而不增加 Dashboard 或主线工程变更。

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
