#!/usr/bin/env bash
set -e

# Default log level can be overridden via `--build-arg LOG_LEVEL=...` or `docker run -e LOG_LEVEL=...`
LOG_LEVEL=${LOG_LEVEL:-info}

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level "$LOG_LEVEL"
