# OpenCode Environment Manager TUI

A modern terminal-based user interface (TUI) for managing OpenCode development environments in Docker containers.

## Overview

The Environment Manager TUI replaces multiple shell scripts with a unified, interactive interface for creating, configuring, managing, and monitoring OpenCode environments. It provides real-time status updates, log viewing, and quick access to all environment operations.

## Features

### Core Functionality

- **Environment Management**
  - List all environments with live status updates
  - Create new environments with interactive wizard
  - Start/Stop/Restart environments
  - Build/Rebuild container images
  - Delete environments (with confirmation)
  - Clone/Duplicate existing environments
  - Bulk operations (start-all, stop-all, build-all)

- **Configuration Management**
  - Edit `.env` files with validation
  - Toggle volume mounts (MOUNT_GLOBAL_CONFIG, MOUNT_PROJECT_CONFIG, etc.)
  - Configure server settings (port, password, username)
  - Adjust resource limits (memory, CPU)
  - Configure workspace paths
  - Real-time validation of changes

- **Monitoring & Logs**
  - Real-time container status (running/stopped/building)
  - Port allocation display
  - OpenCode server URL display
  - Live log streaming with filtering
  - Resource usage monitoring (if available)
  - Container health checks

- **Operations**
  - Open interactive shell in environment
  - Execute custom commands
  - View/tail logs with search
  - Inspect environment details (volumes, network, config)
  - Validate environment configuration
  - Remote connection command helper

- **Remote Connection Helper**
  - Display connection command with credentials
  - Interactive connection script (`opencode-connect.sh`)
  - Copy connection command to clipboard
  - Quick connect to running environments

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker Engine
- Docker Compose v2
- OpenCode base image built

### Setup

1. **Install Python dependencies:**

```bash
cd /home/endre/opencode-workspace

# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Make entry points executable:**

```bash
chmod +x envman.py
chmod +x opencode-connect.sh
```

3. **Verify installation:**

```bash
./envman.py --help
./opencode-connect.sh --help
```

## Usage

### Main TUI Application

**Launch the TUI:**

```bash
./envman.py
# or
python envman.py
```

**Keyboard Navigation:**

**Global Keys:**
- `F1` or `1` - Environments Dashboard (main view)
- `F2` or `2` - Create New Environment
- `F3` or `3` - Configure Environment
- `F4` or `4` - View Logs
- `F5` or `5` - Help Screen
- `q` or `Ctrl+C` - Quit application

**Dashboard Navigation:**
- `↑` / `k` - Move selection up
- `↓` / `j` - Move selection down
- `Enter` - Perform primary action on selected environment
- `Space` - Multi-select (for bulk operations)

**Quick Actions (Dashboard):**
- `n` - New Environment
- `c` - Configure selected environment
- `l` - View logs for selected environment
- `s` - Open shell in selected environment
- `i` - Inspect environment details
- `r` - Restart selected environment
- `b` - Build/Rebuild selected environment
- `d` - Delete selected environment (with confirmation)
- `v` - Validate selected environment
- `R` - Refresh status manually
- `/` - Search/Filter environments

**Bulk Actions:**
- `Ctrl+A` - Select all environments
- `Ctrl+D` - Deselect all
- `Ctrl+S` - Start selected environments
- `Ctrl+X` - Stop selected environments
- `Ctrl+B` - Build selected environments

### Remote Connection Helper

**Interactive connection script:**

```bash
./opencode-connect.sh
```

The script will:
1. List all running environments with their connection details
2. Prompt you to select an environment
3. Display the connection command
4. Optionally execute the connection immediately

**Direct connection to specific environment:**

```bash
./opencode-connect.sh vienna-agentic-vibes
```

**List available environments:**

```bash
./opencode-connect.sh --list
```

**Get connection command only (no execution):**

```bash
./opencode-connect.sh vienna-agentic-vibes --dry-run
```

**Connection command format:**

```bash
OPENCODE_SERVER_USERNAME=<username> \
OPENCODE_SERVER_PASSWORD=<password> \
opencode attach http://localhost:<port>
```

**Example:**

```bash
OPENCODE_SERVER_USERNAME=opencode \
OPENCODE_SERVER_PASSWORD=opencode \
opencode attach http://localhost:4100
```

### Standalone Scripts (Fallback)

Legacy shell scripts are preserved in `scripts/` directory for automation, debugging, and edge cases:

```bash
# Create environment (wizard mode)
./scripts/create-environment.sh my-new-env

