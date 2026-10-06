---
id: P-20260913-134010
type: problem
title: Persistence candidate BEGIN END 正文 SHA256 与印刷值不一致
domain: 待分类
ptype: 待分类
level: 待定
status: 已解决
process_captured: true
recorded_by: hermes-A
source_tool: hermes
solution: 
solution_status: 已解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-09-13
tags: [problem]
---

# 🟢 Persistence candidate BEGIN END 正文 SHA256 与印刷值不一致

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 

---

> [!quote] 发生了什么

**事实链：**

```
初算将 END marker 前的 Markdown 分隔换行纳入正文，得 22,235 bytes / f2f549...
按文件印刷约定排除该分隔换行，正文为 22,234 bytes / 635ebe...
与 candidate 声明一致；非 candidate 故障。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==初算边界错误，candidate 哈希正确== | 排除 END 前分隔换行后，SHA-256 = 635ebe... |
| ==已解决== | 采用文件自身 VERBATIM_BODY_BYTES 约定复核 |

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