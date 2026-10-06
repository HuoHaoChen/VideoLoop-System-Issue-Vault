---
id: C-20260911-100013
type: change
title: Hermes 默认模型从 codex-auto-review 切到 gpt-5.6-terra 并加 DeepSeek 官方 fallback
domain: 待分类
problems: [P-20260911-092711]
status: 已应用待观察
baseline_window: 修复前 hermes -z 走 apikey.fun 连续多日 502 失败（agent.log 62 条 Upstream access forbidden）
minimum_effect: hermes -z 端到端连续 3 次返回预期 token，且无 502
confounds: 中转站通道状态本身会漂移，无法排除"恰好在修复同时通道恢复"
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
created: 2026-09-11
updated: 2026-09-11
tags: [change]
---

# 🔵 Hermes 默认模型从 codex-auto-review 切到 gpt-5.6-terra 并加 DeepSeek 官方 fallback

> [!question] 一句话
> apikey.fun 的 26 个模型里只有 `gpt-5.6-terra` / `gpt-5.5` / `gpt-6-astra` 三条通道是活的，
> 而 Hermes 默认压在死掉的 `codex-auto-review` 上；把默认切到活通道即可，**不需要换掉这个供应商**。

---

> [!danger] 改动
> **改前**：
> ```yaml
> model:
>   default: codex-auto-review        # ← 死通道，0/2
>   provider: custom:apikey-fun
> providers:
>   apikey-fun:
>     model: gpt-5.6                  # ← 死通道，0/5
> fallback_providers: []
> ```
> **改后**：
> ```yaml
> model:
>   default: gpt-5.6-terra            # ← 活通道，流式 5/5
>   provider: custom:apikey-fun       # provider / base_url / api_key 均不变
> providers:
>   apikey-fun:
>     model: gpt-5.6-terra
> fallback_providers:
>   - provider: deepseek
>     model: deepseek-v4-pro          # ← DeepSeek 官方直连，异源兜底
> ```
> 注：`fallback_providers` 是现行 key，旧的 `fallback_model` 已被 Hermes 标记为 legacy
> （`hermes_cli/fallback_cmd.py::_write_chain` 写入时会 `pop("fallback_model")`，只保留一个事实源）。

---

## ✅ 怎么做

- [x] 备份：`cp -p config.yaml config.yaml.bak.dsh-20260911-095111`
- [x] `hermes config set model.default gpt-5.6-terra`
- [x] `hermes config set providers.apikey-fun.model gpt-5.6-terra`
- [x] `hermes config set fallback_providers '[{"provider":"deepseek","model":"deepseek-v4-pro"}]'`
- [x] 回读校验：`hermes config get model.default` 等 5 项确认写入
- [x] 端到端复跑 3 次：`hermes -z "Reply with exactly: E2E-N-OK"` → 3/3 返回预期 token
- [x] `hermes config check` 无报错
- [ ] **待人工**：观察数日，确认中转站通道漂移后不再静默整轮失败
- [ ] **待决定**：是否把 `providers.apikey-fun.models` 收敛为仅 3 个活模型，
      并关掉 `discover_models`，以免选择器继续展示 23 个死通道误导选择

---

> [!success] 预测
> 1. 默认模型走通后，`agent.log` 中 apikey.fun 的 502 应从"每轮都有"降到接近 0。
> 2. 若中转站把 `gpt-5.6-terra` 通道也关掉，`fallback_providers` 应让对话落到 DeepSeek 官方，
>    **表现为会话仍能完成、但模型自述或响应风格改变**，而不是整轮失败。
> 3. 若几天后再次出现大面积 502，说明"通道存活集合"已漂移，
>    **此时正确动作是重新扫描存活通道，而不是换供应商**——这正是本卡要防止的复发路径。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 用户明确要求"apikey.fun 是第三方供应商的 gpt，给 hermes 接入并确认能用"，
> 目标是**让这个供应商在 Hermes 里可用**，不是换掉它。
> 所以选最小改动：只把默认指针从死通道挪到活通道，provider 凭证/端点全部不动。
> 加 fallback 是因为该中转站通道会漂移，需要有异源兜底（DeepSeek 官方已独立验证可用）。
>
> **赌的假设**
> - 赌 `gpt-5.6-terra` 的存活不是瞬时窗口，而是相对稳定的通道（流式 5/5 支持这一点，但样本小）。
> - 赌 Hermes 主循环走流式（日志证实 `chat_completion_stream_request`），
>   所以只需关心流式可用性；若日后 Hermes 改用非流式，存活通道会缩到可能只剩 `gpt-5.5`。
> - 赌 `fallback_providers` 的触发的确是"主通道 502 时"——**未实测**，见问题卡「可能偏差」。
>
> **标尺**
> [[模型可用性判定的最小充分证据]]
