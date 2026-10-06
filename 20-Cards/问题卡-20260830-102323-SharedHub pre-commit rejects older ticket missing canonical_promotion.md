---
id: P-20260830-102323
type: problem
title: SharedHub pre-commit rejects older ticket missing canonical_promotion
domain: 系统
ptype: 流程兼容性
level: 一般
status: 已解决
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: C-20260830-102332
solution_status: 已解决
solution_hits: 1
solution_level: 已验证
resolved_at: 2026-08-30
due: 
owner: huohaochen
created: 2026-08-30
tags: [problem]
---

# 🟢 SharedHub pre-commit rejects older ticket missing canonical_promotion

==已解决 → C-20260830-102332== · 系统域 · <kbd>2026-08-30</kbd>

---

> [!question]+ 结论
> SharedHub 的预提交检查要求每张普通任务票据在 `forbidden_actions` 中包含精确值 `canonical_promotion`。AN-0 票据已有更宽泛的 `canonical_or_ssot_promotion`，但缺精确兼容标签，导致本地提交被安全拒绝。补齐同义禁止标签后，AN-0 与 AN-1 票据均通过验证，提交成功。

---

> [!quote] 发生了什么

**事实链：**

```
AN-1 本地提交预检查
  → AN-0 ticket 违反 exact forbidden_actions 合同
  → 发现已有等价但不兼容的宽泛禁止标签
  → 建 P/C 卡并在 AN-1 Maintenance Ticket 下补齐 metadata-only 标签
  → validate_hub：AN-0 PASS、AN-1 PASS
  → 本地 commit d90a15d 成功
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==旧票据的语义正确不等于合同兼容== | 预提交使用精确 label 检查，AN-0 缺 `canonical_promotion`。 |
| ==修复不扩大授权== | 仅增加已有禁止意图的兼容字段；没有变更运行、资产或 Canonical 状态。 |

---

> [!warning] 可能偏差
> - 此修复只验证当前预提交合同；未来 schema/hook 变化仍可能引入新的兼容要求。
> - 已提交的历史票据可能还有其他尚未触发的契约漂移，不能据此断言全部历史票据无误。

---

> [!note]- 过程层（复盘时展开）
> **原话**：预提交失败：`forbidden_actions lacks canonical_promotion`。
> 
> **关键分歧**：跳过预提交，还是以最小元数据改动遵守既有合同。选择后者。
> 
> **标尺**：SharedHub `task-ticket.schema.json` 与 pre-commit validator；P-20260830-102323。
