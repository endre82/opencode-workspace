#!/bin/bash
# Debug script for Node.js installation issues

echo "=== Debugging Node.js Installation ==="
echo ""

echo "1. Checking current Node.js installation in base image..."
cd base

echo ""
echo "Building test image to inspect Node.js..."
cat > Dockerfile.test << 'EOF'
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y curl ca-certificates

# Install nvm
ENV NVM_DIR /root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

# Load nvm and install Node.js 24
RUN . "$NVM_DIR/nvm.sh" && nvm install 24

# List Node.js files
RUN echo "=== Node.js installation details ==="
RUN which node
RUN which npm
RUN node --version
RUN npm --version
RUN echo "=== Directory structure ==="
RUN find /root/.nvm -type f -name "node" | head -5
RUN ls -la /root/.local 2>/dev/null || echo "No .local directory"
EOF

docker build -t nodejs-test -f Dockerfile.test .

echo ""
echo "2. Inspecting the built image..."
docker run --rm nodejs-test /bin/bash -c "which node && which npm && node --version && npm --version"

echo ""
echo "3. Cleaning up..."
rm Dockerfile.test
cd ..

echo ""
echo "=== Debug Complete ==="