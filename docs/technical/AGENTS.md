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

# Volume Mount Control
# Set to 'true' to enable mounting, 'false' to disable
# Note: You must also uncomment corresponding volume in docker-compose.yml
MOUNT_GLOBAL_CONFIG=false        # Mount shared OpenCode config from host
MOUNT_PROJECT_CONFIG=false       # Mount project-specific .opencode config
MOUNT_OPENCODE_ENV_CONFIG=true   # Mount per-environment config (recommended)

# Volume Configuration
# Workspace can be isolated (./workspace) or external path (~/my-env-name)
WORKSPACE_DIR=./workspace        # Workspace directory (isolated by default)
GLOBAL_CONFIG=../shared/config/.opencode  # Global OpenCode config (vienna pattern)
PROJECT_CONFIG=./opencode_project_config  # Per-project config (optional)
OPENCODE_ENV_CONFIG=./opencode_config     # Per-environment config (always mounted)
WORKTREE_DIR=./worktree          # Git worktrees (optional, for VSCode access)

# Server Configuration
OPENCODE_SERVER_ENABLED=true    # Enable OpenCode server
OPENCODE_SERVER_HOST=0.0.0.0    # Server bind address
OPENCODE_SERVER_PORT=4096       # Server port (auto-incremented)
OPENCODE_SERVER_USERNAME=opencode  # Server username (configurable)
OPENCODE_SERVER_PASSWORD=       # Server password (required)
OPENCODE_SERVER_CORS=           # CORS configuration
```

## Volume Mount Configuration

### Quick Presets

**Minimal Setup (Default - vienna-agentic-vibes pattern):**
- Workspace only + OPENCODE_ENV_CONFIG
- Use when: You want isolated environment, no host config sharing
- Volumes: `MOUNT_GLOBAL_CONFIG=false`, `MOUNT_PROJECT_CONFIG=false`

**Standard Setup:**
- Workspace + GLOBAL_CONFIG + OPENCODE_ENV_CONFIG
- Use when: You need shared host OpenCode configuration
- Volumes: `MOUNT_GLOBAL_CONFIG=true`, `MOUNT_PROJECT_CONFIG=false`

**Full Setup:**
- All mounts (Workspace + GLOBAL_CONFIG + PROJECT_CONFIG + OPENCODE_ENV_CONFIG)
- Use when: Complex multi-project setup with shared configurations
- Volumes: `MOUNT_GLOBAL_CONFIG=true`, `MOUNT_PROJECT_CONFIG=true`

### Manual Volume Configuration

To enable/disable volumes after environment creation:

1. **Edit `.env` file** to set MOUNT_* variables:
   ```bash
   MOUNT_GLOBAL_CONFIG=true   # Enable global config mounting
   MOUNT_PROJECT_CONFIG=false # Keep project config disabled
   ```

2. **Edit `docker-compose.yml`** to uncomment corresponding volumes:
   ```yaml
   volumes:
     # Uncomment the volumes you want to mount:
     - ${GLOBAL_CONFIG}:/home/dev/.config/opencode:ro  # Uncommented
     # - ${PROJECT_CONFIG}:/home/dev/workspace/.opencode:rw  # Still commented
   ```

3. **Rebuild and restart** the container:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Volume Mount Purposes

**WORKSPACE_DIR** (always mounted):
- Your working directory inside the container
- Can be isolated (`./workspace`) or external (`~/my-project`)
- Mounted as read-write

**OPENCODE_ENV_CONFIG** (recommended, default: enabled):
- Per-environment OpenCode data and cache
- Stores conversation history, settings, extensions
- Mounted as read-write

**GLOBAL_CONFIG** (optional, default: disabled):
- Shared OpenCode configuration from host system
- Useful for sharing API keys, preferences across environments
- Mounted as read-only (prevents accidental changes)

**PROJECT_CONFIG** (optional, default: disabled):
- Project-specific `.opencode` directory
- Contains project-level prompts, workflows, custom configs
- Mounted as read-write
- Example use: Shared team configuration for specific project

**WORKTREE_DIR** (optional, recommended for git worktree users):
- Git worktrees created by OpenCode
- Enables VSCode to access worktree branches directly
- Mounted as read-write from `./worktree` to `/home/dev/.local/share/opencode/worktree`
- Solves the visibility problem: worktrees normally hidden inside container

### Git Worktree Integration

If you use OpenCode's git worktree feature and want to access worktree branches in VSCode on your host machine, you need to mount the worktree directory.

**Setup:**

1. **Add to `.env` file** (already included in template):
   ```bash
   WORKTREE_DIR=./worktree
   ```

2. **Uncomment in `docker-compose.yml` volumes** (commented by default in template):
   ```yaml
   volumes:
     # Uncomment to enable worktree mounting:
     # - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw
   ```

3. **Create the worktree directory:**
   ```bash
   mkdir -p ./worktree
   ```

4. **If you have existing worktrees, copy them from the container:**
   ```bash
   docker cp <container-name>:/home/dev/.local/share/opencode/worktree/. ./worktree/
   ```

5. **Restart the container:**
   ```bash
   docker compose down && docker compose up -d
   ```

**Benefits:**
- Worktrees appear in `environments/<env-name>/worktree/`
- VSCode can directly open and navigate worktree branches
- Quick context switching between main workspace and worktree branches
- Works with vienna-agentic-vibes pattern (isolated workspace + worktrees)

**Usage in VSCode:**
```bash
# Worktrees are located at:
environments/vienna-agentic-vibes/worktree/a958075e.../branch-name/

