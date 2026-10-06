#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# watcher.py v2 — 统一问题反馈引擎 全自动守护（本地确定性核心 + 证据闭环）
# 用法:
#   python3 watcher.py --scan --verify [--since N] [--max N] [--dry-run]
#   python3 watcher.py --enrich-draft          # 按需离线加工：给待解决自动卡起草根因/解决（调 Codex，不上 launchd）
#   python3 watcher.py --selftest              # 专业跑通测试（逆向思维失败模式 × 第一性原理不变量）
#
# 核心不变量（第一性原理）:
#   I1 每个真实错误签名恰好建一张卡（状态文件去重，幂等）
#   I2 解决状态只被证据改变：复发=被推翻；N 天不复发且有解法=已解决+已验证；AI 声称不算数
#   I3 每小时循环纯本地、无网络、无 LLM、有界时间；单源失败不拖垮整体；失败自愈 + 自报
#
# 失败模式防护（逆向思维）: 进程崩溃→launchd KeepAlive 立即重试；睡眠→醒后补跑；
#   状态文件损坏→自动重建；目录缺失→跳过；单文件过大→截断读取；状态文件原子写+限量。
#
# 测试隔离: 环境变量 SIFE_WATCH_ROOT 覆盖仓库根（selftest 用临时目录）；
#   SIFE_WATCH_CODEX_DIR / SIFE_WATCH_HERMES_DIR 覆盖日志目录。
import sys, os, re, json, glob, hashlib, datetime, importlib.util, tempfile, subprocess, time

_OVR = os.environ.get("SIFE_WATCH_ROOT")
ROOT      = _OVR or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX     = os.path.join(ROOT, "00-Inbox")
CARDS     = os.path.join(ROOT, "20-Cards")
DB        = os.path.join(ROOT, "known_error_db.json")
STATE     = os.path.expanduser("~/.dsh/sife-watcher-state.json") if not _OVR \
            else os.path.join(_OVR, "watcher-state.json")
ERR_LOG   = "/tmp/sife-watcher.err"
SURVIVE_DAYS = 7
ERROR_RE  = re.compile(r"(error|exception|traceback|fail(ed|ure)?|operation not permitted|permission denied|"
                        r"at capacity|timed? ?out|invalid_request|unauthorized|403|401|500|"
                        r"not found|no such file|exit code [1-9]|错误|失败|异常|超时|拒绝|无权限)", re.I)
NOISE_RE  = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|"
                        r"/[^\s,;\"']+|https?://[^\s]+|\d{4}-\d{2}-\d{2}[T ][\d:]+|\b\d+\b", re.I)
_STOP = {"is","at","of","to","in","on","be","or","and","no","it","we","you","the",
         "a","an","if","not","this","that","for","with","was","are","but","do","did",
         "has","had","by","as","so","up","my","me","he","she","they","can","will"}
MAX_SCAN_FILES = 500
MAX_STATE_SIGS = 1000
MAX_LINE = 4000

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def now_text():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def today():
    return datetime.date.today().isoformat()

