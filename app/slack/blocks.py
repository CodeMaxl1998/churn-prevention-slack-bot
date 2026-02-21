from typing import Any, Dict, List, Optional

from app.reporting.utils import fmt_int, fmt_money, fmt_pct

def _status_emoji(status: str) -> str:
    return {
        "OPEN": ":rotating_light:",
        "ACCEPTED": ":white_check_mark:",
        "DECLINED": ":no_entry_sign:",
        "DISMISSED": ":wastebasket:",
    }.get(status, ":grey_question:")

def _offer_summary(case: Dict[str, Any]) -> str:
    offer = case.get("offer")
    if not offer:
        return "_No offer proposed yet._"
    details = (offer.get("details") or "").strip()
    if len(details) > 120:
        details = details[:117] + "…"
    expiry = offer.get("expiry") or "—"
    typ = offer.get("type") or "—"
    return f"*{typ}* — {details}\n_Expires_: {expiry}"

def _next_step_text(case: Dict[str, Any]) -> str:
    status = case.get("status", "OPEN")
    if status != "OPEN":
        return "Case is closed."
    if not case.get("offer"):
        return f"Next: <@{case['approver_user_id']}> proposes the special offer."
    return f"Next: <@{case['initiator_user_id']}> holds the meeting and closes the case."

def _action_button(text: str, action_id: str, value: str, style: Optional[str] = None) -> Dict[str, Any]:
    btn: Dict[str, Any] = {
        "type": "button",
        "text": {"type": "plain_text", "text": text},
        "action_id": action_id,
        "value": value,
    }
    if style:
        btn["style"] = style
    return btn

def case_controls_blocks(case: Dict[str, Any], viewer_user_id: str) -> List[Dict[str, Any]]:
    case_id = case["case_id"]
    status = case.get("status", "OPEN")
    initiator = case["initiator_user_id"]
    approver = case["approver_user_id"]
    stakeholder = case["stakeholder_user_id"]
    offer_exists = bool(case.get("offer"))

    header = (
        f"{_status_emoji(status)} *Churn Prevention Case* `{case_id}`\n"
        f"*Ad account*: `{case['ad_account_id']}`"
        + (f" ({case.get('account_name')})" if case.get("account_name") else "")
        + "\n"
        f"*Initiator*: <@{initiator}>   •   *Approver*: <@{approver}>   •   *Stakeholder*: <@{stakeholder}>"
    )

    blocks: List[Dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": header}},
        {"type": "divider"},
    ]

    kpi = case.get("kpi")
    if kpi:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": (
                    f"*Finance snapshot ({kpi.get('range','')})*\n"
                    f"Spend: *{fmt_money(float(kpi.get('spend', 0.0)))}*  •  "
                    f"Impressions: *{fmt_int(float(kpi.get('impressions', 0)))}*  •  "
                    f"CTR: *{fmt_pct(float(kpi.get('ctr', 0.0)))}*  •  "
                    f"E-CPCL: *{fmt_money(float(kpi.get('e_cpcl', 0.0)))}*"
                )},
            }
        )
    else:
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Finance snapshot*\n_Generating / not available yet._"}}
        )

    blocks += [
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Offer*\n{_offer_summary(case)}"}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"*Status*: *{status}*  •  {_next_step_text(case)}"}]},
    ]

    actions: List[Dict[str, Any]] = []

    if status == "OPEN":
        if not offer_exists:
            if viewer_user_id == approver:
                actions.append(_action_button("Propose offer", "cp_propose_offer", case_id, style="primary"))
            if viewer_user_id == initiator:
                actions.append(_action_button("Dismiss case", "cp_dismiss_case", case_id, style="danger"))
        else:
            if viewer_user_id == initiator:
                actions.append(_action_button("Offer accepted", "cp_offer_accepted", case_id, style="primary"))
                actions.append(_action_button("Offer declined", "cp_offer_declined", case_id, style="danger"))
                actions.append(_action_button("Dismiss case", "cp_dismiss_case", case_id, style="danger"))
    else:
        if viewer_user_id == initiator:
            actions.append(_action_button("Reopen case", "cp_reopen_case", case_id))

    if actions:
        blocks.append({"type": "actions", "elements": actions})

    return blocks
