#!/bin/bash
# OpenCode Environment Manager TUI - Installer
# Automated installation with virtual environment setup

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_BASE="${HOME}/.local/share/opencode-workspace"
INSTALL_BIN="${HOME}/.local/bin"
VENV_DIR="${INSTALL_BASE}/venv"
CONFIG_FILE="${HOME}/.opencode-workspace.conf"
LOG_FILE="${INSTALL_BASE}/installation-log.txt"

# Version
VERSION="1.0.0"

# Detect workspace root (current directory by default)
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation state
EXISTING_INSTALL=false
SHELL_PROFILES_UPDATED=()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE" 2>/dev/null || true
    
    case "$level" in
        INFO)  echo -e "${BLUE}ℹ${NC} $message" ;;
        OK)    echo -e "${GREEN}✓${NC} $message" ;;
        WARN)  echo -e "${YELLOW}⚠${NC} $message" ;;
        ERROR) echo -e "${RED}✗${NC} $message" ;;
        *)     echo "$message" ;;
    esac
}

print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo "║       OpenCode Environment Manager TUI - Installer v${VERSION}       ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    
    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    while true; do
        read -p "$prompt" response
        response=${response:-$default}
        case "$response" in
            [Yy]*) return 0 ;;
            [Nn]*) return 1 ;;
            *) echo "Please answer yes or no." ;;
        esac
    done
}

cleanup_on_error() {
    log ERROR "Installation failed. Rolling back changes..."
    
    # Remove installation directory if it was created during this run
    if [ -d "$INSTALL_BASE" ] && [ "$EXISTING_INSTALL" = false ]; then
        log INFO "Removing ${INSTALL_BASE}"
        rm -rf "$INSTALL_BASE"
    fi
    
    log ERROR "Installation incomplete. Check ${LOG_FILE} for details."
    exit 1
}

trap cleanup_on_error ERR

# ============================================================================
# PREFLIGHT CHECKS
# ============================================================================

check_python() {
    print_section "Checking Python installation"
    
    if ! command -v python3 &> /dev/null; then
        log ERROR "Python 3 is not installed"
        echo ""
        echo "Please install Python 3.8 or higher:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-venv"
        echo "  macOS: brew install python3"
        return 1
    fi
    
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local major=$(echo "$python_version" | cut -d. -f1)
    local minor=$(echo "$python_version" | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        log ERROR "Python ${python_version} found, but 3.8+ required"
        return 1
    fi
    
    log OK "Python ${python_version} found"
    
    # Check for venv module
    if ! python3 -m venv --help &> /dev/null; then
        log ERROR "Python venv module not available"
        echo ""
        echo "Please install python3-venv:"
        echo "  Ubuntu/Debian: sudo apt install python3-venv"
        return 1
    fi
    
    log OK "Python venv module available"
    return 0
}

check_docker() {
    print_section "Checking Docker"
    
    if ! command -v docker &> /dev/null; then
        log WARN "Docker is not installed"
        echo ""
        echo "Docker is required to manage environments. Please install:"
        echo "  https://docs.docker.com/get-docker/"
        echo ""
        if ! ask_yes_no "Continue without Docker?"; then
            return 1
        fi
    else
        local docker_version=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
        log OK "Docker ${docker_version} found"
        
        # Test Docker access
        if docker ps &> /dev/null; then
            log OK "Docker daemon is accessible"
        else
            log WARN "Cannot access Docker daemon (may need to add user to docker group)"
            echo ""
            echo "If you see permission errors, run:"
            echo "  sudo usermod -aG docker \$USER"
            echo "  newgrp docker"
        fi
    fi
    
    return 0
}

check_workspace() {
    print_section "Detecting workspace"
    
    # Check if we're in the workspace directory
    if [ -d "$WORKSPACE_ROOT/envman" ] && [ -d "$WORKSPACE_ROOT/environments" ]; then
        log OK "Workspace root found: ${WORKSPACE_ROOT}"
    elif [ -f "$WORKSPACE_ROOT/envman.py" ]; then
        log OK "Workspace root found: ${WORKSPACE_ROOT}"
    else
        log WARN "Could not auto-detect workspace root"
        echo ""
        echo "Current directory: ${WORKSPACE_ROOT}"
        echo ""
        read -p "Enter workspace root path [${WORKSPACE_ROOT}]: " user_workspace
        WORKSPACE_ROOT="${user_workspace:-$WORKSPACE_ROOT}"
        
        if [ ! -d "$WORKSPACE_ROOT" ]; then
            log ERROR "Directory does not exist: ${WORKSPACE_ROOT}"
            return 1
        fi
    fi
    
    return 0
}

check_existing_install() {
    print_section "Checking for existing installation"
    
    if [ -d "$INSTALL_BASE" ]; then
        EXISTING_INSTALL=true
        log WARN "Existing installation found at ${INSTALL_BASE}"
        echo ""
        echo "Options:"
        echo "  1) Upgrade (preserve config)"
        echo "  2) Reinstall (clean install)"
        echo "  3) Repair (fix broken installation)"
        echo "  4) Cancel"
        echo ""
        read -p "Choose [1-4]: " choice
        
        case "$choice" in
            1) log INFO "Upgrade mode selected" ;;
            2) 
                log INFO "Reinstall mode selected"
                if ask_yes_no "Delete existing installation?"; then
                    log INFO "Removing ${INSTALL_BASE}"
                    rm -rf "$INSTALL_BASE"
                    EXISTING_INSTALL=false
                else
                    log ERROR "Installation cancelled"
                    exit 0
                fi
                ;;
            3) log INFO "Repair mode selected" ;;
            *)
                log INFO "Installation cancelled"
                exit 0
                ;;
        esac
    else
        log OK "No existing installation found"
    fi
    
    return 0
}

