---
id: C-20260913-212058
type: change
title: 外部 AI 返回即原样 capture → hash → managed identity；producer-native 与 envelope 必须分离
domain: 待分类
problems: []
status: 设计中
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 待校准
calibrated: false
calibration_ref: 
process_captured: false
recorded_by: dsh-A
source_tool: dsh
evaluator: 第二裁判
due: 
created: 2026-09-13
tags: [change]
---

# 🔵 外部 AI 返回即原样 capture → hash → managed identity；producer-native 与 envelope 必须分离

> [!question] 一句话
> 外部 AI 每返回一次结论就**立即原样落盘**为受管 evidence artifact 并记 hash；
> 后续任何包装（envelope / 转述 / 摘要）必须与该 raw artifact **身份分离**，不得冒充 producer-native。

---

> [!danger] 改动
> **改前**：外部 AI 返回直接进入对话，需要时由人/DSH 转述给下一环。落盘的常是**包装件**
> （DSH 写的 envelope/摘要）；raw 输出即便被内嵌也无独立身份。
> **改后**（目标形态）：
> ```text
> 外部 AI 返回
>   → 原样 capture 为独立文件（不做任何包装）
>   → 立即 sha256 + bytes
>   → 进入受管 identity/provenance
>   → 若确需 envelope/摘要，另建独立制品并在 provenance 显式区分：
>        role = RAW_PRODUCER_OUTPUT       （生产者原文）
>        role = AUDIT_EVIDENCE_ENVELOPE   （DSH 包装）
>        explicitly_not = RAW_PRODUCER_OUTPUT
> ```
> **禁止**：把 envelope 标注为与 raw 等同；在无 producer-native 落盘时声称 producer-native 来源。
> 若只能走回退路径（从 envelope 内嵌块抽取），provenance **必须**写明：
> ```text
> PRODUCER_NATIVE_EXPORT_CURRENTLY_AVAILABLE = NO
> RAW_OUTPUT_RECOVERED_FROM_MANAGED_ENVELOPE = YES
> ```


---

## ✅ 怎么做

- [x] 立即落盘外部 AI 返回（shell 重定向到**独立** raw 文件，而非只在 /tmp 或只在对话里）
- [x] 记录 raw 的 bytes + sha256
- [x] 为 raw 分配受管 Git blob 身份（与 envelope 不同 path / 不同 blob）
- [x] 机械校验 envelope 内嵌块 == raw artifact（逐字节）
- [x] 在 provenance 中显式区分 role 并禁止折叠
- [ ] **制度化**：把「外部 AI 返回 → 原样落盘」写进各工具通道固定步骤，不依赖 DSH 临场记得
- [ ] 为回退路径补一条**强制**声明（producer-native 不可得时必须显式否定）
- [ ] 评估 /tmp 作为暂存区的可靠性（本轮 2921-byte raw 曾只存于 /tmp，重启即失）


---

> [!success] 预测
> 若执行「原样落盘 + 独立身份」，跨工具 handoff 不再依赖转述，producer-level provenance 可机械验证。
> **已部分验证**：D3 工作流后段，Hermes Issue-B raw 输出被固化为独立受管制品
> （`EFFECTIVE-V6/HERMES_B_ISSUE_B_DESIGN_AUDIT_RAW.txt`，2921 bytes，blob `fef9f055…`），
> 并与 envelope 内嵌块机械比对为**逐字节相等**，因而能以
> `PRODUCER_NATIVE_EXPORT_CURRENTLY_AVAILABLE = YES` 声称真实的 producer-native 来源 ——
> 这是同一问题的**正面版本**，说明机制可行。
> 反向预测：若不制度化，下一个外部 AI 通道（GPT/Codex/Marvis）仍会在同一处断裂。


---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 缺口不在「有没有记录」，而在「记录能否证明来源」。因此关键不是多写文档，
> 而是把 raw 与 envelope 的**身份**分开，并让分离**机械可验**。
> 
> **赌的假设**
> - 假设外部 AI 返回可被原样捕获（人肉通道下需用户配合，尚无自动机制）——**未验证**。
> - 假设「原样落盘」不与各工具会话隐私/留存策略冲突——**未评估**。
> 
> **标尺**：[[CAL-20260826-194451]]（同为「以产物为准」家族）
> **关联**：[[P-20260913-212057]] · [[C-20260913-212101]]