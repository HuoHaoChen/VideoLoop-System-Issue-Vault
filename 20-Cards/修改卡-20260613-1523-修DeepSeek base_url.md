---
id: C-20260613-1523
type: change
title: 修DeepSeek base_url
domain: 系统
problems: [P-20260613-1510]
status: 执行中
baseline_window: 当前——模型报「无法访问外部网络」，web 工具调用失败
minimum_effect: 模型能成功调用 web_search 工具并返回搜索结果
confounds: DeepSeek API 服务本身波动；V4-pro 是否支持 function calling
status: 已结案
significance: 方向性
verdict: 有效
calibrated: true
calibration_ref: 浏览器成功访问HackerNews并返回搜索结果
process_captured: true
recorded_by: huohaochen
evaluator: 第二裁判
blind: true
observe_window: 0d
due: 2026-06-13
owner: huohaochen
created: 2026-06-13
tags: [change]
---

# 🔵 修 DeepSeek base_url

> [!question] 一句话
> 把 `base_url` 从 `https://api.deepseek.com/v1` 改成 `https://api.deepseek.com`，去掉多余的 /v1。

---

> [!danger] 改动
> **改前**：`base_url: https://api.deepseek.com/v1`
> **改后**：`base_url: https://api.deepseek.com`

---

## ✅ 怎么做

- [ ] ① `hermes config set model.base_url https://api.deepseek.com`
- [ ] ② `/reset` 重启会话
- [ ] ③ 问 DeepSeek：帮我搜一下今天的热点新闻

---

> [!success] 预测
> 模型能收到 web_search 工具，成功搜索并返回结果。

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> base_url 多一个 /v1 → Hermes 拼路径变成 /v1/v1/chat/completions → 404 → 工具列表传不到模型 → 模型说「上不了网」
> 
> **赌的假设**
> 去掉 /v1 后请求路径恢复正常，工具列表能正常传给 DeepSeek
> 
> **标尺**
> 模型是否成功调用 web_search 并返回真实搜索结果
