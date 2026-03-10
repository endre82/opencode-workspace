#!/bin/bash
# OpenCode Environments Management Script

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENTS_DIR="${BASE_DIR}/environments"

case "$1" in
    list)
        echo "Available environments:"
        echo "======================="
        for env in $(find "${ENVIRONMENTS_DIR}" -maxdepth 1 -type d -name "dev*" | sort); do
            env_name=$(basename "${env}")
            if [ -f "${env}/docker-compose.yml" ]; then
                echo "✓ ${env_name}"
            fi
        done
        echo ""
        echo "Template:"
        echo "  template/ (for creating new environments)"
        ;;
    
    build-all)
        echo "Building all environments..."
        for env in $(find "${ENVIRONMENTS_DIR}" -maxdepth 1 -type d -name "dev*"); do
            env_name=$(basename "${env}")
            echo "Building ${env_name}..."
            (cd "${env}" && docker-compose build)
        done
        ;;
    
    start-all)
        echo "Starting all environments..."
        for env in $(find "${ENVIRONMENTS_DIR}" -maxdepth 1 -type d -name "dev*"); do
            env_name=$(basename "${env}")
            echo "Starting ${env_name}..."
            (cd "${env}" && docker-compose up -d)
        done
        ;;
    
    stop-all)
        echo "Stopping all environments..."
        for env in $(find "${ENVIRONMENTS_DIR}" -maxdepth 1 -type d -name "dev*"); do
            env_name=$(basename "${env}")
            echo "Stopping ${env_name}..."
            (cd "${env}" && docker-compose down)
        done
        ;;
    
    status)
        echo "Environment Status:"
        echo "==================="
        for env in $(find "${ENVIRONMENTS_DIR}" -maxdepth 1 -type d -name "dev*"); do
            env_name=$(basename "${env}")
            container_name="opencode-${env_name}"
            if docker ps --filter "name=${container_name}" --format "table {{.Names}}\t{{.Status}}" | grep -q "${container_name}"; then
                docker ps --filter "name=${container_name}" --format "✓ {{.Names}}: {{.Status}}"
            else
                echo "✗ ${container_name}: Not running"
            fi
        done
        ;;
    
    exec)
        if [ -z "$2" ]; then
            echo "Usage: $0 exec <environment> [command]"
            echo "Example: $0 exec dev1 bash"
            exit 1
        fi
        ENV_NAME="$2"
        COMMAND="${3:-bash}"
        ENV_DIR="${ENVIRONMENTS_DIR}/${ENV_NAME}"
        
        if [ ! -d "${ENV_DIR}" ]; then
            echo "Error: Environment ${ENV_NAME} not found"
            exit 1
        fi
        
        (cd "${ENV_DIR}" && docker-compose exec "opencode-${ENV_NAME}" ${COMMAND})
        ;;
    
    logs)
        if [ -z "$2" ]; then
            echo "Usage: $0 logs <environment>"
            echo "Example: $0 logs dev1"
            exit 1
        fi
        ENV_NAME="$2"
        ENV_DIR="${ENVIRONMENTS_DIR}/${ENV_NAME}"
        
        if [ ! -d "${ENV_DIR}" ]; then
            echo "Error: Environment ${ENV_NAME} not found"
            exit 1
        fi
        
        (cd "${ENV_DIR}" && docker-compose logs -f)
        ;;
    
    *)
        echo "OpenCode Environments Management"
        echo "================================"
        echo "Commands:"
        echo "  list          - List all available environments"
        echo "  build-all     - Build all environment images"
        echo "  start-all     - Start all environments"
        echo "  stop-all      - Stop all environments"
        echo "  status        - Show status of all environments"
        echo "  exec <env>    - Execute command in environment"
        echo "  logs <env>    - Show logs for environment"
        echo ""
        echo "Environment-specific commands:"
        echo "  cd environments/<env-name>"
        echo "  docker-compose build    # Build this environment"
        echo "  docker-compose up -d    # Start this environment"
        echo "  docker-compose down     # Stop this environment"
        echo "  docker-compose logs     # View logs"
        ;;
esac
