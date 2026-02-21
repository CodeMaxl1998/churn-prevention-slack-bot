# Slack Setup

## 1) Create Slack App
- https://api.slack.com/apps
- Create new app from scratch

## 2) OAuth scopes
Bot token scopes:
- commands
- chat:write
- files:write

Install app into workspace, copy:
- Bot token → `SLACK_BOT_TOKEN`
- Signing secret → `SLACK_SIGNING_SECRET`

## 3) Enable Interactivity
Enable Interactivity & Shortcuts.
Set Request URL:
`https://<ngrok-id>.ngrok-free.app/slack/events`

## 4) Create Slash Command
Command: `/churn-prevention-start`
Request URL:
`https://<ngrok-id>.ngrok-free.app/slack/events`

## 5) Run locally
`./run.sh` + `ngrok http 8000`