# Manage environments
./scripts/manage-environments.sh list
./scripts/manage-environments.sh start-all
./scripts/manage-environments.sh stop-all
./scripts/manage-environments.sh status
./scripts/manage-environments.sh exec dev1 bash
./scripts/manage-environments.sh logs dev1

# Validate environment
./scripts/validate-environment.sh dev1

# Update environment to new template
./scripts/update-environment.sh dev1

# Build and test all
./scripts/build-and-test.sh

# Setup network
./scripts/setup-network.sh

# Debug Node.js installation
./scripts/debug-nodejs.sh
```

## Architecture

### Project Structure

```
opencode-workspace/
├── envman.py                  # Main TUI entry point
├── opencode-connect.sh        # Remote connection helper
├── TUI-README.md              # This file
├── requirements.txt           # Python dependencies
│
├── envman/                    # TUI application package
│   ├── __init__.py
│   ├── app.py                 # Main Textual application
│   │
│   ├── screens/               # Application screens
│   │   ├── __init__.py
│   │   ├── dashboard.py       # Main environment list view
│   │   ├── create.py          # Environment creation wizard
│   │   ├── configure.py       # Configuration editor
│   │   ├── logs.py            # Log viewer with filtering
│   │   ├── inspect.py         # Environment details view
│   │   └── help.py            # Help screen
│   │
│   ├── widgets/               # Reusable UI components
│   │   ├── __init__.py
│   │   ├── env_table.py       # Environment list table
│   │   ├── status.py          # Status indicators & badges
│   │   ├── actions.py         # Action buttons
│   │   ├── progress.py        # Progress bars & spinners
│   │   └── forms.py           # Form inputs with validation
│   │
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── environment.py     # Environment class & state
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── docker.py          # Docker operations & queries
│   │   ├── config.py          # Config file parsing & writing
│   │   ├── validation.py      # Environment validation
│   │   ├── creator.py         # Environment creation logic
│   │   └── discovery.py       # Environment discovery & scanning
│   │
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── scripts.py         # Shell script execution wrapper
│       ├── helpers.py         # Helper functions
│       ├── constants.py       # Constants & defaults
│       └── exceptions.py      # Custom exceptions
│
├── scripts/                   # Legacy shell scripts (fallback)
│   ├── create-environment.sh
│   ├── manage-environments.sh
│   ├── validate-environment.sh
│   ├── update-environment.sh
│   ├── build-and-test.sh
│   ├── setup-network.sh
│   └── debug-nodejs.sh
│
├── environments/              # Environment instances
│   ├── template/              # Template for new environments
│   ├── vienna-agentic-vibes/  # Example environment
│   ├── test-env/
│   └── ...
│
├── base/                      # Base Docker image
│   └── Dockerfile
│
└── shared/                    # Shared resources
    ├── config/                # Shared OpenCode configs
    └── models/                # Shared AI models