def signature(text):
    t = NOISE_RE.sub("#", text or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t[:90] or "未命名签名"

def tokenize(text):
    text = (text or "").lower()
    toks = set(re.findall(r"[a-z0-9_./-]{2,}", text)) - _STOP
    for seg in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(seg) == 1:
            toks.add(seg)
        for i in range(len(seg) - 1):
            toks.add(seg[i:i+2])
    return toks

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            print("WARN 状态文件损坏，重建空状态（自愈）")
    return {"seen": {}, "err_mark": 0}

def save_state(st):
    # 原子写：先写临时文件再 rename，崩溃也不会留下半个 JSON
    st["seen"] = dict(sorted(st["seen"].items(),
                             key=lambda kv: kv[1].get("last", ""))[-MAX_STATE_SIGS:])
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    os.replace(tmp, STATE)

# ─────────────────────────── 错误提取（只认真实错误字段） ───────────────────────────

def extract_error_texts(obj, out):
    if not isinstance(obj, dict):
        return
    t = obj.get("type")
    p = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
    err, perr = obj.get("error"), p.get("error")
    is_err = t in ("error", "api_error", "exception", "failed")
    is_err = is_err or p.get("status") in ("error", "failed", "incomplete")
    is_err = is_err or err is not None or perr is not None
    if not is_err:
        return
    for k in ("message", "text", "content", "output", "summary"):
        v = obj.get(k) or p.get(k)
        if isinstance(v, str):
            out.append(v[:200])
    for e in (err, perr):
        if isinstance(e, dict) and e.get("message"):
            out.append(str(e["message"])[:200])
        elif isinstance(e, str):
            out.append(e[:200])

def _iter_files(root, patterns, since):
    cutoff = time.time() - since * 86400
    seen, n = set(), 0
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            if n >= MAX_SCAN_FILES or fp in seen:
                continue
            seen.add(fp); n += 1
            try:
                if os.path.getmtime(fp) < cutoff:
                    continue
            except OSError:
                continue
            yield fp

def scan_codex(since, hits):
    root = os.environ.get("SIFE_WATCH_CODEX_DIR") or os.path.expanduser("~/.codex/sessions")
    if not os.path.isdir(root):
        print("SKIP codex（目录不存在: %s）" % root)
        return
    for fp in _iter_files(root, [os.path.join(root, "**", "*.jsonl")], since):
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line[:MAX_LINE]
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
    root = os.environ.get("SIFE_WATCH_HERMES_DIR") or os.path.expanduser("~/.hermes")
    if not os.path.isdir(root):
        print("SKIP hermes（目录不存在: %s）" % root)
        return
    for fp in _iter_files(root, [os.path.join(root, "*.log"),
                                 os.path.join(root, "cron", "output", "*")], since):
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line[:MAX_LINE]
                    if ERROR_RE.search(line):
                        hits.append((signature(line), "hermes", fp, line.strip()[:200]))
        except OSError:
            pass

# ─────────────────────────── 自报：watcher 自身故障也要进系统 ───────────────────────────

def scan_marvis(since, hits):
    """扫描 Marvis 本地会话库（data.db messages 表）中的错误文本。
    安全设计：库不可读/表结构变更 → 跳过并打印 SKIP，绝不拖垮其他源（防脆）。"""
    db = os.environ.get("SIFE_WATCH_MARVIS_DB") or os.path.expanduser(
        "~/.marvis/database/data.db")
    if not os.path.exists(db):
        print("SKIP marvis（数据库不存在: %s）" % db)
        return
    try:
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True, timeout=5)
        con.execute("PRAGMA query_only=ON")
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        if "messages" not in tables:
            print("SKIP marvis（messages 表缺失，可能升级改库）")
            con.close()
            return
        cols = [r[1] for r in con.execute("PRAGMA table_info(messages)")]
        need = {"role", "content", "created_at", "tool_name"}
        if not need.issubset(set(cols)):
            print("SKIP marvis（messages 表结构变更）")
            con.close()
            return
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=since)).isoformat()
        rows = con.execute(
            "SELECT role, content, tool_name, created_at FROM messages "
            "WHERE created_at >= ? ORDER BY created_at DESC LIMIT 500",
            (cutoff,)).fetchall()
        con.close()
    except Exception as ex:
        print("SKIP marvis（读取失败，防脆跳过: %s）" % ex)
        return
    for role, content, tool_name, created_at in rows:
        if role not in ("assistant", "tool"):
            continue
        text = (content or "")[:4000]
        if not text:
            continue
        m = ERROR_RE.search(text)
        if not m:
            continue
        start = max(0, m.start() - 60)
        snippet = text[start:m.end() + 120].strip()
        if len(snippet) < 8:
            continue
        hits.append((signature(snippet), "marvis", db + ":" + str(tool_name or role), snippet))


