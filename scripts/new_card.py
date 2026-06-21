#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 一键建卡: python new_card.py <type> "标题"
# 支持类型: problem / change / calibration / meta / inspiration / persona / values / worldview
# VideoLoop V2.3 — Tabbit 修复版 2026-06-18
# 修复内容: C1(calibration body双写) C2(meta缺period) C3(inspiration缺失) M5(文件名安全) L1(ID碰撞)
# 2026-06-21 新增: persona / values / worldview 三类 IP 实体
import sys, os, re, datetime

KIND  = sys.argv[1] if len(sys.argv) > 1 else "problem"
TITLE = sys.argv[2] if len(sys.argv) > 2 else "未命名"
now   = datetime.datetime.now()

# ── 全部八种类型 ───────────────────────────────────────────────
PREFIX  = {"problem":"P","change":"C","calibration":"CAL",
           "meta":"M","inspiration":"INS",
           "persona":"PER","values":"VAL","worldview":"WV"}.get(KIND, "P")
CN      = {"problem":"问题卡","change":"修改卡","calibration":"校准卡",
           "meta":"元卡","inspiration":"灵感卡",
           "persona":"人格卡","values":"价值观卡","worldview":"世界观卡"}
cn_type = CN.get(KIND, "问题卡")

# ── L1 修复：加入秒数，防同分钟 ID 碰撞 ─────────────────────────
cid        = PREFIX + "-" + now.strftime("%Y%m%d-%H%M%S")
cid_suffix = cid.split("-", 1)[1]
date       = now.strftime("%Y-%m-%d")
ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── M5 修复：过滤文件名特殊字符，防路径穿越 ─────────────────────
safe_title = re.sub(r'[/\\:*?"<>|\x00-\x1f.]', '_', TITLE).strip('_ ')[:80]
out = os.path.join(ROOT, "20-Cards",
                   cn_type + "-" + cid_suffix + "-" + safe_title + ".md")

L = []
a = L.append

# ════════════════════════════════════════════════════════════════
#  FRONTMATTER
# ════════════════════════════════════════════════════════════════
a("---")
a("id: "    + cid)
a("type: "  + KIND)
a("title: " + TITLE)

if KIND == "problem":
    a("domain: 待分类"); a("ptype: 待分类"); a("level: 待定"); a("status: 未处理")
    a("process_captured: false"); a("recorded_by: hermes-A")
    a("due: "); a("owner: huohaochen")

elif KIND == "change":
    a("domain: 待分类"); a("problems: []"); a("status: 设计中")
    a("baseline_window: "); a("minimum_effect: "); a("confounds: ")
    a("significance: 方向性"); a("borrows_from: 无")
    a("verdict: 待校准"); a("calibrated: false"); a("calibration_ref: ")
    a("process_captured: false"); a("recorded_by: hermes-A")
    a("evaluator: 第二裁判"); a("due: ")

elif KIND == "calibration":
    a("domain: 待分类")
    a("target: "); a("method: 预测校准"); a("sample_size: ")
    a("reliability_note: n 过小时只报方向，禁止写统计显著")
    a("validity_note: 评分与真实热度方向是否一致")
    a("status: 进行中")

elif KIND == "meta":
    a("period: " + now.strftime("%Y-%m"))
    a("status: 进行中")

elif KIND == "inspiration":
    a("raw: ")
    a("domain: 待分类"); a("status: 捕获"); a("target_exit: 待定")
    a("exit_status: 待出库"); a("recorded_by: hermes-A"); a("priority: 中")
    a("review_date: " + (datetime.date.today()
                         + datetime.timedelta(days=14)).isoformat())

elif KIND in ("persona", "values", "worldview"):
    a("statement: ")
    a("domain: 待分类")
    a("status: 草稿")
    if KIND == "worldview":
        a("method: ")

a("created: " + date)
a("tags: [" + KIND + "]")
a("---"); a("")

# ════════════════════════════════════════════════════════════════
#  BODY
# ════════════════════════════════════════════════════════════════
if KIND == "problem":
    a("# 🟢 " + TITLE); a("")
    a("==待处理== · 待分类 · <kbd>未设</kbd>"); a("")
    a("---"); a("")
    a("> [!question]+ 结论"); a("> "); a(""); a("---"); a("")
    a("> [!quote] 发生了什么"); a("")
    a("**事实链：**"); a(""); a("```"); a(""); a("```"); a("")
    a("---"); a("")
    a("| 判断 | 依据 |"); a("|:-----|:-----|"); a("| ==判断== | 依据 |"); a("")
    a("---"); a("")
    a("> [!warning] 可能偏差"); a("> - "); a("> - "); a(""); a("---"); a("")
    a("> [!note]- 过程层（复盘时展开）")
    a("> **原话**："); a("> "); a("> ")
    a("> **关键分歧**："); a("> "); a("> ")
    a("> **标尺**：[[]]")

