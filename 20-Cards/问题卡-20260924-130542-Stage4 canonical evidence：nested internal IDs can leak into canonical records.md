---
id: P-20260924-130542
type: problem
title: Stage4 canonical evidence：nested internal IDs can leak into canonical records
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: hermes-A
source_tool: hermes
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-09-24
tags: [problem]
---

# 🟢 Stage4 canonical evidence：nested internal IDs can leak into canonical records

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> canonical evidence 仅检查顶层字段名，未递归检查 canonical 字段值；调用方可在列表元素中嵌入 `CORRELATION_ID` / `INVOCATION_ID`，并被成功物化进 §六。

---

> [!quote] 发生了什么

**事实链：**

```
1. `cli.assemble_canonical_evidence()` 直接接收 caller-supplied 列表，未调用 `_assert_no_internal_fields()`。
2. `evidence_materializer._validate_record()` 只验证相关字段为 list，未验证元素类型或递归 internal-only key。
3. 通过真实 `run_query()` 提交 `KNOWLEDGE_MISSING=[{"CORRELATION_ID":"cor-leak","INVOCATION_ID":"inv-leak"}]`。
4. finalize 返回 FINALIZED；临时 canonical authority 同时包含两个 internal-only key 和值。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==真实 canonical isolation violation== | 冻结契约要求两个 internal ID 不得出现在 canonical evidence record。 |

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