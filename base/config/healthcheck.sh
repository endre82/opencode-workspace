#!/bin/bash
# Health check for OpenCode server

# Default values if not set
HOST="${OPENCODE_SERVER_HOST:-0.0.0.0}"
PORT="${OPENCODE_SERVER_PORT:-4096}"

# Build curl command with authentication if password is set
CURL_CMD="curl -s"
if [ -n "${OPENCODE_SERVER_PASSWORD}" ]; then
    USERNAME="${OPENCODE_SERVER_USERNAME:-opencode}"
    CURL_CMD="${CURL_CMD} --user ${USERNAME}:${OPENCODE_SERVER_PASSWORD}"
fi

# Check if server is running
if $CURL_CMD "http://${HOST}:${PORT}/global/health" > /dev/null 2>&1; then
    exit 0
else
    exit 1
fi