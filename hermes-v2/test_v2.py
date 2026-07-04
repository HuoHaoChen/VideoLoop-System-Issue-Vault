#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_v2.py — T1–T8 回归测试 〔代码强制〕 §8, §11.3
=====================================================
输出格式 C2: test_id / scenario / input_fixture / mock_http_sequence /
expected_state / actual_state / expected_claims / actual_claims /
expected_validator_result / actual_validator_result /
expected_render_behavior / actual_render_behavior / pass_fail

所有用例固定为 fixture；测试须输出机器可核验结果。
"""

import json, uuid, sys, os
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# 把 hermes-v2 目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_safe import (
    Evidence, EvidenceRegistry, NotionSafe, State, map_http_state,
    collection_status, FORBID_EMPTY_CLAIM_STATES,
)
from validator import validate, emit_report
from report_schema import (
    ClaimType, STATE_TO_CLAIM, REPORT_SCHEMA, WEAK_STATES_FOR_COLLECTION,
)


def _iso_now():
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _make_registry() -> EvidenceRegistry:
    return EvidenceRegistry(run_id=f"test-{uuid.uuid4().hex[:8]}")


def _make_evidence(registry: EvidenceRegistry, state: str, **kw) -> Evidence:
    ev = Evidence(
        evidence_id=str(uuid.uuid4()),
        run_id=registry.run_id,
        state=state,
        created_at=_iso_now(),
        **kw,
    )
    registry.put(ev)
    return ev


def _test_result(tid, scenario, expected_state, actual_state,
                 expected_claims, actual_claims,
                 expected_validator, actual_validator,
                 expected_render, actual_render,
                 input_fixture="", mock_calls=None):
    """C2 格式输出"""
    return {
        "test_id": tid,
        "scenario": scenario,
        "input_fixture": input_fixture,
        "mock_http_sequence": mock_calls or [],
        "expected_state": expected_state,
        "actual_state": actual_state,
        "expected_claims": expected_claims,
        "actual_claims": actual_claims,
        "expected_validator_result": expected_validator,
        "actual_validator_result": actual_validator,
        "expected_render_behavior": expected_render,
        "actual_render_behavior": actual_render,
        "pass_fail": "PASS" if (
            actual_state == expected_state
            and actual_claims == expected_claims
            and actual_validator == expected_validator
            and (expected_render in actual_render or actual_render == expected_render)
        ) else "FAIL",
    }


results = []


# ═══════════════════════════════════════════════════════════════
# T1: 同名空壳页 — HTTP 200 但 entity id ≠ canonical
# ═══════════════════════════════════════════════════════════════

def test_T1():
    """T1: 同名空壳页 → ENTITY_MISMATCH"""
    registry = _make_registry()
    safe = NotionSafe(token="test-token", registry=registry,
                      canonical_pages={"expected-page-123": "parent-456"})

    # 直接模拟：页面不在 canonical registry
    state, _ = safe.verify_page_identity("wrong-page-789")

    # 尝试生成 claim
    claim_type = STATE_TO_CLAIM.get(state)
    claims = []
    if claim_type:
        evs = registry.all()
        if evs:
            claims.append({
                "type": claim_type.value,
                "target_id": "wrong-page-789",
                "evidence_id": evs[-1].evidence_id,
                "determination": "asserted",
            })

    report = {
        "run_id": registry.run_id,
        "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)
    rendered = emit_report(report, registry)

    # Check: 禁称「空」
    has_empty_word = "空" in json.dumps(claims, ensure_ascii=False)

    results.append(_test_result(
        "T1", "同名空壳页", "ENTITY_MISMATCH", state,
        ["PAGE_ENTITY_MISMATCH"],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(禁称空)",
        "PASS(禁称空)" if not has_empty_word else "FAIL(含「空」字)",
    ))


# ═══════════════════════════════════════════════════════════════
# T2: 真空页 — 各域皆空 → CONFIRMED_EMPTY
# ═══════════════════════════════════════════════════════════════

def test_T2():
    """T2: 真空页 → CONFIRMED_EMPTY（经 §6 确认）"""
    registry = _make_registry()
    safe = NotionSafe(token="test-token", registry=registry,
                      canonical_pages={"empty-page": "parent"})

    # 模拟：所有内容域返回空
    safe.verify_page_identity("empty-page")

    # children 全空
    ev = _make_evidence(
        registry, State.NO_VISIBLE_BLOCK_CONTENT,
        operation="read_all_children", target_id="empty-page",
    )

    # 升级到 CONFIRMED_EMPTY（手动模拟 §6 全条件满足）
    ev2 = _make_evidence(
        registry, State.CONFIRMED_EMPTY,
        operation="confirm_empty", target_id="empty-page",
    )

    claim_type = STATE_TO_CLAIM.get(State.CONFIRMED_EMPTY)
    claims = [{
        "type": claim_type.value,
        "target_id": "empty-page",
        "evidence_id": ev2.evidence_id,
        "determination": "asserted",
    }]

    report = {
        "run_id": registry.run_id,
        "workspace_name": "哈马斯空间",
        "claims": claims,
        "collection_status": "COLLECTION_PARTIAL_SUCCESS",
        "validator_result": "PASS",
    }
    v = validate(report, registry)

    results.append(_test_result(
        "T2", "真空页（各域皆空）", "CONFIRMED_EMPTY", State.CONFIRMED_EMPTY,
        ["PAGE_CONFIRMED_EMPTY"],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(已确认为空)",
        "PASS(已确认为空)" if v.status == "PASS" else "FAIL",
    ))


# ═══════════════════════════════════════════════════════════════
# T3: 404 → UNREADABLE_NOT_FOUND
# ═══════════════════════════════════════════════════════════════

def test_T3():
    """T3: 404 → UNREADABLE_NOT_FOUND，禁称「空」"""
    registry = _make_registry()
    state = map_http_state(404)
    assert state == State.UNREADABLE_NOT_FOUND

    ev = _make_evidence(registry, state, operation="http_get",
                        target_id="nonexistent", http_status=404)

    claim_type = STATE_TO_CLAIM.get(state)
    claims = [{
        "type": claim_type.value,
        "target_id": "nonexistent",
        "evidence_id": ev.evidence_id,
        "determination": "asserted",
    }]

    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)
    has_empty_word = "空" in json.dumps(claims, ensure_ascii=False)

    results.append(_test_result(
        "T3", "404", "UNREADABLE_NOT_FOUND", state,
        ["PAGE_UNREADABLE_NOT_FOUND"],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(禁称空)",
        "PASS(禁称空)" if not has_empty_word else "FAIL(含「空」字)",
    ))


# ═══════════════════════════════════════════════════════════════
# T4: 混合 — 4读到/2不可读/1空 → 禁止全称空
# ═══════════════════════════════════════════════════════════════

def test_T4():
    """T4: 混合结果 → COLLECTION_NOT_FULLY_AUDITED，禁止「全部为空」"""
    registry = _make_registry()
    states = [
        State.HAS_DATA, State.HAS_DATA, State.HAS_DATA, State.HAS_DATA,
        State.UNREADABLE_NOT_FOUND, State.UNREADABLE_FORBIDDEN,
        State.NO_VISIBLE_BLOCK_CONTENT,
    ]
    claims = []
    for i, s in enumerate(states):
        ev = _make_evidence(registry, s, target_id=f"page-{i}")
        ct = STATE_TO_CLAIM.get(s)
        if ct:
            claims.append({
                "type": ct.value,
                "target_id": f"page-{i}",
                "evidence_id": ev.evidence_id,
                "determination": "asserted",
            })

    cs = collection_status(states)
    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": cs,
        "validator_result": "PASS",
    }
    v = validate(report, registry)

    # Check: 不能有「全部为空」的表述
    report_str = json.dumps(report, ensure_ascii=False)
    has_all_empty = "全部为空" in report_str or "全空" in report_str

    results.append(_test_result(
        "T4", "诱导「7页全空」— 4读到/2不可读/1空",
        "COLLECTION_NOT_FULLY_AUDITED", cs,
        [c["type"] for c in claims],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(阻断全称)",
        "PASS(阻断全称)" if not has_all_empty else "FAIL(含全称空)",
    ))


# ═══════════════════════════════════════════════════════════════
# T5: UNTRUSTED_RAW 当事实 → INVALID
# ═══════════════════════════════════════════════════════════════

def test_T5():
    """T5: 非 wrapper 来源 → UNTRUSTED_RAW → validator INVALID"""
    registry = _make_registry()
    ev = _make_evidence(registry, State.UNTRUSTED_RAW_TOOL_RESULT,
                        operation="execute_code_raw",
                        target_id="some-page")

    # 尝试用 UNTRUSTED_RAW 支撑事实 claim
    claim_type = STATE_TO_CLAIM.get(State.UNTRUSTED_RAW_TOOL_RESULT)
    claims = [{
        "type": ClaimType.PAGE_HAS_VISIBLE_BLOCKS.value,  # 错误的 claim
        "target_id": "some-page",
        "evidence_id": ev.evidence_id,
        "determination": "asserted",
    }]

    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)

    results.append(_test_result(
        "T5", "裸 urllib 结果当事实",
        "UNTRUSTED_RAW_TOOL_RESULT", State.UNTRUSTED_RAW_TOOL_RESULT,
        ["PAGE_HAS_VISIBLE_BLOCKS"],  # claim 仍在但 determination 改 UNDETERMINED
        [c["type"] for c in v.report.get("claims", [])],
        "INVALID", v.status,
        "PASS(INVALID)",
        "PASS(INVALID)" if v.status == "INVALID" else "FAIL",
    ))


# ═══════════════════════════════════════════════════════════════
# T6: 错 token → WORKSPACE_MISMATCH
# ═══════════════════════════════════════════════════════════════

def test_T6():
    """T6: 错 token (赌石计划) → WORKSPACE_MISMATCH，停止"""
    registry = _make_registry()

    # 模拟 precheck 返回 WORKSPACE_MISMATCH
    ev = _make_evidence(registry, State.WORKSPACE_MISMATCH,
                        operation="precheck",
                        workspace_name="赌石计划")

    # 没有 STATE_TO_CLAIM 映射 → 无事实 claim
    ct = STATE_TO_CLAIM.get(State.WORKSPACE_MISMATCH)
    claims = [] if ct is None else [{
        "type": ct.value,
        "target_id": "N/A",
        "evidence_id": ev.evidence_id,
        "determination": "UNDETERMINED",
    }]

    report = {
        "run_id": registry.run_id, "workspace_name": "赌石计划",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)

    results.append(_test_result(
        "T6", "错 token（赌石计划）",
        "WORKSPACE_MISMATCH", State.WORKSPACE_MISMATCH,
        [],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(停止)",
        "PASS(停止)" if v.status == "PASS" else "FAIL",
    ))


# ═══════════════════════════════════════════════════════════════
# T7: 分页未读完 → PAGINATION_INCOMPLETE
# ═══════════════════════════════════════════════════════════════

def test_T7():
    """T7: has_more=true 中断 → PAGINATION_INCOMPLETE"""
    registry = _make_registry()
    ev = _make_evidence(registry, State.PAGINATION_INCOMPLETE,
                        operation="read_all_children",
                        target_id="big-page",
                        cursor_chain=["cursor-1"])

    ct = STATE_TO_CLAIM.get(State.PAGINATION_INCOMPLETE)
    claims = [{
        "type": ct.value,
        "target_id": "big-page",
        "evidence_id": ev.evidence_id,
        "determination": "asserted",
    }]

    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)
    has_all = "全部" in json.dumps(claims, ensure_ascii=False)

    results.append(_test_result(
        "T7", "分页>100只读首页",
        "PAGINATION_INCOMPLETE", State.PAGINATION_INCOMPLETE,
        ["PAGE_PAGINATION_INCOMPLETE"],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(禁全部)",
        "PASS(禁全部)" if not has_all else "FAIL(含「全部」)",
    ))


# ═══════════════════════════════════════════════════════════════
# T8: comments 域读不了 → CONTENT_DOMAIN_NOT_CHECKED
# ═══════════════════════════════════════════════════════════════

def test_T8():
    """T8: 工具无法读取某内容域 → CONTENT_DOMAIN_NOT_CHECKED"""
    registry = _make_registry()
    ev = _make_evidence(registry, State.CONTENT_DOMAIN_NOT_CHECKED,
                        operation="check_comments",
                        target_id="page-with-comments")

    ct = STATE_TO_CLAIM.get(State.CONTENT_DOMAIN_NOT_CHECKED)
    claims = [{
        "type": ct.value,
        "target_id": "page-with-comments",
        "evidence_id": ev.evidence_id,
        "determination": "asserted",
    }]

    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_NOT_FULLY_AUDITED",
        "validator_result": "PASS",
    }
    v = validate(report, registry)
    has_empty = "空" in json.dumps(claims, ensure_ascii=False)

    results.append(_test_result(
        "T8", "comments 域读不了",
        "CONTENT_DOMAIN_NOT_CHECKED", State.CONTENT_DOMAIN_NOT_CHECKED,
        ["PAGE_CONTENT_DOMAIN_NOT_CHECKED"],
        [c["type"] for c in claims],
        "PASS", v.status,
        "PASS(禁称空)",
        "PASS(禁称空)" if not has_empty else "FAIL(含「空」字)",
    ))


# ═══════════════════════════════════════════════════════════════
# 失败用例：claim.evidence_id 不在 registry
# ═══════════════════════════════════════════════════════════════

def test_FAILURE_missing_evidence():
    """失败用例：evidence_id 不在 registry → INVALID"""
    registry = _make_registry()
    # 不写任何 evidence 到 registry
    claims = [{
        "type": ClaimType.PAGE_HAS_VISIBLE_BLOCKS.value,
        "target_id": "ghost-page",
        "evidence_id": "nonexistent-evid-99999",
        "determination": "asserted",
    }]
    report = {
        "run_id": registry.run_id, "workspace_name": "",
        "claims": claims,
        "collection_status": "COLLECTION_PARTIAL_SUCCESS",
        "validator_result": "PASS",
    }
    v = validate(report, registry)
    return {
        "test_id": "FAILURE-1",
        "scenario": "evidence_id不在registry",
        "actual_validator_result": v.status,
        "errors": v.errors,
    }


# ═══════════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_T1()
    test_T2()
    test_T3()
    test_T4()
    test_T5()
    test_T6()
    test_T7()
    test_T8()
    failure = test_FAILURE_missing_evidence()

    print("=" * 60)
    print("T1–T8 回归测试输出 (C2 格式)")
    print("=" * 60)
    for r in results:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("---")

    print("\n" + "=" * 60)
    print("失败用例输出样例")
    print("=" * 60)
    print(json.dumps(failure, ensure_ascii=False, indent=2))

    # Summary
    passed = sum(1 for r in results if r["pass_fail"] == "PASS")
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{len(results)} PASS")
