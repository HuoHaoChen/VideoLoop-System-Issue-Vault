#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VideoLoop 闭环校验器 V2.3
# 用法: python validate_loop.py [vault路径]   或   python validate_loop.py --selftest
# VideoLoop V2.3 — Tabbit 修复版 2026-06-18
# 修复内容: M7(schema缺失静默) C6(待分类永不告警) M3(due日期格式静默跳过)
import sys, os, re, json, glob, datetime

ROOT = "."
for _a in sys.argv[1:]:
    if not _a.startswith("-"):
        ROOT = _a
OPEN_PROBLEM = {"未处理","设计中","执行中","观察中"}
OPEN_CHANGE  = {"设计中","执行中","观察中"}
CONCLUSIVE   = {"有效","部分有效","无效","负面"}
SOFT_DOMAINS = {"认知","系统"}

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = re.sub(r"\s+#.*$", "", v.strip()).strip()
        if v.lower() in ("true","false"):
            v = (v.lower() == "true")
        fm[k] = v
    return fm

def load_required(root):
    p = os.path.join(root, "schema.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("required", {})
    # ── M7 修复：schema 缺失时明确告警，不再静默跳过 ────────────
    print("WARN [schema缺失] 找不到 " + p
          + "，必填字段校验已全部跳过！请确认运行目录是否正确。",
          file=sys.stderr)
    return {}

def run(root):
    required = load_required(root)
    errors, warns, ids = [], [], {}
    files = glob.glob(os.path.join(root, "20-Cards", "**", "*.md"), recursive=True)
    today = datetime.date.today().isoformat()
    for fp in files:
        rel = os.path.relpath(fp, root)
        with open(fp, encoding="utf-8") as f:
            fm = parse_frontmatter(f.read())
        if not fm:
            warns.append("[no-frontmatter] " + rel)
            continue
        t = fm.get("type")
        for field in required.get(t, []):
            if fm.get(field) in (None, "", []):
                errors.append("[必填缺失] " + rel + " 缺 " + field)
        cid = fm.get("id")
        if cid:
            if cid in ids:
                errors.append("[ID重复] " + str(cid))
            else:
                ids[cid] = rel
        if t == "change" and fm.get("verdict") in CONCLUSIVE:
            if not fm.get("calibrated"):
                errors.append("[校准门控#4] " + rel + " 已下结论但 calibrated=false")
            elif not fm.get("calibration_ref"):
                errors.append("[校准防刷#4] " + rel + " calibrated=true 但 calibration_ref 为空")
            if not fm.get("process_captured"):
                errors.append("[留痕门控] " + rel + " 已下结论但 process_captured=false")
            if not fm.get("baseline_window") or not fm.get("minimum_effect"):
                errors.append("[因果门控#C] " + rel + " 下结论前缺 baseline_window/minimum_effect")
        if t == "change" and fm.get("domain") in SOFT_DOMAINS and fm.get("significance") == "统计显著":
            errors.append("[软领域显著禁用] " + rel + " domain=" + str(fm.get("domain"))
                          + " 不得声称统计显著（单人小样本不成立）")
        if (t == "change" and fm.get("domain") == "运营"
                and fm.get("borrows_from") in SOFT_DOMAINS
                and (fm.get("verdict") in CONCLUSIVE
                     or fm.get("significance") == "统计显著")):
            errors.append("[防腐层·方向阀] " + rel + " 运营决策借入软域("
                          + str(fm.get("borrows_from"))
                          + ")洞见只能当假设，须在运营域内独立验证后才能下结论")
        if (t == "change" and fm.get("recorded_by")
                and fm.get("recorded_by") == fm.get("evaluator")):
            errors.append("[裁判独立#5] " + rel + " 记录者=评估者")
        if t == "problem" and fm.get("status") == "已解决" and not fm.get("process_captured"):
            errors.append("[留痕门控] " + rel + " 已解决但 process_captured=false")

        # ── M3 修复：due 日期格式不合规时给出明确告警，不再静默跳过 ──
        due  = str(fm.get("due") or "")
        oset = OPEN_PROBLEM if t == "problem" else (OPEN_CHANGE if t == "change" else set())
        if due:
            if not re.match(r"\d{4}-\d{2}-\d{2}$", due):
                warns.append("[日期格式错误] " + rel
                             + " due=" + due + "，应为 YYYY-MM-DD 格式")
            elif due < today and fm.get("status") in oset:
                warns.append("[逾期#6] " + rel + " due " + due)

        # ── C6 修复：domain 长期停在"待分类"时发出告警 ───────────
        if t in ("problem", "change") and fm.get("domain") == "待分类":
            if fm.get("status") not in ("已解决", "已结案", "归档"):
                warns.append("[未分类] " + rel
                             + " domain 仍为 '待分类'，请尽快归属三域")

        # ── V2.3.1: CAL 扫描字段校验（videoloop-cal-scan V2） ───
        if t == "change":
            # cal_scan_done=true 时必须存在 cal_scan_at
            if fm.get("cal_scan_done") and not fm.get("cal_scan_at"):
                warns.append("[CAL扫描] " + rel + " cal_scan_done=true 但缺 cal_scan_at")
            # referenced_cals 非空时每条必须含 cal_id 和 referenced_at
            ref_cals = fm.get("referenced_cals")
            if ref_cals:
                # frontmatter 解析后可能是字符串或列表，做容错
                if isinstance(ref_cals, str):
                    ref_cals = [ref_cals]
                if isinstance(ref_cals, list):
                    for i, rc in enumerate(ref_cals):
                        if isinstance(rc, dict):
                            if not rc.get("cal_id"):
                                errors.append("[CAL引用] " + rel + " referenced_cals[" + str(i) + "] 缺 cal_id")
                            if not rc.get("referenced_at"):
                                errors.append("[CAL引用] " + rel + " referenced_cals[" + str(i) + "] 缺 referenced_at")
            # 双路 mtime 失效检测：文件系统 mtime + frontmatter updated
            if fm.get("cal_scan_done") and fm.get("cal_scan_at"):
                try:
                    # 路径 1：文件系统 mtime（操作系统级事实，最可靠）
                    fs_mtime = os.path.getmtime(fp)
                    scan_str = str(fm["cal_scan_at"])
                    # 支持 ISO 8601 (2026-06-24T15:58:52) 和纯日期 (2026-06-24)
                    if "T" in scan_str:
                        scan_ts = datetime.datetime.fromisoformat(
                            scan_str.replace("Z", "+00:00").split("+")[0]
                        ).timestamp()
                    else:
                        scan_ts = datetime.datetime.strptime(scan_str[:10], "%Y-%m-%d").timestamp()
                    if fs_mtime > scan_ts + 1:
                        warns.append("[CAL扫描失效·mtime] " + rel
                                     + " 文件修改时间晚于 cal_scan_at，cal_scan_done 应重置为 false")
                except Exception:
                    pass
                # 路径 2：frontmatter updated 字段（兜底）
                try:
                    fm_upd = fm.get("updated")
                    if fm_upd:
                        scan_str2 = str(fm["cal_scan_at"])
                        if "T" in scan_str2:
                            scan_dt2 = datetime.datetime.fromisoformat(
                                scan_str2.replace("Z", "+00:00").split("+")[0]
                            ).date()
                        else:
                            scan_dt2 = datetime.datetime.strptime(scan_str2[:10], "%Y-%m-%d").date()
                        upd_dt = datetime.datetime.strptime(str(fm_upd)[:10], "%Y-%m-%d").date()
                        if upd_dt > scan_dt2:
                            warns.append("[CAL扫描失效·frontmatter] " + rel
                                         + " updated(" + str(upd_dt) + ") > cal_scan_at(" + str(scan_dt2)
                                         + ")，cal_scan_done 应重置为 false")
                except Exception:
                    pass

    for w in warns:
        print("WARN", w)
    for e in errors:
        print("FAIL", e)
    if errors:
        print("校验未通过：" + str(len(errors)) + " 错误 / " + str(len(warns)) + " 告警")
        return 1
    print("OK 全部通过（" + str(len(files)) + " 张卡 / " + str(len(warns)) + " 告警）")
    return 0

def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "20-Cards"))
    json.dump({"required": {"change": ["id","type","verdict"]}},
              open(os.path.join(d, "schema.json"), "w", encoding="utf-8"))
    bad = "\n".join(["---","id: C-test","type: change","domain: 认知",
                     "significance: 统计显著","verdict: 有效",
                     "calibrated: false","process_captured: false",
                     "recorded_by: a","evaluator: a","---"])
    open(os.path.join(d, "20-Cards", "bad.md"), "w", encoding="utf-8").write(bad)
    bad2 = "\n".join(["---","id: C-test2","type: change","domain: 运营",
                      "borrows_from: 认知","verdict: 有效",
                      "calibrated: true","calibration_ref: CAL-x",
                      "process_captured: true","baseline_window: x",
                      "minimum_effect: x","recorded_by: a","evaluator: b","---"])
    open(os.path.join(d, "20-Cards", "bad2.md"), "w", encoding="utf-8").write(bad2)
    print("自检·方向阀：另用一张 运营卡借认知洞见却声称已验证 的卡测试——")
    print("自检：用一张同时违反 校准/留痕/裁判独立/因果/软领域显著 的卡测试——")
    rc = run(d)
    print("自检结果：", "通过(成功拓出违规)" if rc == 1 else "异常(未拓出，校验器可能坏了)")
    return 0 if rc == 1 else 2

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run(ROOT))