def self_report(st, dry):
    if dry or os.environ.get("SIFE_WATCH_ROOT"):
        return False
    if not os.path.exists(ERR_LOG):
        return False
    cur = os.path.getsize(ERR_LOG)
    if cur <= int(st.get("err_mark", 0)):
        return False
    with open(ERR_LOG, encoding="utf-8", errors="ignore") as f:
        f.seek(max(0, cur - 2000))
        tail = f.read().strip()
    if not tail:
        return False
    fn = os.path.join(INBOX, "auto-%s-self.md" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    with open(fn, "w", encoding="utf-8") as f:
        f.write("---\ntype: inbox\nsource_tool: launchd\nseverity: 待定\ndomain: 系统\n"
                "title: watcher 自身运行故障（自报）\ncreated: %s\n---\n"
                "## 症状\n%s\n\n## 根因\n未定位\n\n## 解决记录\n" % (today(), tail))
    st["err_mark"] = cur
    print("自报：watcher 自身故障已投递 %s" % fn)
    if not os.environ.get("SIFE_WATCH_ROOT"):
        try:
            INGEST = load_module("ingest", os.path.join(ROOT, "scripts", "ingest.py"))
            INGEST.main()
        except Exception as ex:
            print("FAIL 自报入库异常（下轮重试）: %s" % ex)
    return True

# ─────────────────────────── 扫描建卡 ───────────────────────────

def cmd_scan(dry, since, max_tickets):
    hits = []
    scan_codex(since, hits)
    scan_hermes(since, hits)
    scan_marvis(since, hits)
    st = load_state()
    created = skipped = 0
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
        fn = os.path.join(INBOX, "auto-%s-%s-%s.md" % (
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), source,
            hashlib.md5(sig.encode("utf-8")).hexdigest()[:8]))
        with open(fn, "w", encoding="utf-8") as f:
            f.write("---\ntype: inbox\nsource_tool: %s\nseverity: 待定\ndomain: 系统\n"
                    "title: %s\nsig: %s\nauto: true\ncreated: %s\n---\n"
                    "## 症状\n自动捕获自 %s：\n%s\n\n## 根因\n未定位\n\n## 解决记录\n"
                    % (source, sig[:60], sig, today(), fp, snippet))
        print("自动建卡投递: %s (%s)" % (sig[:60], source))
        created += 1
    if created and not dry:
        save_state(st)
    if created and not dry and not os.environ.get("SIFE_WATCH_ROOT"):
        INGEST = load_module("ingest", os.path.join(ROOT, "scripts", "ingest.py"))
        try:
            INGEST.main()
        except Exception as ex:
            print("FAIL ingest 调用异常（下轮重试）: %s" % ex)
    print("扫描完成：%d 个错误命中，新建 %d，跳过(已知/超限) %d" % (len(hits), created, skipped))
    return 0

# ─────────────────────────── 证据闭环验证 ───────────────────────────

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

def write_frontmatter_field(fp, key, value):
    c = open(fp, encoding="utf-8").read()
    m = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n?)(.*)$", c, re.S)
    if not m:
        return False
    lines = m.group(2).splitlines()
    prefix = key + ":"
    done = False
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            lines[i] = key + ": " + value
            done = True
            break
    if not done:
        lines.insert(1, key + ": " + value)
    open(fp, "w", encoding="utf-8").write(m.group(1) + "\n".join(lines) + m.group(3) + m.group(4))
    return True