# Open in VSCode:
code environments/vienna-agentic-vibes/worktree/a958075e.../branch-name/

# Or create symlinks in workspace root for easier access
```


## Agent Workflow Guidelines

### Creating New Environments
1. Run interactive setup: `./create-environment.sh <new_env>`
   - **Step 1: User Configuration** - Prompts for USER_ID and GROUP_ID
   - **Step 2: Workspace Configuration** - Choose isolated (./workspace) or external path
   - **Step 3: Volume Mount Configuration** - Select which volumes to mount
   - **Step 4: Server Configuration** - Username, password, and port
   - Creates all required directories
   - Assigns unique UID/GID and port
   - Uncomments volumes in docker-compose.yml based on selections
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

## Exception Logging System

### Overview
The OpenCode Workspace TUI includes a comprehensive exception logging system that automatically captures all uncaught exceptions with full context. This enables AI agents to debug and fix issues with complete information.

### Log File Location
```
~/.local/share/opencode-workspace/logs/exceptions.log
```

### Log Format
Each exception is logged as a single-line JSON object with the following structure:

```json
{
  "timestamp": "2026-03-17T00:59:12.386334",
  "exception_type": "ValueError",
  "exception_message": "invalid literal for int() with base 10: 'not_a_number'",
  "stack_trace": [
    {
      "file": "/path/to/file.py",
      "line": 123,
      "function": "function_name",
      "code": "problematic_code_line"
    }
  ],
  "context": {
    "screen": "CreationWizard",
    "step": 1,
    "user_action": "clicked_next_button",
    "environment_name": "myenv"
  },
  "system_info": {
    "python_version": "3.12.3",
    "platform": "Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39",
    "docker_available": true,
    "docker_version": "24.0.7"
  },
  "process_info": {
    "pid": "app.py",
    "cwd": "/home/endre/opencode-workspace"
  }
}
```

### Key Features
- **Automatic Capture**: Global exception hook catches all uncaught exceptions
- **Rich Context**: Includes screen, step, user action, environment name
- **Full Stack Traces**: Multi-level stack traces with file paths and line numbers
- **System Information**: Python version, platform, Docker status
- **JSON Format**: Single-line JSON for easy parsing by AI
- **Log Rotation**: 10MB max per file, keeps 5 backup files
- **Thread-Safe**: Uses locks for concurrent writes
- **Fail-Safe**: Logger failures won't crash the app

### How It Works
1. **Global Hook**: `install_global_hook()` replaces `sys.excepthook` at app startup
2. **Context Tracking**: Screens call `set_context()` in `on_mount()` methods
3. **Automatic Logging**: When an exception occurs, the hook:
   - Gathers current context from thread-local storage
   - Collects system information
   - Formats stack trace
   - Writes JSON entry to log file
   - Calls original exception hook (so app behavior is unchanged)

### Integration Points
- **App Initialization**: `envman/app.py` calls `install_global_hook()` in `__init__`
- **Screen Context**: All screens call `set_context()` in `on_mount()`:
  - `Dashboard`: `set_context(screen="Dashboard")`
  - `CreationWizard`: `set_context(screen="CreationWizard", step=1)`
  - `LogsScreen`: `set_context(screen="LogsViewer", environment_name=...)`
  - `InspectScreen`: `set_context(screen="InspectEnvironment", environment_name=...)`
  - `ConfigScreen`: `set_context(screen="ConfigEditor", environment_name=...)`
  - `DeleteScreen`: `set_context(screen="DeleteEnvironment", environment_name=...)`

### Using the Exception Logger
**For AI Agents (Debugging):**
When a user reports an issue, simply ask them to:
1. Reproduce the error
2. Check the exception log: `cat ~/.local/share/opencode-workspace/logs/exceptions.log`
3. Provide the latest JSON entry

**For Development:**
```python
from envman.utils.exception_logger import install_global_hook, set_context

