#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# watcher.py — 统一问题反馈引擎 v4 全自动守护
# 用法:
#   python3 watcher.py --scan            # 扫描工具会话日志，新错误签名自动建卡
#   python3 watcher.py --verify          # 存活/复发证据自动升降解法信誉
#   python3 watcher.py --scan --verify   # 两者都做（launchd 每小时跑）
#   python3 watcher.py --dry-run         # 只报告不落盘
#   python3 watcher.py --since N         # 只扫最近 N 天（默认 3）
#   python3 watcher.py --max N           # 每轮最多自动建 N 张卡（默认 10，防洪水）
#
# 设计：人零操作。问题自动捕获 → KEDB 自动查重 → 解法自动验证。
#   复发 = 证伪（被推翻）；N 天不复发 = 证真（已验证）。
#   唯一保留人工：severity=S1 升级（安全阀）。
import sys, os, re, json, glob, datetime, importlib.util, shutil

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX     = os.path.join(ROOT, "00-Inbox")
CARDS     = os.path.join(ROOT, "20-Cards")
DB        = os.path.join(ROOT, "known_error_db.json")
STATE     = os.path.expanduser("~/.dsh/sife-watcher-state.json")
ERROR_RE  = re.compile(r"(error|exception|traceback|fail(ed|ure)?|operation not permitted|permission denied|"
                        r"at capacity|timed? ?out|invalid_request|unauthorized|403|401|500|"
                        r"not found|no such file|exit code [1-9]|错误|失败|异常|超时|拒绝|无权限)", re.I)
NOISE_RE  = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|"
                        r"/[^\s,;\"']+|https?://[^\s]+|\d{4}-\d{2}-\d{2}[T ][\d:]+|\b\d+\b", re.I)
SURVIVE_DAYS = 7   # 已解决解法存活 N 天不复发 → 已验证

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

INGEST = load_module("ingest", os.path.join(ROOT, "scripts", "ingest.py"))
TICKET = load_module("ticket", os.path.join(ROOT, "scripts", "ticket.py"))
KEDB   = load_module("kedb", os.path.join(ROOT, "scripts", "kedb.py"))

def now_text():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"seen": {}}

def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def signature(text):
    t = NOISE_RE.sub("#", text or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t[:90] or "未命名签名"

def extract_error_texts(obj, out):
    """只认真实错误事件字段：type=error 类 / payload.status=error / 顶层 error 键。"""
    if not isinstance(obj, dict):
        return
    t = obj.get("type")
    p = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
    is_err = t in ("error", "api_error", "exception", "failed")
    is_err = is_err or p.get("status") in ("error", "failed", "incomplete")
    err = obj.get("error")
    perr = p.get("error")
    is_err = is_err or err is not None or perr is not None
    if not is_err:
        return
    for k in ("message", "text", "content", "output", "summary"):
        v = obj.get(k) or p.get(k)
        if isinstance(v, str):
            out.append(v[:200])
    if isinstance(err, dict) and err.get("message"):
        out.append(str(err["message"])[:200])
    elif isinstance(err, str):
        out.append(err[:200])
    if isinstance(perr, dict) and perr.get("message"):
        out.append(str(perr["message"])[:200])
    elif isinstance(perr, str):
        out.append(perr[:200])

def scan_codex(since, hits):
    root = os.path.expanduser("~/.codex/sessions")
    if not os.path.isdir(root):
        return
    cutoff = time.time() - since * 86400
    for fp in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        try:
            if os.path.getmtime(fp) < cutoff:
                continue
        except OSError:
            continue
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    texts = []
                    extract_error_texts(obj, texts)
                    for t in texts:
                        hits.append((signature(t), "codex", fp, t))
        except OSError:
            pass

def scan_hermes(since, hits):
    root = os.path.expanduser("~/.hermes")
    if not os.path.isdir(root):
        return
    cutoff = time.time() - since * 86400
    patterns = [os.path.join(root, "*.log"),
                os.path.join(root, "cron", "output", "*")]
    for pat in patterns:
        for fp in glob.glob(pat):
            try:
                if os.path.getmtime(fp) < cutoff:
                    continue
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if ERROR_RE.search(line):
                            hits.append((signature(line), "hermes", fp, line.strip()[:200]))
            except OSError:
                pass

def cmd_scan(dry, since, max_tickets):
    hits = []
    scan_codex(since, hits)
    scan_hermes(since, hits)
    st = load_state()
    created = 0
    skipped = 0
    for sig, source, fp, snippet in hits:
        rec = st["seen"].get(sig)
        if rec:
            rec["count"] += 1
            rec["last"] = now_text()
            skipped += 1
            continue
        if created >= max_tickets:
            skipped += 1
            continue
        st["seen"][sig] = {"count": 1, "first": now_text(), "last": now_text(), "source": source}
        if dry:
            print("[dry-run] 新签名 → %s | %s | %s" % (source, sig, snippet[:60]))
            created += 1
            continue
        fn = "auto-%s-%s-%s.md" % (datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), source, created)
        with open(os.path.join(INBOX, fn), "w", encoding="utf-8") as f:
            f.write("---\ntype: inbox\nsource_tool: %s\nseverity: 待定\ndomain: 系统\ntitle: %s\ncreated: %s\n---\n"
                    "## 症状\n自动捕获自 %s：\n%s\n\n## 根因\n未定位\n\n## 解决记录\n"
                    % (source, sig[:60], datetime.date.today().isoformat(), fp, snippet))
        print("自动建卡投递: %s (%s)" % (sig[:60], source))
        created += 1
    if created and not dry:
        save_state(st)
    if not dry and created:
        INGEST.main()
    print("扫描完成：%d 个错误命中，新建 %d，跳过(已知/超限) %d" % (len(hits), created, skipped))
    return 0