check_permissions() {
    print_section "Checking permissions"
    
    # Check ~/.local/ write access
    if [ ! -d "$HOME/.local" ]; then
        log INFO "Creating ${HOME}/.local"
        mkdir -p "$HOME/.local"
    fi
    
    if [ -w "$HOME/.local" ]; then
        log OK "Write access to ${HOME}/.local"
    else
        log ERROR "No write access to ${HOME}/.local"
        return 1
    fi
    
    # Check if we can create directories
    if mkdir -p "$INSTALL_BIN" 2>/dev/null; then
        log OK "Can create ${INSTALL_BIN}"
    else
        log ERROR "Cannot create ${INSTALL_BIN}"
        return 1
    fi
    
    return 0
}

# ============================================================================
# INSTALLATION FUNCTIONS
# ============================================================================

create_directories() {
    print_section "Creating installation directories"
    
    mkdir -p "$INSTALL_BASE"
    mkdir -p "$INSTALL_BIN"
    mkdir -p "${INSTALL_BASE}/backup"
    
    # Initialize log file
    touch "$LOG_FILE"
    
    log OK "Created ${INSTALL_BASE}"
    log OK "Created ${INSTALL_BIN}"
}

create_venv() {
    print_section "Creating Python virtual environment"
    
    if [ -d "$VENV_DIR" ] && [ "$EXISTING_INSTALL" = true ]; then
        log INFO "Virtual environment already exists"
        if ask_yes_no "Recreate virtual environment?"; then
            log INFO "Removing old venv"
            rm -rf "$VENV_DIR"
        else
            log INFO "Keeping existing venv"
            return 0
        fi
    fi
    
    log INFO "Creating venv at ${VENV_DIR}"
    python3 -m venv "$VENV_DIR"
    
    log OK "Virtual environment created"
    
    # Activate venv
    source "${VENV_DIR}/bin/activate"
    
    log INFO "Upgrading pip and setuptools"
    pip install --quiet --upgrade pip setuptools wheel
    
    log OK "pip upgraded"
}

install_dependencies() {
    print_section "Installing Python dependencies"
    
    source "${VENV_DIR}/bin/activate"
    
    local requirements="${WORKSPACE_ROOT}/requirements.txt"
    
    if [ ! -f "$requirements" ]; then
        log ERROR "requirements.txt not found at ${requirements}"
        return 1
    fi
    
    log INFO "Installing from ${requirements}"
    
    pip install --quiet -r "$requirements"
    
    log OK "Dependencies installed"
    
    # Verify critical packages
    log INFO "Verifying installations..."
    
    python3 -c "import textual" 2>/dev/null && log OK "textual installed" || log ERROR "textual not found"
    python3 -c "import docker" 2>/dev/null && log OK "docker-py installed" || log WARN "docker-py not found"
    python3 -c "import dotenv" 2>/dev/null && log OK "python-dotenv installed" || log ERROR "python-dotenv not found"
    python3 -c "import yaml" 2>/dev/null && log OK "pyyaml installed" || log ERROR "pyyaml not found"
}

