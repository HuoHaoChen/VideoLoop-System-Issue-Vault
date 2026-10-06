---
id: P-20261002-181318
type: problem
title: TEST07 TRANSFORM_TARGET 多目标聚合把任一变化误判为全部变化
domain: 测试与价值判定
ptype: 聚合逻辑误判
level: S3
status: 已定位
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: 将 TARGET_MUST_CHANGE 从 bool(changed) 改为 len(changed)==len(targets)，保留 target 集合完全一致门；补四组合回归和 ALL_CHANGED→ANY_CHANGED mutation。
solution_status: 已实施
solution_hits: 0
solution_level: 待验证
resolved_at: 2026-10-02 18:37
due: 
owner: huohaochen
created: 2026-10-02
tags: [problem]
---

# 🟢 TEST07 TRANSFORM_TARGET 多目标聚合把任一变化误判为全部变化

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> TEST07 R3.3 的多目标 TRANSFORM 聚合使用 `bool(changed)`，把“至少一个目标变化”误判成“全部目标变化”。已形成 R3.3.1 最小修补并完成机械验证；独立审计仍待 NEW CLEAN Claude Code。

---

> [!quote] 发生了什么

**事实链：**

```
ACTION_TARGETS = [A, B]
A 变化 / B 不变，或 A 不变 / B 变化
→ R3.3 实际派生 POSITIVE
→ VALUE 合同要求 NEGATIVE
→ 根因：TARGET_MUST_CHANGE 使用 bool(changed)
→ 修补：len(changed) == len(targets)
→ suite 265/265 PASS；mutation 32/32 killed
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==问题可复现== | 隔离最小反例得到 POSITIVE / POSITIVE / POSITIVE / NEGATIVE，前两项违反合同 |
| ==修补范围最小== | 只改一条聚合表达式、四条回归和一个 mutation；合同与 non-blocking 项未改 |
| ==机械验证通过== | 完整 suite 265/265；32/32 mutants killed；live 四件工件哈希不变 |

---

> [!warning] 可能偏差
> - 本卡由修补执行者记录；`已实施` 不替代第二裁判的独立审计。
> - R3.3.1 只有 NEW CLEAN Claude Code PASS 后才可交 Hermes。

---

> [!note]- 过程层（复盘时展开）
> **原话**：价值合同要求 TRANSFORM_TARGET 的全部 ACTION_TARGETS 都满足变化要求才为 POSITIVE。
>
> **关键分歧**：`TARGETS` 集合完全一致只能保证“看了全部对象”，不能保证聚合函数采用全称量化。
>
> **标尺**：`VALUE_EVIDENCE_CONTRACT_V1` §7.1；`R3_3_1_TRANSFORM_AGGREGATION_FREEZE_V1.json`。
