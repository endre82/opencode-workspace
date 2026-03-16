#!/bin/bash
# OpenCode Remote Connection Helper
# Interactive tool for connecting to OpenCode environments

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# When running from installation, read workspace root from file
if [ -f "${SCRIPT_DIR}/workspace-root" ]; then
    WORKSPACE_ROOT=$(cat "${SCRIPT_DIR}/workspace-root")
else
    # When running from source, assume script is in workspace root
    WORKSPACE_ROOT="${SCRIPT_DIR}"
fi

ENVIRONMENTS_DIR="${WORKSPACE_ROOT}/environments"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display header
show_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║          OpenCode Environment Connection Helper              ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Function to parse .env file
parse_env() {
    local env_file="$1"
    local key="$2"
    
    if [ ! -f "$env_file" ]; then
        echo ""
        return
    fi
    
    grep "^${key}=" "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'"
}

# Function to check if container is running
is_container_running() {
    local container_name="$1"
    docker ps --filter "name=${container_name}" --format "{{.Names}}" 2>/dev/null | grep -q "^${container_name}$"
}

# Function to get container status
get_container_status() {
    local container_name="$1"
    
    if is_container_running "$container_name"; then
        echo "🟢 Running"
    elif docker ps -a --filter "name=${container_name}" --format "{{.Names}}" 2>/dev/null | grep -q "^${container_name}$"; then
        echo "🔴 Stopped"
    else
        echo "⚪ Not Created"
    fi
}

