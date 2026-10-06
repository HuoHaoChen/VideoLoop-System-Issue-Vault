---
id: P-20260924-130543
type: problem
title: Stage4 terminal state：malformed §六#0 commit locator accepted as ALREADY_FINALIZED
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

# 🟢 Stage4 terminal state：malformed §六#0 commit locator accepted as ALREADY_FINALIZED

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> `FINALIZATION_COMMITTED` 的 locator 校验允许 `§六#0`；但 canonical locator 由 1-based record index 生成，因此该 malformed commit 被错误接受为 ALREADY_FINALIZED。

---

> [!quote] 发生了什么

**事实链：**

```
1. `ParsedCanonicalRecord.LOCATOR` 明确使用 1-based index。
2. `CANONICAL_RECORD_LOCATOR_PATTERN = re.compile(r"§六#\\d+")` 接受 0 和非规范前导零。
3. 构造 scoped TASK_ID、64 位小写 SHA、locator=`§六#0` 的唯一 commit。
4. finalize 实测返回 ALREADY_FINALIZED，而非 FAILED_CLOSED；authority 未写，但非法终态被信任。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==真实 durable-close correctness violation== | 冻结契约要求 malformed FINALIZATION_COMMITTED 不得成为 terminal state。 |

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