#!/bin/bash
# Health check for OpenCode server and code-server

# Default values if not set
HOST="${OPENCODE_SERVER_HOST:-0.0.0.0}"
PORT="${OPENCODE_SERVER_PORT:-4096}"

# Build curl command with authentication if password is set
CURL_CMD="curl -s"
if [ -n "${OPENCODE_SERVER_PASSWORD}" ]; then
    USERNAME="${OPENCODE_SERVER_USERNAME:-opencode}"
    CURL_CMD="${CURL_CMD} --user ${USERNAME}:${OPENCODE_SERVER_PASSWORD}"
fi

# Check if OpenCode server is running
if ! $CURL_CMD "http://${HOST}:${PORT}/global/health" > /dev/null 2>&1; then
    echo "OpenCode server health check failed"
    exit 1
fi

# Check if code-server is running (if enabled)
if [ "${CODE_SERVER_ENABLED:-true}" = "true" ]; then
    CODE_PORT="${CODE_SERVER_PORT:-8096}"
    if ! curl -s "http://localhost:${CODE_PORT}/" > /dev/null 2>&1; then
        echo "code-server health check failed"
        exit 1
    fi
fi

# Check if Web UI is running (if enabled)
if [ "${WEBUI_ENABLED:-true}" = "true" ]; then
    WEBUI_PORT="${WEBUI_PORT:-9096}"
    if ! curl -s "http://localhost:${WEBUI_PORT}/health" > /dev/null 2>&1; then
        echo "Web UI health check failed"
        exit 1
    fi
fi

exit 0