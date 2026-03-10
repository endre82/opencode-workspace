#!/bin/bash
# Create new OpenCode environment

if [ -z "$1" ]; then
    echo "Usage: $0 <environment-name>"
    echo "Example: $0 dev3"
    exit 1
fi

ENV_NAME="$1"
ENV_DIR="environments/${ENV_NAME}"

if [ -d "${ENV_DIR}" ]; then
    echo "Error: Environment ${ENV_NAME} already exists"
    exit 1
fi

echo "Creating new environment: ${ENV_NAME}"
echo ""

# Prompt for username
read -p "Enter OpenCode server username [opencode]: " SERVER_USERNAME
SERVER_USERNAME=${SERVER_USERNAME:-opencode}

# Prompt for password
read -sp "Enter OpenCode server password (leave empty to generate random): " SERVER_PASSWORD
echo ""
if [ -z "$SERVER_PASSWORD" ]; then
    SERVER_PASSWORD=$(openssl rand -base64 12)
    echo "Generated random password: ${SERVER_PASSWORD}"
fi

# Create directory structure
echo "Creating directory structure..."
mkdir -p "${ENV_DIR}/workspace"
mkdir -p "${ENV_DIR}/opencode_config"
mkdir -p "shared/config"
mkdir -p "shared/models"

# Copy and customize templates
cp environments/template/docker-compose.yml.template "${ENV_DIR}/docker-compose.yml"
cp environments/template/.env.template "${ENV_DIR}/.env"

# Replace placeholders
sed -i "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/docker-compose.yml"
sed -i "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/.env"

# Assign next available user ID
LAST_UID=$(find environments/ -name ".env" -type f ! -path "*/template/*" -exec grep USER_ID {} \; | cut -d= -f2 | sort -n | tail -1)
if [ -z "$LAST_UID" ]; then
    LAST_UID=999
fi
NEXT_UID=$((LAST_UID + 1))
sed -i "s/USER_ID=.*/USER_ID=${NEXT_UID}/" "${ENV_DIR}/.env"
sed -i "s/GROUP_ID=.*/GROUP_ID=${NEXT_UID}/" "${ENV_DIR}/.env"
sed -i "s/CONTAINER_NAME=.*/CONTAINER_NAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"
sed -i "s/HOSTNAME=.*/HOSTNAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"

# Assign next available server port
LAST_PORT=$(find environments/ -name ".env" -type f ! -path "*/template/*" -exec grep OPENCODE_SERVER_PORT {} \; | cut -d= -f2 | sort -n | tail -1)
if [ -z "$LAST_PORT" ]; then
    LAST_PORT=4095
fi
NEXT_PORT=$((LAST_PORT + 1))
sed -i "s/OPENCODE_SERVER_PORT=.*/OPENCODE_SERVER_PORT=${NEXT_PORT}/" "${ENV_DIR}/.env"

# Set server credentials
sed -i "s/OPENCODE_SERVER_USERNAME=.*/OPENCODE_SERVER_USERNAME=${SERVER_USERNAME}/" "${ENV_DIR}/.env"
sed -i "s/OPENCODE_SERVER_PASSWORD=.*/OPENCODE_SERVER_PASSWORD=${SERVER_PASSWORD}/" "${ENV_DIR}/.env"

# Set volume paths
sed -i "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=./workspace|" "${ENV_DIR}/.env"
sed -i "s|GLOBAL_CONFIG=.*|GLOBAL_CONFIG=~/.config/opencode:ro|" "${ENV_DIR}/.env"
sed -i "s|OPENCODE_ENV_CONFIG=.*|OPENCODE_ENV_CONFIG=./opencode_config:rw|" "${ENV_DIR}/.env"

echo ""
echo "✅ Environment ${ENV_NAME} created successfully"
echo ""
echo "📋 Configuration Summary:"
echo "   User ID assigned: ${NEXT_UID}"
echo "   Server port assigned: ${NEXT_PORT}"
echo "   Server username: ${SERVER_USERNAME}"
echo "   Server password: ${SERVER_PASSWORD}"
echo ""
echo "📁 Directories created:"
echo "   ${ENV_DIR}/workspace"
echo "   ${ENV_DIR}/opencode_config"
echo "   ../../shared/config"
echo "   ../../shared/models"
echo ""
echo "Next steps:"
echo "1. Review ${ENV_DIR}/.env for any customizations"
echo "2. Run: cd ${ENV_DIR} && docker compose build"
echo "3. Run: cd ${ENV_DIR} && docker compose up -d"
echo ""
echo "Connect via OpenCode TUI:"
echo "  opencode --host localhost --port ${NEXT_PORT} --username ${SERVER_USERNAME} --password ${SERVER_PASSWORD}"