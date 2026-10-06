---
id: C-20260913-212101
type: change
title: 外部 AI 审计裁决必须做 verdict-block 解析与 provider-error 签名检测，退出码不可作为验收依据
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

# 🔵 外部 AI 审计裁决必须做 verdict-block 解析与 provider-error 签名检测，退出码不可作为验收依据

> [!question] 一句话
> 外部 AI 审计 CLI 的**退出码不能作为验收依据**。
> 裁决必须靠**解析 verdict block** 来判定；provider/传输层错误文本必须被识别为「审计未执行」。
> 条件不满足时：`AUDIT_EXECUTED = NO` / `AUDIT_VERDICT = NOT_AVAILABLE` / **FAIL_CLOSED**。

---

> [!danger] 改动
> **改前**：以 `hermes -z` 的退出码判定审计是否成功（EXIT=0 → 认为审计已执行）。
> **改后**：退出码**不作为验收依据**，只作辅助信号。必须检查：
> ```text
> 机械验收条件（全部满足才算 AUDIT_EXECUTED = YES）：
>  1. expected verdict block present         （预期的裁决块存在）
>  2. required verdict token parseable       （必需的裁决 token 可解析）
>  3. output minimum structural completeness （输出达到最低结构完整度）
>  4. explicit BLOCKERS field                （显式 BLOCKERS 字段存在）
>  5. provider-error signatures absent       （无 provider/传输层错误签名）
>  6. audit response != transport/runtime failure text
>                                            （输出不等于传输/运行时失败文本）
>
> 任一不满足：
>   AUDIT_EXECUTED = NO
>   AUDIT_VERDICT  = NOT_AVAILABLE
>   → FAIL_CLOSED（不得把该次运行记为 PASS/FAIL 裁决）
> ```


---

## ✅ 怎么做

- [x] 不只看退出码；先读 stdout 原文并检查是否含错误签名
- [x] 校验输出长度（本例 138 bytes 远低于正常裁决块，是显著信号）
- [x] 校验 verdict block 与 BLOCKERS 字段是否可解析
- [x] 判定「不是裁决」→ 不予采信 → 重试（本例第 2 次返回 2287-byte 完整裁决）
- [ ] **制度化**：把上述 6 条机械验收条件固化为派发包装器的统一前置校验
- [ ] 建立 provider-error 签名表（至少含 `API call failed after N retries`、`can't reach the model provider`、`rate limit`、`offline` 等）
- [ ] 区分「审计未执行」与「审计执行但返回 FAIL」——两者都必须 FAIL_CLOSED，但原因不同


---

> [!success] 预测
> 若执行机械验收条件，则「退出码 0 + provider 失败文本」不会再被记成审计成功，
> 证据链不会写入伪造的裁决。
> 反向预测：若只依赖退出码，则任何 provider/网络抖动都会在审计链上**静默降级为假 PASS**——
> 这是本卡认为风险最高的失效模式。
> 本轮已实际发生一次，被人工逐字阅读 stdout 拦下；
> **拦下它的是「读原文」这个习惯，不是任何自动机制。**


---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 因为「审计是否执行」是一个**可机械判定**的问题，不需要判断力：
> 裁决块存在与否、错误签名有无，都是字符串层面的事实。
> 把它做成机械门控，成本极低、收益极高。
> 
> **赌的假设**
> - 假设 provider-error 签名表足够覆盖常见失败；未覆盖的失败模式仍可能漏网——**未验证**。
> - 假设「最低结构完整度」可定义得足够一般（不同审计员输出格式不同）——**未验证**。
> 
> **标尺**：[[CAL-20260826-194451]] —— 异步 AI 任务验收看产物不看进程退出
> **关联（同根因）**：[[P-20260911-140711]]（WorkBuddy 实例） · [[CAL-20260826-194451]]
> **关联（同族不同根因，只关联不合并）**：
> - [[P-20260913-171938]] / [[C-20260913-172013]] —— Hermes CLI 派发通道的沙箱权限拒绝。
>   同为「派发 hermes 时外层信号与真实结果不一致」，但根因是**权限拒绝**（响亮失败），
>   与本卡的**退出码伪装成功**（静默失败）机制不同。
> - [[C-20260913-211150]] / [[CAL-20260913-211151]] —— 审计脚本外层包装引用未定义变量导致执行中止。
>   同属「包装层完整性」，但那是**包装自身报错**（响亮），本卡是**包装报错却被记为成功**。
> **关联（证据链族）**：[[P-20260913-212057]] · [[C-20260913-212058]]