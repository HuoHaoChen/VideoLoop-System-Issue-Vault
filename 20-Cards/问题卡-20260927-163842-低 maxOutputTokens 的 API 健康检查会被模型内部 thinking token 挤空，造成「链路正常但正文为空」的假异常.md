---
id: P-20260927-163842
type: problem
title: 低 maxOutputTokens 的 API 健康检查会被模型内部 thinking token 挤空，造成「链路正常但正文为空」的假异常
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: true
recorded_by: dsh-A
source_tool: dsh
solution: 连通性/健康探针的输出预算不得贴着「期望正文长度」给（如 32），必须显著大于模型 reasoning 开销；且当 finishReason=MAX_TOKENS 且 usageMetadata.thoughtsTokenCount 接近 maxOutputTokens 时，应判「预算不足 / INCONCLUSIVE」，不得判「链路故障 / 供应商不可用」。探针载荷保持与业务无关的最小串。
solution_status: 待验证
solution_hits: 1
solution_level: 待验证
resolved_at:
due:
owner: huohaochen
created: 2026-09-27
tags: [problem, 模型调用, 探针设计]
---

# 🟢 低 maxOutputTokens 的 API 健康检查会被模型内部 thinking token 挤空，造成「链路正常但正文为空」的假异常

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 健康检查 / 连通性探针如果只看「HTTP 200 + 正文非空」，把 `maxOutputTokens` 设得贴着期望正文长度（例如只要 21 个字符就设 32），**可能被模型内部 reasoning（thinking）token 全部吃掉**，返回 `content` 为空、`finishReason = MAX_TOKENS`。
>
> 这会被朴素地误判成「模型不可用 / 链路故障」，但**链路其实是完全正常的**——错在**调用方的输出预算**没有把 reasoning 开销算进去。判 `BLOCKED` 属于把**自己的参数失误**记到**供应商**头上。

---

> [!quote] 发生了什么

**事实链（同一链路 · 同一模型 · 同一载荷，只改了一个参数）：**

```
首轮  2026-09-27 16:30  Gemini 官方直连  gemini-3.8-flash
  maxOutputTokens  = 32
  promptTokenCount = 14
  thoughtsTokenCount = 29          ← 思考几乎吃光全部预算
  totalTokenCount  = 43
  content          = {}            ← 空正文
  finishReason     = MAX_TOKENS
  HTTP             = 200   responseId = N9S4apyFG4HNrfcPwqHs2Qo   serviceTier = standard
  quota/billing/provider error = 无
  → 判定 INCONCLUSIVE（不是 provider failure）

重试  2026-09-27 16:37  Gemini 官方直连  gemini-3.8-flash   仅 maxOutputTokens 32 → 256
  maxOutputTokens  = 256
  thoughtsTokenCount = 93          ← 本轮思考更多！
  totalTokenCount  = 115
  content          = 'CALIBRATION_PREFLIGHT_OK'
  finishReason     = STOP
  HTTP             = 200   responseId = ndW4aqmnJ-Gy2-roPhJbogAQ
  → 判定 PASS

关键：重试时 thoughtsTokenCount = 93 > 首轮 29。
      若沿用 32 的预算，重试**依然**会是空正文 → 根因确为输出预算，与供应商无关。
```

> [!tip] 载荷
> 两次都是与业务完全无关的最小测试串：`Return exactly:\nCALIBRATION_PREFLIGHT_OK`。
> 未发送任何正式评测内容、题库、阈值或 oracle —— 探针与业务解耦。

---

| 判断 | 依据 |
|:-----|:-----|
| ==链路正常== | HTTP 200；`requested model = returned model = gemini-3.8-flash`；真实 `responseId`；`serviceTier = standard`；无 429 / 无 quota exhausted / 无 billing required / 无 provider unavailable |
| ==错在调用方输出预算== | 唯一变量 `maxOutputTokens` 32 → 256，结果从「空正文」变为「正确正文」；且 `thoughtsTokenCount` 与预算同数量级（29 vs 32） |
| ==不得判 BLOCKED== | 四项 BLOCKED 触发条件一项都未出现；判 provider failure 会**误伤供应商并掩盖我方配置问题** |
| ==必须判 INCONCLUSIVE== | 成功条件要求「返回有效内容」未满足，但无任何供应商侧故障信号 —— 既不是 PASS，也不是 FAIL/BLOCKED |

---

> [!warning] 可能偏差
> - **thinking 开销会波动**：同一载荷两次分别为 29 / 93 token。因此「预算该给多大」**没有硬下限**，只能说必须显著大于 reasoning 开销 + 期望正文长度；建议探针不低于 256。
> - **单次观察外推有限**：本次仅覆盖 Gemini 官方直连的一个模型，不能直接推出其他模型 / 其他网关的同类阈值，只能作为**设计原则**。
> - **不能仅凭 finishReason 判断**：`MAX_TOKENS` 也可能真的表示「正文过长被截断」，需结合 `thoughtsTokenCount` 与 `maxOutputTokens` 的大小关系才能区分「思考挤空」与「正文截断」。

---

> [!note]- 过程层（复盘时展开）
> **原话**（首轮如实上报，未甩锅给供应商）：
> > 根因如实归为 DSH 自身参数化失误：请求 maxOutputTokens = 32，而本次思考消耗 thoughtsTokenCount = 29，可见输出预算被挤空——不是供应商侧限制。
>
> **关键分歧**：首轮之后存在两条路——(A) 判 `BLOCKED`、上报「Gemini 不可用」；(B) 判 `INCONCLUSIVE`、如实标注为我方参数问题并申请一次放大预算的重试。
> 选了 (B)。事后重试证明 (B) 正确：链路一直是好的。
>
> **与 KE-006 的关系（近邻，但**不是**复发）**：
> - KE-006「Hermes 将 API 空返回误判为数据为空」的根因是**传感器不确定性**——把工具返回值当事实，无法区分「权限未传播导致读不到」与「真的空」；其 workaround 是「遇空结果加 ⚠️不排除是我读不到」。
> - 本条根因是**调用方输出预算未计入 reasoning token**，属可计算的配置问题，不是认知模型问题。
> - 且 KE-006 的 workaround **首轮已被遵守**（判 INCONCLUSIVE 而非「数据为空 / 链路故障」）。
> - 故判为**不同根因**，未走 ingest 复发路径。**是否合并请人工裁决**——本卡为 `source_tool=dsh` 自报，**不做自我评价**。
>
> **标尺**：[[健康检查必须能区分「对端坏」与「我没问好」]]
