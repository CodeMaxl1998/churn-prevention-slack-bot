# Churn Prevention Slack Workflow Bot

A Slack workflow bot that helps teams prevent churn:
1) Start a churn case
2) Auto-generate a finance snapshot PDF for the approver
3) Approver proposes an offer
4) Initiator finalizes status (accepted/declined) in Slack

## Demo
(Add screenshots/GIF here)

## Local Setup
1. Create `.env` from `.env.example`
2. Install deps
3. Run: `./run.sh`
4. Expose: `ngrok http 8000`
5. Set Slack URLs to `{ngrok}/slack/events`

## Architecture
- `app/slack/*` Slack UI + handlers
- `app/reporting/*` KPI + PDF generation
- `app/store/*` case persistence (in-memory in dev)

## Roadmap
- Persistent storage (SQLite)
- Background jobs for PDF generation
- Real Ads API integration
