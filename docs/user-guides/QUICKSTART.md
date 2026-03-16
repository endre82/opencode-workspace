# OpenCode Environment Manager - Quick Start Guide

Get up and running with the Environment Manager TUI in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Docker Engine running
- Docker Compose v2
- OpenCode base image built (run `cd base && docker build ...`)

## Installation

### 1. Install Python Dependencies

```bash
# Install to user site-packages (recommended)
pip install --user -r requirements.txt

# OR create a virtual environment (isolated)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Check Python dependencies
python -c "import textual; print('Textual installed:', textual.__version__)"
python -c "import docker; print('Docker SDK installed')"

# Check scripts are executable
ls -l envman.py opencode-connect.sh
```

If not executable, run:
```bash
chmod +x envman.py opencode-connect.sh
```

## Usage

### Remote Connection Helper (Works Now!)

Connect to running OpenCode environments:

```bash
# Interactive mode - select from running environments
./opencode-connect.sh

# List all environments
./opencode-connect.sh --list

# Connect to specific environment
./opencode-connect.sh vienna-agentic-vibes

# Show connection command without executing
./opencode-connect.sh vienna-agentic-vibes --dry-run
```

**Example Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║          OpenCode Environment Connection Helper              ║
╚═══════════════════════════════════════════════════════════════╝

Available environments:

  1) vienna-agentic-vibes    🟢 Running   Port: 4100   User: opencode
  2) test-env                🔴 Stopped   Port: 4097   User: admin

Select environment [1-2]: 1

Connecting to: vienna-agentic-vibes
Connection command:
  OPENCODE_SERVER_USERNAME=opencode \
  OPENCODE_SERVER_PASSWORD=opencode \
  opencode attach http://localhost:4100

Press Enter to connect, or Ctrl+C to cancel...
```

### TUI Application (Coming Soon!)

The full TUI is built and ready, but requires Textual to be installed:

```bash
# Launch the TUI
./envman.py

# OR with Python directly
python envman.py
```

**Note:** If you get import errors, make sure you've installed dependencies:
```bash
pip install --user textual python-dotenv pyyaml docker
```

## Legacy Scripts (Still Work!)

All the old scripts are still available in `scripts/` directory:

```bash
# Create new environment
./scripts/create-environment.sh my-new-env

# Manage environments
./scripts/manage-environments.sh list
./scripts/manage-environments.sh start-all
./scripts/manage-environments.sh stop-all
./scripts/manage-environments.sh status

# Validate environment
./scripts/validate-environment.sh my-env

# Update environment template
./scripts/update-environment.sh my-env

# Build and test
./scripts/build-and-test.sh
```

## Common Tasks

### Create Your First Environment

```bash
# Using the creation script (interactive)
./scripts/create-environment.sh my-first-env

# Follow the prompts to configure:
# 1. User ID/GID (default: your current user)
# 2. Workspace location (isolated or external)
# 3. Volume mounts (minimal, standard, or full)
# 4. Server credentials and port

# Start the environment
cd environments/my-first-env
docker compose up -d

# Connect to it
./opencode-connect.sh my-first-env
```

### Start an Existing Environment

```bash
# Using docker compose directly
cd environments/<env-name>
docker compose up -d

# OR using management script
./scripts/manage-environments.sh start-all
```

### View Environment Status

```bash
# Using management script
./scripts/manage-environments.sh status

# OR using connection helper
./opencode-connect.sh --list
```

### Open Shell in Environment

```bash
# Using management script
./scripts/manage-environments.sh exec <env-name> bash

# OR using docker compose
cd environments/<env-name>
docker compose exec opencode-<env-name> bash
```

## Troubleshooting

### "Cannot connect to Docker daemon"

Make sure Docker is running:
```bash
docker ps

# If error, start Docker service
sudo systemctl start docker  # Linux
# OR open Docker Desktop (Mac/Windows)

# Ensure your user has Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### "ModuleNotFoundError: No module named 'textual'"

Install Python dependencies:
```bash
pip install --user -r requirements.txt

# OR in virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

### "Environment not found"

Check the environment directory exists:
```bash
ls environments/

# Each environment should have:
# - .env file
# - docker-compose.yml file
```

### Scripts not executable

```bash
chmod +x envman.py opencode-connect.sh
chmod +x scripts/*.sh
```

## Next Steps

1. **Read the full documentation**: See `TUI-README.md` for complete feature list
2. **Explore your environments**: Use `./opencode-connect.sh --list`
3. **Try the TUI**: Run `./envman.py` once dependencies are installed
4. **Create more environments**: Each developer can have multiple isolated workspaces

## Getting Help

- **TUI Help**: Press `F5` or `?` in the TUI for keyboard shortcuts
- **Script Help**: Run any script with `--help` flag
- **Full Docs**: See `TUI-README.md` and `AGENTS.md`
- **Connection Helper Help**: `./opencode-connect.sh --help`

## What's Working Right Now

✅ **Remote Connection Helper** - Fully functional!
  - Interactive environment selection
  - List all environments with status
  - Copy/display connection commands
  - Direct connection to environments

✅ **Legacy Scripts** - All working in `scripts/` directory
  - Create environments
  - Manage (start/stop/status)
  - Validate configurations
  - Build and test

✅ **TUI Core** - Built and ready (needs dependencies installed)
  - Environment discovery
  - Status monitoring
  - Configuration parsing
  - Docker integration

## What's Next

The TUI application is fully coded and will provide:
- Real-time environment status dashboard
- Interactive environment creation wizard
- Configuration editor with validation
- Log viewer with filtering
- Start/stop/restart operations
- Build management
- And much more!

Just install the Python dependencies to use it:
```bash
pip install --user textual python-dotenv pyyaml docker
./envman.py
```

---

**Happy environment managing!** 🚀
