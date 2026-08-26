# VideoLoop｜系统问题反馈引擎 (SIFE)

> System Issue Feedback Engine — 以系统自身故障、流程卡点、工具误判和 AI 越权为输入，用「捕获→定级→归因→修复→校准→防再发」闭环，把每次系统问题沉淀为可复用的系统校准卡。

```
SIFE（系统账号·独立隔离）
  P → 风险矩阵定级 → C → CAL → Meta → KEDB
        │（S1 致命一次即升，其余按严重度×频率矩阵）
        │（方向阀：借想法不搬确定性 + 人工确认）
        ▼
  control-plane / 13_rule_candidates / pending → RFC → dry-run → human owner → active
```

旧名 ~~内容判断校准引擎~~ 已废弃，内容判断职能归还主账号。

## 四库分工

| 库 | 定位 |
|----|------|
| Notion（主账号） | 灵感处理 + 当前运行记录 |
| SIFE（系统账号） | 系统问题反馈引擎 + 故障校准 |
| Hermes | 执行代理 + 安全封装 |
| GitHub (control-plane) | 规则版本源（schema / prompt / validator / changelog） |

## 核心闭环

**P → C → CAL → Meta** 结构互锁。C 卡必须显式引用 CAL（`calibration_ref`），不可只靠人工自觉。

## 三件真机器

| 机器 | 说明 |
|------|------|
| ① 严重度×频率风险矩阵 | S1 致命一次即升，S4 轻微批量处理，替代一刀切 repeat≥3 |
| ② 4 个真实指标 | 复发率 / MTTD / MTTR / CAL 命中率（月度 Meta 卡读出） |
| ③ 已知错误库 KEDB | 新问题先查库，命中则 repeat_count+1 自动套矩阵 |

## 卡型（仅系统域）

| 类型 | 命令 | 用途 |
|------|------|------|
| 系统问题卡 | `problem` | 捕获系统故障 — 现象+触发+证据，含 severity 定级 |
| 系统修复卡 | `change` | 设计方案 — 怎么改，judgment_change 必须带 calibration_ref |
| 系统校准卡 | `calibration` | 沉淀系统校准 — 含 hit_count 命中计数 |
| 月度元卡 | `meta` | 读出 4 指标 + 复查 KEDB |

## 目录结构

```
系统问题反馈引擎/
├── 10-Principles/     # 核心原则
├── 13_rule_candidates/# 规则候选池（方向阀入口）
├── 20-Cards/          # 活跃卡片库（P / C / CAL / M）
├── 30-Dashboards/     # 系统域看板
├── 90-Templates/      # 系统域模板
├── config/            # 配置与防腐层
├── hermes-v2/         # 防瞎编测试套件
├── scripts/           # 自动化脚本
├── schema.json        # 卡片 Schema (v3.1.1)
└── known_error_db.json# 已知错误库 KEDB
```

## 命令

```bash
建卡: python scripts/new_card.py problem "标题"
建卡: python scripts/new_card.py change "标题"
建卡: python scripts/new_card.py calibration "标题"
建卡: python scripts/new_card.py meta "标题"
查库: python scripts/kedb.py check "症状关键词"
入库: python scripts/ingest.py            # 00-Inbox 快速投递 → KEDB 查重 → 建 P 卡
校验: python scripts/validate_loop.py .
备份: python scripts/backup.py
```

## 边界

- 只存系统问题，不存运营/认知域内容（已纯化至主账号）
- 系统问题永不直接改 active 规则
- 升 rule_candidate 均经人工确认 + 方向阀
- 本库独立于 control-plane / runtime-export / knowledge-vault

## 四工具接入 (V3.2)

DSH / GPT / Codex / Hermes 遇到的问题与解决记录统一进入本引擎。新卡带 `source_tool` 字段（hermes/codex/dsh/gpt/human/other），KEDB 复发自动 repeat_count+1 并挂 `ke_ref`。接入协议见 `config/四工具反馈接入协议.md`（唯一事实源），覆盖看板见 `30-Dashboards/四工具覆盖看板.md`。