def cmd_verify(dry):
    now = datetime.datetime.now()
    cards = []
    for fp in glob.glob(os.path.join(CARDS, "**", "*.md"), recursive=True):
        try:
            fm = parse_frontmatter(open(fp, encoding="utf-8").read())
        except OSError:
            continue
        if fm.get("type") == "problem":
            cards.append((fp, fm))
    by_sig = {}
    for fp, fm in cards:
        if fm.get("sig"):
            by_sig.setdefault(fm["sig"], []).append((fp, fm))
    promoted = demoted = 0
    for fp, fm in cards:
        cid = fm.get("id", "?")
        sig = fm.get("sig") or ""
        newer_same_sig = False
        if sig and sig in by_sig:
            for fp2, fm2 in by_sig[sig]:
                if fm2.get("id") == cid:
                    continue
                if (fm2.get("created") or "") >= (fm.get("created") or ""):
                    newer_same_sig = True
                    break
        # 降级：已解决但同类签名再犯 → 被推翻（复发证据）
        if fm.get("solution_status") == "已解决" and newer_same_sig \
                and fm.get("solution_level") != "被推翻":
            if dry:
                print("[dry-run] 复发降级 %s → 被推翻" % cid)
            else:
                write_frontmatter_field(fp, "solution_level", "被推翻")
                print("复发降级 %s → 被推翻" % cid)
            demoted += 1
            continue
        # 升格：有解法草案、超过存活期、无同类复发 → 已解决+已验证（存活证据）
        if fm.get("solution_status") != "已解决" and (fm.get("solution") or "").strip() \
                and not newer_same_sig:
            try:
                cd = datetime.datetime.strptime((fm.get("created") or "")[:10], "%Y-%m-%d")
            except ValueError:
                continue
            if (now - cd).days < SURVIVE_DAYS:
                continue
            if dry:
                print("[dry-run] 存活升格 %s → 已解决+已验证" % cid)
            else:
                hits = int(fm.get("solution_hits") or 0)
                write_frontmatter_field(fp, "solution_status", "已解决")
                write_frontmatter_field(fp, "solution_level", "已验证")
                write_frontmatter_field(fp, "solution_hits", str(hits + 1))
                write_frontmatter_field(fp, "resolved_at", now_text())
                print("存活升格 %s → 已解决+已验证" % cid)
            promoted += 1
    print("证据验证完成：升格 %d，降级 %d（其余待观察）" % (promoted, demoted))
    return 0

# ─────────────────────────── 按需离线加工（不上 launchd） ───────────────────────────

def cmd_enrich(dry, max_cards=3):
    """给待解决自动卡起草根因/解决（调 Codex，每次最多 3 张，失败跳过不阻塞）。"""
    codex_bin = os.environ.get("SIFE_WATCH_CODEX_BIN") or os.path.expanduser("~/codex-cli/bin/codex")
    node_dir = os.path.expanduser("~/Downloads/node-v22.23.2-darwin-arm64/bin")
    if not os.path.exists(codex_bin):
        print("SKIP enrich：Codex 不可用（%s）" % codex_bin)
        return 0
    targets = []
    for fp in glob.glob(os.path.join(CARDS, "**", "*.md"), recursive=True):
        fm = parse_frontmatter(open(fp, encoding="utf-8").read())
        if fm.get("type") == "problem" and not (fm.get("solution") or "").strip() \
                and fm.get("source_tool") in ("codex", "hermes", "launchd"):
            targets.append((fp, fm))
        if len(targets) >= max_cards:
            break
    if not targets:
        print("无可加工卡（要么都已解决，要么未到加工轮次）。")
        return 0
    env = dict(os.environ)
    env["PATH"] = node_dir + ":" + env.get("PATH", "")
    for fp, fm in targets:
        cid = fm.get("id", "?")
        prompt = ("读这张问题卡 %s，基于症状起草两行内容（不要改文件）：\n"
                  "根因: <一句话>\n解决: <一句话>\n只输出这两行。" % fp)
        try:
            r = subprocess.run([codex_bin, "exec", "--skip-git-repo-check", "-C", ROOT, prompt],
                               capture_output=True, text=True, timeout=900, env=env)
            out = (r.stdout or "").strip()
            m1 = re.search(r"根因[:：]\s*(.+)", out)
            m2 = re.search(r"解决[:：]\s*(.+)", out)
            if dry:
                print("[dry-run] %s 起草：%s / %s" % (cid, m1 and m1.group(1), m2 and m2.group(1)))
                continue
            if m1:
                write_frontmatter_field(fp, "根因", m1.group(1))
            if m2:
                write_frontmatter_field(fp, "solution", m2.group(1))
            print("%s 已起草（根因/解决）。仍需存活证据才能升格。" % cid)
        except Exception as ex:
            print("FAIL enrich %s: %s（跳过，不影响主循环）" % (cid, ex))
    return 0

