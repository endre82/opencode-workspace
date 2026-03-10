#!/bin/bash
# Update existing OpenCode environment to match new template format

if [ -z "$1" ]; then
    echo "Usage: $0 <environment-name>"
    echo "Example: $0 dev1"
    echo ""
    echo "This script updates an existing environment to match the new template format"
    echo "with dynamic parameters and proper directory structure."
    exit 1
fi

ENV_NAME="$1"
ENV_DIR="environments/${ENV_NAME}"

if [ ! -d "${ENV_DIR}" ]; then
    echo "Error: Environment ${ENV_NAME} not found"
    exit 1
fi

echo "Updating environment: ${ENV_NAME}"
echo ""

# Backup existing files
BACKUP_DIR="${ENV_DIR}/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "${BACKUP_DIR}"
cp "${ENV_DIR}/.env" "${BACKUP_DIR}/.env.backup"
cp "${ENV_DIR}/docker-compose.yml" "${BACKUP_DIR}/docker-compose.yml.backup"
echo "✅ Backups created in: ${BACKUP_DIR}"

# Read existing configuration
if [ -f "${ENV_DIR}/.env" ]; then
    EXISTING_USER_ID=$(grep "^USER_ID=" "${ENV_DIR}/.env" | cut -d= -f2)
    EXISTING_GROUP_ID=$(grep "^GROUP_ID=" "${ENV_DIR}/.env" | cut -d= -f2)
    EXISTING_PORT=$(grep "^OPENCODE_SERVER_PORT=" "${ENV_DIR}/.env" | cut -d= -f2)
    EXISTING_USERNAME=$(grep "^OPENCODE_SERVER_USERNAME=" "${ENV_DIR}/.env" | cut -d= -f2)
    EXISTING_PASSWORD=$(grep "^OPENCODE_SERVER_PASSWORD=" "${ENV_DIR}/.env" | cut -d= -f2)
    
    echo "📋 Existing configuration:"
    echo "   USER_ID: ${EXISTING_USER_ID}"
    echo "   GROUP_ID: ${EXISTING_GROUP_ID}"
    echo "   PORT: ${EXISTING_PORT}"
    echo "   USERNAME: ${EXISTING_USERNAME}"
    echo "   PASSWORD: [hidden]"
    echo ""
fi

# Prompt for updates
read -p "Update OpenCode server username [${EXISTING_USERNAME:-opencode}]: " SERVER_USERNAME
SERVER_USERNAME=${SERVER_USERNAME:-${EXISTING_USERNAME:-opencode}}

read -sp "Update OpenCode server password (leave empty to keep current): " SERVER_PASSWORD
echo ""
if [ -z "$SERVER_PASSWORD" ]; then
    SERVER_PASSWORD="${EXISTING_PASSWORD}"
    echo "Keeping existing password"
else
    echo "Password updated"
fi

# Create required directories
echo "Creating required directories..."
mkdir -p "${ENV_DIR}/opencode_config"
mkdir -p "shared/config"
mkdir -p "shared/models"

# Copy and customize templates
echo "Applying new template format..."
cp environments/template/docker-compose.yml.template "${ENV_DIR}/docker-compose.yml.new"
cp environments/template/.env.template "${ENV_DIR}/.env.new"

# Replace placeholders in new files
sed -i "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/docker-compose.yml.new"
sed -i "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/.env.new"

# Apply existing configuration to new files
if [ -n "$EXISTING_USER_ID" ]; then
    sed -i "s/USER_ID=.*/USER_ID=${EXISTING_USER_ID}/" "${ENV_DIR}/.env.new"
    sed -i "s/GROUP_ID=.*/GROUP_ID=${EXISTING_GROUP_ID}/" "${ENV_DIR}/.env.new"
fi

if [ -n "$EXISTING_PORT" ]; then
    sed -i "s/OPENCODE_SERVER_PORT=.*/OPENCODE_SERVER_PORT=${EXISTING_PORT}/" "${ENV_DIR}/.env.new"
fi

# Set server credentials
sed -i "s/OPENCODE_SERVER_USERNAME=.*/OPENCODE_SERVER_USERNAME=${SERVER_USERNAME}/" "${ENV_DIR}/.env.new"
if [ -n "$SERVER_PASSWORD" ]; then
    sed -i "s/OPENCODE_SERVER_PASSWORD=.*/OPENCODE_SERVER_PASSWORD=${SERVER_PASSWORD}/" "${ENV_DIR}/.env.new"
fi

# Set container name and hostname
sed -i "s/CONTAINER_NAME=.*/CONTAINER_NAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env.new"
sed -i "s/HOSTNAME=.*/HOSTNAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env.new"

# Set volume paths
sed -i "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=./workspace|" "${ENV_DIR}/.env.new"
sed -i "s|GLOBAL_CONFIG=.*|GLOBAL_CONFIG=~/.config/opencode:ro|" "${ENV_DIR}/.env.new"
sed -i "s|OPENCODE_ENV_CONFIG=.*|OPENCODE_ENV_CONFIG=./opencode_config:rw|" "${ENV_DIR}/.env.new"

# Replace old files with new ones
mv "${ENV_DIR}/docker-compose.yml.new" "${ENV_DIR}/docker-compose.yml"
mv "${ENV_DIR}/.env.new" "${ENV_DIR}/.env"

echo ""
echo "✅ Environment ${ENV_NAME} updated successfully"
echo ""
echo "📋 Updated configuration:"
echo "   Container name: opencode-${ENV_NAME}"
echo "   Hostname: opencode-${ENV_NAME}"
echo "   Server username: ${SERVER_USERNAME}"
echo "   Volume mounts:"
echo "     - ./workspace → /home/dev/workspace"
echo "     - ~/.config/opencode → /home/dev/.config/opencode (ro)"
echo "     - ./opencode_config → /home/dev/.local/share/opencode (rw)"
echo ""
echo "⚠️  Important notes:"
echo "   1. The environment now uses the new template format"
echo "   2. Shared mounts (../../shared/config, ../../shared/models) have been removed"
echo "   3. Backups are available in: ${BACKUP_DIR}"
echo "   4. You may need to rebuild the container:"
echo "      cd ${ENV_DIR} && docker compose build"
echo ""
echo "To revert changes, restore from backup:"
echo "  cp ${BACKUP_DIR}/.env.backup ${ENV_DIR}/.env"
echo "  cp ${BACKUP_DIR}/docker-compose.yml.backup ${ENV_DIR}/docker-compose.yml"