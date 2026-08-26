---
type: inbox
source_tool: human
severity: 待定
title:
created: date
---
# 四工具快速投递（30 秒版）

> DSH / GPT / Codex / Hermes 任一工具遇到真实故障、误判、越权或配置坑 → 复制本模板到 `00-Inbox/`，填下面几行，跑 `python3 scripts/ingest.py` 入库。
> 投递前先查库：`python3 scripts/kedb.py check "症状关键词"` — 命中 = 复发（ingest 自动 repeat_count+1 挂 ke_ref），不要重复建卡。

- [ ] source_tool：dsh / gpt / codex / hermes / human（谁遇到/谁上报）
- [ ] severity：S1 致命（一次即升）/ S2 严重 / S3 一般 / S4 轻微
- [ ] 一句话标题（frontmatter 的 title）

## 症状

（现象 + 触发条件 + 证据）

## 根因

（已定位就写；没定位写「未定位」）

## 解决记录

（已修 → 方案；未修 → 临时规避 + 下一步）
