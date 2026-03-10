#!/bin/bash
# Build and test the OpenCode environment setup

echo "=== OpenCode Environment Setup Test ==="
echo ""

# Get current user's UID and GID
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)
CURRENT_USER=$(whoami)

# Export as environment variables for Docker Compose
export USER_ID=${CURRENT_UID}
export GROUP_ID=${CURRENT_GID}

# Warn if UID/GID are system IDs (typically < 1000)
if [ ${CURRENT_UID} -lt 1000 ] || [ ${CURRENT_GID} -lt 1000 ]; then
    echo "⚠️  Warning: UID/GID are system IDs (< 1000). This may cause issues with user creation."
    echo "   The container will rename the existing system user to 'dev'."
    echo ""
fi

echo "Current user: ${CURRENT_USER}"
echo "Current UID: ${CURRENT_UID}"
echo "Current GID: ${CURRENT_GID}"
echo ""

# Step 1: Setup network
echo "1. Setting up Docker network..."
./setup-network.sh

# Step 2: Build base image
echo ""
echo "2. Building base image with UID=${CURRENT_UID}, GID=${CURRENT_GID}..."
cd base
docker build \
  --build-arg USER_ID=${CURRENT_UID} \
  --build-arg GROUP_ID=${CURRENT_GID} \
  -t opencode-base:latest .

if [ $? -ne 0 ]; then
    echo "❌ Base image build failed"
    exit 1
fi
echo "✅ Base image built successfully"
cd ..

# Step 3: Build dev1 environment
echo ""
echo "3. Building dev1 environment..."
cd environments/dev1
docker compose build

if [ $? -ne 0 ]; then
    echo "❌ dev1 environment build failed"
    exit 1
fi
echo "✅ dev1 environment built successfully"

# Step 4: Test dev1 environment
echo ""
echo "4. Testing dev1 environment..."
docker compose up -d
sleep 10

# Verify user configuration
echo ""
echo "5. Verifying user configuration..."
CONTAINER_USER_ID=$(docker compose exec opencode-dev1 id -u)
CONTAINER_GROUP_ID=$(docker compose exec opencode-dev1 id -g)
CONTAINER_USERNAME=$(docker compose exec opencode-dev1 whoami)
CONTAINER_HOME=$(docker compose exec opencode-dev1 bash -c 'echo $HOME')

echo "Container username: ${CONTAINER_USERNAME}"
echo "Container home directory: ${CONTAINER_HOME}"
echo "Container User ID: ${CONTAINER_USER_ID}"
echo "Container Group ID: ${CONTAINER_GROUP_ID}"

if [ "${CONTAINER_USER_ID}" = "${CURRENT_UID}" ] && [ "${CONTAINER_GROUP_ID}" = "${CURRENT_GID}" ]; then
    echo "✅ User/Group correctly set to ${CURRENT_USER} (UID=${CURRENT_UID}, GID=${CURRENT_GID})"
else
    echo "❌ User/Group mismatch: expected ${CURRENT_USER} (UID=${CURRENT_UID}, GID=${CURRENT_GID}), got ${CONTAINER_USERNAME} (UID=${CONTAINER_USER_ID}, GID=${CONTAINER_GROUP_ID})"
fi

# Verify Node.js installation
echo ""
echo "6. Verifying Node.js installation..."
docker compose exec opencode-dev1 node --version
docker compose exec opencode-dev1 npm --version

# Verify OpenCode installation
echo ""
echo "7. Verifying OpenCode installation..."
if docker compose exec opencode-dev1 bash -c "source ~/.bashrc && opencode --version" > /dev/null 2>&1; then
    echo "✅ OpenCode installed successfully"
    docker compose exec opencode-dev1 bash -c "source ~/.bashrc && opencode --version"
else
    echo "❌ OpenCode installation failed"
    echo "Debugging info:"
    # Check if binary exists in correct location
    docker compose exec opencode-dev1 ls -la /home/dev/.opencode/bin/ 2>/dev/null || echo "No .opencode/bin directory"
    docker compose exec opencode-dev1 bash -c "which opencode || echo 'opencode not in PATH'; echo 'PATH:'; echo \$PATH"
fi

# Step 5: Cleanup
echo ""
echo "8. Cleaning up..."
docker compose down -v
cd ../..

echo ""
echo "=== Test Complete ==="
echo "The setup is working correctly with ${CURRENT_USER} (UID=${CURRENT_UID}, GID=${CURRENT_GID})!"