```

### Technology Stack

**Core Framework:**
- **Textual** (v0.50+) - Modern Python TUI framework
  - Reactive, async-first architecture
  - Rich widgets library (tables, forms, modals, etc.)
  - CSS-like styling system
  - Hot reload during development

**Dependencies:**
- **python-dotenv** - Parse and write `.env` files
- **pyyaml** - Parse and write `docker-compose.yml` files
- **docker** - Docker SDK for Python (container status queries)
- **rich** - Terminal formatting (bundled with Textual)

**Optional:**
- **pyperclip** - Clipboard support for copying connection commands
- **pytest** - Testing framework

### Design Principles

1. **User-Centric**: Keyboard-driven navigation, vim-style keybindings, clear visual feedback
2. **Real-Time**: Auto-refresh status updates, live log streaming
3. **Safe**: Confirmation dialogs for destructive operations, validation before changes
4. **Extensible**: Modular architecture, easy to add new screens/features
5. **Backward Compatible**: Legacy scripts preserved for automation and debugging
6. **Self-Documenting**: Built-in help, context-sensitive hints, clear error messages

## Implementation Plan

### Phase 1: Core TUI Structure ✅ (Foundation)

**Goals:**
- Setup project structure with proper Python packaging
- Create main Textual application scaffold
- Implement basic navigation and UI layout
- Move existing scripts to `scripts/` subfolder

**Deliverables:**
- `envman/` package structure created
- Main `envman.py` entry point functional
- Empty dashboard screen with navigation
- `requirements.txt` with dependencies
- Scripts moved to `scripts/` directory

**Testing:**
- TUI launches without errors
- Navigation between screens works
- Keyboard shortcuts respond correctly
- Quit functionality works

---

### Phase 2: Environment Discovery & Display ✅

**Goals:**
- Implement environment scanning and parsing
- Display environments in table format
- Query Docker for container status
- Extract configuration details

**Deliverables:**
- `Environment` model class with properties:
  - name, status, port, url, username, password
  - workspace_dir, volumes, resource_limits
- `DiscoveryService` to scan `environments/` directory
- `DockerService` to query container status
- `ConfigService` to parse `.env` and `docker-compose.yml`
- Dashboard table populated with real environment data
- Status indicators (🟢 running, 🔴 stopped, 🟡 building)

**Testing:**
- All existing environments discovered
- Status accurately reflects container state
- Configuration values correctly parsed
- Table displays all columns correctly

---

### Phase 3: Basic Operations ✅

**Goals:**
- Implement start/stop/restart operations
- Build container images
- Open shell access
- Provide user feedback for operations

**Deliverables:**
- Start environment: `docker compose up -d`
- Stop environment: `docker compose down`
- Restart environment: stop + start
- Build environment: `docker compose build`
- Shell access: `docker compose exec opencode-<env> bash`
- Progress indicators and notifications
- Error handling with helpful messages
- Auto-refresh after operations

**Testing:**
- Start/stop/restart work correctly
- Build completes successfully
- Shell access opens interactive terminal
- Status updates reflect changes
- Errors display helpful messages

---

### Phase 4: Environment Creation ✅

**Goals:**
- Implement multi-step creation wizard
- Validate user input in real-time
- Generate environment configuration
- Create directory structure and files

**Deliverables:**
- Creation wizard with steps:
  1. Environment name (validate uniqueness)
  2. User configuration (UID/GID, timezone)
  3. Workspace configuration (isolated vs external path)
  4. Volume mount configuration (presets + custom)
  5. Server configuration (username, password, auto-assigned port)
  6. Review & confirm
- Port auto-assignment (find next available port)
- Template-based file generation
- Directory creation and permission setup
- Post-creation validation

**Testing:**
- Wizard completes successfully
- All files created correctly
- Unique port assigned
- Environment appears in dashboard
- Can start newly created environment

---

### Phase 5: Configuration Management ✅

**Goals:**
- Edit environment `.env` files
- Toggle volume mounts
- Validate configuration changes
- Backup original files

**Deliverables:**
- Configuration editor screen with form:
  - User settings (UID, GID, timezone)
  - Container settings (name, hostname)
  - Volume mounts (toggle switches)
  - Server settings (port, username, password)
  - Resource limits (memory, CPU, SHM)
- Real-time validation:
  - Port range (1024-65535)
  - UID/GID format
  - Path existence
  - No port conflicts
- Save with backup (`.env.backup`)
- Auto-update `docker-compose.yml` volume comments
- Restart prompt if container is running

**Testing:**
- All fields editable
- Validation catches errors
- Saved changes persist
- Backup files created
- Volume toggle updates compose file

---

### Phase 6: Monitoring & Logs ✅

**Goals:**
- Real-time log streaming
- Log filtering and search
- Environment inspection view
- Container health monitoring

**Deliverables:**
- Log viewer screen:
  - Stream logs with `docker compose logs -f`
  - Scrollable history (vim keybindings)
  - Filter by keyword/regex
  - Color-coded log levels
  - Clear logs / export to file
- Inspection view:
  - Container details (ID, image, uptime)
  - Mounted volumes list
  - Network configuration
  - Resource usage (if available)
  - Environment variables
  - Quick access to config files
- Status auto-refresh (every 3 seconds)
- Health check indicators

**Testing:**
- Logs stream in real-time
- Filtering works correctly
- Inspection shows accurate data
- Auto-refresh updates status
- No performance degradation

---

### Phase 7: Advanced Features ✅

**Goals:**
- Bulk operations on multiple environments
- Remote connection helper integration
- Environment validation
- Search and filtering

**Deliverables:**
- Multi-select in environment table (Space to toggle)
- Bulk operations:
  - Start-all / Stop-all / Build-all
  - Progress tracking for multiple operations
  - Parallel execution where safe
- Remote connection helper:
  - Display connection command in inspection view
  - Copy to clipboard (if pyperclip available)
  - Launch `opencode-connect.sh` from TUI
- Validation:
  - Run `validate-environment.sh` script
  - Display results in modal
  - Highlight issues in environment list
- Search/Filter:
  - Filter by name (regex support)
  - Filter by status (running/stopped)
  - Filter by port range

**Testing:**
- Multi-select works correctly
- Bulk operations complete successfully
- Connection command accurate
- Validation catches issues
- Search filters correctly

---

### Phase 8: Polish & Documentation ✅

**Goals:**
- Comprehensive help system
- Error handling improvements
- Documentation and examples
- User experience refinement

**Deliverables:**
- Help screen (F5):
  - All keyboard shortcuts
  - Feature descriptions
  - Quick start guide
  - Troubleshooting tips
- Context-sensitive help hints
- Confirmation dialogs for destructive operations
- Toast notifications for all operations
- Detailed error messages with recovery suggestions
- Loading states and progress indicators
- Keyboard shortcut cheat sheet (always visible)
- Updated README.md with TUI usage
- Updated AGENTS.md with new structure
- Tutorial/first-run guide
- Example configurations

**Testing:**
- Help screen complete and accurate
- All operations provide feedback
- Errors are user-friendly
- Documentation is clear
- First-time users can get started quickly

---

## Remote Connection Helper

### `opencode-connect.sh` Script

A standalone script for quick remote connections to OpenCode environments.

**Features:**
- Interactive environment selection
- Automatic credential loading from `.env` files
- Dry-run mode (display command without executing)
- List all available environments
- Direct connection by environment name
- Integration with TUI application

**Usage Examples:**

```bash
# Interactive mode - select from list
./opencode-connect.sh

