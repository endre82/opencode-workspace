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
echo "=========================================="
echo "  OpenCode Environment Setup"
echo "=========================================="
echo ""

# Get host user IDs for defaults
HOST_UID=$(id -u)
HOST_GID=$(id -g)

# === STEP 1: USER CONFIGURATION ===
echo "📋 Step 1: User Configuration"
echo ""

# Prompt for USER_ID
read -p "Enter USER_ID (default: ${HOST_UID}): " USER_ID
USER_ID=${USER_ID:-$HOST_UID}

# Prompt for GROUP_ID
read -p "Enter GROUP_ID (default: ${HOST_GID}): " GROUP_ID
GROUP_ID=${GROUP_ID:-$HOST_GID}

echo ""

# === STEP 2: WORKSPACE CONFIGURATION ===
echo "📁 Step 2: Workspace Configuration"
echo ""
echo "Choose workspace type:"
echo "  i) Isolated - Uses ./workspace directory (default, recommended)"
echo "  e) External - Custom path outside environment directory"
echo ""
read -p "Workspace type (i/e) [default: i]: " WORKSPACE_TYPE
WORKSPACE_TYPE=${WORKSPACE_TYPE:-i}

if [ "$WORKSPACE_TYPE" = "e" ]; then
    read -p "Enter external workspace path (e.g., ~/my-env-name): " WORKSPACE_DIR
    if [ -z "$WORKSPACE_DIR" ]; then
        echo "⚠️  No path provided, using default ./workspace"
        WORKSPACE_DIR="./workspace"
    fi
else
    WORKSPACE_DIR="./workspace"
fi

echo "   Selected: ${WORKSPACE_DIR}"
echo ""

# === STEP 3: VOLUME MOUNT CONFIGURATION ===
echo "🔗 Step 3: Volume Mount Configuration"
echo ""
echo "Configure which volumes to mount (you can change this later):"
echo ""

# Prompt for GLOBAL_CONFIG mounting
read -p "Mount GLOBAL_CONFIG (shared OpenCode config)? (y/n) [default: n]: " MOUNT_GLOBAL
MOUNT_GLOBAL=${MOUNT_GLOBAL:-n}
if [ "$MOUNT_GLOBAL" = "y" ] || [ "$MOUNT_GLOBAL" = "Y" ]; then
    MOUNT_GLOBAL_CONFIG="true"
    read -p "Enter GLOBAL_CONFIG path (default: ../shared/config/.opencode): " GLOBAL_CONFIG
    GLOBAL_CONFIG=${GLOBAL_CONFIG:-../shared/config/.opencode}
else
    MOUNT_GLOBAL_CONFIG="false"
    GLOBAL_CONFIG="../shared/config/.opencode"
fi

# Prompt for PROJECT_CONFIG mounting
read -p "Mount PROJECT_CONFIG (project-specific config)? (y/n) [default: n]: " MOUNT_PROJECT
MOUNT_PROJECT=${MOUNT_PROJECT:-n}
if [ "$MOUNT_PROJECT" = "y" ] || [ "$MOUNT_PROJECT" = "Y" ]; then
    MOUNT_PROJECT_CONFIG="true"
    read -p "Enter PROJECT_CONFIG path (default: ./opencode_project_config): " PROJECT_CONFIG
    PROJECT_CONFIG=${PROJECT_CONFIG:-./opencode_project_config}
else
    MOUNT_PROJECT_CONFIG="false"
    PROJECT_CONFIG="./opencode_project_config"
fi

# OPENCODE_ENV_CONFIG always mounted
MOUNT_OPENCODE_ENV_CONFIG="true"
read -p "Enter OPENCODE_ENV_CONFIG path (default: ./opencode_config): " OPENCODE_ENV_CONFIG
OPENCODE_ENV_CONFIG=${OPENCODE_ENV_CONFIG:-./opencode_config}

# Prompt for SHARED_AUTH mounting
read -p "Mount SHARED_AUTH (shared provider credentials)? (y/n) [default: y]: " MOUNT_SHARED
MOUNT_SHARED=${MOUNT_SHARED:-y}
if [ "$MOUNT_SHARED" = "y" ] || [ "$MOUNT_SHARED" = "Y" ]; then
    MOUNT_SHARED_AUTH="true"
else
    MOUNT_SHARED_AUTH="false"
fi
SHARED_AUTH_CONFIG="../../shared/auth/auth.json"

