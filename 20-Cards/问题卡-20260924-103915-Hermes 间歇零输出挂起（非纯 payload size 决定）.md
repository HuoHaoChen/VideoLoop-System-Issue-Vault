---
id: P-20260924-103915
type: problem
title: Hermes 间歇零输出挂起（非纯 payload size 决定）
domain: 系统
ptype: 工具传输异常
level: 重要
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
created: 2026-09-24
tags: [problem, transport, hermes]
---

# 🟢 Hermes 间歇零输出挂起（非纯 payload size 决定）

==待处理== · 系统域 · <kbd>9/24</kbd>

---

> [!question]+ 结论
> Hermes 审计调用存在**间歇性零输出挂起**：进程未退出、stdout 无任何输出。

分类 = `INTERMITTENT_TOOL_TRANSPORT_FAILURE`

关键观察：**不接受「payload 过大」作为唯一解释** —— 16KB 量级 payload 亦可能连续挂起，而更大 payload 曾正常返回。故 payload 体积不是成败的充分判据。

---

> [!quote] 发生了什么

**事实链：**

```
同一审计提示词形态下，调用结果在「正常返回完整裁决块」与「零输出且不退出」之间不稳定切换。
按 payload 体积分档未能稳定预测成败（16KB 级亦连续挂起）。
挂起时无 stdout、无裁决文本 —— 症状本身不携带任何语义信息。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==不是语义审计失败== | 零输出不含任何裁决内容；据以判 FAIL 或 PASS 均属臆造 |
| ==也不是单纯的 payload 问题== | 16KB 级 payload 亦连续挂起，破坏「缩小即恢复」假设 |
| ==分类== | `INTERMITTENT_TOOL_TRANSPORT_FAILURE` |

---

> [!warning] 可能偏差
> - 未抓取挂起时的进程栈/连接状态，无法区分「等网络」「内部循环」「终态未处理」。
> - 「间歇」是多次观察的归纳，**尚无稳定复现配方**；不排除存在未识别的混淆变量（并发、限流、会话复用）。
> - 本卡**不**主张 Hermes 自身有缺陷 —— 传输层、CLI 收尾、上游 provider 均未被排除。

---

> [!note] 与既有卡的关系（非等价，登记以防重复建卡）
> - `C-20260913-212101`：已确立**规则**「传输/运行时失败文本 ≠ 审计裁决；退出码不可作验收依据」。本卡是该规则对应的**具体故障实例之一**，**未**另立同义规则。
> - `P-20260826-194446`（Codex 产物写完但进程挂起不退）：**不同工具、不同症状** —— 该卡是「有产物、收尾不退」，本卡是「零输出挂起」。二者同属工具传输/收尾异常族，但判据与处置不同，**不合并**。

---

> [!success] 运行策略（本卡主张，待验证）
> - focused payload（受控缩小上下文，但**不**把它当作根治手段）
> - retry（挂起后重试，**不**据空输出下结论）
> - timeout（外部超时 kill，避免阻塞后续队列）
> - **transport failure != semantic audit failure**：传输失败一律记 `AUDIT_EXECUTED = NO` / `VERDICT = NOT_AVAILABLE` 并 fail-closed，**不得**把该次运行记为 PASS 或 FAIL

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> 
> 
> **关键分歧**：
> 
> 
> **标尺**：[[]]
