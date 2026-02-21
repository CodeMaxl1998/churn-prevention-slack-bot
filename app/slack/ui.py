from typing import Any, Dict

from slack_sdk import WebClient

from app.slack.blocks import case_controls_blocks

def post_to_case_thread(
    client: WebClient,
    case: Dict[str, Any],
    text: str,
    blocks=None,
):
    payload: Dict[str, Any] = {
        "channel": case["channel_id"],
        "thread_ts": case["thread_ts"],
        "text": text,
    }
    if blocks is not None:
        payload["blocks"] = blocks
    return client.chat_postMessage(**payload)

def upsert_case_panel(client: WebClient, case: Dict[str, Any], viewer_user_id: str, note: str = ""):
    """
    Posts panel once; afterwards edits it. Stores panel_ts on the case.
    """
    text = note or f"Case `{case['case_id']}`"
    blocks = case_controls_blocks(case, viewer_user_id)

    if case.get("panel_ts"):
        return client.chat_update(
            channel=case["channel_id"],
            ts=case["panel_ts"],
            text=text,
            blocks=blocks,
        )

    msg = client.chat_postMessage(
        channel=case["channel_id"],
        thread_ts=case["thread_ts"],
        text=text,
        blocks=blocks,
    )
    case["panel_ts"] = msg["ts"]
    return msg