def parse_frontmatter(content):
    m = re.match(r"^---\n(.*?)\n---", content, re.S)
    fm = {}
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm

def cmd_verify(dry):
    """存活证据自动验证：待验证解法 N 天不复发→已验证；复发→被推翻。"""
    now = datetime.datetime.now()
    actions = []
    cards = []
    for fp in glob.glob(os.path.join(CARDS, "**", "*.md"), recursive=True):
        fm = parse_frontmatter(open(fp, encoding="utf-8").read())
        if fm.get("type") != "problem":
            continue
        cards.append((fp, fm))
    by_ref = {}
    for fp, fm in cards:
        by_ref.setdefault(fm.get("ke_ref"), []).append((fp, fm))
    for fp, fm in cards:
        if fm.get("solution_status") != "已解决" or fm.get("solution_level") != "待验证":
            continue
        ra = fm.get("resolved_at") or ""
        try:
            rd = datetime.datetime.strptime(ra[:10], "%Y-%m-%d")
        except ValueError:
            continue
        if (now - rd).days < SURVIVE_DAYS:
            continue
        ref = fm.get("ke_ref")
        recurred = False
        if ref and ref in by_ref:
            for fp2, fm2 in by_ref[ref]:
                if fm2.get("id") == fm.get("id"):
                    continue
                c2 = fm2.get("created") or ""
                if c2 and c2 >= (fm.get("created") or ""):
                    recurred = True
                    break
        verdict = "被推翻" if recurred else "已验证"
        actions.append((fp, fm.get("id", "?"), verdict, ref, recurred))
    for fp, cid, verdict, ref, recurred in actions:
        if dry:
            print("[dry-run] %s %s → %s" % (cid, "复发" if recurred else "存活", verdict))
            continue
        TICKET.verify_ticket(cid, "无效" if recurred else "有效")
        print("%s %s → %s（%s证据）" % (cid, "复发" if recurred else "存活", verdict,
              "复发" if recurred else "存活 %d 天" % SURVIVE_DAYS))
    print("自动验证完成：%d 个解法待验证，本轮处理 %d" % (sum(1 for _, fm in cards
        if fm.get("solution_status") == "已解决" and fm.get("solution_level") == "待验证"), len(actions)))
    return 0

import time

def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    since = 3
    max_tickets = 10
    if "--since" in argv:
        i = argv.index("--since")
        if i + 1 < len(argv):
            since = int(argv[i + 1])
    if "--max" in argv:
        i = argv.index("--max")
        if i + 1 < len(argv):
            max_tickets = int(argv[i + 1])
    do_scan = "--scan" in argv
    do_verify = "--verify" in argv
    if not (do_scan or do_verify):
        do_scan = do_verify = True
    rc = 0
    if do_scan:
        rc |= cmd_scan(dry, since, max_tickets)
    if do_verify:
        rc |= cmd_verify(dry)
    return rc

if __name__ == "__main__":
    sys.exit(main())
