---
id: P-20260911-044011
type: problem
title: Codex 额度报错时间格式变更，导致 run-codex-batch.sh 额度解析静默失效
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: dsh-A
source_tool: dsh
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-09-11
tags: [problem]
---

# 🟢 Codex 额度报错时间格式变更，导致 run-codex-batch.sh 额度解析静默失效

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 供应商报错文案是**外部可变依赖**。任何把时间格式写死成正则的额度解析，都会在文案改版时**静默失效**——不报错、不报警，直接走到「非额度类失败，退出 1」，把无人值守链掐断在最需要它的时刻。

---

> [!quote] 发生了什么

**事实链：**

```
2026-09-10 22:2x  codex exec 返回：
  ERROR: You've hit your usage limit. Upgrade to Pro (...) or try again at Sep 11th, 2026 12:26 AM.
                  ↑ 月份名 + 序数后缀 th + 年份 + 12 小时制

        ↓ 对比现有解析

~/Downloads/codex-work/run-codex-batch.sh：
  grep -oE "try again at [0-9]{1,2}:[0-9]{2} ?[AP]?M?"
                  ↑ 只认纯 HH:MM 紧跟可选 AM/PM

        ↓ 结果

RETRY 为空 → 进入 else 分支 → echo "=== 非额度类失败，退出 ===" → exit 1
即：额度耗尽被误判成「非额度类失败」，重试逻辑完全没被触发。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |
| 这是配置坑，不是偶发故障 | 同一脚本对 2026-08 的 `try again at 3:45 PM` 老格式有效，对新格式无效；失效点固定在解析层，与网络／账号状态无关 |
| 危害是「静默」而非「报错」 | 脚本 exit 1 且输出人类可读的「非额度类失败」，看日志的人会以为是真失败，不会去查额度 |

---

> [!warning] 可能偏差
> - 未穷举供应商全部历史格式，只实测了 2 种（新格式、老 HH:MM 格式）
> - 未验证 `sleep` 等待期间进程是否会被系统回收（launchd 场景下需另测）
> - 结论仅覆盖 Codex CLI；ChatGPT 网页端／GPT 额度提示文案未纳入

---

> [!note]- 过程层（复盘时展开）
> **原话**：`ERROR: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at Sep 11th, 2026 12:26 AM.`
> 
> 
> **关键分歧**：
> 
> 
> **标尺**：外部依赖文案解析必须 fail-loud + 多格式回退，禁止单正则写死
>
> **归属**：DSH 在搭建课程蒸馏无人值守管线时实测发现（`~/Workspace/scripts/distill_worker.sh`）
>
> **severity**：待人工定级（按协议 S1 只能由人定）