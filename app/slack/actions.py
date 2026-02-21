import datetime as dt
from slack_sdk import WebClient

from app.slack.app import slack_app
from app.slack.ui import upsert_case_panel, post_to_case_thread
from app.store.memory import get_case

@slack_app.action("cp_propose_offer")
def on_cp_propose_offer(ack, body, client: WebClient, logger):
    ack()
    case_id = body["actions"][0]["value"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["approver_user_id"]:
        client.chat_postEphemeral(
            channel=case["channel_id"],
            user=user_id,
            text=f"Only <@{case['approver_user_id']}> can propose offers for case `{case_id}`.",
        )
        return

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "churn_offer_modal",
            "private_metadata": case_id,
            "title": {"type": "plain_text", "text": "Propose Offer"},
            "submit": {"type": "plain_text", "text": "Send"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "offer_type",
                    "label": {"type": "plain_text", "text": "Offer type"},
                    "element": {
                        "type": "static_select",
                        "action_id": "type",
                        "options": [
                            {"text": {"type": "plain_text", "text": "Free credits"}, "value": "CREDITS"},
                            {"text": {"type": "plain_text", "text": "Discount"}, "value": "DISCOUNT"},
                            {"text": {"type": "plain_text", "text": "Reduced terms"}, "value": "TERMS"},
                            {"text": {"type": "plain_text", "text": "Custom"}, "value": "CUSTOM"},
                        ],
                    },
                },
                {
                    "type": "input",
                    "block_id": "details",
                    "label": {"type": "plain_text", "text": "Offer details"},
                    "element": {"type": "plain_text_input", "action_id": "text", "multiline": True},
                },
                {
                    "type": "input",
                    "block_id": "expiry",
                    "label": {"type": "plain_text", "text": "Offer expiry (YYYY-MM-DD)"},
                    "element": {"type": "plain_text_input", "action_id": "date", "initial_value": (dt.date.today() + dt.timedelta(days=14)).isoformat()},
                },
                {
                    "type": "input",
                    "block_id": "internal_notes",
                    "optional": True,
                    "label": {"type": "plain_text", "text": "Internal notes (optional)"},
                    "element": {"type": "plain_text_input", "action_id": "notes", "multiline": True},
                },
            ],
        },
    )

@slack_app.action("cp_dismiss_case")
def on_cp_dismiss_case(ack, body, client: WebClient, logger):
    ack()
    case_id = body["actions"][0]["value"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["initiator_user_id"]:
        client.chat_postEphemeral(channel=case["channel_id"], user=user_id, text="Only the initiator can dismiss this case.")
        return

    case["status"] = "DISMISSED"
    upsert_case_panel(client, case, viewer_user_id=user_id, note="Case dismissed.")

@slack_app.action("cp_offer_accepted")
def on_cp_offer_accepted(ack, body, client: WebClient, logger):
    ack()
    case_id = body["actions"][0]["value"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["initiator_user_id"]:
        client.chat_postEphemeral(channel=case["channel_id"], user=user_id, text="Only the initiator can close this case.")
        return

    case["status"] = "ACCEPTED"
    upsert_case_panel(client, case, viewer_user_id=user_id, note="Offer accepted. Case closed.")

@slack_app.action("cp_offer_declined")
def on_cp_offer_declined(ack, body, client: WebClient, logger):
    ack()
    case_id = body["actions"][0]["value"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["initiator_user_id"]:
        client.chat_postEphemeral(channel=case["channel_id"], user=user_id, text="Only the initiator can close this case.")
        return

    case["status"] = "DECLINED"
    upsert_case_panel(client, case, viewer_user_id=user_id, note="Offer declined. Case closed.")

@slack_app.action("cp_reopen_case")
def on_cp_reopen_case(ack, body, client: WebClient, logger):
    ack()
    case_id = body["actions"][0]["value"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["initiator_user_id"]:
        client.chat_postEphemeral(channel=case["channel_id"], user=user_id, text="Only the initiator can reopen this case.")
        return

    case["status"] = "OPEN"
    upsert_case_panel(client, case, viewer_user_id=user_id, note="Case reopened.")
