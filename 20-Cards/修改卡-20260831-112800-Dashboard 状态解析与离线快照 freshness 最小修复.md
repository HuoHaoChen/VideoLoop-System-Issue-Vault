---
id: C-20260831-112800
type: change
title: Dashboard 状态解析与离线快照 freshness 最小修复
domain: SharedHub
problems: [P-20260831-112748]
status: 已完成
baseline_window: "2026-08-31 当前 HUB_STATUS 与既有 fallback"
minimum_effect: "live status 不再为 未发现，且明确 ANSIR=RUNNING 与 AN-1S readiness=WAIT；fallback 与 live phase/status 一致且不早于 HUB_STATUS"
confounds: "离线 fallback 仍为带时间戳快照，不代表运行时遥测"
significance: 方向性
borrows_from: 无
verdict: PASS（待第二裁判复核）
calibrated: false
calibration_ref: 
process_captured: true
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-08-31
tags: [change]
---

# 🔵 Dashboard 状态解析与离线快照 freshness 最小修复

> [!question] 一句话
> 在不新增状态字段或第二真相源的前提下，保留 `当前阶段` 为 phase、分开映射运行与 readiness，并用同一解析器重建 fallback。

---

> [!danger] 改动
> **改前**：仅匹配不存在的 `当前状态`，缺失时为 `未发现`；fallback 过期。
> **改后**：显式 `当前状态` 优先；否则保留 `当前阶段` 为 phase，并分开显示 `ANSIR = RUNNING；AN-1S readiness = WAIT`；fallback 与 live 同源重建。

---

## ✅ 怎么做

- [x] 持久化 User + GPT Supervisor 最小维修授权。
- [x] 修正 `dashboard_data.rb` 的状态回退契约。
- [x] 重建 `state.fallback.js`。
- [x] 增加并运行 live/fallback 一致性与 freshness 合同测试。
- [x] 让现有 Dashboard 的 phase 行同时渲染已验证的 runtime/readiness status。

---

> [!success] 预测
> 只修复观察层字段契约；不改变 Hub 状态、ANSIR 门控、Dashboard 权限或其他工程主线。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 读取已存在的 canonical 字段比在状态源增加镜像字段更小、更不易形成双真相。
> 
> **赌的假设**
> `当前阶段` 持续是 lifecycle phase；ANSIR 运行状态和 AN-1S readiness 仍以现有显式 canonical 字段表达；若未来加入 `当前状态`，显式值仍兼容。
> 
> **标尺**
> `01_CONTROL/DASHBOARD/test_status_contract.rb`；第二裁判尚未复核，故 `calibrated=false` 保持不变。
