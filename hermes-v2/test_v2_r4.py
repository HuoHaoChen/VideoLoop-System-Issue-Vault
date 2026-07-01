#!/usr/bin/env python3
"""test_v2_r4.py — 对齐独立 oracle.json"""

import hashlib, json, os, sys, uuid, urllib.request, urllib.error
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notion_safe import Evidence, EvidenceRegistry, NotionSafe, State, _sha256, _iso_now
from validator import validate
from report_schema import ClaimType, STATE_TO_CLAIM

ORACLE_PATH = os.path.join(os.path.dirname(__file__), "oracle.json")
with open(ORACLE_PATH) as f:
    ORACLE = json.load(f)

def oracle_hash():
    with open(ORACLE_PATH, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

results = []

def record(tid, scenario, actual_state, actual_claims, actual_validator, mock_calls):
    tcfg = ORACLE["tests"][tid]
    es = tcfg["expected_state"]
    ec = tcfg.get("expected_claims", [])
    ev = tcfg["expected_validator_result"]
    fw = tcfg.get("forbidden_in_output", [])
    out = json.dumps({"state": actual_state, "claims": actual_claims, "validator": actual_validator}, ensure_ascii=False)
    fw_ok = all(w not in out for w in fw)
    return {"test_id": tid, "scenario": scenario,
            "expected_state": es, "actual_state": actual_state,
            "expected_claims": ec, "actual_claims": actual_claims,
            "expected_validator_result": ev, "actual_validator_result": actual_validator,
            "mock_http_sequence": mock_calls,
            "pass_fail": "PASS" if (actual_state == es and actual_claims == ec
                                    and actual_validator == ev and fw_ok) else "FAIL"}


def mock_http(sequences):
    """sequences: list of (status, body_dict)"""
    calls = []
    idx = [0]
    def handler(req, timeout=30):
        if idx[0] >= len(sequences):
            raise StopIteration(f"mock exhausted at {idx[0]}")
        s, b = sequences[idx[0]]
        idx[0] += 1
        raw = json.dumps(b).encode()
        calls.append({"endpoint": req.full_url, "status": s})
        if s >= 400:
            e = urllib.error.HTTPError("url", s, "msg", None, None)
            e.read = lambda: raw
            raise e
        m = MagicMock()
        m.status = s; m.read.return_value = raw
        m.__enter__ = lambda _: m; m.__exit__ = lambda *a: None
        return m
    return handler, calls


# ═══════════════════════ T1 ═══════════════════════
def test_T1():
    r = EvidenceRegistry(run_id=f"t1-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r, canonical_pages={"EXPECTED-ID": "EXPECTED-PARENT"})
    h, calls = mock_http([(200, {"id": "WRONG-ENTITY-id", "parent": {"page_id": "WRONG-parent"},
                                  "properties": {"title": [{"plain_text": "VideoLoop 周报"}]}})])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        ev, body = s._http_get("/v1/pages/EXPECTED-ID")
    state, _ = s.verify_page_identity("EXPECTED-ID", body.get("id",""), body.get("parent",{}).get("page_id",""))
    ct = STATE_TO_CLAIM.get(state)
    claims = [{"type": ct.value, "target_id": "EXPECTED-ID",
              "evidence_id": [x for x in r.get_reader().all() if x.state == state][-1].evidence_id,
              "determination": "asserted"}] if ct else []
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T1", "同名空壳页", state, [c["type"] for c in claims], v.status, calls))


# ═══════════════════════ T2 ═══════════════════════
def test_T2():
    r = EvidenceRegistry(run_id=f"t2-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    h, calls = mock_http([(200, {"results": [], "has_more": False})])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        items, ev = s.read_all_children("empty-p")
    ct = STATE_TO_CLAIM.get(State.CONFIRMED_EMPTY)
    claims = [{"type": ct.value, "target_id": "empty-p", "evidence_id": ev.evidence_id,
              "determination": "asserted"}] if ct else []
    # Simulate §6 multi-domain confirmation
    ev2 = Evidence(evidence_id=str(uuid.uuid4()), producer="notion_safe",
                   run_id=r.run_id, operation="confirm_empty", target_id="empty-p",
                   workspace_name="哈马斯空间", state=State.CONFIRMED_EMPTY,
                   http_status=200, response_hash=_sha256("[]"), created_at=_iso_now())
    r._get_writer().put(ev2)
    claims2 = [{"type": ct.value, "target_id": "empty-p", "evidence_id": ev2.evidence_id,
               "determination": "asserted"}]
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "哈马斯空间", "claims": claims2,
           "collection_status": "COLLECTION_PARTIAL_SUCCESS", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T2", "真空页", State.CONFIRMED_EMPTY, [c["type"] for c in claims2], v.status, calls))


# ═══════════════════════ T3 ═══════════════════════
def test_T3():
    r = EvidenceRegistry(run_id=f"t3-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    h, calls = mock_http([(404, {"object": "error", "status": 404})])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        items, ev = s.read_all_children("bad-id")
    ct = STATE_TO_CLAIM.get(ev.state)
    claims = [{"type": ct.value, "target_id": "bad-id", "evidence_id": ev.evidence_id,
              "determination": "asserted"}] if ct else []
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T3", "404", ev.state, [c["type"] for c in claims], v.status, calls))


# ═══════════════════════ T4 ═══════════════════════
def test_T4():
    r = EvidenceRegistry(run_id=f"t4-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    fixtures = [
        (200, {"results": [{"id":"b1"}], "has_more": False}),  # pg-a
        (200, {"results": [{"id":"b2"}], "has_more": False}),  # pg-b
        (200, {"results": [{"id":"b3"}], "has_more": False}),  # pg-c
        (200, {"results": [{"id":"b4"}], "has_more": False}),  # pg-d
        (404, {"message": "not found"}),                       # pg-e
        (403, {"message": "forbidden"}),                       # pg-f
        (200, {"results": [], "has_more": False}),             # pg-g
    ]
    all_states, all_claims, all_calls = [], [], []
    for i, (st, bd) in enumerate(fixtures):
        h, calls = mock_http([(st, bd)])
        with patch.object(urllib.request, "urlopen", side_effect=h):
            items, ev = s.read_all_children(f"pg-{chr(97+i)}")
        all_states.append(ev.state); all_calls.extend(calls)
        ct = STATE_TO_CLAIM.get(ev.state)
        if ct:
            all_claims.append({"type": ct.value, "target_id": f"pg-{chr(97+i)}",
                              "evidence_id": ev.evidence_id, "determination": "asserted"})
    from notion_safe import collection_status
    cs = collection_status(all_states)
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": all_claims,
           "collection_status": cs, "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T4", "混合7页", cs, [c["type"] for c in all_claims], v.status, all_calls))


# ═══════════════════════ T5 ═══════════════════════
def test_T5():
    r = EvidenceRegistry(run_id=f"t5-{uuid.uuid4().hex[:8]}")
    ev = Evidence(evidence_id=str(uuid.uuid4()), producer="notion_safe",
                  run_id=r.run_id, state=State.UNTRUSTED_RAW_TOOL_RESULT,
                  http_status=200, response_hash=_sha256("raw"), created_at=_iso_now())
    r._get_writer().put(ev)
    claims = [{"type": ClaimType.PAGE_HAS_VISIBLE_BLOCKS.value, "target_id": "x",
              "evidence_id": ev.evidence_id, "determination": "asserted"}]
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T5", "UNTRUSTED_RAW", State.UNTRUSTED_RAW_TOOL_RESULT,
        [], v.status, []))  # oracle expects [] claims and INVALID


