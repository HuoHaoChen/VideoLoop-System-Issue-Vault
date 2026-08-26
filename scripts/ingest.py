#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 四工具快速投递入库 — 扫描 00-Inbox/*.md → KEDB 查重 → 建 P 卡 → 移入 processed/
# 用法:
#   python ingest.py             # 处理 00-Inbox 全部投递件
#   python ingest.py --dry-run   # 只演练不落盘
# 投递件格式见 90-Templates/TEMPLATE-快速投递.md
# 铁律: 新问题先查 KEDB；命中则 repeat_count+1 并挂 ke_ref（复发不重复建卡）；
#       新条目不自动登记 KEDB（KEDB 由人工确认后录入，防止 AI 自报污染）。
import sys, os, re, json, glob, shutil, datetime, importlib.util

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX     = os.path.join(ROOT, "00-Inbox")
PROCESSED = os.path.join(INBOX, "processed")
DB        = os.path.join(ROOT, "known_error_db.json")
MATCH_MIN = 2   # 查询与 KEDB 条目共享 token 数 ≥ 2 判为命中

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

NEW_CARD = load_module("new_card", os.path.join(ROOT, "scripts", "new_card.py"))
KEDB     = load_module("kedb", os.path.join(ROOT, "scripts", "kedb.py"))

def parse_inbox(fp):
    with open(fp, encoding="utf-8") as f:
        raw = f.read()
    fm, body = {}, raw
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm, body

def pick_title(fm, body):
    t = (fm.get("title") or "").strip()
    if t:
        return t
    skip = {"症状", "根因", "解决", "解决记录", "修复", "标题", "备注", "证据", "事实链"}
    for line in body.splitlines():
        line = line.strip()
        line = re.sub(r"^#+\s*", "", line)
        line = line.lstrip("- >").strip()
        if not line or line in skip:
            continue
        if line.startswith(("[", "|", "`", "(")):
            continue
        return line[:60]
    return "未命名投递"

def find_best_match(text):
    q = KEDB.tokenize(text)
    db = KEDB.load_db()
    best, best_score = None, 0
    for e in db["entries"]:
        s, _ = KEDB.score_entry(q, e)
        if s > best_score:
            best, best_score = e, s
    return best, best_score

def bump_kedb(ke, new_pid):
    with open(DB, encoding="utf-8") as f:
        db = json.load(f)
    for e in db["entries"]:
        if e["known_error_id"] == ke["known_error_id"]:
            e["repeat_count"] = int(e.get("repeat_count", 0)) + 1
            rel = e.setdefault("关联", {})
            ps = rel.get("P")
            if isinstance(ps, list):
                if new_pid not in ps:
                    ps.append(new_pid)
            elif ps:
                rel["P"] = [ps, new_pid]
            else:
                rel["P"] = new_pid
            e["last_recurrence"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")

def process_file(fp, dry):
    fm, body = parse_inbox(fp)
    if fm.get("type") != "inbox":
        print("跳过非投递件（缺 type: inbox）: %s" % os.path.basename(fp))
        return
    tool = fm.get("source_tool") or "human"
    if tool not in ("hermes", "codex", "dsh", "gpt", "human", "other"):
        tool = "human"
    title    = pick_title(fm, body)
    severity = fm.get("severity") or "待定"
    ke, score = find_best_match(title + "\n" + body)
    matched = ke is not None and score >= MATCH_MIN
    if dry:
        print("[dry-run] %s → P卡 title=%r tool=%s severity=%s ke=%s" % (
            os.path.basename(fp), title, tool, severity,
            ke["known_error_id"] if matched else "-"))
        return
    extra = {"severity": severity,
             "detected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    if matched:
        extra["ke_ref"] = ke["known_error_id"]
    out, cid = NEW_CARD.build_card("problem", title, tool, extra)
    if matched:
        bump_kedb(ke, cid)
        print("命中 KEDB %s → repeat_count+1；P 卡 %s 已挂 ke_ref" % (ke["known_error_id"], cid))
    else:
        print("KEDB 无命中（新问题）→ 已建 P 卡 %s；若为已知顽疾，人工确认后登记 KEDB" % cid)
    print("已创建:", out)
    os.makedirs(PROCESSED, exist_ok=True)
    dest = os.path.join(PROCESSED,
                        datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                        + "-" + os.path.basename(fp))
    shutil.move(fp, dest)
    print("投递件已归档:", dest)

def main():
    dry = "--dry-run" in sys.argv
    files = [f for f in glob.glob(os.path.join(INBOX, "*.md"))]
    if not files:
        print("00-Inbox 无待处理投递件。")
        return 0
    for fp in sorted(files):
        try:
            process_file(fp, dry)
        except Exception as ex:
            print("FAIL 处理失败: %s — %s" % (fp, ex), file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
