## 3.2.0 (2026-08-26) — 四工具统一接入
- 定位扩展：DSH / GPT / Codex / Hermes 四工具的问题与解决记录统一进入本引擎
- problem/change/calibration 新增可选字段 source_tool（hermes/codex/dsh/gpt/human/other）
- problem 新增可选字段 ke_ref（KEDB 命中回指，复发先查库不重复建卡）
- 新增 scripts/kedb.py：KEDB 模糊查库（分词重叠匹配 + 复发升级提示）
- 新增 scripts/ingest.py：00-Inbox 快速投递 → KEDB 去重 → 自动建卡
- new_card.py 新增 --tool 参数（默认 human），自动写 source_tool 与 recorded_by 身份
- validate_loop.py 新增 source_tool 缺失告警（2026-08-26 后新卡生效，旧卡豁免）
- 新增 30-Dashboards/四工具覆盖看板.md；修复 5 个被 obsidian-git 冲突损坏的看板
- 新增 config/四工具反馈接入协议.md（四工具唯一事实源）；00-Inbox/ 投递目录
- known_error_db.json 升 1.1.0：全部条目补 source_tool

# CHANGELOG

## 3.1.1 (2026-07-02) — SIFE 迁库
- 整库正名为 VideoLoop｜系统问题反馈引擎 (SIFE)
- Git remote → VideoLoop-System-Issue-Vault
- README/README-For-Humans 重写为 SIFE 定位
- 旧名「内容判断校准引擎」废弃，职能归还主账号
- meta 新增 4 个月度指标字段：recurrence_rate / mttd / mttr / cal_hit_rate
- meta 新增 3 个 KEDB 复查字段：kedb_reviewed / kedb_closed / kedb_recurred
- M 元卡从普通复盘升格为引擎月度体检卡
- 90-Templates 新增 TEMPLATE-Meta.md

## 3.1.0 (2026-07-02) — SIFE 地基②
- problem 新增 `detected_at` 可选字段（问题实际发生时间，算 MTTD）
- change 新增 `resolved_at` 可选字段（C 卡结案时间，算 MTTR）
- calibration 新增 `hit_count` 可选字段（CAL 命中计数，算 CAL 命中率）

## 3.0.0 (2026-07-01)
- V3 升级：定位为「内容判断校准引擎」
- 新增 asset_type 字段
- 新增 change 的 calibration_ref 必填规则
- 新增 25-Assets / 50-TruthSource / 60-IP-Identity 目录

## 2.3.1 (2026-06-24)
- 新增 change 类型 cal_scan_done / cal_scan_at / cal_scan_result / referenced_cals

## 2.3 (2026-06-21)
- 新增 persona / values / worldview 三类实体
- inspiration 增加 persona_ref / value_ref / worldview_ref

## 2.3 (2026-06-18)
- Tabbit 修复版：C1-C3 + M5 + L1

## 2.2 (2026-06-13)
- 初始版本：problem / change / calibration / meta 四类实体 + 三域 + 防腐层
