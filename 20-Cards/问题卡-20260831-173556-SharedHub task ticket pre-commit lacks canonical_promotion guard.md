---
id: P-20260831-173556
type: problem
title: SharedHub task ticket pre-commit lacks canonical_promotion guard
domain: 待分类
ptype: 待分类
level: 待定
status: 已解决
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: 在 Task Ticket 与对应 Maintenance Ticket 的 forbidden_actions 中补齐 canonical_promotion，并在 receipt 中记录未发生该动作；SharedHub 治理校验与提交钩子均通过。
solution_status: 已解决
solution_hits: 1
solution_level: 已验证
resolved_at: 2026-08-31
due: 
owner: huohaochen
created: 2026-08-31
tags: [problem]
---

# 🟢 SharedHub task ticket pre-commit lacks canonical_promotion guard

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> Dashboard UX Finding Task Ticket 未声明 pre-commit 强制要求的 `canonical_promotion` 禁止项；补齐最小护栏后，本地治理校验与提交钩子均通过。

---

> [!quote] 发生了什么

**事实链：**

```
1. 独立本地 commit 被 pre-commit 拦截，报错为 `forbidden_actions lacks canonical_promotion`。
2. 未创建 commit，未发生 Dashboard、Cross-Window 或主线状态变更。
3. 仅在对应 Maintenance Ticket、Task Ticket 和 Receipt 中补齐该护栏及未发生断言。
4. `validate_hub.rb --no-snapshot`、资产检查与后续 commit hook 通过。
```

---

| 判断 | 依据 |
|:-----|:-----|
| Task Ticket 的禁止动作清单必须满足 pre-commit 合同。 | pre-commit 的 `FAIL FORBIDDEN_ACTIONS` 明确指出缺少 `canonical_promotion`。 |
| 修复为最小治理同步，未扩大工程范围。 | 仅补齐票据/回执护栏；Dashboard 与 Cross-Window 文件没有变更。 |

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
