---
id: C-20260901-184928
type: change
title: Phase A 将读取缓存限定为 resolve scope 并强制真实路径 source root
domain: 待分类
problems: [P-20260901-184853]
status: 本地验证完成待独立校准
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 本地验证通过，待第二裁判确认
calibrated: false
calibration_ref: 
process_captured: true
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-09-01
tags: [change]
---

# 🔵 Phase A 将读取缓存限定为 resolve scope 并强制真实路径 source root

> [!question] 一句话
> 将同一次 resolve 的读缓存隔离在 `ResolveSession`，并以 canonical real path 强制 ticket 的 source-root 合同。

---

> [!danger] 改动
> **改前**：`SourceReader`、Normalizer 将 cache/state 保留在实例上；路径只作词法检查。
> **改后**：每次 normalize 新建 session；读取前完成 `File.realpath` 和允许根验证。

---

## ✅ 怎么做

- [x] 新建 resolve-local `ResolveSession` cache/read counts。
- [x] 对允许根与候选路径做真实路径验证，拒绝 escape/broken/disallowed。
- [x] 覆盖跨 resolve、别名去重、内容变更和边界反证测试。
- [ ] 

---

> [!success] 预测
> 同实例跨 resolve 不会携带事实；同 resolve 仍按 canonical source 去重；任何未授权真实路径在读取前被拒绝。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 
> 
> **赌的假设**
> 
> 
> **标尺**
> [[]]
