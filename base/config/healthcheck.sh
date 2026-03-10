#!/bin/bash
# Health check for OpenCode server

# Default values if not set
HOST="${OPENCODE_SERVER_HOST:-0.0.0.0}"
PORT="${OPENCODE_SERVER_PORT:-4096}"

# Check if server is running
if curl -s "http://${HOST}:${PORT}/global/health" > /dev/null 2>&1; then
    exit 0
else
    exit 1
fi