---
id: P-20261001-060043
type: problem
title: claude-route 缓存 quota-ok 无 until 上限，官方 OAuth token 过期后仍走官方通道致长任务中途 401 失败
domain: 工具路由
ptype: 配置坑
level: S2
status: 未处理
process_captured: true
recorded_by: dsh-A
source_tool: dsh
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-10-01
tags: [problem, claude-route, oauth, routing]
---

# 🟠 claude-route 缓存 quota-ok 无 until 上限，官方 OAuth token 过期后仍走官方通道致长任务中途 401 失败

==待处理== · 工具路由 · <kbd>S2</kbd>

---

> [!question]+ 结论
> claude-route 在 `source=cache` 且缓存条目 `until=-`（无过期时间）时，把一次历史 quota-ok
> 判定当作**永久有效**，于是在官方 OAuth token 已过期的情况下仍选择 official 通道。
> 短任务不暴露；**长任务（数分钟级）会在中途撞上 401**，此时已产生的时间与费用全部损失。

---

> [!quote] 发生了什么

**事实链：**

```
2026-10-01 05:52:51  claude-route log: run mode=official source=cache reason=quota-ok until=-
                     ← until=-（缓存条目未设过期时间）
2026-10-01 05:52:51  DSH 启动 claude -p --model claude-opus-5（TEST-05 D-23 只读追迹）
2026-10-01 06:00:01  RC=1  duration_ms=426379（约 7 分 6 秒）  num_turns=33
                     is_error=true  terminal_reason=api_error  api_error_status=401
                     result="Failed to authenticate. API Error: 401 OAuth access token has expired.
                             Re-authenticate to continue."
                     已产生费用 total_cost_usd=2.750897（不可回收）
2026-10-01 06:00:01  claude-route log: official run failed rc=1 -> 下次重新探测额度
2026-10-01 06:00:06  claude-route status → 当前通道 = 第三方 API (oauth-invalid / probe)
```

**附带（非本问题）**：同一次调用另有 `permission_denials`，Bash `cat` 读
`09-TEST04-.../control/*.json` 被沙箱拒绝。改用 Read 工具后正常，故单列不计入。

---

| 判断 | 依据 |
|:-----|:-----|
| ==缓存无 until 即视为永久有效== | `status` 与 log 同时显示 `source=cache reason=quota-ok until=-` |
| ==official 通道 token 实为过期== | 运行后 probe 立即返回 `thirdparty (oauth-invalid)`，`HTTP=401` |
| ==失败发生于任务中途而非启动时== | duration_ms=426379、num_turns=33 后才终止，非启动即失败 |
| ==费用不可回收== | `total_cost_usd=2.750897` 已计入 |

---

> [!warning] 可能偏差
> - 05:54 之前的 probe 曾返回 `official (quota-ok) until=10-01 06:05`。无法区分
>   「token 在 05:52–06:00 之间才过期」与「额度判定与 OAuth 凭据有效性本就是两套独立凭据」。
> - 仅一次失败样本，未验证第三方通道上的同类长任务是否也会中途失败。
> - S2 为 DSH 自评；按协议 severity=S1 只能由人定，本条不主张 S1。
> - 记录者与判定者同为 DSH，尚无第二裁判。

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> `"result":"Failed to authenticate. API Error: 401 OAuth access token has expired. Re-authenticate to continue."`
>
> **关键分歧**：
> 路由层把「额度够不够」当成通道可用性的充分条件；实际可用性 = 额度 ∧ 凭据有效。
> 缓存只保留前者的旧结论且不带 `until`，于是后者的变化无法被观测到。
>
> **候选缓解（均未验证）**：
> ① `until` 缺失时强制重新 probe，不采信 cache；
> ② 长任务开始前先做一次极短 canary 调用验证凭据；
> ③ 长任务因 401 失败后自动在备用通道重试一次。
>
> **标尺**：[[]]
