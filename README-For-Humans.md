# SIFE — 给人类的说明

## 这是什么

SIFE（System Issue Feedback Engine）是一套系统问题反馈引擎。你的 Hermes、Notion、Obsidian、脚本出故障——这里记一笔。每次修完沉淀成校准卡，下次同样问题来了秒识别。

它不是内容判断系统（那个归主账号），只做一件事：**把每次系统故障变成可复用的防再发资产**。

## 四张核心卡片

| 卡 | 什么时候建 | 一句话 |
|:---|:---|:---|
| **问题卡 (P)** | 系统出故障了 |「Hermes 把 API 空返回当成数据为空」 |
| **修改卡 (C)** | 你决定怎么修 |「在 memory 写入传感器不确定性原则」 |
| **校准卡 (CAL)** | 修完了沉淀原则 |「AI 自报不可信——验收只认硬凭据」 |
| **元卡 (M)** | 每月体检 |「复发率降了没、MTTR 缩短没、CAL 命中率升了没」 |

## 一个故障怎么走到一条规则

```
系统故障 → P 卡（定 severity）
    ↓
风险矩阵判升级（S1 一次即升）
    ↓
C 卡修复 → CAL 沉淀
    ↓
KEDB 登记（下次同样故障秒匹配）
    ↓
Meta 月度复查 4 指标
    ↓
S1 走方向阀 → control-plane rule_candidate
```

## 怎么用

```bash
cd ~/Desktop/系统问题反馈引擎

# 1. 发现系统故障 → 建问题卡
python3 scripts/new_card.py problem "故障标题"

# 2. 打开文件，填 severity + 症状 + 触发条件

# 3. 设计方案 → 建修改卡
python3 scripts/new_card.py change "修复方案"

# 4. 修完沉淀 → 建校准卡
python3 scripts/new_card.py calibration "标尺名称"

# 5. 登记 KEDB
# 编辑 known_error_db.json，新增已知错误条目

# 6. 月末体检
# 建元卡，读出 4 指标
```

## 三个铁律

1. **先查 KEDB 再建 P 卡** — 同样问题不建重复卡，hit_count+1
2. **S1 一次即升** — 致命问题不等复发，直接走方向阀
3. **校准卡要回答「你到底拦住了几次」** — hit_count 是 CAL 唯一硬指标

## 更多

- `config/` — 三域说明、防腐层、CAL 引用规则
- `10-Principles/` — 系统核心原则
- `hermes-v2/` — Hermes 防瞎编验收测试套件
- `schema.json` — 卡片字段定义 (v3.1.1)
- `known_error_db.json` — 已知错误库
