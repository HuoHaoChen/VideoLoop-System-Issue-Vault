#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# KEDB 已知错误库查库工具 — SIFE 铁律：新问题先查库，命中即复发，走 repeat_count 流程，不重复建卡
# 用法:
#   python3 scripts/kedb.py check "症状关键词" [--域 系统|工作|认知] [--top N]
#   python3 scripts/kedb.py list
#   python3 scripts/kedb.py matrix
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "known_error_db.json")
DOMAIN_MAP = {"系统": "系统", "工作": "运营", "认知": "认知"}

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

def entry_domain(entry):
    """返回条目所属域；历史条目没有 domain 时按「系统」处理。"""
    return entry.get("domain") or "系统"

def repeat_count(entry):
    """读取复发次数，异常值按 0 处理，避免统计命令中断。"""
    try:
        return int(entry.get("repeat_count", 0))
    except (TypeError, ValueError):
        return 0

def check(query, top=0, domain=None):
    db = load_db()
    q = tokenize(query)
    scored = []
    for e in db["entries"]:
        if domain and entry_domain(e) != domain:
            continue
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
            repeat_count(e), e.get("永久修复状态", "-")))
        print("  方案: " + str(e.get("workaround", ""))[:120])
        print("  解法可信度: %s（事实验证有效 %s 次）%s" % (
            e.get("solution_level", "待验证"), e.get("solution_hits", 0),
            " ⚠️ 已被推翻，禁止推荐" if e.get("solution_level") == "被推翻" else ""))
        print("  症状: " + str(e.get("症状", ""))[:120])
        print("  根因: " + str(e.get("根因", ""))[:120])
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
        print("KE %s [%s] domain=%s repeat=%d %s | P=%s C=%s | %s" % (
            e.get("known_error_id"), e.get("severity"),
            entry_domain(e), repeat_count(e), e.get("永久修复状态", "-"),
            rel.get("P"), rel.get("C"), str(e.get("症状", ""))[:60]))

def matrix():
    """按完全相同的根因分簇，展示跨工具复发与工具分布。"""
    db = load_db()
    clusters = {}
    tool_counts = {}
    for entry in db["entries"]:
        root_cause = str(entry.get("根因", ""))
        clusters.setdefault(root_cause, []).append(entry)
        source_tool = str(entry.get("source_tool") or "-")
        tool_counts[source_tool] = tool_counts.get(source_tool, 0) + 1

    cross_tool_cluster_count = 0
    for root_cause, entries in clusters.items():
        source_tools = sorted({str(entry.get("source_tool") or "-") for entry in entries})
        is_cross_tool = len(source_tools) >= 2
        if is_cross_tool:
            cross_tool_cluster_count += 1
            print("⚠️ 跨工具复发")
        print("根因: " + root_cause)
        print("来源工具: " + ", ".join(source_tools))
        print("复发次数: %d" % sum(repeat_count(entry) for entry in entries))
        print("条目: " + ", ".join(
            "%s(%s)" % (entry.get("known_error_id", "-"), entry.get("severity", "-"))
            for entry in entries))
        print()

    tool_summary = ", ".join(
        "%s=%d" % (tool, tool_counts[tool]) for tool in sorted(tool_counts))
    print("汇总: 总簇数=%d，跨工具簇数=%d，各工具条目数=%s" % (
        len(clusters), cross_tool_cluster_count, tool_summary or "无"))

def parse_check_args(argv):
    """解析 check 参数，返回 (query, top, domain) 或抛出 ValueError。"""
    if not argv:
        raise ValueError("缺少症状关键词")

    query = argv[0]
    top = 0
    domain = None
    index = 1
    while index < len(argv):
        option = argv[index]
        if option == "--top":
            if index + 1 >= len(argv):
                raise ValueError("--top 需要 N")
            try:
                top = int(argv[index + 1])
            except ValueError:
                raise ValueError("--top 的 N 必须是整数")
            index += 2
        elif option == "--域":
            if index + 1 >= len(argv):
                raise ValueError("--域 需要 系统、工作或认知")
            requested_domain = argv[index + 1]
            if requested_domain not in DOMAIN_MAP:
                raise ValueError("--域 仅支持 系统、工作或认知")
            domain = DOMAIN_MAP[requested_domain]
            index += 2
        else:
            raise ValueError("未知参数: %s" % option)
    return query, top, domain

def print_usage(file=sys.stderr):
    print('用法: python3 scripts/kedb.py check "症状关键词" [--域 系统|工作|认知] [--top N]', file=file)
    print('      python3 scripts/kedb.py list', file=file)
    print('      python3 scripts/kedb.py matrix', file=file)

def main():
    argv = sys.argv[1:]
    if not argv or argv[0] == "list":
        list_entries()
        return 0
    if argv[0] == "check":
        try:
            query, top, domain = parse_check_args(argv[1:])
        except ValueError as error:
            print("参数错误: %s" % error, file=sys.stderr)
            print_usage()
            return 2
        if not query.strip():
            print_usage()
            return 2
        check(query, top, domain)
        return 0
    if argv[0] == "matrix" and len(argv) == 1:
        matrix()
        return 0
    print_usage()
    return 2

if __name__ == "__main__":
    sys.exit(main())
