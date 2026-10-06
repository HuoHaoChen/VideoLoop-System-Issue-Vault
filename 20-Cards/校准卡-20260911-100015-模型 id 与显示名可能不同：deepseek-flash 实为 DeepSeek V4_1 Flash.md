---
id: CAL-20260911-100015
type: calibration
title: 模型 id 与显示名可能不同：deepseek-flash 实为 DeepSeek V4.1 Flash
domain: 待分类
source_tool: dsh
target: 模型身份识别
method: 预测校准
sample_size: 2 个独立信息源交叉验证
reliability_note: n 过小时只报方向，禁止写统计显著
validity_note: 评分与真实热度方向是否一致
status: 进行中
created: 2026-09-11
tags: [calibration]
---

# 🔵 模型 id 与显示名可能不同：deepseek-flash 实为 DeepSeek V4.1 Flash

> [!question] 校准什么
> 用户问"Hermes 有没有 DeepSeek V4.1 Flash"，我按**模型 id 字面**去找 `v4.1-flash`，
> 只找到 OpenRouter 的 `deepseek/deepseek-v4.1-flash`，于是断言
> **"DeepSeek 官方只有 deepseek-flash / deepseek-v4-pro，没有 V4.1 Flash，装不了"**。
>
> 这个结论是错的：**官方 API 的 `deepseek-flash` 就是 DeepSeek V4.1 Flash**，
> 也就是说 Hermes 的 `deepseek` 直连 provider 一直都有它（其列表里就有 `deepseek-flash`）。
> 我还据错误结论建了问题卡，需要一并更正。

---

> [!danger] 校准后的标尺
> **旧标尺（错误）**：
> 在 provider 的模型列表里搜目标版本的**字面字符串**（如 `v4.1-flash`）；
> 搜不到 → "没有这个模型"；
> 再去问官方端点要这个字面 id，被拒 → "官方没上线，装不了"。
>
> **新标尺**：
> 1. **版本号不等于模型 id**。厂商常用内部 id（`deepseek-flash`）承载对外品牌名
>    （"DeepSeek V4.1 Flash"），两者可以完全不同名。
>    判定"有没有某版本模型"**必须比对 display name，不能只比 id 字面**。
> 2. **优先查模型元数据源，而不是猜 id**：
>    - `~/.hermes/models_dev_cache.json`（models.dev 快照，带 `name` 字段）
>    - 各工具自己的目录（如 `~/.dsh/settings.yaml` 里 pi-ai provider 的 `models[].name`）
>    本次两者一致给出：`id=deepseek-flash` → `name=DeepSeek V4.1 Flash`。
> 3. **对官方 API 的报错要正确解读**：
>    DeepSeek 回 `The supported API model names are deepseek-flash, deepseek-v4-pro,
>    but you passed deepseek-v4.1-flash`——这只证明"**没有这个 id**"，
>    **不证明"没有这个模型"**。当时我把它读成了后者。
> 4. **别名要当成同一个模型处理**：本次确认的官方别名关系——
>    - `deepseek-flash` = DeepSeek V4.1 Flash（本体）
>    - `deepseek-v4-flash` = legacy alias，请求由 V4.1-Flash 服务
>    - `deepseek-v4-flash-vision-exp` = legacy alias，请求由 V4.1-Flash 服务
>    - `deepseek-v4-pro` = legacy，自 2026-09-14 12:00（北京）起路由到 V4.1-Flash
>    来源：`~/.dsh/settings.yaml::llm-deepseek.models[].description`
> 5. **下次再被问"某工具支不支持某模型"，先做三步**：
>    ① 拉该 provider 的模型列表 → ② 用 display name / models.dev 反查 id →
>    ③ 对候选 id 发一次真实请求确认能出 token。**做完再答。**

---

> [!warning] 可能偏差
> - 版本归属由 **models.dev 快照 + DSH 自身配置**两个来源交叉确认，
>   但**两者都可能是同一个上游数据源的二手转述**，严格说不是厂商一手公告。
>   若要 100% 确认，应查 DeepSeek 官方文档 / 更新日志。
> - 用"让模型自报版本"来验证**失败**了：模型在无系统提示时只是随机猜测，
>   `deepseek-flash` 自报时甚至猜了 "OpenAI GPT-4o"。**这条路不可用作证据。**
> - `deepseek-v4-pro` → V4.1-Flash 的迁移时间是 2026-09-14，**本卡记录时尚未生效**，
>   该条属于"即将生效的别名"，不能当成当前事实使用。
> - 该经验来自 DeepSeek 一家，其他厂商的 id/品牌名对应关系未验证。

---

## 📊 调用日志

<!-- 调用次数是健康信号，不是目标。高频≠好尺。零引用≠废尺。禁止按调用次数排名、禁止自动删卡。 -->

| 日期 | 场景 | domain | 事后验证 |
|:---|:---|:---|:---|
| 2026-09-11 | 判断 Hermes 直连 DeepSeek 是否有 V4.1 Flash，按 id 字面搜索得出"没有" | 模型身份识别 | 被 models.dev（name=DeepSeek V4.1 Flash）与 DSH 配置（name=DeepSeek-V4.1-Flash）双双推翻 |
| 2026-09-11 | 同上，用"模型自报版本"做二次验证 | 模型身份识别 | 方法本身无效，模型自报纯属猜测，不可作证据 |