copy_application_files() {
    print_section "Copying application files"
    
    # Copy envman package
    if [ -d "${WORKSPACE_ROOT}/envman" ]; then
        log INFO "Copying envman package"
        cp -r "${WORKSPACE_ROOT}/envman" "${INSTALL_BASE}/"
        log OK "envman package copied"
    else
        log ERROR "envman directory not found in workspace"
        return 1
    fi
    
    # Copy opencode-connect.sh
    if [ -f "${WORKSPACE_ROOT}/opencode-connect.sh" ]; then
        log INFO "Copying opencode-connect.sh"
        cp "${WORKSPACE_ROOT}/opencode-connect.sh" "${INSTALL_BASE}/"
        chmod +x "${INSTALL_BASE}/opencode-connect.sh"
        log OK "opencode-connect.sh copied"
    fi
    
    # Store workspace root reference
    echo "${WORKSPACE_ROOT}" > "${INSTALL_BASE}/workspace-root"
    
    log OK "Application files copied"
}

create_wrapper_script() {
    print_section "Creating oc-workspace-tui command"
    
    local wrapper="${INSTALL_BIN}/oc-workspace-tui"
    
    cat > "$wrapper" << 'WRAPPER_EOF'
#!/bin/bash
# OpenCode Workspace TUI - System-wide wrapper
# Auto-generated by installer

set -euo pipefail

INSTALL_BASE="${HOME}/.local/share/opencode-workspace"
VENV_DIR="${INSTALL_BASE}/venv"
CONFIG_FILE="${HOME}/.opencode-workspace.conf"

# Detect workspace root
detect_workspace() {
    # 1. Check command line argument
    if [ -n "${WORKSPACE_ROOT:-}" ]; then
        echo "$WORKSPACE_ROOT"
        return 0
    fi
    
    # 2. Check environment variable
    if [ -n "${OPENCODE_WORKSPACE:-}" ]; then
        echo "$OPENCODE_WORKSPACE"
        return 0
    fi
    
    # 3. Check config file
    if [ -f "$CONFIG_FILE" ]; then
        local root=$(grep "workspace_root" "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
        if [ -n "$root" ] && [ -d "$root" ]; then
            echo "$root"
            return 0
        fi
    fi
    
    # 4. Check workspace-root file
    if [ -f "${INSTALL_BASE}/workspace-root" ]; then
        local root=$(cat "${INSTALL_BASE}/workspace-root")
        if [ -d "$root" ]; then
            echo "$root"
            return 0
        fi
    fi
    
    # 5. Walk up directory tree
    local current="$PWD"
    while [ "$current" != "/" ]; do
        if [ -d "$current/environments" ] && [ -d "$current/envman" ]; then
            echo "$current"
            return 0
        fi
        current="$(dirname "$current")"
    done
    
    # 6. Check git root
    if git rev-parse --show-toplevel &>/dev/null; then
        echo "$(git rev-parse --show-toplevel)"
        return 0
    fi
    
    echo ""
    return 1
}

# Show error and exit
die() {
    echo "Error: $*" >&2
    exit 1
}

# Check installation
if [ ! -d "$VENV_DIR" ]; then
    die "Virtual environment not found. Please reinstall: bash install-envman-tui.sh"
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Detect workspace
WORKSPACE=$(detect_workspace)
if [ -z "$WORKSPACE" ]; then
    die "Could not detect workspace root. Use --workspace <path> or set OPENCODE_WORKSPACE env var"
fi

# Change to workspace directory
cd "$WORKSPACE" || die "Could not change to workspace: $WORKSPACE"

# Parse command
COMMAND="${1:-}"

case "$COMMAND" in
    ""|dashboard)
        # Launch TUI dashboard
        exec python3 envman.py
        ;;
    
    list)
        # Quick list environments
        exec python3 -c "
