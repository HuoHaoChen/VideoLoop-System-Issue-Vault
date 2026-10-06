---
id: P-20260924-131604
type: problem
title: Stage4 meta-out 可覆盖自定义 runtime staging 且误报 COMMITTED
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

# 🟢 Stage4 meta-out 可覆盖自定义 runtime staging 且误报 COMMITTED

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> `_assert_safe_meta_out()` 未接收/检查本次调用的 `runtime_root`，因此 meta-out 可指向 caller-selected `<runtime_root>/staging/YYYY-MM-DD.jsonl`，覆盖刚写入的 QUERY_STAGED；run_query 随后仍追加 QUERY_COMMITTED 并返回 COMMITTED。

---

> [!quote] 发生了什么

**事实链：**

```
1. run_query() 仅把 authority_context.repo_root 传给 _assert_safe_meta_out()，没有传 runtime_root。
2. guard 只检查 repo roots 的 staging 与包内默认 staging。
3. 临时目录实测：meta_out=<custom runtime>/staging/2026-09-24.jsonl 被接受。
4. _write_meta_out() 用 os.replace 覆盖 QUERY_STAGED 所在 JSONL；commit_query() 再追加 QUERY_COMMITTED。
5. run_query 返回 COMMITTED，但 load_records() 报首行缺 EVENT，staging 状态已损坏、无法 finalize。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==真实 correctness / isolation violation== | 成功返回与持久 staging 状态矛盾；meta-out 可破坏本次 query 的内部状态。 |

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