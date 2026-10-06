---
id: C-20260913-172013
type: change
title: 派发 hermes CLI 前将 DSH 沙箱提权至 danger-full-access（或为 ~/.hermes/logs 开白名单）
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

# 🔵 派发 hermes CLI 前将 DSH 沙箱提权至 danger-full-access（或为 ~/.hermes/logs 开白名单）

> [!question] 一句话
> DSH 在 `workspace-write` 下无法启动 `hermes -z`（hermes 需写 `~/.hermes/logs/agent.log`）。派发 hermes 前把该命令的沙箱提到 `danger-full-access`；根治方向是为 `~/.hermes/**` 开运行期白名单。

---

> [!danger] 改动
> **改前**：直接以后台任务执行 `hermes -z "$(cat PROMPT.md)"`，在默认 `workspace-write` 策略下运行 → `EXIT=1`、stdout 0 字节。
> **改后**：同一命令原样重试，仅附 `sandbox_permissions=danger-full-access` + 一句理由 → `EXIT=0`，返回完整审计结论。
> **注意**：这是**规避**不是根治。真正的修复是为 hermes 运行期路径（至少 `~/.hermes/logs/`，可能还有 config/cache/secrets）开白名单，使其无需全域提权。

---

## ✅ 怎么做

- [x] 确认 stderr 而非只看 stdout（stdout 0 字节极易被误判成「审计无输出」）
- [x] 判定为沙箱 EPERM 而非工具崩溃（`--help` 可执行、报错指向写入路径）
- [x] 按「一次一提升」原样重试，申请最小可用更宽模式并附理由
- [x] 提权后验证 `EXIT=0` 且产出非空
- [ ] **根治**：探明 hermes 全部运行期写入路径，评估白名单方案是否可行（未做）
- [ ] 评估 `danger-full-access` 的实际风险面，给出更窄的替代（未做）

---

> [!success] 预测
> 提权后 hermes 可正常启动并返回审计结论。**已验证成立**：本次重审返回 `EXIT=0`、2699 字节、`POST_PIN_AUDIT_VERDICT = PASS`。
> 更长期预测：若不开白名单，任何「DSH 直调外部 AI 工具」的外部审计编排都会**静默失败**——这会直接侵蚀裁判独立性（外部通道断了却没人发现）。


---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 提权是当时唯一能在**不改变任务授权范围**的前提下恢复外部审计通道的动作。
> 用户明确要求 DSH 不得自审、必须直调 Hermes-B，因此「放弃外部审计退回自审」是**不可接受**的选项（违反裁判独立性），只能修通道。
> 
> **赌的假设**
> - 假设被拒路径只有日志一条，其余运行期路径都已在工作区内或已可写。**未验证**。
> - 假设 `danger-full-access` 的风险面在本任务内可接受（只读审计，未写 Source Vault）。该假设**未被独立评估**。
> 
> **标尺**
> [[裁判独立性协议]] —— 外部裁判通道不可用时，正确的动作是修复通道或如实上报，而不是让同工具顶替认证。
> 
> **关联**：[[P-20260913-171938]]