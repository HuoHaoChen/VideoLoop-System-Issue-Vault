---
id: C-20260902-125951
type: change
title: 修复 SharedHub Canonical Admission 唯一性、精确 lineage 与 legacy byte binding
domain: 待分类
problems: [P-20260902-125941]
status: 已实施待第二裁判
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 待第二裁判独立校准
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

# 🔵 修复 SharedHub Canonical Admission 唯一性、精确 lineage 与 legacy byte binding

> [!question] 一句话
> 使用既有 Control Plane 授权对象承载完整 exact Canonical Admission source set；签发、canonical predecessor 与 legacy predecessor 全部 fail closed，并统一 v2 revalidation SSoT。

---

> [!danger] 改动
> **改前**：单记录 schema-valid 可绕过 ID 唯一性；lineage 按 ID 查找；legacy 只检查 digest 格式；Annex 保留第二个 revalidation 字段。
> **改后**：唯一 production issuance API 从固定 authority source set 读取；四项 canonical locator 全匹配；legacy 重算 exact bytes SHA-256；v2 仅使用 revalidation_basis_refs。

---

## ✅ 怎么做

- [x] 增加 Work6B 直接反例并通过本地回归
- [ ] 等待第二裁判独立验收，不由 codex-A 自评 calibrated

---

> [!success] 预测
> 

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
