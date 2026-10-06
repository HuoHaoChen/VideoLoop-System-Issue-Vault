---
id: P-20260913-212057
type: problem
title: 外部 AI 结论未在生产者侧原样落盘，跨工具 handoff 只能依赖转述，producer-level provenance 缺失
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
created: 2026-09-13
tags: [problem]
---

# 🟢 外部 AI 结论未在生产者侧原样落盘，跨工具 handoff 只能依赖转述，producer-level provenance 缺失

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 跨工具协作链上，外部 AI（GPT-C / GPT-B / Hermes）的产出**没有自动进入受管 evidence artifact**。
> 下游 handoff 只能依赖 User 或 DSH 的**转述**：SHA-256 只能锁定「落盘之后」的字节，
> **无法证明**落盘内容忠实于生产者原始输出。后果不是「不方便」，
> 而是 **producer-level provenance 在关键环节结构性缺失**。

---

> [!quote] 发生了什么

**事实链：**

```text
同一根因本轮至少出现四次：

1) GPT-C 的 FAIL_CLOSED ruling
   - 只存在于用户与 GPT-C 的对话中
   - DSH 检索 "SRC_01_NORMATIVE_MATERIALIZATION_AUTHORITY_NOT_DURABLY_BOUND"
     与 "Issue-A"/"ISSUE_A"/"ISSUE-A" → 命中 0 次
   - 后果：为 GPT-B 准备裁定包时第 6 项无法提供逐字原文，
     只能以「用户转述 + 明确来源标注」入包

2) GPT-B 的 authority adjudication
   - 检索 NEW_AUTHORITY_BINDING_REQUIRED / EXISTING_AUTHORITY_SUFFICIENT
     → 仅命中 DSH 自己的输出模板与 STATE.md，无 GPT-B 产出文件

3) GPT-B 的 V2 设计
   - 唯一可得来源是用户在任务指令中的转述
   - 固化后只能声明 faithfulness = CANNOT_BE_PROVEN_BY_HASH

4) Hermes 的 Issue-B 审计原始输出
   - 最初只存在于 /tmp/pinv5/hermes_issueb.out（2921 bytes）
   - 直到 PRE-WRITE 第 3 项要求「定位产生 PASS 的那份审计结果」才发现
     **它此前未落盘**——audit_results/ 里只有 prompt
   - 该件随后成为 PINNED_EFFECTIVE_V6 证据链的一环，
     差点出现「被 pin 的对象不存在」

共同形态：生产者产出 → 无受管落盘 → 只能转述 → 转述不可哈希验证。
```

---

| 判断 | 依据 |
|:-----|:-----|
| 这是**结构性缺口**，非偶发疏忽 | 四次分属三个生产者（GPT-C/GPT-B/Hermes）与两种通道（人肉转述、CLI），同一形态重复 |
| 转述可承载信息，但**不能**承载 provenance | 转述内容的哈希只锁落盘之后；生产者原输出与转述之间无机械可验关系 |
| 真实风险已发生 | PINNED_EFFECTIVE_V6 证据链中审计结果一度无 durable 来源，需 PRE-WRITE 阶段补救固化 |
| 与「哈希能否证明忠实原始出处」是同一问题 | Source Vault README 自述能力边界即包含『落盘内容忠实于原始出处』不可证 |

---

> [!warning] 可能偏差
> - 仅覆盖 DSH 可实测的四个实例；其他工具通道可能有更多未被观测的同类实例。
> - 「未落盘」基于 DSH 对 workspace 与 Source Vault 的检索，**不等于**本机任何位置都不存在。
> - 未评估强制自动落盘是否引入新风险（例如把不该持久化的中间产物写入受管库）。
> - severity 未定级（协议铁律：S1 只能由人定）。本卡倾向 S1/S2，需人确认。

---

> [!note]- 过程层（复盘时展开）
> **原话**（DSH 检索结论）：
> `"SRC_01_NORMATIVE_MATERIALIZATION_AUTHORITY_NOT_DURABLY_BOUND"  全库命中 0 次`
> `audit_results/ 中只有 prompt；原始输出仅存在于 /tmp/pinv5/hermes_issueb.out`
> 
> **关键分歧**：
> - 一度把「我有转述」当作「我有证据」。转述是信息通道，不是证据通道。
> - 直到 PRE-WRITE 强制要求「重算那一份审计的字节与哈希，不得依赖 DSH 摘要」，
>   缺口才暴露。**是流程强制项逼出了缺口，不是自觉发现的。**
> 
> **标尺**：[[C-20260913-212058]]
> **关联**：[[C-20260913-212058]] · [[P-20260911-140711]] · [[C-20260913-212101]]