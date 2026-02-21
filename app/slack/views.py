import datetime as dt
from slack_sdk import WebClient

from app.slack.app import slack_app
from app.slack.pdf_actions import generate_and_upload_finance_snapshot
from app.slack.ui import post_to_case_thread, upsert_case_panel
from app.store.memory import create_case

@slack_app.view("churn_start_modal")
def churn_start_modal_submit(ack, body, client: WebClient, logger):
    ack()

    channel_id = body["view"]["private_metadata"]
    initiator_user_id = body["user"]["id"]
    v = body["view"]["state"]["values"]

    ad_account_id = v["ad_account"]["id"]["value"].strip()
    account_name = (v["account_name"]["name"].get("value") or "").strip()
    stakeholder_user_id = v["stakeholder"]["user"]["selected_user"]
    approver_user_id = v["approver"]["user"]["selected_user"]

    root = client.chat_postMessage(
        channel=channel_id,
        text=(
            f":rotating_light: *Churn Prevention Case* started by <@{initiator_user_id}>.\n"
            f"*Ad account:* `{ad_account_id}` {f'({account_name})' if account_name else ''}\n"
            f"*Stakeholder:* <@{stakeholder_user_id}>\n"
            f"*Finance approver:* <@{approver_user_id}>"
        ),
    )
    thread_ts = root["ts"]

    case = create_case(
        channel_id=channel_id,
        thread_ts=thread_ts,
        initiator_user_id=initiator_user_id,
        approver_user_id=approver_user_id,
        stakeholder_user_id=stakeholder_user_id,
        ad_account_id=ad_account_id,
        account_name=account_name,
    )

    upsert_case_panel(client, case, viewer_user_id=initiator_user_id, note="Case created.")

    try:
        post_to_case_thread(client, case, "Generating finance snapshot…")
        generate_and_upload_finance_snapshot(client, case)
    except Exception as e:
        post_to_case_thread(client, case, f":x: Failed to generate finance snapshot: `{e}`")

    upsert_case_panel(client, case, viewer_user_id=initiator_user_id, note="Finance snapshot ready.")

@slack_app.view("churn_offer_modal")
def churn_offer_modal_submit(ack, body, client: WebClient, logger):
    from app.store.memory import get_case
    from app.slack.ui import upsert_case_panel, post_to_case_thread

    ack()
    case_id = body["view"]["private_metadata"]
    case = get_case(case_id)
    user_id = body["user"]["id"]

    if user_id != case["approver_user_id"]:
        post_to_case_thread(client, case, ":no_entry: Offer submission rejected (not authorized).")
        return

    v = body["view"]["state"]["values"]
    offer_type = v["offer_type"]["type"]["selected_option"]["value"]
    details = v["details"]["text"]["value"].strip()
    expiry = v["expiry"]["date"]["value"].strip()
    notes = (v["internal_notes"]["notes"].get("value") or "").strip()

    case["offer"] = {
        "type": offer_type,
        "details": details,
        "expiry": expiry,
        "notes": notes,
        "created_by": user_id,
        "created_at": dt.datetime.utcnow().isoformat(),
    }

    upsert_case_panel(client, case, viewer_user_id=case["initiator_user_id"], note="Offer proposed.")
