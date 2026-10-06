---
id: P-20260911-092711
type: problem
title: Hermes 默认模型 codex-auto-review 在 apikey.fun 上不可用（26 模型仅 3 个通道存活）
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: dsh-A
source_tool: dsh
solution: 把 model.default 与 providers.apikey-fun.model 从 codex-auto-review 改为 gpt-5.6-terra；并把 fallback_providers 设为 deepseek/deepseek-v4-pro
solution_status: 已解决
solution_hits: 2
solution_level: 已验证
resolved_at: 2026-09-25 08:34
due: 
owner: huohaochen
created: 2026-09-11
updated: 2026-09-11
tags: [problem, misdiagnosis-corrected]
---

# 🟢 Hermes 默认模型 codex-auto-review 在 apikey.fun 上不可用（26 模型仅 3 个通道存活）

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> apikey.fun（`https://aiapi888.setbug.cn/v1`）**本身可用**，但它的 26 个模型里**只有 3 个通道是活的**：
> `gpt-5.6-terra`、`gpt-5.5`、`gpt-6-astra`。其余 23 个（含 Hermes 原本默认指向的 `codex-auto-review`）
> 一律返回 HTTP 502 `Upstream access forbidden, please contact administrator`。
>
> **所以真正的故障是"默认模型选在了一条死通道上"**，不是"中转站全挂"。
> 已修复：默认模型改 `gpt-5.6-terra`，并加 DeepSeek 官方 `deepseek-v4-pro` 作 fallback。端到端 3/3 复跑通过。
>
> ⚠️ **本卡第一版结论（"全模型 502，需联系管理员"）是错的**，已按下文「误判复盘」更正。

---

> [!quote] 发生了什么

**事实链：**

```
1. 起因：用户要求把第三方供应商 apikey.fun 的 GPT 接入 Hermes 并确认可用。

2. 配置现状（~/.hermes/config.yaml）：
   model.default  = codex-auto-review      ← 指向 apikey.fun
   model.provider = custom:apikey-fun
   model.base_url = https://aiapi888.setbug.cn/v1
   providers.apikey-fun.model = gpt-5.6    ← 也是死通道

3. GET /v1/models → 200，26 个模型（静态列表，与可用性无关）

4. 非流式逐个调用 → 全部 502，故一度误判为"全挂"。

5. 转折点：改测**流式**（stream:true）后发现部分模型能出 token。

6. 量化实验（每模型 2~5 次，max_tokens=10）：
   ┌────────────────────┬──────────┬──────────┐
   │ 模型                │ 非流式    │ 流式     │
   ├────────────────────┼──────────┼──────────┤
   │ gpt-5.6-terra      │ 2/5      │ 5/5 ✅   │
   │ gpt-5.5            │ 4/5      │ 5/5 ✅   │
   │ gpt-6-astra        │   -      │ 2/2 ✅   │
   │ gpt-5.6            │ 0/5 ❌   │ 0/5 ❌   │
   │ codex-auto-review  │ 0/2 ❌   │ 0/2 ❌   │
   │ gpt-5.6-sol        │   -      │ 0/2 ❌   │
   │ gpt-5.6-sol-pro    │   -      │ 0/2 ❌   │
   │ gpt-5.6-luna       │   -      │ 0/2 ❌   │
   │ gpt-5.4 / -mini    │   -      │ 0/2 ❌   │
   │ gpt-5.3-codex      │   -      │ 0/2 ❌   │
   │ gpt-5.2 / gpt-6    │   -      │ 0/2 ❌   │
   └────────────────────┴──────────┴──────────┘
   → 26 个模型：3 活 23 死。存活通道流式比非流式稳（非流式常返回空 body）。

7. 独立佐证：
   - ~/.dsh/settings.yaml 里 DSH 给 apikeyfun 只注册了 4 个模型，
     其中 gpt-5.6-terra 正是用户当时在用的（截图里高亮选中）。
   - 无效 key → 401 INVALID_API_KEY；有效 key → 502。排除鉴权问题。

8. Hermes 主循环本来就走流式（日志里 chat_completion_stream_request），
   所以 Hermes 侧的失败全部源于"默认模型在死通道上"，与请求模式无关。

9. 修复并验证：
   hermes config set model.default gpt-5.6-terra
   hermes config set providers.apikey-fun.model gpt-5.6-terra
   hermes config set fallback_providers '[{"provider":"deepseek","model":"deepseek-v4-pro"}]'
   → hermes -z 端到端复跑 3 次：E2E-1-OK / E2E-2-OK / E2E-3-OK（3/3）
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==中转站可用，不是全挂== | 存活通道流式 5/5、非流式 4/5 稳定通过 |
| ==故障是"默认模型压在死通道"== | 26 模型中 23 个 502；默认的 codex-auto-review 正在这 23 个里 |
| ==不是鉴权问题== | 无效 key 得 401，有效 key 得 502（非 401/403） |
| ==不是本机网络问题== | 同机同时刻 OpenRouter / DeepSeek 官方均正常 |
| ==列表 ≠ 可用== | `/v1/models` 返回 200 且 26 个模型，但仅 3 个真能出 token |
| ==流式比非流式稳== | 存活通道流式 5/5，非流式出现空 body（2/5、4/5） |

---

> [!warning] 可能偏差
> - 存活通道会随时间漂移：中转站的上游通道状态是动态的，"3 活 23 死"是 2026-09-11 09:5x 的快照，明天可能变。**不要把它当长期事实。**
> - 每模型仅 2~5 次采样，`gpt-5.6-terra` 非流式 2/5 与 `gpt-5.5` 非流式 4/5 的差异可能是采样噪声而非真实差异。
> - 未拿到该站余额/额度接口（`/v1/dashboard/billing/*`、`/api/user/self` 均 404），**无法区分**"通道被封"与"余额/权限不足"。
> - 未测 images / audio 端点（gpt-image-1 / -1.5 / -2、gpt-4o-audio-preview、gpt-4o-realtime-preview）。
> - 未验证 fallback 真的会触发（需人为打断主通道才能测），仅确认配置已写入且通过 `hermes config check`。

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> 「apikye.fun 是第三方供应商的 gpt，給 hermes 可以介入并确认能用。」
> 被问"默认模型选哪个"时用户答：「apikye.fun 是第三方供应商，它的 gpt 模型」
> —— 即用户自始就要求"让 apikey.fun 的 GPT 能用"，而本卡第一版却给出"全挂、建议换掉该 provider"的反向结论。
>
>
> **关键分歧 / 误判复盘（这是本卡最该沉淀的部分）**：
> 第一版结论"全模型 502，需联系中转站管理员"是在**两个方法论错误**叠加下得出的：
>
> 1. **只测一种请求模式**：全程只发 `stream:false`。而该中转站存活通道在非流式下会返回空 body / 502，
>    流式才稳定。单模式采样把"部分可用"误读成了"全部不可用"。
> 2. **把一次窗口内的全失败外推为持续故障**：当时恰逢一批通道不健康，
>    我据此写下"至少 6 天全部失败、零成功轮次"——而日志里的 62 条 502，
>    实际只说明"这几条通道一直没通"，不能推出"整个中转站一直没通"。
>
> 另一个更值得警惕的点：**用户已经在另一处（DSH）正常使用 `gpt-5.6-terra`**，
> 截图里高亮的就是它。当时我把截图当成"界面而已、不代表可用"，
> 反而忽略了"用户手上正在跑的活通道"这条最强线索——
> **当用户指着某个界面说"它能用"时，应先假设用户是对的，再去解释差异，而不是先否定。**
>
>
> **标尺**：[[模型可用性判定的最小充分证据]]
