#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# KEDB 已知错误库查库工具 — SIFE 铁律：新问题先查库，命中即复发，走 repeat_count 流程，不重复建卡
# 用法:
#   python kedb.py check "症状关键词"        # 模糊查库，按得分排序
#   python kedb.py check "症状" --top 3      # 只看前 3 条
#   python kedb.py list                      # 全部条目一览
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "known_error_db.json")

def load_db():
    if not os.path.exists(DB):
        print("WARN [KEDB缺失] 找不到 " + DB, file=sys.stderr)
        return {"entries": []}
    with open(DB, encoding="utf-8") as f:
        return json.load(f)

def tokenize(text):
    """中英混排分词：英文按字母数字串(≥2)，中文按单字+2字滑窗。"""
    text = (text or "").lower()
    toks = set(re.findall(r"[a-z0-9_./-]{2,}", text))
    for seg in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(seg) == 1:
            toks.add(seg)
        for i in range(len(seg) - 1):
            toks.add(seg[i:i+2])
    return toks

def score_entry(query_toks, entry):
    """查询 tokens 与 KEDB 条目（症状+根因+ID+文件名）的重叠得分。"""
    blob = " ".join(str(x) for x in [entry.get("症状", ""), entry.get("根因", ""),
                    entry.get("known_error_id", ""), entry.get("file", "")]).lower()
    toks = tokenize(blob)
    hit = query_toks & toks
    for q in query_toks:
        if len(q) >= 3 and q in blob:
            hit.add(q)
    return len(hit), hit

def check(query, top=0):
    db = load_db()
    q = tokenize(query)
    scored = []
    for e in db["entries"]:
        s, _ = score_entry(q, e)
        if s > 0:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("无命中 — 这是新问题，可以建卡。")
        return 0
    rows = scored if top <= 0 else scored[:top]
    for s, e in rows:
        print("KE %s  [severity=%s]  得分=%d  repeat=%d  [%s]" % (
            e.get("known_error_id"), e.get("severity"), s,
            int(e.get("repeat_count", 0)), e.get("永久修复状态", "-")))
        print("  症状: " + str(e.get("症状", ""))[:120])
        print("  根因: " + str(e.get("根因", ""))[:120])
        print("  方案: " + str(e.get("workaround", ""))[:120])
        print("  关联: P=%s C=%s  来源=%s" % (e.get("关联", {}).get("P"),
              e.get("关联", {}).get("C"), e.get("source_tool", "-")))
        print()
    best = scored[0][1]
    if best.get("severity") == "S1":
        print("注意: 命中 S1 条目 — 风险矩阵一次即升。复发请走 ingest.py（repeat_count+1 自动挂 ke_ref），不要重复建卡。")
    else:
        print("命中已有条目 = 复发。用 ingest.py 投递会自动 repeat_count+1 并挂 ke_ref；不要手工重复建卡。")
    return len(scored)

def list_entries():
    db = load_db()
    for e in db["entries"]:
        rel = e.get("关联", {})
        print("KE %s [%s] repeat=%d %s | P=%s C=%s | %s" % (
            e.get("known_error_id"), e.get("severity"),
            int(e.get("repeat_count", 0)), e.get("永久修复状态", "-"),
            rel.get("P"), rel.get("C"), str(e.get("症状", ""))[:60]))

def main():
    argv = sys.argv[1:]
    if not argv or argv[0] == "list":
        list_entries()
        return 0
    if argv[0] == "check":
        query = argv[1] if len(argv) > 1 else ""
        top = 0
        if "--top" in argv:
            i = argv.index("--top")
            if i + 1 < len(argv):
                try:
                    top = int(argv[i + 1])
                except ValueError:
                    top = 0
        if not query.strip():
            print('用法: python kedb.py check "症状关键词"', file=sys.stderr)
            return 2
        check(query, top)
        return 0
    print('用法: python kedb.py check "症状" | list', file=sys.stderr)
    return 2

if __name__ == "__main__":
    sys.exit(main())