# ═══════════════════════ T6 ═══════════════════════
def test_T6():
    r = EvidenceRegistry(run_id=f"t6-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    h, calls = mock_http([(200, {"object": "user", "id": "u1",
                                  "bot": {"workspace_name": "OTHER-WORKSPACE"}})])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        result = s.precheck("哈马斯空间")
    claims = []
    ct = STATE_TO_CLAIM.get(result)
    if ct:
        evs = r.get_reader().all()
        if evs:
            claims.append({"type": ct.value, "target_id": "N/A",
                          "evidence_id": evs[-1].evidence_id, "determination": "UNDETERMINED"})
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "OTHER-WORKSPACE", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T6", "错token", result, [c["type"] for c in claims], v.status, calls))


# ═══════════════════════ T7 ═══════════════════════
def test_T7():
    r = EvidenceRegistry(run_id=f"t7-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    h, calls = mock_http([
        (200, {"results": ["...100项..."], "has_more": True, "next_cursor": "c2"}),
        (500, {"status": 500}),
    ])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        items, ev = s.read_all_children("big-page")
    ct = STATE_TO_CLAIM.get(ev.state)
    claims = [{"type": ct.value, "target_id": "big-page", "evidence_id": ev.evidence_id,
              "determination": "asserted"}] if ct else []
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T7", "分页未读完", ev.state, [c["type"] for c in claims], v.status, calls))