elif KIND == "change":
    a("# 🔵 " + TITLE); a("")
    a("> [!question] 一句话"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 改动"); a("> **改前**："); a("> **改后**："); a(""); a("---"); a("")
    a("## ✅ 怎么做"); a(""); a("- [ ] "); a("- [ ] "); a(""); a("---"); a("")
    a("> [!success] 预测"); a("> "); a(""); a("---"); a("")
    a("> [!note]- 过程层（复盘时展开）")
    a("> **为什么选这个方案**"); a("> "); a("> ")
    a("> **赌的假设**"); a("> "); a("> ")
    a("> **标尺**"); a("> [[]]")

elif KIND == "calibration":
    a("# 🔵 " + TITLE); a("")
    a("> [!question] 校准什么"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 校准后的标尺")
    a("> **旧标尺**："); a("> **新标尺**："); a(""); a("---"); a("")
    a("> [!warning] 可能偏差"); a("> - "); a(""); a("---"); a("")
    a("## 📊 调用日志"); a("")
    a("<!-- 调用次数是健康信号，不是目标。高频≠好尺。零引用≠废尺。"
      "禁止按调用次数排名、禁止自动删卡。 -->"); a("")
    a("| 日期 | 场景 | domain | 事后验证 |")
    a("|:---|:---|:---|:---|")
    a("|  |  |  |  |")

elif KIND == "meta":
    a("# 📋 Meta · " + TITLE); a("")
    a("## 本月原则复审"); a("")
    a("- [ ] 系统核心原则是否还成立？")
    a("- [ ] schema 字段是否与实际使用保持一致？")
    a('- [ ] 有无长期搁置的"待分类"卡片需要归域？'); a("")
    a("---"); a("")
    a("## 月度统计"); a("")
    a("| 指标 | 数值 |"); a("|:---|:---|")
    a("| P 卡新增 | |"); a("| C 卡结案 | |")
    a("| CAL 调用次数 | |"); a("| INS 卡出库 | |"); a("")
    a("---"); a("")
    a("## 本月最大收获"); a(""); a("> "); a("")
    a("## 下月计划调整"); a(""); a("- ")

elif KIND == "inspiration":
    a("# 💡 " + TITLE); a("")
    a("> [!quote] 原始闪念（写入后不可改、永不删）"); a("> "); a("")
    a("---"); a("")
    a("> [!note]- 加工记录（加工时展开）")
    a("> **来源场景**：")
    a("> **初步方向**：")
    a("> **关联校准卡**：[[]]"); a("")
    a("---"); a("")
    a("## 出库状态"); a("")
    a("- [ ] 已关联 P 卡或 C 卡")
    a("- [ ] 已归属域")
    a("- [ ] 已复评（review_date 后）")

elif KIND == "persona":
    a("# 🎭 " + TITLE); a("")
    a("> [!question] 一句话定义"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 这个人格在内容中的表现")
    a("> **观众感受到的**："); a("> **背后的操作**："); a(""); a("---"); a("")
    a("| 场景 | 这个人格会怎么说/做 |")
    a("|:---|:---|")
    a("|  |  |"); a("")
    a("---"); a("")
    a("## 相关案例（通过 Dataview 反向查询自动生成）"); a("")
    a("```dataview")
    a("TABLE type AS 类型, domain AS 领域, status AS 状态")
    a("FROM \"20-Cards\"")
    a("WHERE persona_ref = this.id OR value_ref = this.id OR worldview_ref = this.id")
    a("SORT created DESC")
    a("```")

elif KIND == "values":
    a("# 🏛️ " + TITLE); a("")
    a("> [!question] 价值观声明"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 这个价值观如何影响内容决策")
    a("> **允许/鼓励的**："); a("> **禁止/回避的**："); a(""); a("---"); a("")
    a("> [!warning] 这个价值观可能在什么情况下被挑战"); a("> - "); a("")
    a("---"); a("")
    a("## 相关案例（通过 Dataview 反向查询自动生成）"); a("")
    a("```dataview")
    a("TABLE type AS 类型, domain AS 领域, status AS 状态")
    a("FROM \"20-Cards\"")
    a("WHERE persona_ref = this.id OR value_ref = this.id OR worldview_ref = this.id")
    a("SORT created DESC")
    a("```")

elif KIND == "worldview":
    a("# 🌐 " + TITLE); a("")
    a("> [!question] 世界观声明"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 这个世界观提供的解释框架")
    a("> **核心机制**："); a("> **可操作的结论**："); a(""); a("---"); a("")
    a("> [!success] 预测：如果这个世界观成立，在内容中应该观察到什么"); a("> "); a("")
    a("---"); a("")
    a("## 相关案例（通过 Dataview 反向查询自动生成）"); a("")
    a("```dataview")
    a("TABLE type AS 类型, domain AS 领域, status AS 状态")
    a("FROM \"20-Cards\"")
    a("WHERE persona_ref = this.id OR value_ref = this.id OR worldview_ref = this.id")
    a("SORT created DESC")
    a("```")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("已创建", out)
