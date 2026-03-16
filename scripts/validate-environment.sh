#!/bin/bash
# Validate an OpenCode environment

if [ -z "$1" ]; then
    echo "Usage: $0 <environment-name>"
    echo "Example: $0 dev1"
    exit 1
fi

ENV_NAME="$1"
ENV_DIR="environments/${ENV_NAME}"
CONTAINER_NAME="opencode-${ENV_NAME}"

echo "Validating environment: ${ENV_NAME}"
echo "================================"

# Check if environment directory exists
if [ ! -d "${ENV_DIR}" ]; then
    echo "❌ Error: Environment directory not found: ${ENV_DIR}"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "${ENV_DIR}/docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in ${ENV_DIR}"
    exit 1
fi

# Check if container is running
if docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
    echo "✅ Container is running: ${CONTAINER_NAME}"
    
    # Test OpenCode installation
    echo "Testing OpenCode installation..."
    if docker exec "${CONTAINER_NAME}" opencode --version > /dev/null 2>&1; then
        echo "✅ OpenCode is installed"
        docker exec "${CONTAINER_NAME}" opencode --version
    else
        echo "❌ OpenCode is not installed or not in PATH"
    fi
    
    # Test OpenCode server if enabled
    echo "Testing OpenCode server..."
    SERVER_PORT=$(grep OPENCODE_SERVER_PORT "${ENV_DIR}/.env" | cut -d= -f2)
    if [ -n "${SERVER_PORT}" ]; then
        if curl -s "http://localhost:${SERVER_PORT}/global/health" > /dev/null 2>&1; then
            echo "✅ OpenCode server is running on port ${SERVER_PORT}"
        else
            echo "❌ OpenCode server is not responding on port ${SERVER_PORT}"
        fi
    else
        echo "⚠️  OpenCode server port not configured"
    fi
    
    # Test Node.js installation
    echo "Testing Node.js installation..."
    if docker exec "${CONTAINER_NAME}" node --version > /dev/null 2>&1; then
        echo "✅ Node.js is installed"
        docker exec "${CONTAINER_NAME}" node --version
    else
        echo "❌ Node.js is not installed"
    fi
    
    # Test volume mounts
    echo "Testing volume mounts..."
    if docker exec "${CONTAINER_NAME}" ls -d /home/dev/workspace > /dev/null 2>&1; then
        echo "✅ Workspace volume is mounted"
    else
        echo "❌ Workspace volume is not mounted"
    fi
    
    # Test user permissions
    echo "Testing user permissions..."
    USER_ID=$(docker exec "${CONTAINER_NAME}" id -u)
    EXPECTED_UID=$(grep USER_ID "${ENV_DIR}/.env" | cut -d= -f2)
    if [ "$USER_ID" = "$EXPECTED_UID" ]; then
        echo "✅ User ID matches configuration: ${USER_ID}"
    else
        echo "❌ User ID mismatch: got ${USER_ID}, expected ${EXPECTED_UID}"
    fi
    
else
    echo "⚠️  Container is not running: ${CONTAINER_NAME}"
    echo "To start it: cd ${ENV_DIR} && docker-compose up -d"
fi

echo ""
echo "Validation complete"
