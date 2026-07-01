# VideoLoop V3.0｜内容判断校准引擎

> Content Judgment Calibration Engine — 活跃校准引擎 + 长期判断资产库

**VideoLoop 不被 Notion 替代，而是作为内容判断资产训练系统的活跃校准引擎继续运行。**

```
Notion         → 灵感处理 + 当前运行记录
VideoLoop      → 活跃校准引擎 + 判断资产沉淀
Hermes         → 执行代理 + 安全封装 + 卡片触发器
GitHub         → 规则版本源（schema / prompt / validator / changelog）
```

## 核心机制

**P → C → CAL → Meta** 结构互锁闭环。C 卡必须显式引用 CAL（`calibration_ref`），不可只靠人工自觉。

## 三域

| Domain | 中文 | 证据强度 | 说明 |
|--------|------|----------|------|
| 运营 | Operations | 强 — 可说「有效/已验证」 | 内容发布、数据反馈、用户反应 |
| 认知 | Cognition | 软 — 最多「方向性」 | 偏见、恐惧、误判、判断习惯 |
| 系统 | System | 隔离 | 工具、流程、脚本、配置 |

**防腐层：跨域可以借想法，不能借确定性。**

## 卡片类型（8 种 + 新资产容器）

| 类型 | 命令 | 用途 |
|:---|:---|:---|
| 问题卡 | `problem` | 捕获问题 — 什么不对 |
| 修改卡 | `change` | 设计方案 — 怎么改（涉及判断校准必须带 `calibration_ref`） |
| 校准卡 | `calibration` | 定义标尺 —「有效」是什么意思 |
| 元卡 | `meta` | 月度原则复盘 |
| 灵感卡 | `inspiration` | 捕获原始洞察 |
| 人格卡 | `persona` | 定义你的人格侧面 |
| 价值观卡 | `values` | 定义你的核心价值观 |
| 世界观卡 | `worldview` | 定义你解释世界的核心模型 |

**新资产类型（通过 `asset_type` 字段扩展承载，30 条验证后再决定是否独立卡型）：**

| asset_type | 用途 |
|:---|:---|
| `user_pain_hypothesis` | 用户困境假设 |
| `counterintuitive_judgment` | 反常识判断 |
| `boundary_condition` | 边界条件 |
| `failure_antipattern` | 失败反模式 |

## 目录结构

```
VideoLoop/
├── 00-Inbox/          # 降级后备入口（Notion 不可用时的原始捕获）
├── 10-Principles/     # 核心原则
├── 20-Cards/          # 活跃卡片库（P / C / CAL / Meta / INS / PER / VAL / WV）
├── 25-Assets/         # 内容判断资产沉淀（用户困境 / 反常识 / 边界 / 反模式）
├── 30-Dashboards/     # 看板
├── 40-Projects/       # 项目索引
├── 50-TruthSource/    # 动态真相源（只引用已校验资产，S2/S3 准入）
├── 60-IP-Identity/    # IP 实体层（人格 / 价值观 / 世界观）
├── 90-Templates/      # 模板
├── config/            # 配置与防腐层
├── scripts/           # 自动化脚本
└── hermes-v2/         # 安全封装层（防 AI 瞎编）
```

## 命令

```
建卡: python scripts/new_card.py problem "标题"
建卡: python scripts/new_card.py change "标题"
建卡: python scripts/new_card.py calibration "标题"
建卡: python scripts/new_card.py meta "标题"
建卡: python scripts/new_card.py inspiration "标题"
建卡: python scripts/new_card.py persona "人格侧面名"
建卡: python scripts/new_card.py values "价值观名"
建卡: python scripts/new_card.py worldview "世界观名"
校验: python scripts/validate_loop.py .
自检: python scripts/validate_loop.py --selftest
备份: python scripts/backup.py
```
