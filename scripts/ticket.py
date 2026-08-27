#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 统一问题反馈引擎 v4：30 秒建卡、补充解法与查看待解决问题。
# 用法：
#   python3 scripts/ticket.py "标题" [--症状 TEXT] [--解决 TEXT] [--域 系统|工作|认知]
#       [--工具 dsh|codex|gpt|hermes|human|other]
#   python3 scripts/ticket.py solve <ID或文件名片段> "解法"
#   python3 scripts/ticket.py list [--待解决]
#   python3 scripts/ticket.py verify <ID或文件名片段> 有效|无效
# 示例：
#   python3 scripts/ticket.py "接口超时" --症状 "请求 30 秒后失败" --域 系统 --工具 codex
#   python3 scripts/ticket.py solve P-20260827 "增加 10 秒超时和重试"

import argparse
import datetime
import glob
import importlib.util
import json
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(ROOT, "20-Cards")
MATCH_MIN = 4
DOMAIN_MAP = {"工作": "运营", "系统": "系统", "认知": "认知"}
PENDING_STATUSES = {"未处理", "设计中", "执行中", "观察中"}


def load_module(name, path):
    """按本仓库脚本约定，从同目录 Python 文件载入模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NEW_CARD = load_module("new_card", os.path.join(ROOT, "scripts", "new_card.py"))
KEDB = load_module("kedb", os.path.join(ROOT, "scripts", "kedb.py"))
TOOL_VALID = NEW_CARD.TOOL_VALID
RECORDER = NEW_CARD.RECORDER


def now_text():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def print_usage():
    print("""用法：
  python3 scripts/ticket.py \"标题\" [--症状 TEXT] [--解决 TEXT] [--域 系统|工作|认知]
      [--工具 dsh|codex|gpt|hermes|human|other]
  python3 scripts/ticket.py solve <ID或文件名片段> \"解法\"
  python3 scripts/ticket.py list [--待解决]

