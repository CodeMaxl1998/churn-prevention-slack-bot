import time
import uuid
from typing import Any, Dict, Optional

CASES: Dict[str, Dict[str, Any]] = {}

def new_case_id() -> str:
    return uuid.uuid4().hex[:6].upper()

def get_case(case_id: str) -> Dict[str, Any]:
    c = CASES.get(case_id)
    if not c:
        raise ValueError(f"Unknown case_id: {case_id}")
    return c

def latest_open_case_for_user(user_id: str) -> Optional[Dict[str, Any]]:
    open_cases = [c for c in CASES.values() if c.get("status") == "OPEN" and c.get("initiator_user_id") == user_id]
    open_cases.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return open_cases[0] if open_cases else None

def create_case(
    *,
    channel_id: str,
    thread_ts: str,
    initiator_user_id: str,
    approver_user_id: str,
    stakeholder_user_id: str,
    ad_account_id: str,
    account_name: str,
) -> Dict[str, Any]:
    case_id = new_case_id()
    CASES[case_id] = {
        "case_id": case_id,
        "created_at": time.time(),
        "status": "OPEN",
        "channel_id": channel_id,
        "thread_ts": thread_ts,
        "panel_ts": None,
        "initiator_user_id": initiator_user_id,
        "approver_user_id": approver_user_id,
        "stakeholder_user_id": stakeholder_user_id,
        "ad_account_id": ad_account_id,
        "account_name": account_name,
        "offer": None,
        "kpi": None,
    }
    return CASES[case_id]
