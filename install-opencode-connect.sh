#!/bin/bash
# OpenCode Remote Connection Helper - Installer Script
# For deployment to GitHub and easy installation

set -euo pipefail

INSTALL_DIR="${HOME}/.local/bin"
SCRIPT_NAME="opencode-connect"
GITHUB_RAW_URL="https://raw.githubusercontent.com/YOUR_ORG/opencode-workspace/main/opencode-connect.sh"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║    OpenCode Remote Connection Helper - Installer              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if curl or wget is available
if command -v curl &> /dev/null; then
    DOWNLOADER="curl -fsSL"
elif command -v wget &> /dev/null; then
    DOWNLOADER="wget -qO-"
else
    echo -e "${RED}Error: Neither curl nor wget found. Please install one of them.${NC}"
    exit 1
fi

# Create install directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}Creating installation directory: ${INSTALL_DIR}${NC}"
    mkdir -p "$INSTALL_DIR"
fi

# Download the script
echo -e "${BLUE}Downloading opencode-connect script...${NC}"
if ! $DOWNLOADER "$GITHUB_RAW_URL" > "${INSTALL_DIR}/${SCRIPT_NAME}"; then
    echo -e "${RED}Error: Failed to download script from ${GITHUB_RAW_URL}${NC}"
    echo -e "${YELLOW}Note: Update GITHUB_RAW_URL in this installer with your repository URL${NC}"
    exit 1
fi

# Make executable
chmod +x "${INSTALL_DIR}/${SCRIPT_NAME}"

echo -e "${GREEN}✅ Installation successful!${NC}"
echo ""
echo "Script installed to: ${INSTALL_DIR}/${SCRIPT_NAME}"
echo ""

# Check if install directory is in PATH
if [[ ":$PATH:" == *":${INSTALL_DIR}:"* ]]; then
    echo -e "${GREEN}✅ ${INSTALL_DIR} is already in your PATH${NC}"
    echo ""
    echo "Usage:"
    echo -e "  ${BLUE}${SCRIPT_NAME} --list${NC}              # List all environments"
    echo -e "  ${BLUE}${SCRIPT_NAME} <env-name>${NC}         # Connect to environment"
    echo -e "  ${BLUE}${SCRIPT_NAME} --help${NC}             # Show help"
else
    echo -e "${YELLOW}⚠️  ${INSTALL_DIR} is not in your PATH${NC}"
    echo ""
    echo "Add the following line to your shell configuration file:"
    echo "  (~/.bashrc, ~/.zshrc, or ~/.profile)"
    echo ""
    echo -e "  ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then reload your shell:"
    echo -e "  ${BLUE}source ~/.bashrc${NC}  # or ~/.zshrc"
    echo ""
    echo "Or run directly:"
    echo -e "  ${BLUE}${INSTALL_DIR}/${SCRIPT_NAME} --help${NC}"
fi

echo ""
echo -e "${GREEN}Happy connecting!${NC} 🚀"
echo ""
