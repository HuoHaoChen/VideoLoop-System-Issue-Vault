---
id: P-20260901-184853
type: problem
title: Phase A SourceReader 跨 resolve 缓存与真实路径授权缺口
domain: 待分类
ptype: 待分类
level: 待定
status: 已修复待独立校准
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: C-20260901-184928
solution_status: 已解决
solution_hits: 1
solution_level: 已验证
resolved_at: 2026-09-08 00:13
due: 
owner: huohaochen
created: 2026-09-01
tags: [problem]
---

# 🟢 Phase A SourceReader 跨 resolve 缓存与真实路径授权缺口

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 已将来源缓存、visited/read state、累计 sources 和 findings 限定为单次 resolve；读取前以 `File.realpath` 验证最终目标位于 ticket 明示的 source roots。

---

> [!quote] 发生了什么

**事实链：**

```
同一 Normalizer：resolve A -> 修改来源 -> resolve B 曾可复用 A 的 reader cache。
修复后：15 项 Phase A 反证/单元测试通过；V1.0–V1.4R 历史回归全部通过。
```

---

| 判断 | 依据 |
|:-----|:-----|
| 本地修复有效，尚待独立裁判 | SourceReader 每次 normalize 建立新的 ResolveSession；symlink escape、broken symlink、disallowed root 均有拒绝测试 |

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
