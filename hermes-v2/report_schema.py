"""
report_schema.json — V2 报告 JSON schema
=========================================
按 B.1/B.2/B.3 规格。封闭 claim 枚举 + 状态→claim 固定映射。
修正4: FORBID_EMPTY_RENDER 统一复用 notion_safe.FORBID_EMPTY_CLAIM_STATES
"""

from enum import Enum
from notion_safe import FORBID_EMPTY_CLAIM_STATES as FORBID_EMPTY_RENDER


# ═══════════════════════════════════════════════════════════════
# B.1 Claim 封闭枚举 〔代码强制〕
# ═══════════════════════════════════════════════════════════════

class ClaimType(str, Enum):
    PAGE_HAS_VISIBLE_BLOCKS = "PAGE_HAS_VISIBLE_BLOCKS"
    PAGE_NO_VISIBLE_BLOCK_CONTENT = "PAGE_NO_VISIBLE_BLOCK_CONTENT"
    PAGE_CONFIRMED_EMPTY = "PAGE_CONFIRMED_EMPTY"
    PAGE_ENTITY_MISMATCH = "PAGE_ENTITY_MISMATCH"
    PAGE_UNREADABLE_AUTH = "PAGE_UNREADABLE_AUTH"
    PAGE_UNREADABLE_FORBIDDEN = "PAGE_UNREADABLE_FORBIDDEN"
    PAGE_UNREADABLE_NOT_FOUND = "PAGE_UNREADABLE_NOT_FOUND"
    PAGE_UNREADABLE_DELETED_OR_ARCHIVED = "PAGE_UNREADABLE_DELETED_OR_ARCHIVED"
    PAGE_PAGINATION_INCOMPLETE = "PAGE_PAGINATION_INCOMPLETE"
    PAGE_CONTENT_DOMAIN_NOT_CHECKED = "PAGE_CONTENT_DOMAIN_NOT_CHECKED"
    COLLECTION_PARTIAL_SUCCESS = "COLLECTION_PARTIAL_SUCCESS"
    COLLECTION_NOT_FULLY_AUDITED = "COLLECTION_NOT_FULLY_AUDITED"


# ═══════════════════════════════════════════════════════════════
# B.2 状态→claim 固定映射 〔代码强制〕
# ═══════════════════════════════════════════════════════════════

STATE_TO_CLAIM: dict[str, ClaimType] = {
    "HAS_DATA":                     ClaimType.PAGE_HAS_VISIBLE_BLOCKS,
    "NO_VISIBLE_BLOCK_CONTENT":     ClaimType.PAGE_NO_VISIBLE_BLOCK_CONTENT,
    "CONFIRMED_EMPTY":              ClaimType.PAGE_CONFIRMED_EMPTY,
    "ENTITY_MISMATCH":              ClaimType.PAGE_ENTITY_MISMATCH,
    "UNREADABLE_AUTH":              ClaimType.PAGE_UNREADABLE_AUTH,
    "UNREADABLE_FORBIDDEN":         ClaimType.PAGE_UNREADABLE_FORBIDDEN,
    "UNREADABLE_NOT_FOUND":         ClaimType.PAGE_UNREADABLE_NOT_FOUND,
    "UNREADABLE_DELETED_OR_ARCHIVED": ClaimType.PAGE_UNREADABLE_DELETED_OR_ARCHIVED,
    "PAGINATION_INCOMPLETE":        ClaimType.PAGE_PAGINATION_INCOMPLETE,
    "CONTENT_DOMAIN_NOT_CHECKED":   ClaimType.PAGE_CONTENT_DOMAIN_NOT_CHECKED,
    # UNTRUSTED_RAW / PROMPT_INJECTION_SUSPECTED → 无事实 claim → 强制 UNDETERMINED
}

# 弱状态集合 — 禁止全称空结论 §11.2
WEAK_STATES_FOR_COLLECTION = {
    "ENTITY_MISMATCH", "WORKSPACE_MISMATCH",
    "PAGINATION_INCOMPLETE", "PARTIAL_READ", "UNSUPPORTED_CONTENT_PRESENT",
    "UNREADABLE_AUTH", "UNREADABLE_FORBIDDEN", "UNREADABLE_NOT_FOUND",
    "UNREADABLE_DELETED_OR_ARCHIVED",
    "TRANSIENT_TIMEOUT", "TRANSIENT_RATE_LIMIT", "TRANSIENT_5XX",
    "UNTRUSTED_RAW_TOOL_RESULT", "NO_VISIBLE_BLOCK_CONTENT",
    "PROMPT_INJECTION_SUSPECTED", "CONTENT_DOMAIN_NOT_CHECKED",
}

# 修正4: FORBID_EMPTY_RENDER 已统一复用 notion_safe.FORBID_EMPTY_CLAIM_STATES(上方 import)
# 旧本地定义已删除，避免两份不同步。


# ═══════════════════════════════════════════════════════════════
# B.3 Report JSON schema
# ═══════════════════════════════════════════════════════════════

REPORT_SCHEMA = {
    "type": "object",
    "required": ["run_id", "workspace_name", "claims", "collection_status", "validator_result"],
    "properties": {
        "run_id": {"type": "string"},
        "workspace_name": {"type": "string"},
        "canonical_registry_version": {"type": "string"},
        "collection_status": {
            "enum": ["COLLECTION_PARTIAL_SUCCESS", "COLLECTION_NOT_FULLY_AUDITED", None]
        },
        "validator_result": {
            "enum": ["PASS", "INVALID"]
        },
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "target_id", "evidence_id", "determination"],
                "properties": {
                    "type": {"enum": [c.value for c in ClaimType]},
                    "target_id": {"type": "string"},
                    "evidence_id": {"type": "string"},
                    "determination": {"enum": ["asserted", "UNDETERMINED"]},
                },
            },
        },
    },
}
