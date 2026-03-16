#!/bin/bash
# Setup shared Docker network for OpenCode environments

NETWORK_NAME="opencode-network"

echo "Setting up OpenCode network: ${NETWORK_NAME}"

# Check if network exists
if docker network inspect ${NETWORK_NAME} > /dev/null 2>&1; then
    echo "Network ${NETWORK_NAME} already exists"
else
    echo "Creating network ${NETWORK_NAME}..."
    docker network create ${NETWORK_NAME}
    echo "Network ${NETWORK_NAME} created"
fi

echo "Network setup complete"