echo ""

# === STEP 4: SERVER CONFIGURATION ===
echo "🖥️  Step 4: Server Configuration"
echo ""

# Prompt for username
read -p "Enter OpenCode server username [default: opencode]: " SERVER_USERNAME
SERVER_USERNAME=${SERVER_USERNAME:-opencode}

# Prompt for password
read -sp "Enter OpenCode server password (leave empty to generate random): " SERVER_PASSWORD
echo ""
if [ -z "$SERVER_PASSWORD" ]; then
    SERVER_PASSWORD=$(openssl rand -base64 12)
    echo "   Generated random password: ${SERVER_PASSWORD}"
fi

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

# Calculate code-server port (OpenCode port + 4000)
CODE_SERVER_PORT=$((SERVER_PORT + 4000))

# Calculate Web UI port (OpenCode port + 5000)
WEBUI_PORT=$((SERVER_PORT + 5000))

# Create directory structure
echo "Creating directory structure..."
mkdir -p "${ENV_DIR}/workspace"
mkdir -p "${ENV_DIR}/opencode_config"
mkdir -p "shared/config"
mkdir -p "shared/models"

# Copy and customize templates
cp environments/template/docker-compose.yml.template "${ENV_DIR}/docker-compose.yml"
cp environments/template/.env.template "${ENV_DIR}/.env"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed syntax
    SED_INPLACE="sed -i ''"
else
    # Linux sed syntax
    SED_INPLACE="sed -i"
fi

# Replace placeholders
$SED_INPLACE "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/docker-compose.yml"
$SED_INPLACE "s/{{ENV_NAME}}/${ENV_NAME}/g" "${ENV_DIR}/.env"

# Update .env file with user-provided values
$SED_INPLACE "s/USER_ID=.*/USER_ID=${USER_ID}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/GROUP_ID=.*/GROUP_ID=${GROUP_ID}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/CONTAINER_NAME=.*/CONTAINER_NAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/HOSTNAME=.*/HOSTNAME=opencode-${ENV_NAME}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/OPENCODE_SERVER_PORT=.*/OPENCODE_SERVER_PORT=${SERVER_PORT}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/OPENCODE_SERVER_USERNAME=.*/OPENCODE_SERVER_USERNAME=${SERVER_USERNAME}/" "${ENV_DIR}/.env"
$SED_INPLACE "s|OPENCODE_SERVER_PASSWORD=.*|OPENCODE_SERVER_PASSWORD=${SERVER_PASSWORD}|" "${ENV_DIR}/.env"
$SED_INPLACE "s/CODE_SERVER_PORT=.*/CODE_SERVER_PORT=${CODE_SERVER_PORT}/" "${ENV_DIR}/.env"
$SED_INPLACE "s|CODE_SERVER_PASSWORD=.*|CODE_SERVER_PASSWORD=${SERVER_PASSWORD}|" "${ENV_DIR}/.env"
$SED_INPLACE "s/WEBUI_PORT=.*/WEBUI_PORT=${WEBUI_PORT}/" "${ENV_DIR}/.env"
$SED_INPLACE "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=${WORKSPACE_DIR}|" "${ENV_DIR}/.env"
$SED_INPLACE "s|GLOBAL_CONFIG=.*|GLOBAL_CONFIG=${GLOBAL_CONFIG}|" "${ENV_DIR}/.env"
$SED_INPLACE "s|PROJECT_CONFIG=.*|PROJECT_CONFIG=${PROJECT_CONFIG}|" "${ENV_DIR}/.env"
$SED_INPLACE "s|OPENCODE_ENV_CONFIG=.*|OPENCODE_ENV_CONFIG=${OPENCODE_ENV_CONFIG}|" "${ENV_DIR}/.env"
$SED_INPLACE "s/MOUNT_GLOBAL_CONFIG=.*/MOUNT_GLOBAL_CONFIG=${MOUNT_GLOBAL_CONFIG}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/MOUNT_PROJECT_CONFIG=.*/MOUNT_PROJECT_CONFIG=${MOUNT_PROJECT_CONFIG}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/MOUNT_OPENCODE_ENV_CONFIG=.*/MOUNT_OPENCODE_ENV_CONFIG=${MOUNT_OPENCODE_ENV_CONFIG}/" "${ENV_DIR}/.env"
$SED_INPLACE "s/MOUNT_SHARED_AUTH=.*/MOUNT_SHARED_AUTH=${MOUNT_SHARED_AUTH}/" "${ENV_DIR}/.env"

