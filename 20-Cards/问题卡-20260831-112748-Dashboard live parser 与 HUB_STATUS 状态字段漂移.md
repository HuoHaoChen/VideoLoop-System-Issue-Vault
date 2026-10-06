---
id: P-20260831-112748
type: problem
title: Dashboard live parser 与 HUB_STATUS 状态字段漂移
domain: 待分类
ptype: 待分类
level: 待定
status: 已解决
process_captured: true
recorded_by: codex-A
source_tool: codex
solution: "Live parser 保留 HUB_STATUS canonical 当前阶段为 phase，并在缺少显式 当前状态 时分开映射 ANSIR_CURRENT_STATE 与 AN_1S_READINESS；offline fallback 由同一解析器重建，并以一致性、freshness 与语义合同测试验证。"
solution_status: 已解决
solution_hits: 2
solution_level: 已验证
resolved_at: 2026-09-07 00:12
due: 
owner: huohaochen
created: 2026-08-31
tags: [problem]
---

# 🟢 Dashboard live parser 与 HUB_STATUS 状态字段漂移

==已解决== · 待分类 · <kbd>本地合同验证</kbd>

---

> [!question]+ 结论
> 已在 `TASK-DASHBOARD-STATUS-DEFECT-001` 的 User + GPT Supervisor 明确最小维修授权下解决；未修改 Dashboard 架构、运行控制或状态真相边界。

---

> [!quote] 发生了什么

**事实链：**

```
1. `HUB_STATUS.md` 的现行状态字段为 `当前阶段`。
2. live parser 仅匹配 `当前状态`，无匹配时返回 `未发现`。
3. `state.fallback.js` 未在后续 Hub 状态变更后重建。
4. 修复后 live/fallback 均输出 `ANSIR = RUNNING；AN-1S readiness = WAIT`；现有 Dashboard 行同时显示 phase 与该 status，且 fallback 不早于 `HUB_STATUS.md`。
```

---

| 判断 | 依据 |
|:-----|:-----|
| 已解决 | `01_CONTROL/DASHBOARD/test_status_contract.rb`、`05_AUDIT/PHASEDASHBOARDSTATUS/DASHBOARD_STATUS_CONTRACT_REMEDIATION_AUDIT.md` |

---

> [!warning] 可能偏差
> - 离线 snapshot 本质仍不是实时状态，必须显示其生成时间。
> - 将来若状态字段再次变更，应重跑合同测试并重建 fallback。

---

> [!note]- 过程层（复盘时展开）
> **原话**：Dashboard 状态解析与状态文件字段不一致，导致 `status=未发现`。
> 
> **关键分歧**：不向 `HUB_STATUS` 添加重复字段；改为让观察层兼容现行 canonical 字段，并分开表达运行状态与 readiness。
> 
> **标尺**：`01_CONTROL/DASHBOARD/test_status_contract.rb`
