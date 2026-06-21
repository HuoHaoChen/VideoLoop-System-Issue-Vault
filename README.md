# VideoLoop V2.3

单一真相源 = 本仓库。卡片分「结论层（执行）」与「过程层（成长）」。
三域平权：每张卡用 domain 标注属于 运营 / 认知 / 系统，三类同等专业纳入。

## 卡片类型

| 类型 | 命令 | 用途 |
|:---|:---|:---|
| 问题卡 | `problem` | 捕获问题 — 什么不对 |
| 修改卡 | `change` | 设计方案 — 怎么改 |
| 校准卡 | `calibration` | 定义标尺 —「有效」是什么意思 |
| 元卡 | `meta` | 月度原则复盘 |
| 灵感卡 | `inspiration` | 捕获原始洞察 |
| 人格卡 | `persona` | 定义你的人格侧面 |
| 价值观卡 | `values` | 定义你的核心价值观 |
| 世界观卡 | `worldview` | 定义你解释世界的核心模型 |

## 命令

```
建卡: python scripts/new_card.py problem "标题"
建卡: python scripts/new_card.py calibration "标题"
建卡: python scripts/new_card.py persona "人格侧面名"
建卡: python scripts/new_card.py values "价值观名"
建卡: python scripts/new_card.py worldview "世界观名"
校验: python scripts/validate_loop.py .
自检: python scripts/validate_loop.py --selftest
备份: python scripts/backup.py
```
