from fastapi import FastAPI, Request

from app.slack.app import handler

api = FastAPI()

@api.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)

@api.get("/health")
def health():
    return {"ok": True}
