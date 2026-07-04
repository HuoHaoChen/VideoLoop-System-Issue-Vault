---
id: ""
type: meta
title: ""
domain: 系统
period: ""
status: 进行中
recurrence_rate: ""
mttd: ""
mttr: ""
cal_hit_rate: ""
kedb_reviewed: []
kedb_closed: []
kedb_recurred: []
created: ""
tags: [meta, 月度复盘]
---

# 📊 M 元卡：月度复盘

==进行中== · 系统 · <kbd></kbd>

---

## 一、4 个引擎健康指标

| 指标 | 本月读数 | 上月 | 趋势 | 说明 |
|------|---------|------|------|------|
| 复发率 | | | | 已修复问题中发生复发的比例 |
| MTTD 检出时延 | | | | 问题发生→P 卡建立的平均时间 |
| MTTR 修复时长 | | | | P 卡建立→C 卡结案的平均时间 |
| CAL 命中率 | | | | CAL 成功拦截复发的比例 |

> 变好方向：复发率↓ / MTTD↓ / MTTR↓ / CAL命中率↑

---

## 二、KEDB 复查

### 本月复查条目

| KEDB ID | 症状简述 | 永久修复状态 | 本月是否有复发 | 操作 |
|---------|---------|-------------|--------------|------|
| | | | | |

### 可结案条目

| KEDB ID | 结案理由 |
|---------|---------|
| | |

### 复发条目（需重新评估）

| KEDB ID | 复发次数 | 是否触发升级 |
|---------|---------|-------------|
| | | |

---

## 三、本月新增/变更

### 新增 P 卡

```dataview
TABLE status AS "状态", ptype AS "问题类型"
FROM "20-Cards"
WHERE type = "problem" AND created >= date({{period}}-01) AND created < date({{period}}-01) + dur(1 month)
SORT created DESC
```

### 新增 C 卡

```dataview
TABLE status AS "状态", verdict AS "判定"
FROM "20-Cards"
WHERE type = "change" AND created >= date({{period}}-01) AND created < date({{period}}-01) + dur(1 month)
SORT created DESC
```

### 新增/更新 CAL 卡

```dataview
TABLE status AS "状态", method AS "方法"
FROM "20-Cards"
WHERE type = "calibration" AND created >= date({{period}}-01) AND created < date({{period}}-01) + dur(1 month)
SORT created DESC
```

---

## 四、引擎判断

> 这个月引擎整体是在变好、持平、还是变差？为什么？

---

> [!note]- 过程层
> M 元卡 = 引擎月度体检卡，不是普通复盘。
> 核心职能：每月读出 4 个指标 + 复查 KEDB。
> 禁止误删/误标为非系统域。
