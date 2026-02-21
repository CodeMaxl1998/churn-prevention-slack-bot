import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    slack_bot_token: str
    slack_signing_secret: str

def get_settings() -> Settings:
    return Settings(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN", ""),
        slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET", ""),
    )