# Function to discover environments
discover_environments() {
    local show_all="$1"
    local environments=()
    
    for env_dir in "${ENVIRONMENTS_DIR}"/*; do
        if [ ! -d "$env_dir" ]; then
            continue
        fi
        
        local env_name=$(basename "$env_dir")
        
        # Skip template and shared directories
        if [ "$env_name" = "template" ] || [ "$env_name" = "shared" ]; then
            continue
        fi
        
        local env_file="${env_dir}/.env"
        if [ ! -f "$env_file" ]; then
            continue
        fi
        
        # Parse configuration
        local container_name=$(parse_env "$env_file" "CONTAINER_NAME")
        if [ -z "$container_name" ]; then
            container_name="opencode-${env_name}"
        fi
        
        local server_enabled=$(parse_env "$env_file" "OPENCODE_SERVER_ENABLED")
        if [ "$server_enabled" != "true" ]; then
            continue
        fi
        
        local status=$(get_container_status "$container_name")
        
        # If not showing all, skip non-running environments
        if [ "$show_all" = "false" ] && [ "$status" != "🟢 Running" ]; then
            continue
        fi
        
        local port=$(parse_env "$env_file" "OPENCODE_SERVER_PORT")
        local username=$(parse_env "$env_file" "OPENCODE_SERVER_USERNAME")
        local password=$(parse_env "$env_file" "OPENCODE_SERVER_PASSWORD")
        local host=$(parse_env "$env_file" "OPENCODE_SERVER_HOST")
        
        # Default host to localhost for connection
        if [ -z "$host" ] || [ "$host" = "0.0.0.0" ]; then
            host="localhost"
        fi
        
        environments+=("${env_name}|${status}|${port}|${username}|${password}|${host}")
    done
    
    # Only print if we have environments
    if [ ${#environments[@]} -gt 0 ]; then
        printf '%s\n' "${environments[@]}"
    fi
}

# Function to display environment list
display_environments() {
    local show_all="$1"
    local environments
    
    mapfile -t environments < <(discover_environments "$show_all")
    
    if [ ${#environments[@]} -eq 0 ]; then
        if [ "$show_all" = "true" ]; then
            echo -e "${YELLOW}No environments found.${NC}"
        else
            echo -e "${YELLOW}No running environments found.${NC}"
            echo -e "Use ${BLUE}--list${NC} to see all environments."
        fi
        return 1
    fi
    
    echo "Available environments:"
    echo ""
    
    local idx=1
    for env in "${environments[@]}"; do
        IFS='|' read -r name status port username password host <<< "$env"
        printf "  %d) %-30s %s   Port: %-5s   User: %s\n" "$idx" "$name" "$status" "$port" "$username"
        ((idx++))
    done
    
    echo ""
    
    return 0
}

# Function to build connection command
build_connection_command() {
    local username="$1"
    local password="$2"
    local host="$3"
    local port="$4"
    
    echo "OPENCODE_SERVER_USERNAME=${username} OPENCODE_SERVER_PASSWORD=${password} opencode attach http://${host}:${port}"
}

# Function to connect to environment
connect_to_environment() {
    local env_name="$1"
    local dry_run="$2"
    
    local env_file="${ENVIRONMENTS_DIR}/${env_name}/.env"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}Error: Environment '${env_name}' not found.${NC}"
        return 1
    fi
    
    # Parse configuration
    local container_name=$(parse_env "$env_file" "CONTAINER_NAME")
    if [ -z "$container_name" ]; then
        container_name="opencode-${env_name}"
    fi
    
    local server_enabled=$(parse_env "$env_file" "OPENCODE_SERVER_ENABLED")
    if [ "$server_enabled" != "true" ]; then
        echo -e "${RED}Error: OpenCode server is not enabled for environment '${env_name}'.${NC}"
        echo -e "Set OPENCODE_SERVER_ENABLED=true in ${env_file}"
        return 1
    fi
    
    local status=$(get_container_status "$container_name")
    if [ "$status" != "🟢 Running" ]; then
        echo -e "${YELLOW}Warning: Environment '${env_name}' is not running.${NC}"
        echo -e "Start it first with: ${BLUE}cd environments/${env_name} && docker compose up -d${NC}"
        return 1
    fi
    
    local port=$(parse_env "$env_file" "OPENCODE_SERVER_PORT")
    local username=$(parse_env "$env_file" "OPENCODE_SERVER_USERNAME")
    local password=$(parse_env "$env_file" "OPENCODE_SERVER_PASSWORD")
    local host=$(parse_env "$env_file" "OPENCODE_SERVER_HOST")
    
    # Default host to localhost for connection
    if [ -z "$host" ] || [ "$host" = "0.0.0.0" ]; then
        host="localhost"
    fi
    
    # Validate required fields
    if [ -z "$port" ] || [ -z "$username" ]; then
        echo -e "${RED}Error: Missing required configuration (port or username) in ${env_file}${NC}"
        return 1
    fi
    
    # Build connection command
    local cmd=$(build_connection_command "$username" "$password" "$host" "$port")
    
    echo ""
    echo -e "${GREEN}Connecting to: ${env_name}${NC}"
    echo ""
    echo "Connection command:"
    echo -e "  ${BLUE}${cmd}${NC}"
    echo ""
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}(Dry-run mode: command not executed)${NC}"
        return 0
    fi
    
    echo -e "Press ${GREEN}Enter${NC} to connect, or ${RED}Ctrl+C${NC} to cancel..."
    read -r
    
    # Execute connection
    eval "$cmd"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $(basename "$0") [environment-name] [options]

OpenCode Remote Connection Helper - Connect to OpenCode environments easily.

Options:
  --list              List all environments (including stopped ones)
  --dry-run           Display connection command without executing
  --help              Show this help message

Examples:
  $(basename "$0")                          # Interactive mode: select from running environments
  $(basename "$0") my-env                   # Connect to specific environment
  $(basename "$0") my-env --dry-run         # Show connection command only
  $(basename "$0") --list                   # List all environments

Connection command format:
  OPENCODE_SERVER_USERNAME=<user> OPENCODE_SERVER_PASSWORD=<pass> opencode attach http://localhost:<port>

EOF
}

# Main function
main() {
    local env_name=""
    local dry_run="false"
    local list_all="false"
    local interactive="true"
    
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                show_usage
                exit 0
                ;;
            --list|-l)
                list_all="true"
                interactive="false"
                shift
                ;;
            --dry-run|-d)
                dry_run="true"
                shift
                ;;
            -*)
                echo -e "${RED}Error: Unknown option: $1${NC}"
                echo "Use --help for usage information."
                exit 1
                ;;
            *)
                env_name="$1"
                interactive="false"
                shift
                ;;
        esac
    done
    
    show_header
    
    # List mode
    if [ "$list_all" = "true" ]; then
        display_environments "true"
        exit 0
    fi
    
    # Direct connection mode
    if [ -n "$env_name" ]; then
        connect_to_environment "$env_name" "$dry_run"
        exit $?
    fi
    
    # Interactive mode
    if [ "$interactive" = "true" ]; then
        local environments
        
        if ! display_environments "false"; then
            exit 1
        fi
        
        mapfile -t environments < <(discover_environments "false")
        
        echo -n "Select environment [1-${#environments[@]}]: "
        read -r selection
        
        # Validate selection
        if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#environments[@]} ]; then
            echo -e "${RED}Error: Invalid selection.${NC}"
            exit 1
        fi
        
        # Get selected environment
        local selected_env="${environments[$((selection-1))]}"
        IFS='|' read -r env_name status port username password host <<< "$selected_env"
        
        connect_to_environment "$env_name" "$dry_run"
        exit $?
    fi
}

# Run main function
main "$@"