# Install at app startup
install_global_hook()

# Set context in screens
set_context(screen="Dashboard")

# Set context with step changes
set_context(screen="CreationWizard", step=2)

# Set context for user actions
set_context(user_action="clicked_create_button", environment_name="myenv")
```

### Manual Exception Logging
For caught exceptions that you want to log but handle locally:
```python
from envman.utils.exception_logger import exception_context

with exception_context(screen="Dashboard", user_action="refresh"):
    # Code that might raise exceptions
    refresh_environments()
```

### Testing the Logger
```bash
# Test with a simple exception
python3 -c "
import sys
sys.path.insert(0, '/home/endre/.local/share/opencode-workspace')
from envman.utils.exception_logger import install_global_hook, set_context
install_global_hook()
set_context(screen='TestScreen', step=1)
x = 1 / 0  # This will be logged
"

# View the log
cat ~/.local/share/opencode-workspace/logs/exceptions.log | tail -1 | python3 -m json.tool
```

### Benefits for AI Debugging
When a user says "fix the exception", the AI has access to:
- **Exact error message** and exception type
- **Full stack trace** showing where it happened
- **User context**: What screen/step they were on
- **Action context**: What triggered the exception
- **System environment**: Python version, Docker status, etc.
- **Process info**: Working directory, PID

This eliminates the need for back-and-forth questions about:
- "What were you doing when it crashed?"
- "What error message did you see?"
- "What version are you running?"
- "Can you show me the full traceback?"

### File Structure
```
envman/utils/exception_logger.py  # Main logging implementation
envman/app.py                     # Global hook installation
envman/screens/*.py               # Context tracking in screens
~/.local/share/opencode-workspace/logs/exceptions.log  # Log file
```

### Notes
- The logger creates the log directory automatically if it doesn't exist
- Log rotation creates backup files: `exceptions.log.1`, `.log.2`, etc.
- Each log entry is a single line for easy `tail -f` monitoring
- JSON format ensures structured data for AI parsing
- Context is thread-local, so it works with async operations

## Notes

- No Cursor rules (`.cursorrules` or `.cursor/`) or Copilot rules (`.github/copilot-instructions.md`) found
- Mixed usage of `docker compose` (two words) and `docker-compose` (hyphenated) - be consistent
- All scripts are in root directory with `.sh` extension
- Template system available in `environments/template/` for creating new environments