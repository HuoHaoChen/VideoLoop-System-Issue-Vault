---
id: P-20260928-151558
type: problem
title: Hermes 三方中转上游拒绝短输入导致辅助请求超时（Upstream rejected illegal short-input distillation or heartbeat probing）
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
created: 2026-09-28
tags: [problem]
---

# 🟢 Hermes 三方中转上游拒绝短输入导致辅助请求超时（Upstream rejected illegal short-input distillation or heartbeat probing）

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

## 追加观察 2026-09-28 15:58（第二轮实测，recorded_by=dsh-A，同一取证方，append-only）

1. **Hermes 侧密钥文件未变**：`~/.hermes/.env` 的 birth / modify / change 三者全部 = 2026-09-21 15:54:09，
   SHA256 `3874bf1ec3accd67a0c6ffa72611258a832f7bb015a6e8c622f9987130ea57c7`；
   `auth.json` 的 `credential_pool['custom:apikey.fun']` 为空数组 ⇒ 该 provider 的密钥只来源于 `key_env`。
   ⇒ 排查"换了密钥为什么没生效"时，**先看 `.env` 的 ctime 而不是 mtime**，可直接判定文件是否被重写过。

2. **新增故障形态（比 400 更隐蔽）**：高度重复的中文文本（1000/2000 字同句重复）请求
   **两次都 120s 静默超时、0 字节**，而同样长度但内容不重复的请求正常返回。
   ⇒ 上游反蒸馏检测在命中时**可能挂住连接而不是干净地报 400**；这会把 Hermes 的超时预算直接烧满。
   ⇒ 处理建议：大段重复/模板化文本先本地去重再送。

3. **短输入失败方式会漂移**：同一 "PONG" 探针，第一轮快速返回 400（明确拒绝），
   第二轮变成 30s 静默超时。⇒ 不能依赖该接口固定返回错误码来做健康检查。

4. **`logprobs` 静默失效**：请求带 `logprobs:true` 返回 200，但 `choices[].logprobs` 字段被丢弃。
   ⇒ 静默降级比报错更危险，不要依赖 logprobs 做任何判定。

5. **上游隐藏前缀不恒定**：同一 payload 的隐藏前缀第一轮在 4479–4605 之间漂移（极差 126），
   第二轮 10 次调用全部精确 = 4386（极差 0）。串行与并发结果一致 ⇒ 属时间维度的上游路由变化。
   ⇒ **不要把「固定 token 偏移」当作跨时间稳定的指纹**，只能在同一时段内使用。
