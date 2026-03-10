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

# Get host user IDs for defaults
HOST_UID=$(id -u)
HOST_GID=$(id -g)

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

# Prompt for USER_ID
read -p "Enter USER_ID (default: ${HOST_UID}): " USER_ID
USER_ID=${USER_ID:-$HOST_UID}

# Prompt for GROUP_ID
read -p "Enter GROUP_ID (default: ${HOST_GID}): " GROUP_ID
GROUP_ID=${GROUP_ID:-$HOST_GID}

# Prompt for WORKSPACE_DIR
read -p "Enter WORKSPACE_DIR (default: ./workspace): " WORKSPACE_DIR
WORKSPACE_DIR=${WORKSPACE_DIR:-./workspace}

# Prompt for GLOBAL_CONFIG
read -p "Enter GLOBAL_CONFIG (default: ~/.config/opencode): " GLOBAL_CONFIG
GLOBAL_CONFIG=${GLOBAL_CONFIG:-~/.config/opencode}

# Prompt for OPENCODE_ENV_CONFIG
read -p "Enter OPENCODE_ENV_CONFIG (default: ./opencode_config): " OPENCODE_ENV_CONFIG
OPENCODE_ENV_CONFIG=${OPENCODE_ENV_CONFIG:-./opencode_config}

# Find all used ports starting from 4100
USED_PORTS=$(find environments/ -name ".env" -type f ! -path "*/template/*" -exec grep OPENCODE_SERVER_PORT {} \; | cut -d= -f2 | sort -n)
DEFAULT_PORT=4100

# Find next available port starting from 4100
while echo "$USED_PORTS" | grep -q "^${DEFAULT_PORT}$"; do
    DEFAULT_PORT=$((DEFAULT_PORT + 1))
done

# Prompt for SERVER_PORT
read -p "Enter SERVER_PORT (default: ${DEFAULT_PORT}): " SERVER_PORT
SERVER_PORT=${SERVER_PORT:-$DEFAULT_PORT}

# Check if entered port is already used
if echo "$USED_PORTS" | grep -q "^${SERVER_PORT}$"; then
    echo "⚠️  Warning: Port ${SERVER_PORT} is already used, auto-incrementing to next available port"
    # Find next available port starting from entered port
    while echo "$USED_PORTS" | grep -q "^${SERVER_PORT}$"; do
        SERVER_PORT=$((SERVER_PORT + 1))
    done
    echo "✅ Using port ${SERVER_PORT} instead"
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

# Update .env file with user-provided values
sed -i "s/USER_ID=.*/USER_ID=${USER_ID}/" "${ENV_DIR}/.env"
sed -i "s/GROUP_ID=.*/GROUP_ID=${GROUP_ID}/" "${ENV_DIR}/.env"
sed -i "s/CONTAINER_NAME=.*/CONTAINER_NAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"
sed -i "s/HOSTNAME=.*/HOSTNAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"
sed -i "s/OPENCODE_SERVER_PORT=.*/OPENCODE_SERVER_PORT=${SERVER_PORT}/" "${ENV_DIR}/.env"
sed -i "s/OPENCODE_SERVER_USERNAME=.*/OPENCODE_SERVER_USERNAME=${SERVER_USERNAME}/" "${ENV_DIR}/.env"
sed -i "s|OPENCODE_SERVER_PASSWORD=.*|OPENCODE_SERVER_PASSWORD=${SERVER_PASSWORD}|" "${ENV_DIR}/.env"
sed -i "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=${WORKSPACE_DIR}|" "${ENV_DIR}/.env"
sed -i "s|GLOBAL_CONFIG=.*|GLOBAL_CONFIG=${GLOBAL_CONFIG}|" "${ENV_DIR}/.env"
sed -i "s|OPENCODE_ENV_CONFIG=.*|OPENCODE_ENV_CONFIG=${OPENCODE_ENV_CONFIG}|" "${ENV_DIR}/.env"

echo ""
echo "✅ Environment ${ENV_NAME} created successfully"
echo ""
echo "📋 Configuration Summary:"
echo "   USER_ID: ${USER_ID}"
echo "   GROUP_ID: ${GROUP_ID}"
echo "   WORKSPACE_DIR: ${WORKSPACE_DIR}"
echo "   GLOBAL_CONFIG: ${GLOBAL_CONFIG}"
echo "   OPENCODE_ENV_CONFIG: ${OPENCODE_ENV_CONFIG}"
echo "   SERVER_PORT: ${SERVER_PORT}"
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
echo "  opencode --host localhost --port ${SERVER_PORT} --username ${SERVER_USERNAME} --password ${SERVER_PASSWORD}"