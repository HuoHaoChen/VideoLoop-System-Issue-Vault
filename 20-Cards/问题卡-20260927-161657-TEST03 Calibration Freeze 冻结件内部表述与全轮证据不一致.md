---
id: P-20260927-161657
type: problem
title: TEST03 Calibration Freeze 冻结件内部表述与全轮证据不一致
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: codex-A
source_tool: codex
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-09-27
tags: [problem]
---

# 🟢 TEST03 Calibration Freeze 冻结件内部表述与全轮证据不一致

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> TEST-03 Calibration Freeze 的核心哈希与集合摘要可复算通过，但冻结件存在两处非阻塞内部表述不一致：阈值指纹可复算性被写成“无法独立复算”，且“本轮仅新建 2 个文件”与整轮实际新建 3 个文件不一致。冻结件不宜原地改写，应由第二裁判或人决定是否追加独立 errata。

---

> [!quote] 发生了什么

**事实链：**

```
1. CALIBRATION_FREEZE_V1.json 的 THRESHOLD_FINGERPRINT_PROVENANCE.RECOMPUTED_FROM_FORMULA 写为 NO，并称派生算法未记录、无法独立复算。
2. 既有 evidence/DSH_INDEPENDENT_VERIFICATION.json 已记录完整公式、规范化 blob，并声明 REPRODUCIBILITY_GAP_CLOSED。
3. Codex 按该公式独立复算得到 4103502bb9e7d978e05c46fce2f26a27af38634b89324e1e52cd47d7c7205520，与冻结值一致，因此问题是表述漂移，不是指纹失效。
4. CALIBRATION_FREEZE_V1.json 同时写“本轮仅新建 2 个文件”并仅列出 JSON/MD；但同一 formal freeze 轮还新建 CALIBRATION_FREEZE_VERIFICATION.json，台账也明确登记全轮恰好新建 3 个文件。
5. 15 个 canonical input、set digest、双文件互绑、execution bindings、34 个 R3 实质文件与台账 append-only 均独立复算通过；未发现越权修改。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==核心 freeze 仍有效== | 15/15 文件 bytes/hash 匹配；set digest = 01ec9194…；JSON core ↔ Markdown 双向绑定通过 |
| ==文档一致性缺陷== | freeze JSON 的可复算性和文件计数表述与既有 evidence / 台账冲突 |
| ==非阻塞== | 两处问题不改变 canonical 文件、集合摘要、阈值数值或双文件绑定 |

---

> [!warning] 可能偏差
> - “EVALUATOR_CALLS = 0”只能由执行记录和无输出迹象支持，不能仅靠静态冻结文件机械证明。
> - CALIBRATION_FREEZE_VERIFICATION.json 未内嵌 ledger 前缀和 R3 全量基线，复核时需要外部历史快照。

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> `RECOMPUTED_FROM_FORMULA = NO — 指纹派生算法未记录于磁盘任何文件，无法独立复算`
> 
> `未修改任何既有文件（本轮仅新建 2 个文件）`
> 
> **关键分歧**：
> 既有 DSH 独立验证文件已经把公式与 canonical blob 落盘；整轮还创建了 verification JSON，故上述两句不能同时作为全轮事实。
> 
> **标尺**：冻结件不可原地改写；更正应 append-only，且由第二裁判或人决定。
