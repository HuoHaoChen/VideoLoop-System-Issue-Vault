#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 一键建卡: python new_card.py problem "标题"
import sys, os, datetime

KIND = sys.argv[1] if len(sys.argv) > 1 else "problem"
TITLE = sys.argv[2] if len(sys.argv) > 2 else "未命名"
now = datetime.datetime.now()
PREFIX = {"problem":"P","change":"C","calibration":"CAL","meta":"M"}.get(KIND, "P")
CN = {"problem":"问题卡","change":"修改卡","calibration":"校准卡","meta":"元卡"}
cn_type = CN.get(KIND, "问题卡")
cid = PREFIX + "-" + now.strftime("%Y%m%d-%H%M")
cid_suffix = cid.split("-", 1)[1]
date = now.strftime("%Y-%m-%d")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "20-Cards", cn_type + "-" + cid_suffix + "-" + TITLE + ".md")

L = []
a = L.append
a("---"); a("id: " + cid); a("type: " + KIND); a("title: " + TITLE)
if KIND == "problem":
    a("domain: 待分类"); a("ptype: 待分类"); a("level: 待定"); a("status: 未处理")
    a("process_captured: false"); a("recorded_by: hermes-A"); a("due: "); a("owner: huohaochen")
elif KIND == "change":
    a("domain: 待分类"); a("problems: []"); a("status: 设计中"); a("baseline_window: "); a("minimum_effect: "); a("confounds: "); a("significance: 方向性"); a("borrows_from: 无")
    a("verdict: 待校准"); a("calibrated: false"); a("calibration_ref: "); a("process_captured: false")
    a("recorded_by: hermes-A"); a("evaluator: 第二裁判"); a("due: ")
elif KIND == "calibration":
    a("target: "); a("method: 预测校准"); a("sample_size: "); a("status: 进行中")
a("created: " + date); a("tags: [" + KIND + "]"); a("---"); a("")
if KIND == "problem":
    a("# \U0001f7e2 " + TITLE); a("")
    a("==待处理== · 待分类 · <kbd>未设</kbd>"); a("")
    a("---"); a("")
    a("> [!question]+ 结论"); a("> "); a(""); a("---"); a("")
    a("> [!quote] 发生了什么"); a("")
    a("**事实链：**"); a(""); a("```"); a(""); a("```"); a("")
    a("---"); a("")
    a("| 判断 | 依据 |"); a("|:-----|:-----|"); a("| ==判断== | 依据 |"); a("")
    a("---"); a("")
    a("> [!warning] 可能偏差"); a("> - "); a("> - "); a(""); a("---"); a("")
    a("> [!note]- 过程层（复盘时展开）"); a("> **原话**："); a("> "); a("> "); a("> **关键分歧**："); a("> "); a("> "); a("> **标尺**：[[]]")
elif KIND == "change":
    a("# \U0001f535 " + TITLE); a("")
    a("> [!question] 一句话"); a("> "); a(""); a("---"); a("")
    a("> [!danger] 改动"); a("> **改前**："); a("> **改后**："); a(""); a("---"); a("")
    a("## \u2705 怎么做"); a(""); a("- [ ] "); a("- [ ] "); a(""); a("---"); a("")
    a("> [!success] 预测"); a("> "); a(""); a("---"); a("")
    a("> [!note]- 过程层（复盘时展开）"); a("> **为什么选这个方案**"); a("> "); a("> "); a("> **赌的假设**"); a("> "); a("> "); a("> **标尺**"); a("> [[]]")
elif KIND == "calibration":
    a("target: "); a("method: 预测校准"); a("sample_size: "); a("status: 进行中")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("已创建", out)