# Connect to specific environment
./opencode-connect.sh vienna-agentic-vibes

# Show connection command without executing
./opencode-connect.sh vienna-agentic-vibes --dry-run

# List all running environments
./opencode-connect.sh --list

# Show help
./opencode-connect.sh --help
```

**Script Workflow:**

1. **Discovery Phase:**
   - Scan `environments/` directory
   - Parse `.env` files for server configuration
   - Query Docker for container status
   - Filter to only running environments (unless `--list` specified)

2. **Selection Phase:**
   - Display numbered list of environments with:
     - Environment name
     - Status (running/stopped)
     - Port
     - Username
   - Prompt user for selection (if not specified as argument)

3. **Connection Phase:**
   - Construct connection command:
     ```bash
     OPENCODE_SERVER_USERNAME=<username> \
     OPENCODE_SERVER_PASSWORD=<password> \
     opencode attach http://localhost:<port>
     ```
   - Display command to user
   - Execute (unless `--dry-run`)

**Output Example:**

```
╔═══════════════════════════════════════════════════════════════╗
║          OpenCode Environment Connection Helper              ║
╚═══════════════════════════════════════════════════════════════╝

Available environments:

  1) vienna-agentic-vibes    🟢 Running   Port: 4100   User: opencode
  2) test-env                🟢 Running   Port: 4097   User: admin
  3) code-reviewing-framework 🔴 Stopped   Port: 4098   User: opencode

