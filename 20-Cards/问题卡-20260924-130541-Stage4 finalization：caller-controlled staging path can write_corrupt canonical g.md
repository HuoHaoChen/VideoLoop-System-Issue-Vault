---
id: P-20260924-130541
type: problem
title: Stage4 finalization：caller-controlled staging path can write/corrupt canonical governance
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

# 🟢 Stage4 finalization：caller-controlled staging path can write/corrupt canonical governance

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> Stage-4 finalization/query 未隔离 caller-controlled `runtime_root` 与 staging 路径；staging 可落入治理目录，或通过 symlink/hard path alias 写入 canonical authority。该问题违反 NORMAL_QUERY 不写 canonical governance，并可使 STEP E 在 out-of-band 复检前污染 §六。

---

> [!quote] 发生了什么

**事实链：**

```
1. `runtime_io.staging_dir(runtime_root)` 直接拼接调用方路径，无治理目录/authority containment 检查。
2. `append_jsonl()` 使用普通 `open(..., "ab")`，会跟随 staging JSONL symlink。
3. 临时仓库实测：`runtime_root=<repo>/10-系统` 时 query 返回 COMMITTED，并创建 `<repo>/10-系统/staging/2026-09-24.jsonl`。
4. 临时 authority 实测：staging 日文件 symlink 指向 authority 时，QUERY_STAGED 被追加到 authority；文件 SHA 改变。
5. STEP E 注入同类 alias 时，finalize 返回 FAILED_CLOSED/SECTION_6_WRITE=False，但 authority 已被 FINALIZATION_INTENT 污染。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==真实 canonical-authority violation== | 本实现自身通过 staging 写入口改变 canonical authority，且发生在 STEP F stale-state 复检之前。 |

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