示例：
  python3 scripts/ticket.py \"接口超时\" --症状 \"请求 30 秒后失败\" --域 系统 --工具 codex
  python3 scripts/ticket.py solve P-20260827 \"增加 10 秒超时和重试\"
  python3 scripts/ticket.py list --待解决
  python3 scripts/ticket.py verify P-20260827 有效""")


def find_kedb_match(text):
    """返回得分最高且达到阈值的 KEDB 条目；无命中时返回 (None, 0)。"""
    query_tokens = KEDB.tokenize(text)
    best_entry, best_score = None, 0
    for entry in KEDB.load_db()["entries"]:
        score, _ = KEDB.score_entry(query_tokens, entry)
        if score > best_score:
            best_entry, best_score = entry, score
    if best_entry is not None and best_score >= MATCH_MIN:
        return best_entry, best_score
    return None, best_score


def append_ticket_notes(path, symptom, solution):
    """将 ticket 的直录文本追加到卡片正文，保留 new_card 的原有模板。"""
    with open(path, "a", encoding="utf-8") as handle:
        if symptom:
            handle.write("\n## 📋 症状（ticket 直录）\n\n" + symptom + "\n")
        if solution:
            handle.write("\n## ✅ 解决（ticket 直录）\n\n" + solution + "\n")


def create_ticket(args):
    """执行默认建卡入口。"""
    tool = args.tool
    if tool not in TOOL_VALID:
        print("WARN 未知 --工具 值: %s → 回退 human" % tool, file=sys.stderr)
        tool = "human"

    symptom = args.symptom or ""
    solution = args.solution or ""
    matched_entry, _ = find_kedb_match(args.title + " " + symptom)

    extra = {
        "domain": DOMAIN_MAP.get(args.domain, "待分类"),
        "severity": "待定",
        "solution": solution,
        "solution_status": "已解决" if solution else "待解决",
        "detected_at": now_text(),
    }
    if matched_entry is not None:
        extra["ke_ref"] = matched_entry.get("known_error_id", "")
        print("⚠️ 命中已知错误 %s（domain=%s）：方案：%s —— 复发！已挂 ke_ref" % (
            matched_entry.get("known_error_id", "-"),
            matched_entry.get("domain", "-"),
            matched_entry.get("workaround", ""),
        ))

    path, card_id = NEW_CARD.build_card("problem", args.title, tool, extra)

    # 去重：build_card 写死了 domain: 待分类，extra 已带真实域时删掉硬编码行
    if extra.get("domain") not in (None, "", "待分类"):
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        content = content.replace("domain: 待分类\n", "", 1)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)

    if solution:
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        content = content.replace("status: 未处理", "status: 已解决")
        content = content.replace("process_captured: false", "process_captured: true")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)

    append_ticket_notes(path, symptom, solution)
    print("卡ID: %s" % card_id)
    print("文件路径: %s" % path)
    print("KEDB 命中: %s" % (matched_entry.get("known_error_id") if matched_entry else "否"))
    print("解决状态: %s" % ("已解决" if solution else "待解决"))
    return 0


def parse_frontmatter(content):
    """解析卡片开头的简单 YAML frontmatter（每行 key: value）。"""
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", content, re.S)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def scan_cards():
    """列出 20-Cards 下所有 Markdown 卡片（包括分目录存放的卡片）。"""
    pattern = os.path.join(CARDS_DIR, "**", "*.md")
    return sorted(glob.glob(pattern, recursive=True))


def read_card(path):
    with open(path, encoding="utf-8") as handle:
        content = handle.read()
    return content, parse_frontmatter(content)


def matching_cards(selector):
    """按 ID 精确、ID 前缀、文件名包含片段的优先级寻找候选卡。"""
    cards = []
    for path in scan_cards():
        _, frontmatter = read_card(path)
        cards.append((path, frontmatter))

    exact = [(path, fm) for path, fm in cards if fm.get("id") == selector]
    if exact:
        return exact
    prefix = [(path, fm) for path, fm in cards if fm.get("id", "").startswith(selector)]
    if prefix:
        return prefix
    return [(path, fm) for path, fm in cards if selector in os.path.basename(path)]


def set_or_insert(lines, key, value, after_key=None):
    """更新 frontmatter 字段；字段不存在时插入到指定字段之后。"""
    prefix = key + ":"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = key + ": " + value
            return

    insert_at = len(lines)
    if after_key is not None:
        anchor = after_key + ":"
        for index, line in enumerate(lines):
            if line.startswith(anchor):
                insert_at = index + 1
                break
    lines.insert(insert_at, key + ": " + value)


def update_solution_frontmatter(content, solution):
    """写入 solve 所需字段，同时保留卡片正文和其他 frontmatter 原样不动。"""
    match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n?)(.*)$", content, re.S)
    if not match:
        raise ValueError("卡片没有可更新的 frontmatter")

    lines = match.group(2).splitlines()
    set_or_insert(lines, "solution", solution, after_key="title")
    set_or_insert(lines, "solution_status", "已解决", after_key="solution")
    set_or_insert(lines, "status", "已解决", after_key="solution_status")
    set_or_insert(lines, "process_captured", "true", after_key="status")
    set_or_insert(lines, "resolved_at", now_text(), after_key="process_captured")
    return match.group(1) + "\n".join(lines) + match.group(3) + match.group(4)


def print_candidates(candidates):
    print("匹配到多个卡片，未修改：")
    for path, frontmatter in candidates:
        print("- %s | %s | %s" % (
            frontmatter.get("id", "-"),
            frontmatter.get("title", os.path.basename(path)),
            path,
        ))


def solve_ticket(selector, solution):
    candidates = matching_cards(selector)
    if not candidates:
        print("ERROR 未找到匹配卡片：%s；请用 list 查看。" % selector, file=sys.stderr)
        return 2
    if len(candidates) > 1:
        print_candidates(candidates)
        return 1

    path, frontmatter = candidates[0]
    content, _ = read_card(path)
    try:
        updated = update_solution_frontmatter(content, solution)
    except ValueError as error:
        print("ERROR 无法更新 %s：%s" % (path, error), file=sys.stderr)
        return 1
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
    print("已解决: %s" % frontmatter.get("id", os.path.basename(path)))
    print("文件路径: %s" % path)
    return 0


def list_tickets(pending_only):
    rows = []
    for path in scan_cards():
        _, frontmatter = read_card(path)
        solution_status = frontmatter.get("solution_status", "")
        status = frontmatter.get("status", "")
        if pending_only and not (
            frontmatter.get("type") == "problem"
            and (solution_status == "待解决"
                 or (not solution_status and status in PENDING_STATUSES))
        ):
            continue
        rows.append((
            frontmatter.get("id", "-"),
            frontmatter.get("domain", "-"),
            solution_status or "-",
            frontmatter.get("source_tool", "-"),
            frontmatter.get("title", os.path.basename(path)),
        ))

    print("id | domain | 解决状态 | 来源 | 标题")
    print("--- | --- | --- | --- | ---")
    for row in rows:
        print(" | ".join(row))
    if not rows:
        print("（无匹配卡片）")
    return 0


def create_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("title")
    parser.add_argument("--症状", dest="symptom", default="", metavar="TEXT")
    parser.add_argument("--解决", dest="solution", default="", metavar="TEXT")
    parser.add_argument("--域", dest="domain", choices=tuple(DOMAIN_MAP), metavar="系统|工作|认知")
    parser.add_argument("--工具", dest="tool", default="human", metavar="TOOL")
    return parser


def verify_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("selector", metavar="ID或文件名片段")
    parser.add_argument("verdict", choices=("有效", "无效"), metavar="有效|无效")
    return parser


def verify_ticket(selector, verdict):
    """解法动态真相源确认：有效→已验证+hits+1；无效→被推翻。带 ke_ref 时同步 KEDB 信誉。"""
    candidates = matching_cards(selector)
    if not candidates:
        print("未找到匹配卡片: %s（可用 list 查看）" % selector)
        return 2
    if len(candidates) > 1:
        print("匹配到多个候选，请用更精确的 ID：")
        print_candidates(candidates)
        return 2
    path, fm = candidates[0]
    cid = fm.get("id", "?")
    with open(path, encoding="utf-8") as handle:
        content = handle.read()
    m = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n?)(.*)$", content, re.S)
    if not m:
        print("卡片 frontmatter 无法解析: %s" % path)
        return 2
    lines = m.group(2).splitlines()
    if verdict == "有效":
        hits = 0
        for line in lines:
            if line.startswith("solution_hits:"):
                try:
                    hits = int(line.split(":", 1)[1].strip() or 0)
                except ValueError:
                    hits = 0
        set_or_insert(lines, "solution_hits", str(hits + 1), after_key="solution_status")
        set_or_insert(lines, "solution_level", "已验证", after_key="solution_hits")
    else:
        set_or_insert(lines, "solution_level", "被推翻", after_key="solution_hits")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(m.group(1) + "\n".join(lines) + m.group(3) + m.group(4))
    ke_ref = fm.get("ke_ref")
    if ke_ref:
        db_path = os.path.join(ROOT, "known_error_db.json")
        db = json.load(open(db_path, encoding="utf-8"))
        for e in db["entries"]:
            if e.get("known_error_id") == ke_ref:
                if verdict == "有效":
                    e["solution_hits"] = int(e.get("solution_hits", 0)) + 1
                    e["solution_level"] = "已验证"
                else:
                    e["solution_level"] = "被推翻"
        json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        with open(db_path, "a", encoding="utf-8") as handle:
            handle.write("\n")
        print("KEDB %s 信誉已同步" % ke_ref)
    print("已验证 %s: solution_level=%s" % (cid, "已验证" if verdict == "有效" else "被推翻"))
    return 0


def solve_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("selector", metavar="ID或文件名片段")
    parser.add_argument("solution", metavar="解法")
    return parser


def list_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--待解决", dest="pending_only", action="store_true")
    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print_usage()
        return 2
    if argv[0] in ("-h", "--help"):
        print_usage()
        return 0

    if argv[0] == "solve":
        if len(argv) > 1 and argv[1] in ("-h", "--help"):
            print_usage()
            return 0
        args = solve_parser().parse_args(argv[1:])
        return solve_ticket(args.selector, args.solution)

    if argv[0] == "verify":
        if len(argv) > 1 and argv[1] in ("-h", "--help"):
            print_usage()
            return 0
        args = verify_parser().parse_args(argv[1:])
        return verify_ticket(args.selector, args.verdict)

    if argv[0] == "list":
        if len(argv) > 1 and argv[1] in ("-h", "--help"):
            print_usage()
            return 0
        args = list_parser().parse_args(argv[1:])
        return list_tickets(args.pending_only)

    args = create_parser().parse_args(argv)
    return create_ticket(args)


if __name__ == "__main__":
    sys.exit(main())