Select environment [1-3]: 1

Connecting to: vienna-agentic-vibes
Connection command:
  OPENCODE_SERVER_USERNAME=opencode \
  OPENCODE_SERVER_PASSWORD=opencode \
  opencode attach http://localhost:4100

Press Enter to connect, or Ctrl+C to cancel...

[Executes command]
```

**GitHub Deployment - Installer Script:**

For public deployment, create `install-opencode-connect.sh`:

```bash
#!/bin/bash
# OpenCode Remote Connection Helper Installer

INSTALL_DIR="/usr/local/bin"
SCRIPT_URL="https://raw.githubusercontent.com/your-org/opencode-workspace/main/opencode-connect.sh"

echo "Installing OpenCode Connection Helper..."

# Download script
curl -fsSL "$SCRIPT_URL" -o "$INSTALL_DIR/opencode-connect"

# Make executable
chmod +x "$INSTALL_DIR/opencode-connect"

echo "✅ Installed successfully!"
echo "Usage: opencode-connect [environment-name] [options]"
```

**Installation:**

```bash
# One-line installer
curl -fsSL https://raw.githubusercontent.com/your-org/opencode-workspace/main/install-opencode-connect.sh | bash

# Manual installation
wget https://raw.githubusercontent.com/your-org/opencode-workspace/main/opencode-connect.sh
chmod +x opencode-connect.sh
sudo mv opencode-connect.sh /usr/local/bin/opencode-connect
```

---

## Configuration Reference

### Environment `.env` File Structure

```bash
# User Configuration
USER_ID=1000                    # Host user ID for file ownership
GROUP_ID=1000                   # Host group ID
TIMEZONE=UTC                    # Container timezone

# Container Configuration
CONTAINER_NAME=opencode-<env>   # Docker container name
HOSTNAME=opencode-<env>         # Container hostname

# Network Configuration
NETWORK_NAME=opencode-network   # Shared Docker network

# Volume Configuration
WORKSPACE_DIR=./workspace       # Workspace directory (isolated or external)
GLOBAL_CONFIG=../shared/config/.opencode  # Shared OpenCode config
PROJECT_CONFIG=./opencode_project_config  # Project-specific config
OPENCODE_ENV_CONFIG=./opencode_config     # Per-environment config
WORKTREE_DIR=./worktree         # Git worktrees (optional)

# Volume Mount Control (toggle in TUI)
MOUNT_GLOBAL_CONFIG=false       # Mount shared config
MOUNT_PROJECT_CONFIG=false      # Mount project config
MOUNT_OPENCODE_ENV_CONFIG=true  # Mount per-env config (recommended)

# Server Configuration
OPENCODE_SERVER_ENABLED=true    # Enable OpenCode server
OPENCODE_SERVER_HOST=0.0.0.0    # Server bind address
OPENCODE_SERVER_PORT=4096       # Server port (auto-assigned)
OPENCODE_SERVER_USERNAME=opencode  # Server username
OPENCODE_SERVER_PASSWORD=       # Server password (required)
OPENCODE_SERVER_CORS=           # CORS configuration

