#!/usr/bin/env bash
set -e

export PYTHONPATH="$(pwd)"

uvicorn app.main:api --host 0.0.0.0 --port 8000 --reload