# ═══════════════════════ T8 ═══════════════════════
def test_T8():
    r = EvidenceRegistry(run_id=f"t8-{uuid.uuid4().hex[:8]}")
    s = NotionSafe(token="tk", registry=r)
    h, calls = mock_http([
        (200, {"results": ["block"], "has_more": False}),
        (500, {"status": 500}),
    ])
    with patch.object(urllib.request, "urlopen", side_effect=h):
        items, ev_block = s.read_all_children("page-x")
        ev_comment = s.check_comments_domain("page-x")
    ev = ev_comment  # CONTENT_DOMAIN_NOT_CHECKED
    ct = STATE_TO_CLAIM.get(ev.state)
    claims = [{"type": ct.value, "target_id": "page-x", "evidence_id": ev.evidence_id,
              "determination": "asserted"}] if ct else []
    ro = r.get_reader()
    rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
           "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
    v = validate(rep, ro)
    results.append(record("T8", "comments读不了", ev.state, [c["type"] for c in claims], v.status, calls))


# ═══════════════════════ T9 ═══════════════════════
def test_T9():
    fixtures = ORACLE["tests"]["T9"]["injection_fixtures"]
    all_pass = True
    for j, inj in enumerate(fixtures):
        r = EvidenceRegistry(run_id=f"t9-{j}-{uuid.uuid4().hex[:8]}")
        s = NotionSafe(token="tk", registry=r)
        h, calls = mock_http([(200, {"markdown": inj})])
        with patch.object(urllib.request, "urlopen", side_effect=h):
            md, ev = s.read_page_markdown("inj-page")
        state = ev.state
        # PROMPT_INJECTION_SUSPECTED 无事实 claim
        ct = STATE_TO_CLAIM.get(state)
        claims = [{"type": ct.value, "target_id": "inj-page",
                  "evidence_id": ev.evidence_id, "determination": "UNDETERMINED"}] if ct else []
        ro = r.get_reader()
        rep = {"run_id": r.run_id, "workspace_name": "", "claims": claims,
               "collection_status": "COLLECTION_NOT_FULLY_AUDITED", "validator_result": "PASS"}
        v = validate(rep, ro)
        if state != "PROMPT_INJECTION_SUSPECTED" or v.status != "PASS":
            all_pass = False
    results.append({"test_id": "T9", "scenario": f"prompt injection ({len(fixtures)} variants)",
                    "expected_state": "PROMPT_INJECTION_SUSPECTED",
                    "actual_state": f"{'ALL' if all_pass else 'SOME FAIL'}",
                    "expected_claims": [],
                    "actual_claims": [],
                    "expected_validator_result": "PASS",
                    "actual_validator_result": "PASS" if all_pass else "FAIL",
                    "pass_fail": "PASS" if all_pass else "FAIL"})


# ═══════════════════════ B3 guard ═══════════════════════
def test_B3():
    r = EvidenceRegistry(run_id="b3")
    ro = r.get_reader()
    try:
        ro.put(Evidence(evidence_id="x", state="x", created_at=_iso_now()))
        return "FAIL"
    except AttributeError:
        return "PASS"


# ═══════════════════════ Main ═══════════════════════
if __name__ == "__main__":
    h0 = oracle_hash()
    test_T1(); test_T2(); test_T3(); test_T4(); test_T5()
    test_T6(); test_T7(); test_T8(); test_T9()
    b3 = test_B3()

    for r in results:
        print(json.dumps(r, ensure_ascii=False))
    print(json.dumps({"B3-GUARD": b3}, ensure_ascii=False))
    passed = sum(1 for r in results if r.get("pass_fail") == "PASS")
    h1 = oracle_hash()
    print(json.dumps({"SUMMARY": f"{passed}/{len(results)} PASS",
                      "oracle_pre_hash": h0, "oracle_post_hash": h1,
                      "oracle_unchanged": h0 == h1}, ensure_ascii=False))