# ─────────────────────────── 专业跑通测试（selftest） ───────────────────────────

class T:
    def __init__(self):
        self.passed = self.failed = 0
    def check(self, name, cond, detail=""):
        if cond:
            self.passed += 1
            print("PASS %s" % name)
        else:
            self.failed += 1
            print("FAIL %s  %s" % (name, detail))

def cmd_selftest():
    """逆向思维失败模式 × 第一性原理不变量 的跑通测试。全部在临时目录，不碰真实库。"""
    print("=== watcher selftest（临时目录，不碰真实库）===")
    t = T()
    with tempfile.TemporaryDirectory() as d:
        os.environ["SIFE_WATCH_ROOT"] = d
        os.makedirs(os.path.join(d, "00-Inbox"), exist_ok=True)
        os.makedirs(os.path.join(d, "20-Cards"), exist_ok=True)
        codex_dir = os.path.join(d, "codex-logs"); os.makedirs(codex_dir)
        hermes_dir = os.path.join(d, "hermes-logs"); os.makedirs(hermes_dir)
        os.environ["SIFE_WATCH_CODEX_DIR"] = codex_dir
        os.environ["SIFE_WATCH_HERMES_DIR"] = hermes_dir
        global ROOT, INBOX, CARDS, DB, STATE
        ROOT, INBOX, CARDS, DB = d, os.path.join(d, "00-Inbox"), \
            os.path.join(d, "20-Cards"), os.path.join(d, "known_error_db.json")
        STATE = os.path.join(d, "watcher-state.json")

        # T1/T2: 真实错误捕获 + 噪声不进卡
        log1 = os.path.join(codex_dir, "rollout-a.jsonl")
        with open(log1, "w", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": "x", "type": "event_msg",
                "payload": {"type": "task_complete",
                "error": {"message": "Selected model is at capacity. Please try a different model.",
                          "codex_error_info": "server_overloaded"}}}) + "\n")
            f.write(json.dumps({"timestamp": "x", "type": "input_text",
                "payload": {"text": "这句话提到 error 但只是普通对话"}}) + "\n")
        os.utime(log1, (time.time(), time.time()))
        cmd_scan(False, 3, 10)
        inbox_files = glob.glob(os.path.join(INBOX, "*.md"))
        t.check("T1 捕获真实错误且不含噪声", len(inbox_files) == 1,
                "inbox=%d" % len(inbox_files))
        if inbox_files:
            c = open(inbox_files[0], encoding="utf-8").read()
            t.check("T2 卡含 sig/domain/source", "sig:" in c and "domain: 系统" in c
                    and "source_tool: codex" in c)

        # T3: 幂等——再跑一次不重复建卡
        cmd_scan(False, 3, 10)
        t.check("T3 重跑幂等不重复", len(glob.glob(os.path.join(INBOX, "*.md"))) == 1)

        # T4: 同秒多签名不互相覆盖（文件名带序号）
        log2 = os.path.join(codex_dir, "rollout-b.jsonl")
        with open(log2, "w", encoding="utf-8") as f:
            for name in ("alpha", "beta", "gamma"):
                f.write(json.dumps({"type": "error", "error": {"message": "unique failure %s" % name}}) + "\n")
        os.utime(log2, (time.time(), time.time()))
        cmd_scan(False, 3, 10)
        t.check("T4 同秒多签名文件不覆盖", len(glob.glob(os.path.join(INBOX, "*.md"))) == 4,
                "inbox=%d" % len(glob.glob(os.path.join(INBOX, "*.md"))))

        # T5: hermes 文本日志捕获
        with open(os.path.join(hermes_dir, "gateway.log"), "w", encoding="utf-8") as f:
            f.write("2026-08-27 gateway timeout after 30s\n")
        os.utime(os.path.join(hermes_dir, "gateway.log"), (time.time(), time.time()))
        cmd_scan(False, 3, 10)
        t.check("T5 hermes 日志捕获", len(glob.glob(os.path.join(INBOX, "*.md"))) == 5)

        # T6: 状态文件损坏自愈
        with open(STATE, "w", encoding="utf-8") as f:
            f.write("{broken json")
        st = load_state()
        t.check("T6 损坏状态自愈", "seen" in st and "err_mark" in st)

        # T7: 存活升格（有解法草案+超期+无复发）
        old = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        cardA = os.path.join(CARDS, "问题卡-test-A.md")
        open(cardA, "w", encoding="utf-8").write(
            "---\nid: P-test-A\ntype: problem\ntitle: tA\ndomain: 系统\nstatus: 未处理\n"
            "solution: 重试即可\nsolution_status: 待解决\nsolution_level: 待验证\nsolution_hits: 0\n"
            "sig: sig-alpha\ncreated: %s\nsource_tool: codex\n---\n" % old)
        cmd_verify(False)
        fm = parse_frontmatter(open(cardA, encoding="utf-8").read())
        t.check("T7 存活证据升格", fm.get("solution_status") == "已解决"
                and fm.get("solution_level") == "已验证", "got %s/%s"
                % (fm.get("solution_status"), fm.get("solution_level")))

        # T8: 复发降级（同签名新卡出现）
        new = datetime.date.today().isoformat()
        cardB = os.path.join(CARDS, "问题卡-test-B.md")
        open(cardB, "w", encoding="utf-8").write(
            "---\nid: P-test-B\ntype: problem\ntitle: tB\ndomain: 系统\nstatus: 未处理\n"
            "solution: 重试\nsolution_status: 已解决\nsolution_level: 已验证\nsolution_hits: 1\n"
            "sig: sig-beta\ncreated: 2026-08-20\nsource_tool: codex\n---\n")
        cardC = os.path.join(CARDS, "问题卡-test-C.md")
        open(cardC, "w", encoding="utf-8").write(
            "---\nid: P-test-C\ntype: problem\ntitle: tC\ndomain: 系统\nstatus: 未处理\n"
            "solution: \nsolution_status: 待解决\nsolution_level: 待验证\nsolution_hits: 0\n"
            "sig: sig-beta\ncreated: %s\nsource_tool: codex\n---\n" % new)
        cmd_verify(False)
        fm = parse_frontmatter(open(cardB, encoding="utf-8").read())
        t.check("T8 复发证据降级", fm.get("solution_level") == "被推翻",
                "got %s" % fm.get("solution_level"))

        for k in ("SIFE_WATCH_ROOT", "SIFE_WATCH_CODEX_DIR", "SIFE_WATCH_HERMES_DIR"):
            os.environ.pop(k, None)
    print("=== selftest 结果: %d PASS / %d FAIL ===" % (t.passed, t.failed))
    return 0 if t.failed == 0 else 2

def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return cmd_selftest()
    dry = "--dry-run" in argv
    since, max_tickets = 3, 10
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
    do_enrich = "--enrich-draft" in argv
    if not (do_scan or do_verify or do_enrich):
        do_scan = do_verify = True
    rc = 0
    if do_scan:
        st = load_state()
        if self_report(st, dry):
            save_state(st)
        rc |= cmd_scan(dry, since, max_tickets)
    if do_verify:
        rc |= cmd_verify(dry)
    if do_enrich:
        rc |= cmd_enrich(dry)
    return rc

if __name__ == "__main__":
    sys.exit(main())