# Uncomment volumes in docker-compose.yml based on user selection
if [ "$MOUNT_GLOBAL_CONFIG" = "true" ]; then
    $SED_INPLACE 's|# - \${GLOBAL_CONFIG}:|      - ${GLOBAL_CONFIG}:|' "${ENV_DIR}/docker-compose.yml"
fi

if [ "$MOUNT_PROJECT_CONFIG" = "true" ]; then
    $SED_INPLACE 's|# - \${PROJECT_CONFIG}:|      - ${PROJECT_CONFIG}:|' "${ENV_DIR}/docker-compose.yml"
fi

if [ "$MOUNT_SHARED_AUTH" = "true" ]; then
    $SED_INPLACE 's|# - \${SHARED_AUTH_CONFIG}:|      - ${SHARED_AUTH_CONFIG}:|' "${ENV_DIR}/docker-compose.yml"
fi

echo ""
echo "=========================================="
echo "✅ Environment ${ENV_NAME} created successfully"
echo "=========================================="
echo ""
echo "📋 Configuration Summary:"
echo ""
echo "👤 User Configuration:"
echo "   USER_ID: ${USER_ID}"
echo "   GROUP_ID: ${GROUP_ID}"
echo ""
echo "📁 Workspace:"
echo "   Type: $([ \"$WORKSPACE_TYPE\" = \"e\" ] && echo \"External\" || echo \"Isolated\")"
echo "   Path: ${WORKSPACE_DIR}"
echo ""
echo "🔗 Volume Mounts:"
if [ "$MOUNT_GLOBAL_CONFIG" = "true" ]; then
    echo "   ✅ GLOBAL_CONFIG → /home/dev/.config/opencode"
    echo "      Path: ${GLOBAL_CONFIG}"
else
    echo "   ❌ GLOBAL_CONFIG (disabled)"
fi
if [ "$MOUNT_PROJECT_CONFIG" = "true" ]; then
    echo "   ✅ PROJECT_CONFIG → /home/dev/workspace/.opencode"
    echo "      Path: ${PROJECT_CONFIG}"
else
    echo "   ❌ PROJECT_CONFIG (disabled)"
fi
echo "   ✅ OPENCODE_ENV_CONFIG → /home/dev/.local/share/opencode"
echo "      Path: ${OPENCODE_ENV_CONFIG}"
if [ "$MOUNT_SHARED_AUTH" = "true" ]; then
    echo "   ✅ SHARED_AUTH → /home/dev/.local/share/opencode/auth.json"
    echo "      Path: ${SHARED_AUTH_CONFIG}"
else
    echo "   ❌ SHARED_AUTH (disabled)"
fi
echo ""
echo "🖥️  Server Configuration:"
echo "   OpenCode Server Port: ${SERVER_PORT}"
echo "   code-server Port: ${CODE_SERVER_PORT}"
echo "   Web UI Port: ${WEBUI_PORT}"
echo "   Username: ${SERVER_USERNAME}"
echo "   Password: ${SERVER_PASSWORD}"
echo ""
echo "📂 Directories created:"
echo "   ${ENV_DIR}/workspace"
echo "   ${ENV_DIR}/opencode_config"
echo "   ../../shared/config"
echo "   ../../shared/models"
echo ""
echo "💡 Tips:"
echo "   • Edit ${ENV_DIR}/.env to change MOUNT_* variables"
echo "   • Uncomment volumes in ${ENV_DIR}/docker-compose.yml to enable them"
echo "   • Use 'vienna-agentic-vibes' as reference for external workspace setup"
echo ""
echo "Next steps:"
echo "1. Review ${ENV_DIR}/.env for any customizations"
echo "2. Run: cd ${ENV_DIR} && docker compose build"
echo "3. Run: cd ${ENV_DIR} && docker compose up -d"
echo ""
echo "Access your environment:"
echo "  VSCode in Browser: http://localhost:${CODE_SERVER_PORT}"
echo "  Web Management UI: http://localhost:${WEBUI_PORT}"
echo "  OpenCode CLI: OPENCODE_SERVER_USERNAME=${SERVER_USERNAME} OPENCODE_SERVER_PASSWORD=${SERVER_PASSWORD} opencode attach http://localhost:${SERVER_PORT}"