from envman.services.discovery import DiscoveryService
from pathlib import Path
svc = DiscoveryService(Path('$WORKSPACE'))
envs = svc.discover_environments()
print(f'Environments ({len(envs)}):')
for env in envs:
    print(f'  {env.status_icon} {env.name:<30} Port: {env.server_port or \"N/A\":<5} Status: {env.status}')
"
        ;;
    
    status)
        # Show quick status
        exec python3 -c "
from envman.services.discovery import DiscoveryService
from pathlib import Path
svc = DiscoveryService(Path('$WORKSPACE'))
envs = svc.discover_environments()
running = sum(1 for e in envs if e.is_running)
stopped = sum(1 for e in envs if e.is_stopped)
print(f'Total: {len(envs)} | Running: {running} | Stopped: {stopped}')
"
        ;;
    
    connect)
        # Quick connect to environment
        shift
        exec bash "${INSTALL_BASE}/opencode-connect.sh" "$@"
        ;;
    
    logs)
        # View logs for environment
        ENV_NAME="${2:-}"
        if [ -z "$ENV_NAME" ]; then
            die "Usage: oc-workspace-tui logs <environment-name>"
        fi
        cd "environments/${ENV_NAME}" || die "Environment not found: $ENV_NAME"
        exec docker compose logs -f
        ;;
    
    shell)
        # Open shell in environment
        ENV_NAME="${2:-}"
        if [ -z "$ENV_NAME" ]; then
            die "Usage: oc-workspace-tui shell <environment-name>"
        fi
        CONTAINER="opencode-${ENV_NAME}"
        exec docker exec -it "$CONTAINER" bash
        ;;
    
    create)
        # Create new environment
        ENV_NAME="${2:-}"
        exec bash scripts/create-environment.sh "$ENV_NAME"
        ;;
    
    config)
        # Show configuration
        echo "OpenCode Workspace TUI Configuration"
        echo "====================================="
        echo "Workspace Root: $WORKSPACE"
        echo "Install Base:   $INSTALL_BASE"
        echo "Config File:    $CONFIG_FILE"
        echo "Virtual Env:    $VENV_DIR"
        ;;
    
    --version|-v)
        echo "oc-workspace-tui version 1.0.0"
        echo "OpenCode Environment Manager TUI"
        ;;
    
    --workspace)
        export WORKSPACE_ROOT="${2:-}"
        shift 2
        exec "$0" "$@"
        ;;
    
    --uninstall)
        exec bash "${INSTALL_BASE}/uninstall.sh"
        ;;
    
    --help|-h)
        cat << 'HELP_EOF'
OpenCode Workspace TUI - System-wide tool

USAGE:
  oc-workspace-tui [COMMAND] [OPTIONS]

COMMANDS:
  (no args)           Launch TUI dashboard
  list                List all environments
  status              Show environment status summary
  connect <env>       Connect to environment
  logs <env>          View environment logs
  shell <env>         Open shell in environment
  create <name>       Create new environment
  config              Show configuration
  --version, -v       Show version
  --help, -h          Show this help
  --workspace <path>  Override workspace root
  --uninstall         Uninstall TUI

EXAMPLES:
  oc-workspace-tui                          # Launch TUI
  oc-workspace-tui list                     # List environments
  oc-workspace-tui connect my-env           # Connect to my-env
  oc-workspace-tui logs my-env              # View logs
  oc-workspace-tui --workspace ~/my-ws list # Use different workspace

ENVIRONMENT VARIABLES:
  OPENCODE_WORKSPACE  Override workspace root detection
HELP_EOF
        ;;
    
    *)
        echo "Unknown command: $COMMAND"
        echo "Run 'oc-workspace-tui --help' for usage"
        exit 1
        ;;
esac
WRAPPER_EOF
    
    chmod +x "$wrapper"
    log OK "Created ${wrapper}"
}

