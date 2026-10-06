---
type: inbox
title: 安全验证返回值未传播导致 Annex false-pass
source_tool: codex
severity: 待定
domain: 系统
sig: annex-validator-return-propagation
---

## 症状

V1.4R 的 FIRST_TIME history verifier 返回 false，但调用方未将该返回值纳入最终 Gate；在合成合同中可能继续返回一致。独立反证还同时定位了 authority/freshness、外部 attestation 独立性、Decision task identity、exact change set 与状态矩阵缺口。

## 根因

安全关键 verifier 使用“写入 critical 数组 + 布尔返回”的混合协议，但调用点未统一消费所有 required 返回值。

## 解决记录

V1.4R Implementation Repair 将 required verifier 统一汇入 critical aggregation；FIRST_TIME false 明确追加 critical。新增 8 个反证回归及错误类型 fail-closed，26/26 本地合成案例通过。独立校准仍未完成，真实 Handoff 继续阻断。

## 证据

SharedHub/04_WORKSPACE/TASK-CAPABILITY-ADMISSION-HANDOFF-ANNEX-001/tests/run_annex_v14r_contract_boundary_tests.rb
SharedHub/05_AUDIT/PHASECAPABILITYADMISSIONHANDOFF/CAPABILITY_ADMISSION_HANDOFF_ANNEX_CLOSEOUT.md
