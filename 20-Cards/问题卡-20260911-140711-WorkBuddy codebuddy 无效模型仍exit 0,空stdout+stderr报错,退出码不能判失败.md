---
id: P-20260911-140711
type: problem
title: WorkBuddy codebuddy 无效模型仍exit 0,空stdout+stderr报错,退出码不能判失败
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: hermes-A
source_tool: hermes
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

# 🟢 WorkBuddy codebuddy 无效模型仍exit 0,空stdout+stderr报错,退出码不能判失败

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 

---

> [!quote] 发生了什么

**事实链：**

```

```

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |

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

---

> [!warning] 复发记录（2026-09-13 · recorded_by dsh-A）
> **同一根因的第二个实例（不同工具、不同通道）：`hermes -z`**
>
> ```text
> 场景：D3 Record Contract V6 — PINNED_EFFECTIVE_V6 耐久证据链闭合
>       派发 Hermes-B 做 post-correction 独立审计
>
> 观测：hermes -z
>         EXIT = 0
>       stdout 仅 138 bytes，内容为：
>         "API call failed after 3 retries: Hermes can't reach the model provider.
>          You may be offline. Check your internet connection and try again."
>
> 即：进程退出成功 ≠ 审计实际执行。返回的是传输层失败文本，而非裁决。
>
> 实际后果（若未拦下）：该次运行会被记为一次「审计完成」，
>   在 PINNED_EFFECTIVE_V6 证据链里写入伪造的裁决。
>
> fail-closed 行为：DSH 逐字读 stdout 后判定「不是裁决、不予采信」→ 重试；
>   第 2 次返回 2287-byte 完整裁决块（PASS / BLOCKERS NONE）。
>   连通性实测：github.com 200 / api.deepseek.com 401（可达 → 第一次是瞬时的）。
>
> 临时规避：人工读 stdout 原文 + 输出长度异常检测（138 vs 2287）。
> 期望的系统性预防：见 [[C-20260913-212101]]（6 条机械验收条件 + provider-error 签名 + FAIL_CLOSED）。
> ```
>
> **根因判定**：与本卡同根因 —— **包装进程的退出码不反映底层操作的实际结果**。
> 本卡实例为 WorkBuddy/codebuddy；本次实例为 hermes CLI。
> 按 SIFE 查重规则**不重复建 P 卡**，改为在本卡补充复发证据。
>
> **注意差异（不合并根因）**：本次后果面是**审计链被伪造裁决**，比「任务没跑」更严重；
> 但其机制与本卡一致，故归为复发而非新根因。
>
> **关联**：[[C-20260913-212101]] · [[CAL-20260826-194451]] · [[P-20260913-212057]]
