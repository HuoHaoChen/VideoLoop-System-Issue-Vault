#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 一键建卡: python new_card.py problem "标题"
import sys, os, datetime

KIND = sys.argv[1] if len(sys.argv) > 1 else "problem"
TITLE = sys.argv[2] if len(sys.argv) > 2 else "未命名"
now = datetime.datetime.now()
PREFIX = {"problem":"P","change":"C","calibration":"CAL","meta":"M"}.get(KIND, "P")
cid = PREFIX + "-" + now.strftime("%Y%m%d-%H%M")
date = now.strftime("%Y-%m-%d")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "20-Cards", cid + "-" + TITLE + ".md")

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
a("# " + TITLE); a("")
a("## 结论层（执行用）"); a("> "); a("")
a("## 过程层（成长用 · Hermes 追问后提炼，不是全文抄录）")
a("- 当时怪怪的原话："); a("- 为什么这么判："); a("- 追问暴露的关键分歧：")
a("- 用了哪把标尺： [[关联校准卡或原则]]"); a("- 可能偏差：")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("已创建", out)
