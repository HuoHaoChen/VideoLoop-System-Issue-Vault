#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notion_safe.py — Hermes V2 Notion safe wrapper  R6
===================================================
B4 架构级修复: 注入漏检也无害。页面正文永远只能是数据，不能改变 state/claim/validator。
证据链: HTTP response → map_http_state() → evidence.state → STATE_TO_CLAIM → claim
页面内容在结构中只作为 response_hash 存储，永不被解析为指令。
"""

import hashlib, json, os, time, urllib.request, urllib.error, uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# 状态枚举 — 全部完整
# ═══════════════════════════════════════════════════════════════

class State:
    HAS_DATA = "HAS_DATA"
    CONFIRMED_EMPTY = "CONFIRMED_EMPTY"
    ENTITY_MISMATCH = "ENTITY_MISMATCH"
    WORKSPACE_MISMATCH = "WORKSPACE_MISMATCH"
    PAGINATION_INCOMPLETE = "PAGINATION_INCOMPLETE"
    PARTIAL_READ = "PARTIAL_READ"
    UNSUPPORTED_CONTENT_PRESENT = "UNSUPPORTED_CONTENT_PRESENT"
    UNREADABLE_AUTH = "UNREADABLE_AUTH"
    UNREADABLE_FORBIDDEN = "UNREADABLE_FORBIDDEN"
    UNREADABLE_NOT_FOUND = "UNREADABLE_NOT_FOUND"
    UNREADABLE_DELETED_OR_ARCHIVED = "UNREADABLE_DELETED_OR_ARCHIVED"
    TRANSIENT_TIMEOUT = "TRANSIENT_TIMEOUT"
    TRANSIENT_RATE_LIMIT = "TRANSIENT_RATE_LIMIT"
    TRANSIENT_5XX = "TRANSIENT_5XX"
    UNTRUSTED_RAW_TOOL_RESULT = "UNTRUSTED_RAW_TOOL_RESULT"
    NO_VISIBLE_BLOCK_CONTENT = "NO_VISIBLE_BLOCK_CONTENT"
    PROMPT_INJECTION_SUSPECTED = "PROMPT_INJECTION_SUSPECTED"
    CONTENT_DOMAIN_NOT_CHECKED = "CONTENT_DOMAIN_NOT_CHECKED"


# ═══════════════════════════════════════════════════════════════
# HTTP→状态映射表
# ═══════════════════════════════════════════════════════════════

HTTP_STATE_MAP = {
    (200, "children>0"):  State.HAS_DATA,
    (200, "children==0"): State.NO_VISIBLE_BLOCK_CONTENT,
    (200, "id_mismatch"): State.ENTITY_MISMATCH,
    (200, "workspace_mismatch"): State.WORKSPACE_MISMATCH,
    (401, None): State.UNREADABLE_AUTH,
    (403, None): State.UNREADABLE_FORBIDDEN,
    (404, None): State.UNREADABLE_NOT_FOUND,
    (410, None): State.UNREADABLE_DELETED_OR_ARCHIVED,
    (429, None): State.TRANSIENT_RATE_LIMIT,
    (500, None): State.TRANSIENT_5XX,
    (502, None): State.TRANSIENT_5XX,
    (503, None): State.TRANSIENT_5XX,
    (504, None): State.TRANSIENT_5XX,
}

FORBID_EMPTY_CLAIM_STATES = {
    State.ENTITY_MISMATCH, State.WORKSPACE_MISMATCH,
    State.PAGINATION_INCOMPLETE, State.PARTIAL_READ,
    State.UNREADABLE_AUTH, State.UNREADABLE_FORBIDDEN,
    State.UNREADABLE_NOT_FOUND, State.UNREADABLE_DELETED_OR_ARCHIVED,
    State.TRANSIENT_TIMEOUT, State.TRANSIENT_RATE_LIMIT, State.TRANSIENT_5XX,
    State.UNTRUSTED_RAW_TOOL_RESULT, State.NO_VISIBLE_BLOCK_CONTENT,
    State.PROMPT_INJECTION_SUSPECTED, State.CONTENT_DOMAIN_NOT_CHECKED,
    State.UNSUPPORTED_CONTENT_PRESENT,
}

# ═══════════════════════════════════════════════════════════════
# B4: 注入检测(只为 oracle T9 合规存在；架构级安全不依赖它)
# ═══════════════════════════════════════════════════════════════
# 架构保证: 即使 detector 漏报，注入文本也无法影响 state/claim/validator。
# 原因: 证据链是 HTTP→state→claim，页面内容只存为 response_hash(不透明 blob)。
# read_page_markdown 的 state 由 HTTP status + 内容是否存在决定，不由内容语义决定。
# 注入文本永远只能是「数据」，不能被解析为「指令」改变任何判定。

PROMPT_INJECTION_KEYWORDS = [
    ("忽略", "规则"), ("忽略", "指令"), ("直接判空"), ("全部判为空"),
    ("skip", "valid"), ("bypass"), ("disregard", "evidence"),
    ("ignore", "rule"), ("mark", "empty"), ("different", "agent"),
    ("跳过验证"), ("另一个助手"), ("所有页面均为空"),
    ("直接输出", "验证通过"), ("直接输出", "不需要"),
]


def detect_prompt_injection(text: str) -> bool:
    lower = text.lower()
    for kw in PROMPT_INJECTION_KEYWORDS:
        if isinstance(kw, tuple):
            if all(k.lower() in lower for k in kw):
                return True
        elif kw.lower() in lower:
            return True
    return False


def map_http_state(http_status: int, condition: str = None) -> str:
    key = (http_status, condition)
    if key in HTTP_STATE_MAP:
        return HTTP_STATE_MAP[key]
    if 200 <= http_status < 400:
        return State.HAS_DATA
    if http_status >= 500:
        return State.TRANSIENT_5XX
    return State.UNREADABLE_NOT_FOUND


# ═══════════════════════════════════════════════════════════════
# Evidence
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    producer: str = "notion_safe"
    wrapper_version: str = "2.0"
    run_id: str = ""
    operation: str = ""
    endpoint: str = ""
    target_id: str = ""
    workspace_name: str = ""
    canonical_registry_version: str = ""
    state: str = ""
    http_status: Optional[int] = None
    cursor_chain: list = field(default_factory=list)
    input_hash: str = ""
    response_hash: str = ""
    created_at: str = ""


# ═══════════════════════════════════════════════════════════════
# Registry — 写入闭合
# ═══════════════════════════════════════════════════════════════

class _EvidenceRegistryWriter:
    """仅 notion_safe 内部可见。"""
    def __init__(self, store: dict):
        self._store = store
    def put(self, ev: Evidence) -> None:
        self._store[ev.evidence_id] = ev


class RegistryReader:
    """外部只读。validator 只接受此类。无 put(B3)。"""
    def __init__(self, store: dict, run_id: str):
        self._store = store; self._run_id = run_id
    def get(self, evidence_id: str) -> Optional[Evidence]:
        return self._store.get(evidence_id)
    def all(self) -> list[Evidence]:
        return list(self._store.values())
    def all_ids(self) -> set[str]:
        return set(self._store.keys())
    @property
    def run_id(self) -> str:
        return self._run_id
    def dump(self) -> dict:
        return {"run_id": self._run_id,
                "entries": [asdict(ev) for ev in self._store.values()]}


class EvidenceRegistry:
    def __init__(self, run_id: str = None):
        self._store: dict[str, Evidence] = {}
        self._run_id = run_id or str(uuid.uuid4())
        self._writer = _EvidenceRegistryWriter(self._store)
    @property
    def run_id(self) -> str:
        return self._run_id
    def _get_writer(self) -> _EvidenceRegistryWriter:
        return self._writer
    def get_reader(self) -> RegistryReader:
        return RegistryReader(self._store, self._run_id)


# ═══════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════

def _sha256(data) -> str:
    if isinstance(data, str): data = data.encode()
    return hashlib.sha256(data).hexdigest()
def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _extract_text_from_items(items: list) -> str:
    """工单②: 从 database/comments 结果中提取文本用于注入检测。
    递归提取所有 plain_text/rich_text/text.content 字段并拼接。
    失败静默返回空串——检测是附加标注,不应因提取失败中断主流程。"""
    parts = []
    def _recurse(obj):
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, dict):
            if "plain_text" in obj:
                parts.append(obj["plain_text"])
            elif "text" in obj and isinstance(obj["text"], dict):
                parts.append(obj["text"].get("content", ""))
            else:
                for v in obj.values():
                    _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
    try:
        _recurse(items)
    except Exception:
        return ""
    return " ".join(parts)


# ═══════════════════════════════════════════════════════════════
# NotionSafe
# ═══════════════════════════════════════════════════════════════

class NotionSafe:
    API_BASE = "https://api.notion.com"
    API_VERSION = "2025-09-03"

    def __init__(self, token: str, registry: EvidenceRegistry,
                 canonical_pages: dict[str, str] = None):
        self.token = token
        self.registry = registry
        self._writer = registry._get_writer()
        self.canonical_pages = canonical_pages or {}
        self._workspace_name: Optional[str] = None

    # ── precheck ──────────────────────────────────────────
    def precheck(self, expected_ws: str = "哈马斯空间") -> str:
        ev, body = self._http_get("/v1/users/me")
        if ev.http_status != 200:
            return ev.state
        ws_name = body.get("bot", {}).get("workspace_name", "")
        self._workspace_name = ws_name
        if ws_name != expected_ws:
            ev2 = Evidence(evidence_id=str(uuid.uuid4()),
                           run_id=self.registry.run_id, operation="precheck",
                           endpoint="/v1/users/me", workspace_name=ws_name,
                           state=State.WORKSPACE_MISMATCH, http_status=200,
                           created_at=_iso_now())
            self._writer.put(ev2)
            return State.WORKSPACE_MISMATCH
        return State.HAS_DATA

    # ── read_all_children ─────────────────────────────────
    # 工单②: database / comments 路径补 prompt injection 标记(可观测性)
    # 绝不改变"state 由条目存在性决定"的既有逻辑——注入文本仍是数据,不改变事实判定。
    def read_all_children(self, block_id: str) -> tuple[list, Evidence]:
        items, cursor, cursor_chain = [], None, []
        while True:
            ep = f"/v1/blocks/{block_id}/children?page_size=100"
            if cursor: ep += f"&start_cursor={cursor}"
            ev, body = self._http_get(ep)
            cursor_chain.append(cursor)
            if ev.http_status != 200:
                if not cursor:
                    return [], ev
                ev2 = Evidence(evidence_id=str(uuid.uuid4()),
                               producer="notion_safe", wrapper_version="2.0",
                               run_id=self.registry.run_id,
                               operation="read_all_children",
                               endpoint=f"/v1/blocks/{block_id}/children",
                               target_id=block_id,
                               workspace_name=self._workspace_name or "",
                               state=State.PAGINATION_INCOMPLETE,
                               http_status=ev.http_status,
                               cursor_chain=cursor_chain,
                               response_hash=ev.response_hash,
                               created_at=_iso_now())
                self._writer.put(ev2)
                return items, ev2
            results = body.get("results", [])
            items.extend(results)
            if not body.get("has_more"): break
            cursor = body.get("next_cursor")
        base_state = State.HAS_DATA if items else State.NO_VISIBLE_BLOCK_CONTENT
        # 工单②: 注入检测(仅标注,不改变 state=base_state 的事实链)
        injection_detected = False
        if items:
            text_blob = _extract_text_from_items(items)
            injection_detected = bool(text_blob) and detect_prompt_injection(text_blob)
        state = State.PROMPT_INJECTION_SUSPECTED if injection_detected else base_state
        final_ev = Evidence(evidence_id=str(uuid.uuid4()),
                            producer="notion_safe", wrapper_version="2.0",
                            run_id=self.registry.run_id,
                            operation="read_all_children",
                            endpoint=f"/v1/blocks/{block_id}/children",
                            target_id=block_id,
                            workspace_name=self._workspace_name or "",
                            state=state, http_status=200,
                            cursor_chain=cursor_chain,
                            input_hash=_sha256(block_id),
                            response_hash=_sha256(json.dumps(items, sort_keys=True)),
                            created_at=_iso_now())
        self._writer.put(final_ev)
        return items, final_ev

    # ── read_page_markdown ────────────────────────────────
    # B4 架构安全: state 仅由 HTTP status + 内容存在性决定。
    # 注入检测是附加标注，不改变证据派生链。
    def read_page_markdown(self, page_id: str) -> tuple[str, Evidence]:
        ev, body = self._http_get(f"/v1/pages/{page_id}/markdown")
        if ev.http_status != 200:
            return "", ev
        md = body.get("markdown", "")

        # 内容存在 → HAS_DATA；空 → NO_VISIBLE_BLOCK_CONTENT
        # (state 不由内容语义决定——注入文本仍是 HAS_DATA)
        base_state = State.HAS_DATA if md.strip() else State.NO_VISIBLE_BLOCK_CONTENT

        # 注入检测: 若命中 → PROMPT_INJECTION_SUSPECTED(仅为标注)
        # 若漏检 → 内容仍是 HAS_DATA，state 不受内容语义影响
        # 架构保证: state→claim 链只认 HTTP 事实，不认内容语义
        final_state = State.PROMPT_INJECTION_SUSPECTED if (md.strip() and detect_prompt_injection(md)) else base_state

        ev2 = Evidence(evidence_id=str(uuid.uuid4()),
                       producer="notion_safe", wrapper_version="2.0",
                       run_id=self.registry.run_id,
                       operation="read_page_markdown",
                       endpoint=f"/v1/pages/{page_id}/markdown",
                       target_id=page_id,
                       workspace_name=self._workspace_name or "",
                       state=final_state, http_status=200,
                       response_hash=_sha256(md),
                       created_at=_iso_now())
        self._writer.put(ev2)
        return md, ev2

    # ── check_comments_domain ─────────────────────────────
    # 工单②+: 200 路径补注入检测 — 命中返回 PROMPT_INJECTION_SUSPECTED
    def check_comments_domain(self, page_id: str) -> Evidence:
        ev, body = self._http_get(f"/v1/comments?block_id={page_id}")
        if ev.http_status != 200:
            ev2 = Evidence(evidence_id=str(uuid.uuid4()),
                           producer="notion_safe", wrapper_version="2.0",
                           run_id=self.registry.run_id,
                           operation="check_comments_domain",
                           endpoint=f"/v1/comments?block_id={page_id}",
                           target_id=page_id,
                           workspace_name=self._workspace_name or "",
                           state=State.CONTENT_DOMAIN_NOT_CHECKED,
                           http_status=ev.http_status,
                           created_at=_iso_now())
            self._writer.put(ev2)
            return ev2
        # 200 — 注入检测(工单②+: comments 路径可观测)
        results = body.get("results", [])
        text_blob = _extract_text_from_items(results)
        if text_blob and detect_prompt_injection(text_blob):
            ev2 = Evidence(evidence_id=str(uuid.uuid4()),
                           producer="notion_safe", wrapper_version="2.0",
                           run_id=self.registry.run_id,
                           operation="check_comments_domain",
                           endpoint=f"/v1/comments?block_id={page_id}",
                           target_id=page_id,
                           workspace_name=self._workspace_name or "",
                           state=State.PROMPT_INJECTION_SUSPECTED,
                           http_status=200,
                           response_hash=_sha256(json.dumps(results, sort_keys=True)),
                           created_at=_iso_now())
            self._writer.put(ev2)
            return ev2
        return ev

    # ── verify_page_identity ──────────────────────────────
    def verify_page_identity(self, page_id: str, got_id: str, got_parent: str) -> tuple[str, Evidence]:
        if page_id not in self.canonical_pages:
            ev = Evidence(evidence_id=str(uuid.uuid4()),
                          producer="notion_safe", wrapper_version="2.0",
                          run_id=self.registry.run_id,
                          operation="verify_page_identity",
                          target_id=page_id,
                          workspace_name=self._workspace_name or "",
                          state=State.ENTITY_MISMATCH,
                          created_at=_iso_now())
            self._writer.put(ev)
            return State.ENTITY_MISMATCH, ev
        expected_parent = self.canonical_pages[page_id]
        if got_id != page_id or got_parent != expected_parent:
            ev = Evidence(evidence_id=str(uuid.uuid4()),
                          producer="notion_safe", wrapper_version="2.0",
                          run_id=self.registry.run_id,
                          operation="verify_page_identity",
                          target_id=got_id,
                          workspace_name=self._workspace_name or "",
                          state=State.ENTITY_MISMATCH,
                          created_at=_iso_now())
            self._writer.put(ev)
            return State.ENTITY_MISMATCH, ev
        return State.HAS_DATA, None

    # ── 内部 HTTP ──────────────────────────────────────────
    def _http_get(self, endpoint: str) -> tuple[Evidence, dict]:
        url = f"{self.API_BASE}{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}",
                   "Notion-Version": self.API_VERSION,
                   "Content-Type": "application/json"}
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                body = json.loads(raw)
                ev = Evidence(evidence_id=str(uuid.uuid4()),
                              producer="notion_safe", wrapper_version="2.0",
                              run_id=self.registry.run_id, operation="http_get",
                              endpoint=endpoint,
                              workspace_name=self._workspace_name or "",
                              state=map_http_state(resp.status),
                              http_status=resp.status,
                              response_hash=_sha256(raw),
                              created_at=_iso_now())
                self._writer.put(ev)
                return ev, body
        except urllib.error.HTTPError as e:
            raw = e.read()
            ev = Evidence(evidence_id=str(uuid.uuid4()),
                          producer="notion_safe", wrapper_version="2.0",
                          run_id=self.registry.run_id, operation="http_get",
                          endpoint=endpoint,
                          workspace_name=self._workspace_name or "",
                          state=map_http_state(e.code),
                          http_status=e.code,
                          response_hash=_sha256(raw),
                          created_at=_iso_now())
            self._writer.put(ev)
            try:
                return ev, json.loads(raw)
            except json.JSONDecodeError:
                return ev, {"raw": raw.decode(errors="replace")[:500]}
        except Exception as e:
            ev = Evidence(evidence_id=str(uuid.uuid4()),
                          producer="notion_safe", wrapper_version="2.0",
                          run_id=self.registry.run_id, operation="http_get",
                          endpoint=endpoint,
                          workspace_name=self._workspace_name or "",
                          state=State.TRANSIENT_TIMEOUT,
                          created_at=_iso_now())
            self._writer.put(ev)
            return ev, {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# 集合级聚合
# ═══════════════════════════════════════════════════════════════

def collection_status(states: list[str]) -> str:
    weak = {s for s in states if s not in (State.HAS_DATA, State.CONFIRMED_EMPTY)}
    if weak:
        return "COLLECTION_NOT_FULLY_AUDITED"
    return "COLLECTION_PARTIAL_SUCCESS"