# Resource Limits (optional)
MEMORY_LIMIT=2g                 # Memory limit (e.g., 2g, 4g)
CPU_LIMIT=1.0                   # CPU limit (e.g., 0.5, 1.0, 2.0)
SHM_SIZE=1g                     # Shared memory size
```

### Port Assignment Strategy

**Auto-Assignment Algorithm:**
1. Scan all existing environment `.env` files
2. Collect all `OPENCODE_SERVER_PORT` values
3. Start from base port (4096)
4. Find first available port not in use
5. Assign to new environment

**Port Ranges:**
- Base port: 4096
- Range: 4096-4196 (100 environments max)
- Reserved: None (all available)

**Port Conflict Resolution:**
- TUI validates port uniqueness
- Creation wizard auto-assigns next available
- Configuration editor warns on conflicts
- Port can be manually changed if desired

---

## Development

### Local Development Setup

```bash
# Clone repository
git clone <repo-url>
cd opencode-workspace

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (editable mode)
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run TUI in development mode (with hot reload)
textual run --dev envman/app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=envman --cov-report=html

# Run specific test file
pytest tests/test_environment.py

# Run with verbose output
pytest -v
```

### Code Style

```bash
# Format code
black envman/

# Lint code
flake8 envman/

# Type checking
mypy envman/
```

### Textual Development Tools

```bash
# Run with Textual DevTools console
textual console

# Run app with console logging
textual run --dev envman/app.py

# Take screenshot for documentation
textual run envman/app.py --screenshot
```

---

## Troubleshooting

### TUI Won't Launch

**Problem:** `ModuleNotFoundError: No module named 'textual'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Environments Not Showing

**Problem:** Dashboard is empty, no environments listed

**Solution:**
1. Check `environments/` directory exists and contains environment folders
2. Verify each environment has `docker-compose.yml` and `.env` files
3. Check file permissions (readable by current user)
4. Enable debug logging: `LOG_LEVEL=DEBUG ./envman.py`

---

### Docker Connection Failed

**Problem:** "Cannot connect to Docker daemon"

**Solution:**
```bash
# Check Docker is running
docker ps

# Check user has Docker permissions
groups | grep docker

# Add user to docker group if needed
sudo usermod -aG docker $USER
newgrp docker
```

---

### Status Shows Incorrect

**Problem:** Environment shows "Running" but container is stopped (or vice versa)

**Solution:**
1. Manual refresh: Press `R` in dashboard
2. Check Docker status: `docker ps -a | grep opencode`
3. Verify container names match pattern: `opencode-<env-name>`
4. Restart TUI (quit with `q` and relaunch)

---

### Connection Helper Script Fails

**Problem:** `opencode-connect.sh` cannot find OpenCode binary

**Solution:**
```bash
# Ensure OpenCode is installed and in PATH
which opencode

# Install OpenCode if missing
# See OpenCode installation docs

# Check environment variables are set correctly in .env
grep OPENCODE_SERVER .env
```

---

### Build Fails in TUI

**Problem:** Build operation fails with error

**Solution:**
1. Check Docker disk space: `docker system df`
2. View full build logs: `docker compose logs` in environment directory
3. Try building manually: `cd environments/<env> && docker compose build`
4. Check base image exists: `docker images | grep opencode-base`
5. Rebuild base if needed: `cd base && docker build ...`

---

### Permission Errors in Container

**Problem:** File permission errors inside container

**Solution:**
```bash
# Verify UID/GID match host user
id -u  # Should match USER_ID in .env
id -g  # Should match GROUP_ID in .env

# Update .env with correct values
# Rebuild container
cd environments/<env>
docker compose down
docker compose build
docker compose up -d
```

---

## FAQ

### Q: Can I still use the old shell scripts?

**A:** Yes! All scripts are preserved in `scripts/` directory and work exactly as before. The TUI is a wrapper that provides a better interface, but scripts remain available for automation, CI/CD pipelines, and debugging.

---

### Q: How do I update an existing environment to work with the TUI?