update_shell_profiles() {
    print_section "Updating shell profiles"
    
    local path_export="export PATH=\"\$HOME/.local/bin:\$PATH\""
    
    # Detect current shell
    local current_shell=$(basename "$SHELL")
    log INFO "Detected shell: ${current_shell}"
    
    # Check if PATH already includes ~/.local/bin
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        log OK "PATH already includes ~/.local/bin"
        return 0
    fi
    
    # List of profile files to update
    local profiles=()
    
    case "$current_shell" in
        bash)
            [ -f "$HOME/.bashrc" ] && profiles+=("$HOME/.bashrc")
            [ -f "$HOME/.bash_profile" ] && profiles+=("$HOME/.bash_profile")
            ;;
        zsh)
            [ -f "$HOME/.zshrc" ] && profiles+=("$HOME/.zshrc")
            ;;
        fish)
            local fish_config="$HOME/.config/fish/config.fish"
            if [ -f "$fish_config" ]; then
                profiles+=("$fish_config")
                path_export="set -gx PATH \$HOME/.local/bin \$PATH"
            fi
            ;;
        *)
            [ -f "$HOME/.profile" ] && profiles+=("$HOME/.profile")
            ;;
    esac
    
    if [ ${#profiles[@]} -eq 0 ]; then
        log WARN "No shell profile found, creating ~/.profile"
        profiles=("$HOME/.profile")
        touch "$HOME/.profile"
    fi
    
    echo ""
    echo "Will update the following files to add ~/.local/bin to PATH:"
    for profile in "${profiles[@]}"; do
        echo "  - $profile"
    done
    echo ""
    
    if ! ask_yes_no "Proceed with updating shell profiles?"; then
        log WARN "Skipping shell profile updates"
        echo ""
        echo "To use oc-workspace-tui from anywhere, manually add to your shell profile:"
        echo "  ${path_export}"
        return 0
    fi
    
    # Backup and update each profile
    for profile in "${profiles[@]}"; do
        # Create backup
        local backup="${INSTALL_BASE}/backup/$(basename "$profile").backup"
        cp "$profile" "$backup"
        log INFO "Backed up $profile to $backup"
        
        # Check if already has the export
        if grep -q "PATH.*\.local/bin" "$profile" 2>/dev/null; then
            log INFO "$(basename "$profile") already has ~/.local/bin in PATH"
            continue
        fi
        
        # Add export
        echo "" >> "$profile"
        echo "# Added by OpenCode Workspace TUI installer" >> "$profile"
        echo "$path_export" >> "$profile"
        
        log OK "Updated $profile"
        SHELL_PROFILES_UPDATED+=("$profile")
    done
    
    if [ ${#SHELL_PROFILES_UPDATED[@]} -gt 0 ]; then
        log OK "Shell profiles updated"
    fi
}

create_config_file() {
    print_section "Creating configuration file"
    
    cat > "$CONFIG_FILE" << CONFIG_EOF
{
  "workspace_root": "${WORKSPACE_ROOT}",
  "version": "${VERSION}",
  "installed_at": "$(date -Iseconds)",
  "venv_path": "${VENV_DIR}",
  "install_base": "${INSTALL_BASE}"
}
CONFIG_EOF
    
    log OK "Created ${CONFIG_FILE}"
}

create_uninstall_script() {
    print_section "Creating uninstall script"
    
    local uninstall="${INSTALL_BASE}/uninstall.sh"
    
    cat > "$uninstall" << 'UNINSTALL_EOF'
#!/bin/bash
# OpenCode Workspace TUI - Uninstaller
# Auto-generated by installer

set -euo pipefail

INSTALL_BASE="${HOME}/.local/share/opencode-workspace"
INSTALL_BIN="${HOME}/.local/bin"
CONFIG_FILE="${HOME}/.opencode-workspace.conf"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║       OpenCode Workspace TUI - Uninstaller                           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

echo "This will remove:"
echo "  - ${INSTALL_BASE}/"
echo "  - ${INSTALL_BIN}/oc-workspace-tui"
echo "  - ${CONFIG_FILE}"
echo ""
echo "Shell profile modifications will NOT be automatically reverted."
echo "Backups are in ${INSTALL_BASE}/backup/"
echo ""

read -p "Proceed with uninstall? [y/N]: " response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Uninstalling..."

# Remove command
if [ -f "${INSTALL_BIN}/oc-workspace-tui" ]; then
    rm "${INSTALL_BIN}/oc-workspace-tui"
    echo "✓ Removed oc-workspace-tui command"
fi

# Remove config
if [ -f "$CONFIG_FILE" ]; then
    rm "$CONFIG_FILE"
    echo "✓ Removed config file"
fi

# Remove installation directory
if [ -d "$INSTALL_BASE" ]; then
    rm -rf "$INSTALL_BASE"
    echo "✓ Removed installation directory"
fi

echo ""
echo "✓ Uninstall complete!"
echo ""
echo "To remove PATH modifications, manually edit your shell profile:"
echo "  ~/.bashrc, ~/.zshrc, or ~/.profile"
echo ""
UNINSTALL_EOF
    
    chmod +x "$uninstall"
    log OK "Created ${uninstall}"
}

verify_installation() {
    print_section "Verifying installation"
    
    # Test venv activation
    if source "${VENV_DIR}/bin/activate" 2>/dev/null; then
        log OK "Virtual environment activates successfully"
    else
        log ERROR "Failed to activate virtual environment"
        return 1
    fi
    
    # Test Python imports
    if python3 -c "from envman.services.discovery import DiscoveryService" 2>/dev/null; then
        log OK "TUI imports work correctly"
    else
        log ERROR "TUI imports failed"
        return 1
    fi
    
    # Test wrapper script
    if [ -x "${INSTALL_BIN}/oc-workspace-tui" ]; then
        log OK "oc-workspace-tui is executable"
    else
        log ERROR "oc-workspace-tui is not executable"
        return 1
    fi
    
    # Test workspace detection
    if cd /tmp && "${INSTALL_BIN}/oc-workspace-tui" config &>/dev/null; then
        log OK "Workspace detection works from /tmp"
    else
        log WARN "Workspace detection may need configuration"
    fi
    
    log OK "Installation verified"
}

# ============================================================================
# POST-INSTALLATION
# ============================================================================

print_post_install() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo "║                   ✓ Installation Complete!                          ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Installation Details:"
    echo "  • Workspace:   ${WORKSPACE_ROOT}"
    echo "  • Install Dir: ${INSTALL_BASE}"
    echo "  • Command:     ${INSTALL_BIN}/oc-workspace-tui"
    echo "  • Config:      ${CONFIG_FILE}"
    echo "  • Log:         ${LOG_FILE}"
    echo ""
    
    if [ ${#SHELL_PROFILES_UPDATED[@]} -gt 0 ]; then
        echo "Shell Profiles Updated:"
        for profile in "${SHELL_PROFILES_UPDATED[@]}"; do
            echo "  • $profile"
        done
        echo ""
        echo "⚠️  Reload your shell to use the new command:"
        echo "    source ~/.bashrc   # or ~/.zshrc"
        echo ""
        echo "Or start a new terminal session."
        echo ""
    fi
    
    echo "Quick Start:"
    echo "  oc-workspace-tui              # Launch TUI"
    echo "  oc-workspace-tui list         # List environments"
    echo "  oc-workspace-tui --help       # Show help"
    echo ""
    echo "Uninstall:"
    echo "  oc-workspace-tui --uninstall"
    echo ""
    
    if ask_yes_no "Launch TUI now?"; then
        echo ""
        source "${VENV_DIR}/bin/activate"
        cd "$WORKSPACE_ROOT"
        exec python3 envman.py
    fi
}

# ============================================================================
# MAIN INSTALLATION FLOW
# ============================================================================

main() {
    print_header
    
    # Run preflight checks
    check_python || exit 1
    check_docker || exit 1
    check_workspace || exit 1
    check_existing_install || exit 1
    check_permissions || exit 1
    
    # Show installation plan
    print_section "Installation Plan"
    echo "Workspace Root:    ${WORKSPACE_ROOT}"
    echo "Install Location:  ${INSTALL_BASE}"
    echo "Command Location:  ${INSTALL_BIN}/oc-workspace-tui"
    echo "Disk Space:        ~200MB (for venv + dependencies)"
    echo ""
    
    if ! ask_yes_no "Proceed with installation?"; then
        log INFO "Installation cancelled by user"
        exit 0
    fi
    
    # Perform installation
    create_directories
    create_venv
    install_dependencies
    copy_application_files
    create_wrapper_script
    update_shell_profiles
    create_config_file
    create_uninstall_script
    verify_installation
    
    # Show post-install message
    print_post_install
}

# Run main installation
main "$@"
