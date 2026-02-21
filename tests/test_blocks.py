from app.slack.blocks import case_controls_blocks

def test_buttons_for_approver_when_no_offer():
    case = {
        "case_id": "ABC123",
        "status": "OPEN",
        "initiator_user_id": "U_INIT",
        "approver_user_id": "U_APPR",
        "stakeholder_user_id": "U_STAKE",
        "ad_account_id": "acc",
        "account_name": "",
        "offer": None,
        "kpi": None,
    }
    blocks = case_controls_blocks(case, viewer_user_id="U_APPR")
    actions = [b for b in blocks if b.get("type") == "actions"]
    assert actions, "Expected actions block"
    texts = [el["text"]["text"] for el in actions[0]["elements"]]
    assert "Propose offer" in texts
    assert "Dismiss case" not in texts

def test_buttons_for_initiator_when_offer_exists():
    case = {
        "case_id": "ABC123",
        "status": "OPEN",
        "initiator_user_id": "U_INIT",
        "approver_user_id": "U_APPR",
        "stakeholder_user_id": "U_STAKE",
        "ad_account_id": "acc",
        "account_name": "",
        "offer": {"type": "DISCOUNT", "details": "10%", "expiry": "2099-01-01"},
        "kpi": None,
    }
    blocks = case_controls_blocks(case, viewer_user_id="U_INIT")
    actions = [b for b in blocks if b.get("type") == "actions"]
    texts = [el["text"]["text"] for el in actions[0]["elements"]]
    assert "Offer accepted" in texts
    assert "Offer declined" in texts
