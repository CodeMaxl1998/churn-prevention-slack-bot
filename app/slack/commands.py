from slack_sdk import WebClient

from app.slack.app import slack_app
from app.slack.pdf_actions import generate_and_upload_finance_snapshot
from app.slack.ui import post_to_case_thread, upsert_case_panel
from app.store.memory import create_case

@slack_app.command("/churn-prevention-start")
def churn_prevention_start(ack, body, client: WebClient, logger):
    ack()
    channel_id = body["channel_id"]
    trigger_id = body["trigger_id"]

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "churn_start_modal",
            "private_metadata": channel_id,
            "title": {"type": "plain_text", "text": "Start Churn Case"},
            "submit": {"type": "plain_text", "text": "Start"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "ad_account",
                    "label": {"type": "plain_text", "text": "Ad Account ID (UUID)"},
                    "element": {"type": "plain_text_input", "action_id": "id"},
                },
                {
                    "type": "input",
                    "block_id": "account_name",
                    "label": {"type": "plain_text", "text": "Account Name (optional)"},
                    "optional": True,
                    "element": {"type": "plain_text_input", "action_id": "name"},
                },
                {
                    "type": "input",
                    "block_id": "stakeholder",
                    "label": {"type": "plain_text", "text": "Stakeholder (Slack user)"},
                    "element": {"type": "users_select", "action_id": "user"},
                },
                {
                    "type": "input",
                    "block_id": "approver",
                    "label": {"type": "plain_text", "text": "Finance approver (proposes offer)"},
                    "element": {"type": "users_select", "action_id": "user"},
                },
            ],
        },
    )
