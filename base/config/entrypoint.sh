#!/bin/bash
# Note: This script runs as the dev user (not root) due to docker-compose user: directive
# So we cannot use chown commands here

# Initialize OpenCode configuration if not present
if [ ! -f /home/dev/.config/opencode/config.json ]; then
    echo "Initializing OpenCode configuration..."
    mkdir -p /home/dev/.config/opencode
    cp /tmp/opencode-base.json /home/dev/.config/opencode/config.json 2>/dev/null || true
fi

# Ensure directories exist with proper permissions
mkdir -p /home/dev/.local/share/opencode
mkdir -p /home/dev/.config/code-server

# Start code-server if enabled
if [ "${CODE_SERVER_ENABLED:-true}" = "true" ]; then
    echo "🚀 Starting code-server on port ${CODE_SERVER_PORT:-8096}..."
    
    # Create config directory if it doesn't exist
    mkdir -p /home/dev/.config/code-server
    
    # Generate code-server config
    cat > /home/dev/.config/code-server/config.yaml <<EOF
bind-addr: 0.0.0.0:${CODE_SERVER_PORT:-8096}
auth: ${CODE_SERVER_AUTH:-password}
password: ${CODE_SERVER_PASSWORD:-${OPENCODE_SERVER_PASSWORD}}
cert: false
disable-telemetry: ${CODE_SERVER_DISABLE_TELEMETRY:-true}
disable-update-check: ${CODE_SERVER_DISABLE_UPDATE_CHECK:-true}
EOF
    
    # Start code-server in background as dev user
    # Note: Container already runs as dev user via docker-compose user: directive
    cd /home/dev/workspace
    nohup code-server /home/dev/workspace > /home/dev/.local/share/opencode/code-server.log 2>&1 &
    CODE_SERVER_PID=$!
    
    # Wait a moment for startup
    sleep 3
    
    # Check if code-server started
    if ps -p $CODE_SERVER_PID > /dev/null; then
        echo "✅ code-server started successfully (PID: $CODE_SERVER_PID)"
        echo "   Access: http://localhost:${CODE_SERVER_PORT:-8096}"
        if [ "${CODE_SERVER_AUTH}" = "password" ]; then
            PASSWORD="${CODE_SERVER_PASSWORD:-${OPENCODE_SERVER_PASSWORD}}"
            echo "   Password: ${PASSWORD}"
        else
            echo "   Auth: none (no password required)"
        fi
    else
        echo "⚠️  code-server may not have started correctly"
        echo "   Check logs: /home/dev/.local/share/opencode/code-server.log"
    fi
fi

# Start Web Management UI if enabled
if [ "${WEBUI_ENABLED:-true}" = "true" ]; then
    echo "🌐 Starting Web Management UI on port ${WEBUI_PORT:-9096}..."
    
    # Set environment variables for the web UI
    export WEBUI_HOST="${WEBUI_HOST:-0.0.0.0}"
    export WEBUI_PORT="${WEBUI_PORT:-9096}"
    export ENV_NAME="${ENV_NAME:-unknown}"
    export CONTAINER_NAME="${CONTAINER_NAME:-unknown}"
    
    # Start web UI in background using Python module path
    # The envman module is mounted from the host
    cd /home/dev
    nohup python3 -m envman.webui.app > /home/dev/.local/share/opencode/webui.log 2>&1 &
    WEBUI_PID=$!
    
    # Wait a moment for startup
    sleep 2
    
    # Check if web UI started
    if ps -p $WEBUI_PID > /dev/null; then
        echo "✅ Web Management UI started successfully (PID: $WEBUI_PID)"
        echo "   Access: http://localhost:${WEBUI_PORT:-9096}"
        if [ -n "${OPENCODE_SERVER_PASSWORD}" ]; then
            USERNAME="${OPENCODE_SERVER_USERNAME:-opencode}"
            echo "   Username: ${USERNAME}"
            echo "   Password: ${OPENCODE_SERVER_PASSWORD}"
        fi
    else
        echo "⚠️  Web Management UI may not have started correctly"
        echo "   Check logs: /home/dev/.local/share/opencode/webui.log"
    fi
fi

# Start OpenCode server if enabled
if [ "${OPENCODE_SERVER_ENABLED}" = "true" ]; then
    echo "Starting OpenCode server on ${OPENCODE_SERVER_HOST}:${OPENCODE_SERVER_PORT}"
    
    # Build server command
    SERVER_CMD="opencode serve --hostname ${OPENCODE_SERVER_HOST} --port ${OPENCODE_SERVER_PORT}"
    
    # Add CORS if specified
    if [ -n "${OPENCODE_SERVER_CORS}" ]; then
        SERVER_CMD="${SERVER_CMD} --cors ${OPENCODE_SERVER_CORS}"
    fi
    
    # Start server in background
    # Container already runs as dev user, so run directly
    cd /home/dev/workspace
    ${SERVER_CMD} &
    
    # Wait for server to start
    sleep 5
    
    # Check if server started successfully
    CURL_CMD="curl -s"
    if [ -n "${OPENCODE_SERVER_PASSWORD}" ]; then
        USERNAME="${OPENCODE_SERVER_USERNAME:-opencode}"
        CURL_CMD="${CURL_CMD} --user ${USERNAME}:${OPENCODE_SERVER_PASSWORD}"
    fi
    
    if $CURL_CMD "http://${OPENCODE_SERVER_HOST}:${OPENCODE_SERVER_PORT}/global/health" > /dev/null 2>&1; then
        echo "✅ OpenCode server started successfully"
        echo "   Access: http://${OPENCODE_SERVER_HOST}:${OPENCODE_SERVER_PORT}"
        if [ -n "${OPENCODE_SERVER_PASSWORD}" ]; then
            echo "   Username: ${USERNAME}"
            echo "   Password: ${OPENCODE_SERVER_PASSWORD}"
        fi
        echo "   API Docs: http://${OPENCODE_SERVER_HOST}:${OPENCODE_SERVER_PORT}/doc"
    else
        echo "⚠️  OpenCode server may not have started correctly"
    fi
    
    # Keep container running
    tail -f /dev/null
else
    # Start shell (fallback)
    echo "OpenCode server disabled, starting shell..."
    exec "$@"
fi