import os
os.environ["MPLBACKEND"] = "Agg"

from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.settings import get_settings

settings = get_settings()

slack_app = SlackApp(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
)

handler = SlackRequestHandler(slack_app)

from app.slack import commands 
from app.slack import blocks   
from app.slack import ui
from app.slack import actions
from app.slack import views