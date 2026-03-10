# AGENTS.md - OpenCode Workspace Environment

## Project Overview

This is a Docker-based development environment system for OpenCode that provides isolated, reproducible workspaces for multiple developers. The system creates separate Ubuntu 24.04 containers with OpenCode, Node.js, and development tools, while sharing configuration and AI models across environments.

## Build Commands

### Base Image Build
```bash
# Build the shared base image with your host user's UID/GID
cd base
docker build \
  --build-arg USER_ID=$(id -u) \
  --build-arg GROUP_ID=$(id -g) \
  -t opencode-base:latest .
```

### Environment Build
```bash
# Build a specific environment
cd environments/dev1
docker compose build
```

### Complete Build & Test Pipeline
```bash
# Run the full build and test sequence
./build-and-test.sh
```

## Test & Validation Commands

### Environment Validation
```bash
# Validate a specific environment
./validate-environment.sh dev1
```

### Network Setup
```bash
# Create the shared Docker network (run once)
./setup-network.sh
```

### Debug Commands
```bash
# Debug Node.js installation issues
./debug-nodejs.sh
```

## Management Commands

### Multi-Environment Management
```bash
# List all environments
./manage-environments.sh list

# Build all environments
./manage-environments.sh build-all

# Start all environments
./manage-environments.sh start-all

# Stop all environments
./manage-environments.sh stop-all

# Check status of all environments
./manage-environments.sh status

# Execute command in specific environment
./manage-environments.sh exec dev1 bash

# View logs for environment
./manage-environments.sh logs dev1
```

### Environment Creation & Updates
```bash
# Create new environment with interactive setup
./create-environment.sh <env_name>

# Update existing environment to new template format
./update-environment.sh <env_name>
```

### Single Environment Operations
```bash
# Start environment
cd environments/dev1
docker compose up -d

# Stop environment
docker compose down

# Access environment shell
docker compose exec opencode-dev1 bash

# View logs
docker compose logs -f
```

## Code Style Guidelines

### Shell Script Conventions
- **Shebang**: Always use `#!/bin/bash`
- **Error Handling**: Check exit codes manually with `if [ $? -ne 0 ]`
- **Variables**: Use `VAR=value` (no spaces), expand with `${VAR}`
- **Conditionals**: Format as `if [ ... ]; then` with proper spacing
- **Output**: Use emoji icons for status (✅ success, ❌ error, ⚠️ warning)
- **Comments**: Use descriptive comments with space after `#`

### Docker/Docker Compose Patterns
- **Build Arguments**: Always pass `USER_ID` and `GROUP_ID` to match host user
- **Volume Mounts**:
  - System files: Read-only (`:ro`)
  - Configuration: Read-write shared (`:rw`)
  - Models: Read-only shared (`:ro`)
  - Workspace: Read-write isolated
- **Container Naming**: Use `opencode-<env_name>` pattern
- **Hostnames**: Use `opencode-<env_name>` pattern
- **Network**: Use `opencode-network` for all environments

### Naming Conventions
- **Environment Names**: `dev1`, `dev2`, `dev3`, etc.
- **Container Names**: `opencode-<env_name>`
- **Image Tags**: `opencode-base:latest`, `opencode-workspace:<env_name>`
- **Script Names**: Use hyphens: `manage-environments.sh`, `build-and-test.sh`

### File Structure Patterns
- **Base Configuration**: `/home/endre/opencode-workspace/base/`
- **Environment Configs**: `/home/endre/opencode-workspace/environments/<env>/`
- **Shared Resources**: `/home/endre/opencode-workspace/shared/`
- **Management Scripts**: Root directory with `.sh` extension

### Environment Variables (.env files)
```bash
# Standard variables for all environments
USER_ID=1000                    # Maps to host user ID
GROUP_ID=1000                   # Maps to host group ID
TIMEZONE=UTC                    # Timezone synchronization
CONTAINER_NAME=opencode-<env>   # Container naming
HOSTNAME=opencode-<env>         # Container hostname
NETWORK_NAME=opencode-network   # Shared network

# Volume Configuration
WORKSPACE_DIR=./workspace       # Workspace directory
GLOBAL_CONFIG=~/.config/opencode:ro  # Global OpenCode config (read-only)
OPENCODE_ENV_CONFIG=./opencode_config:rw  # Per-environment config (read-write)

# Server Configuration
OPENCODE_SERVER_ENABLED=true    # Enable OpenCode server
OPENCODE_SERVER_HOST=0.0.0.0    # Server bind address
OPENCODE_SERVER_PORT=4096       # Server port (auto-incremented)
OPENCODE_SERVER_USERNAME=opencode  # Server username (configurable)
OPENCODE_SERVER_PASSWORD=       # Server password (required)
OPENCODE_SERVER_CORS=           # CORS configuration
```

## Agent Workflow Guidelines

### Creating New Environments
1. Run interactive setup: `./create-environment.sh <new_env>`
   - Prompts for username (default: "opencode")
   - Prompts for password (generates random if empty)
   - Creates all required directories
   - Assigns unique UID/GID and port
2. Build: `cd environments/<new_env> && docker compose build`
3. Validate: `./validate-environment.sh <new_env>`

### Updating Existing Environments
1. Run migration: `./update-environment.sh <env_name>`
   - Creates backups of existing configuration
   - Preserves existing UID/GID and port
   - Updates to new template format
   - Creates missing directories
2. Rebuild if needed: `cd environments/<env_name> && docker compose build`

### Working Within Environments
1. Access environment: `docker compose exec opencode-<env> bash`
2. Workspace location: `/home/dev/workspace`
3. OpenCode config: `/home/dev/.config/opencode/` (read-only from host)
4. Per-environment config: `/home/dev/.local/share/opencode/` (read-write)
5. Shared models: Mounted from `shared/models/` (read-only)

### Testing Changes
1. Always run `./validate-environment.sh <env>` after modifications
2. Use `./build-and-test.sh` for comprehensive testing
3. Check container logs: `docker compose logs -f`

## Troubleshooting

### Common Issues
1. **Permission Errors**: Ensure `USER_ID`/`GROUP_ID` match host user
2. **Network Issues**: Run `./setup-network.sh` to recreate network
3. **Node.js/OpenCode Installation**: Use `./debug-nodejs.sh`
4. **Container Won't Start**: Check `docker compose logs` for errors

### Debug Commands
```bash
# Check container user mapping
docker compose exec opencode-dev1 id -u
docker compose exec opencode-dev1 id -g

# Verify OpenCode installation
docker compose exec opencode-dev1 opencode --version

# Check mounted volumes
docker compose exec opencode-dev1 ls -la /home/dev/.config/opencode
docker compose exec opencode-dev1 ls -la /home/dev/.local/share/opencode/models

# Test network connectivity
docker compose exec opencode-dev1 ping opencode-dev2.opencode.local
```

## Best Practices for Agents

1. **Isolation**: Each agent should use its own environment with unique UID/GID
2. **Configuration**: Place agent-specific OpenCode config in `shared/config/`
3. **Testing**: Always validate environment after changes
4. **Cleanup**: Use `docker compose down -v` to remove volumes when testing
5. **Documentation**: Update README.md when adding new features or scripts

## Notes

- No Cursor rules (`.cursorrules` or `.cursor/`) or Copilot rules (`.github/copilot-instructions.md`) found
- Mixed usage of `docker compose` (two words) and `docker-compose` (hyphenated) - be consistent
- All scripts are in root directory with `.sh` extension
- Template system available in `environments/template/` for creating new environments