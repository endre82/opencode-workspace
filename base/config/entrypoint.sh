#!/bin/bash
# Fix permissions on mounted volumes
chown -R dev:dev /home/dev/workspace 2>/dev/null || true

# Initialize OpenCode configuration if not present
if [ ! -f /home/dev/.config/opencode/config.json ]; then
    echo "Initializing OpenCode configuration..."
    mkdir -p /home/dev/.config/opencode
    cp /tmp/opencode-base.json /home/dev/.config/opencode/config.json 2>/dev/null || true
    chown -R dev:dev /home/dev/.config/opencode
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