**A:** The TUI reads standard `.env` and `docker-compose.yml` files. If your environment was created with the old scripts, it should work immediately. Run `./scripts/update-environment.sh <env>` if you want to migrate to the newest template format.

---

### Q: Can I customize the TUI appearance?

**A:** Yes! Textual uses CSS-like styling. Create `envman/styles.css` to customize colors, borders, and layout. See Textual documentation for details.

---

### Q: Does the TUI support remote Docker hosts?

**A:** Not currently. The TUI uses `docker compose` commands which respect `DOCKER_HOST` environment variable. You can set this before launching the TUI, but it's not tested extensively.

---

### Q: How do I add a new feature to the TUI?

**A:** 
1. Create a new screen in `envman/screens/` (if it's a new view)
2. Add business logic to `envman/services/`
3. Add keyboard binding in `envman/app.py`
4. Update help screen in `envman/screens/help.py`
5. Add tests in `tests/`
6. Update this documentation

---

### Q: Can I run multiple TUI instances?

**A:** Yes, each instance will show live status updates. However, avoid performing conflicting operations (e.g., two instances trying to start the same environment simultaneously).

---

### Q: How do I deploy this to a team?

**A:** 
1. Commit `envman/` directory and `requirements.txt` to git
2. Each team member clones the repo
3. Each runs `pip install -r requirements.txt`
4. Environments are isolated per developer (use different environment names)
5. Shared resources (base image, models) can be in `shared/` directory

For the connection helper script, use the GitHub installer approach documented above.

---

### Q: What about Windows support?

**A:** The TUI should work on Windows with Docker Desktop and Python installed. However, it's primarily tested on Linux/macOS. Some shell script integrations may require WSL on Windows.

---

### Q: How do I backup my environments?

**A:** 
- Configuration: `.env` and `docker-compose.yml` files in `environments/<env>/`
- Data: Volumes in `environments/<env>/opencode_config/` and workspace
- To backup: `tar -czf backup.tar.gz environments/<env>/`
- To restore: Extract to `environments/` directory

The TUI will automatically discover restored environments.

---

### Q: Can I use this without Docker?

**A:** No, the entire system is built around Docker containers for isolation and reproducibility. If you want to run OpenCode without Docker, use OpenCode directly without this environment management system.

---

## Roadmap

### Short-term (v1.0)
- ✅ Complete all 8 implementation phases
- ✅ Comprehensive testing on existing environments
- ✅ Documentation finalization
- ☐ Release v1.0 with full feature set

### Medium-term (v1.x)
- ☐ Environment import/export (JSON format)
- ☐ Configuration templates (save favorite configs)
- ☐ Resource usage graphs (CPU, memory over time)
- ☐ Environment groups/tags for organization
- ☐ Custom themes and color schemes
- ☐ Plugin system for custom actions
- ☐ Web-based UI alternative (optional)
- ☐ Environment snapshots (save/restore state)

### Long-term (v2.x)
- ☐ Multi-host support (manage environments on different machines)
- ☐ Kubernetes backend support (alongside Docker)
- ☐ Team collaboration features (shared environments)
- ☐ Automated scaling (start/stop based on usage)
- ☐ Integration with CI/CD pipelines
- ☐ Environment provisioning from git repositories
- ☐ Advanced monitoring (Prometheus integration)
- ☐ Environment marketplace (share configs with community)

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow PEP 8, use `black` for formatting
2. **Testing**: Add tests for new features
3. **Documentation**: Update this README and inline docstrings
4. **Commit Messages**: Use conventional commits (feat:, fix:, docs:, etc.)
5. **Pull Requests**: Create PR with clear description and tests

---

## License

[Specify license here]

---

## Credits

- **Textual Framework**: https://textual.textualize.io/
- **OpenCode**: https://opencode.ai/
- **Docker**: https://www.docker.com/

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: [Create an issue]
- Documentation: This README and inline help (F5 in TUI)
- OpenCode Docs: https://opencode.ai/docs

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-16  
**Status:** Implementation in Progress
