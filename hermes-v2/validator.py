#!/usr/bin/env python3
"""validator.py V2.1 — 工单① 加严口径: 写能力黑名单 + EvidenceRegistry/明文 dict 拒绝"""

import json
from dataclasses import dataclass
from typing import Optional
from report_schema import (
    ClaimType, STATE_TO_CLAIM, WEAK_STATES_FOR_COLLECTION,
    FORBID_EMPTY_RENDER,
)
from notion_safe import State, RegistryReader, EvidenceRegistry


# 工单①: 写能力黑名单 — registry 暴露任一项即拒绝
_WRITE_CAPABILITIES = ['put', '__setitem__', 'update', 'clear', 'writer']


def _assert_readonly_registry(registry) -> Optional[str]:
    """检查 registry 是否安全只读。返回错误消息或 None。
    
    白名单(主防线): 必须是 RegistryReader 实例。
    黑名单(defense-in-depth): 含写能力/明文dict/EvidenceRegistry → 拒。
    
    说明: RegistryReader 有私有 _store 属性(Python 无真 private), 
    但无任何公开写方法, caller 须主动越权才能触碰。此阻断防的是
    '无意间传入可写对象', 不防 '蓄意侵犯私有属性'。
    """
    # ── 白名单: 必须为 RegistryReader 实例 ──
    if registry.__class__ is not RegistryReader:
        return "工单①: registry 必须是 RegistryReader 实例 → 拒绝。只接受 RegistryReader。"
    # ── defense-in-depth: 写能力黑名单 + 明文dict/EvidenceRegistry ──
    for cap in _WRITE_CAPABILITIES:
        if hasattr(registry, cap):
            return f"工单①: registry 含写能力 '{cap}' → 拒绝。只接受 RegistryReader。"
    if isinstance(registry, dict):
        return "工单①: registry 是明文 dict → 拒绝。必须用 RegistryReader(r.get_reader()) 包装。"
    if isinstance(registry, EvidenceRegistry):
        return "工单①: registry 是 EvidenceRegistry(含 _get_writer 写入口) → 拒绝。必须传 r.get_reader()。"
    if not hasattr(registry, 'get'):
        return "工单①: registry 无 get 方法 → 不可读,拒绝。只接受 RegistryReader。"
    return None


@dataclass
class ValidationResult:
    status: str
    errors: list
    report: dict


def validate(report_json: dict, registry) -> ValidationResult:
    # ── 工单①: fail-closed 准入 ──
    err = _assert_readonly_registry(registry)
    if err:
        return ValidationResult(
            status="INVALID",
            errors=[err],
            report=dict(report_json),
        )

    errors = []
    report = dict(report_json)
    report_invalid = False

    for i, claim in enumerate(report.get("claims", [])):
        eid = claim.get("evidence_id", "")
        if not eid:
            errors.append(f"B.4.1: claim[{i}] 缺 evidence_id")
            continue
        ev = registry.get(eid)
        if ev is None:
            errors.append(f"B.4.1: claim[{i}] eid={eid} 不在 registry")
            claim["determination"] = "UNDETERMINED"
            continue

        original_determination = claim.get("determination", "")

        if ev.state == State.UNTRUSTED_RAW_TOOL_RESULT:
            claim["determination"] = "UNDETERMINED"
            if original_determination == "asserted":
                errors.append(f"B.4.3: claim[{i}] UNTRUSTED_RAW + asserted → 整份 INVALID")
                report_invalid = True

        claim_type = claim.get("type", "")
        expected_claim = STATE_TO_CLAIM.get(ev.state)
        if expected_claim is None:
            if ev.state not in (State.UNTRUSTED_RAW_TOOL_RESULT,
                                State.WORKSPACE_MISMATCH,
                                State.PROMPT_INJECTION_SUSPECTED):
                errors.append(f"B.4.2: claim[{i}] state={ev.state} 无映射")
            claim["determination"] = "UNDETERMINED"
        elif claim_type != expected_claim.value:
            errors.append(f"B.4.2: claim[{i}] type={claim_type} ≠ expected {expected_claim.value}")
            claim["type"] = expected_claim.value

        if ev.state in FORBID_EMPTY_RENDER:
            if "空" in json.dumps(claim, ensure_ascii=False):
                errors.append(f"B.4.5: claim[{i}] state={ev.state} 禁称「空」")

    all_states = []
    for claim in report.get("claims", []):
        ev = registry.get(claim.get("evidence_id", ""))
        if ev:
            all_states.append(ev.state)
    if any(s in WEAK_STATES_FOR_COLLECTION for s in all_states):
        report["collection_status"] = "COLLECTION_NOT_FULLY_AUDITED"

    has_errors = len(errors) > 0 or report_invalid
    status = "INVALID" if has_errors else "PASS"
    report["validator_result"] = status
    return ValidationResult(status=status, errors=errors, report=report)


def emit_report(report_json: dict, registry) -> str:
    result = validate(report_json, registry)
    if result.status != "PASS":
        return json.dumps({"blocked": True, "reason": "B.4.6 render gate",
                           "errors": result.errors}, ensure_ascii=False, indent=2)
    return json.dumps(result.report, ensure_ascii=False, indent=2)
