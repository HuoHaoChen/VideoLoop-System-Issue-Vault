---
id: C-20260904-181629
type: change
title: 处理 SharedHub 残留 Git index.lock 后重试 P0 持久化
domain: 待分类
problems: []
status: 已完成
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 有效
calibrated: true
calibration_ref: CAL-20260904-181630
process_captured: true
recorded_by: codex-A
source_tool: codex
evaluator: 第二裁判
due: 
created: 2026-09-04
tags: [change]
solution_hits: 1
solution_level: 已验证
---

# 🔵 处理 SharedHub 残留 Git index.lock 后重试 P0 持久化

> [!question] 一句话
> 在核验锁龄和只读占用后解除残留 Git 元数据锁，恢复 P0 的精确暂存与提交。

---

> [!danger] 改动
> **改前**：残留 `.git/index.lock` 阻断 `git add`。
> **改后**：确认无活跃 Git 写进程后解除该锁，`git add` 与提交成功。

---

## ✅ 怎么做

- [x] 核验锁文件状态、占用进程和锁龄后解除精确锁路径。
- [x] 复核内容哈希并完成本地 P0 提交。

---

> [!success] 预测
> 

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
