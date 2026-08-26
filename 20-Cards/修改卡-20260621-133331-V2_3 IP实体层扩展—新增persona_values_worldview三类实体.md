---
id: C-20260621-133331
type: change
title: V2.3 IP实体层扩展—新增persona_values_worldview三类实体
domain: 系统
problems: ["P-20260621-133314"]
status: 已执行
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 待校准
calibrated: true
calibration_ref: CAL-20260613-1649
process_captured: true
recorded_by: hermes-A
evaluator: 第二裁判
due: 
created: 2026-06-21
tags: [change]
---

# 🔵 V2.3 IP实体层扩展—新增persona_values_worldview三类实体

> [!question] 一句话
> 在 VideoLoop 现有流程实体之外，新增「人格/价值观/世界观」三类 IP 身份实体 + 「40-Projects」产出层 + 捕获层协议，使系统从通用问题管理引擎升级为人格化第二大脑。

---

> [!danger] 改动
> **改前**：schema 仅有 problem/change/calibration/meta/inspiration 五类流程实体。无 IP 身份承载能力。
> **改后**：新增 persona（人格卡）/ values（价值观卡）/ worldview（世界观卡）三类实体 + 40-Projects 产出层 + 捕获层协议 + 漏斗检测看板。

---

## ✅ 怎么做

- [x] schema.json 新增 persona/values/worldview 三类实体（required + optional + field 定义）
- [x] schema.json inspiration 新增 persona_ref/value_ref/worldview_ref 可选关联字段
- [x] schema.json 增加 changelog 段（V2.2 / V2.3 / V2.3-IP 三次变更记录）
- [x] new_card.py 支持 persona/values/worldview 建卡（PER-/VAL-/WV- 前缀）
- [x] validate_loop.py 无需改动（动态读取 schema.json required 字段，新类型自动纳入校验）
- [x] 30-Dashboards 新增「世界观总览看板」「价值观总览看板」「漏斗检测」
- [x] 40-Projects/ 目录 + TEMPLATE-Project.md（含 Dataview 自动关联查询）
- [x] README.md V2.2→V2.3，补全 8 种卡类型说明
- [x] README-For-Humans.md 新增（给协作者的人类可读说明）
- [x] videoloop SKILL.md 新增「捕获层协议」+「IP Layer 优先级规则」

---

> [!success] 预测
> 如果此改动有效，则：
> 1. 用户可建 worldview 卡将 Inbox 中的「逆向思维 vs 两面性」显式建模为世界观实体
> 2. 后续 P 卡/C 卡/灵感卡可通过 worldview_ref 回挂到世界观，Dataview 看板自动显示引用热度
> 3. 月度 Meta 时可审计「哪些世界观高频使用，哪些从未出场」
> 4. 40-Projects 模板使 VideoLoop 与实际内容生产（选题/脚本）形成闭环

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> Opus 提案经 Hermes 审计后确认 20/27 条建议直接同意，5 条部分同意（字段设计修正），2 条不同意（前置结构化捕获、未定义 spec 的指令）。修正后方案与 VideoLoop 现有设计约束完全兼容——不改动任何已有卡片、不修改 validate_loop.py 逻辑、不破坏 Inbox 降级容灾设计。
> 
> **赌的假设**
> 1. 人格/价值观/世界观实体对内容创作者的 IP 一致性有实际价值（而非过度工程化）
> 2. Dataview 反向查询能替代手写引用列表，降低维护负担
> 3. 40-Projects 不会被闲置——用户会实际使用它连接 VideoLoop 和内容生产
> 
> **标尺**
> - 三个月后世界观卡是否被实际引用（通过引用统计看板验证）
> - 40-Projects 目录中是否有实际项目卡片（而非只有模板）
> - 月度 Meta 时能否基于 worldview_ref 统计做出「哪些世界观高频出场」的判断
