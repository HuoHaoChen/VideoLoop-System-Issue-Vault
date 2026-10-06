---
id: P-20260924-131603
type: problem
title: Stage4 finalizer 可用 authority 覆盖 flock 载体导致并发穿透
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

# 🟢 Stage4 finalizer 可用 authority 覆盖 flock 载体导致并发穿透

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> `finalize-evidence --authority` 可指向冻结 `.finalize.lock` 本身；STEP F 的 `os.replace` 会替换锁载体 inode，使第二个 finalizer 在第一个尚未 STEP H 释放时取得新 inode 的 flock，击穿 A..H 串行化。

---

> [!quote] 发生了什么

**事实链：**

```
1. finalize_evidence() 固定锁路径，但未拒绝 authority_path 与该锁路径同一文件。
2. _fsync_write() 通过 os.replace(tmp_name, authority_path) 写 authority。
3. 临时副本实测：authority==lock carrier 时，STEP G 探测 lock_is_currently_held(path)=False，但进程内登记仍为 True（登记指向旧 inode）。
4. 双线程复现实测：第二 finalizer 在第一 finalizer STEP G 阻塞、尚未释放时完成 RECOVERED_R2。
5. 同一 correlation 最终产生 2 条 FINALIZATION_COMMITTED，finalization state 变为 AMBIGUOUS。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==真实 correctness / authority violation== | caller-controlled authority 可替换冻结锁载体，导致并发进入并制造重复 commit。 |

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