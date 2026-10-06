---
id: P-20260902-125941
type: problem
title: SharedHub Canonical Extension 三项 Critical false-pass 与 revalidation SSoT 缺口
domain: 待分类
ptype: 待分类
level: 待定
status: 待独立复验
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: C-20260902-125951
solution_status: 已解决
solution_hits: 1
solution_level: 已验证
resolved_at: 2026-09-09 00:13
due: 
owner: huohaochen
created: 2026-09-02
tags: [problem]
---

# 🟢 SharedHub Canonical Extension 三项 Critical false-pass 与 revalidation SSoT 缺口

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> Canonical Extension 的 schema-valid 单记录检查不足以证明 Admission ID 不可变；predecessor 未按 exact source_ref 绑定；legacy locator 未读取真实 bytes；Annex 与 v2 schema 的 revalidation 字段不一致。

---

> [!quote] 发生了什么

**事实链：**

```
独立验收：CRITICAL_FALSE_PASS_COUNT=3 / ANNEX_SCHEMA_SSoT=FAIL
→ 新增固定 Control Plane authority source set + formal AdmissionIssuer
→ exact canonical source_ref/id/schema/digest 校验
→ legacy exact bytes SHA-256 校验
→ v2 统一 revalidation_basis_refs
→ 直接反例 6 runs / 18 assertions 全通过，等待独立复验
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |

---

> [!warning] 可能偏差
> - 
> - 

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> 
> 
> **关键分歧**：
> 
> 
> **标尺**：[[]]
