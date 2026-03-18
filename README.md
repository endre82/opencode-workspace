# OpenCode Workspace Environments

Separated development environments for OpenCode with Ubuntu 24.04.

**NEW:** Remote development with code-server (VSCode in browser), Web Management UI, and namespace-based agent/skill sharing!

## 🎯 Key Features

- **🌐 Remote IDE Access**: Full VSCode experience in your browser
- **📊 Web Management UI**: Browser-based dashboard for monitoring services
- **📦 Namespace System**: Share agents, skills, and workflows across environments
- **🖥️ TUI Management**: Modern terminal UI for environment management
- **🔒 Isolated Environments**: Each developer gets their own containerized workspace
- **📱 Multi-Device Access**: Code from laptop, tablet, or phone on your LAN

## Quick Start

**New to Remote Development?** → [REMOTE_DEV_GUIDE.md](docs/user-guides/REMOTE_DEV_GUIDE.md)

**New Users:** Start here → [QUICKSTART.md](docs/user-guides/QUICKSTART.md)

**For the TUI:** See [TUI-README.md](docs/user-guides/TUI-README.md) for complete documentation.

### Immediate Use (No Installation Required)

```bash
# Create new environment with code-server
./scripts/create-environment.sh my-env

# Build and start
cd environments/my-env
docker compose build
docker compose up -d

# Access VSCode in browser
open http://localhost:8096
# (Password shown during creation)
```

### Full TUI Experience

```bash
# Install Python dependencies
pip install --user -r requirements.txt

# Launch the TUI
./envman.py
```

## Project Structure

```
opencode-workspace/
├── envman.py                  # 🆕 TUI Application (executable)
├── opencode-connect.sh        # 🆕 Remote connection helper (executable)
├── requirements.txt           # 🆕 Python dependencies
│
├── docs/                      # 📚 Documentation
│   ├── README.md             # Documentation index
│   ├── user-guides/          # User documentation
│   ├── overview/             # Project overview
│   ├── phases/               # Implementation phases
│   ├── technical/            # Technical reference
│   └── development/          # Contributor guides
│
├── envman/                    # 🆕 TUI package (812 lines)
│   ├── app.py                # Main Textual application
│   ├── models/               # Data models
│   ├── screens/              # UI screens
│   ├── services/             # Business logic
│   ├── utils/                # Utilities
│   └── widgets/              # UI components
│
├── scripts/                   # Legacy scripts (still working!)
│   ├── create-environment.sh
│   ├── manage-environments.sh
│   └── ... (7 scripts total)
│
├── base/                      # Shared base image
├── environments/              # Environment instances
│   ├── template/             # Template for new environments
│   └── <env-name>/           # Individual environments
└── shared/                    # Shared resources
    ├── namespaces/           # 🆕 Shared agents, skills, workflows
    ├── config/               # Shared OpenCode config
    └── models/               # Shared AI models
```

## Features

### 🆕 Remote Development (code-server)

- **VSCode in Browser**: Full IDE accessible from any device
- **Multi-Device**: Code from laptop, tablet, or phone
- **Local Network**: Access environments from any device on your LAN
- **Persistent Settings**: VSCode configuration persists per environment
- **Extension Support**: Install any VSCode extension

**Quick Access**: `http://localhost:8096` (port auto-assigned per environment)

### 🆕 Namespace System

- **Shared Agents**: Company-wide OpenCode agents for specialized tasks
- **Shared Skills**: Reusable instruction sets and workflows  
- **Team Workflows**: Standardized processes and checklists
- **Knowledge Base**: Shared documentation and context
- **Version Control**: Git-backed namespace versioning
- **Read-Only Mounts**: Safe sharing without accidental modifications

**Location**: `shared/namespaces/global/{agents,skills,workflows,context}/`

### TUI Application

- Interactive dashboard with real-time status
- Environment creation wizard
- Configuration management
- Log viewing and filtering
- Docker integration
- Keyboard-driven navigation

### Remote Connection Helper

- Interactive environment selection
- List all environments with status
- Display connection commands
- Direct connection to environments

### Legacy Scripts (Still Work!)

All original scripts preserved in `scripts/` directory for automation and CI/CD.

## Three Ways to Manage Environments

### 1. TUI Application (Recommended)

```bash
pip install --user -r requirements.txt
./envman.py
```

### 2. Remote Connection Helper

```bash
./opencode-connect.sh --list
./opencode-connect.sh vienna-agentic-vibes
```

### 3. Legacy Scripts

```bash
./scripts/create-environment.sh my-env
./scripts/manage-environments.sh status
```

## Exception Logging System

The TUI includes a comprehensive exception logging system that automatically captures all uncaught exceptions with full context. This enables AI agents to debug and fix issues with complete information.

### Log File Location
```
~/.local/share/opencode-workspace/logs/exceptions.log
```

### Key Features
- **Automatic Capture**: Global exception hook catches all uncaught exceptions
- **Rich Context**: Includes screen, step, user action, environment name
- **Full Stack Traces**: Multi-level stack traces with file paths and line numbers
- **System Information**: Python version, platform, Docker status
- **JSON Format**: Single-line JSON for easy parsing by AI
- **Log Rotation**: 10MB max per file, keeps 5 backup files

### Using the Exception Logger
When reporting issues, simply provide the latest JSON entry from the log file:
```bash
cat ~/.local/share/opencode-workspace/logs/exceptions.log | tail -1 | python3 -m json.tool
```

This eliminates the need for back-and-forth questions about error messages, stack traces, and system environment details.

## Traditional Setup (Still Valid)

1. **Setup shared network:**
   ```bash
   ./scripts/setup-network.sh
   ```

2. **Build base image:**
   ```bash
   cd base
   docker build -t opencode-base:latest .
   ```

3. **Create and start an environment:**
   ```bash
   cd environments/dev1
   docker-compose build
   docker-compose up -d
   ```

4. **Access the environment:**
   ```bash
   docker-compose exec opencode-dev1 bash
   ```

## Managing Environments

Use the management script for common tasks:

```bash
# List all environments
./manage-environments.sh list

# Build all environments
./manage-environments.sh build-all

# Start all environments
./manage-environments.sh start-all

# Check status
./manage-environments.sh status

# Execute command in environment
./manage-environments.sh exec dev1 bash

# View logs
./manage-environments.sh logs dev1
```

## Creating New Environments

Use the automated script to create new environments:

```bash
# Create a new environment with interactive setup
./create-environment.sh dev3

# The script will:
# 1. Prompt for username (default: "opencode")
# 2. Prompt for password (generates random if empty)
# 3. Create all required directories
# 4. Assign unique UID/GID and port
# 5. Generate configuration files

# Build and start
cd environments/dev3
docker compose build
docker compose up -d
```

The script automatically:
- Assigns unique user ID (1000, 1001, 1002...)
- Assigns unique server port (4096, 4097, 4098...)
- Sets proper container naming and hostname
- Creates required directories (workspace, opencode_config, shared/config, shared/models)
- Configures server credentials

## Environment Configuration

Each environment has:
- Own `docker-compose.yml` file (generated from template)
- Own `.env` file with environment variables (generated from template)
- Own `workspace/` directory (isolated workspace)
- Own `opencode_config/` directory (per-environment config)
- Unique user ID to avoid permission conflicts
- Unique container name and hostname
- Unique OpenCode server port (4096, 4097, 4098...)
- Configurable username/password authentication

## Shared Resources

- `shared/config/` - Shared OpenCode configuration (read-write)
- `shared/models/` - Shared AI models (read-only)
- `shared/auth/` - **Shared provider credentials (auth.json)** - Share API keys across all environments
- `opencode-network` - Shared Docker network for inter-container communication

### Shared Provider Credentials

Provider connections (GitHub Copilot, DeepSeek, etc.) can be shared across environments while keeping sessions isolated:

**Setup:**
1. Place your `auth.json` in `shared/auth/auth.json`
2. Enable in environment `.env`:
   ```bash
   MOUNT_SHARED_AUTH=true
   SHARED_AUTH_CONFIG=../../shared/auth/auth.json
   ```
3. The auth file is mounted read-only to `/home/dev/.local/share/opencode/auth.json`

**Benefits:**
- **Shared credentials**: All environments use the same provider authentication
- **Isolated sessions**: Each environment maintains its own session data, logs, and worktrees
- **Single source of truth**: Update credentials once, apply to all environments
- **Read-only mount**: Prevents accidental credential modification

**Example auth.json structure:**
```json
{
  "github-copilot": {
    "type": "oauth",
    "refresh": "gho_...",
    "access": "gho_...",
    "expires": 0
  },
  "deepseek": {
    "type": "api",
    "key": "sk-..."
  }
}
```

## Volume Mounts

Each environment mounts:
- `./workspace` → `/home/dev/workspace` (read-write, isolated)
- `~/.config/opencode` → `/home/dev/.config/opencode` (read-only, host config)
- `./opencode_config` → `/home/dev/.local/share/opencode` (read-write, per-environment)
- `/etc/localtime` → `/etc/localtime` (read-only, time sync)
- `./worktree` → `/home/dev/.local/share/opencode/worktree` (read-write, optional, for VSCode access to git worktrees)
- `../../shared/auth/auth.json` → `/home/dev/.local/share/opencode/auth.json` (read-only, optional, shared provider credentials)

### Git Worktree Integration

OpenCode creates git worktrees inside containers at `/home/dev/.local/share/opencode/worktree/`. To make these accessible in VSCode:

1. **Add to `.env`:**
   ```bash
   WORKTREE_DIR=./worktree
   ```

2. **Add to `docker-compose.yml` volumes:**
   ```yaml
   volumes:
     - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw
   ```

3. **Create directory and restart:**
   ```bash
   mkdir -p ./worktree
   docker compose down && docker compose up -d
   ```

Worktrees appear in `environments/<env-name>/worktree/` and can be opened directly in VSCode. This enables quick context switching between main workspace and worktree branches.

**Example (vienna-agentic-vibes pattern):**
```bash
# Worktrees are located at:
environments/vienna-agentic-vibes/worktree/a958075e.../branch-name/

# Open in VSCode:
code environments/vienna-agentic-vibes/worktree/a958075e.../branch-name/

# Or create symlinks in workspace root for easier access
```

## Server Mode

Each environment runs OpenCode in server mode by default, exposing an HTTP API:

```bash
# Connect via OpenCode TUI
OPENCODE_SERVER_USERNAME=opencode OPENCODE_SERVER_PASSWORD=<your-password> opencode attach http://localhost:<port>

# View API documentation
http://localhost:4096/doc

# Health check endpoint
http://localhost:4096/global/health
```

### Server Configuration (in .env):
- `OPENCODE_SERVER_ENABLED=true` - Enable/disable server mode
- `OPENCODE_SERVER_PORT=4096` - Server port (auto-incremented)
- `OPENCODE_SERVER_USERNAME=opencode` - Basic auth username (configurable)
- `OPENCODE_SERVER_PASSWORD=` - **Required**: Set a secure password
- `OPENCODE_SERVER_CORS=` - Optional CORS origins

## Validation

Validate an environment:
```bash
./validate-environment.sh dev1
```

## Updating Existing Environments

Update an existing environment to new template format:
```bash
./update-environment.sh dev1
```

This script:
- Creates backups of existing configuration
- Preserves existing UID/GID and port
- Updates to new template format
- Creates missing directories
- Prompts for username/password updates

## 📚 Documentation

Complete documentation is available in the [docs/](docs/) directory:

- **[Documentation Index](docs/README.md)** - Complete navigation guide
- **[User Guides](docs/user-guides/)** - Installation, quickstart, TUI, and remote development
- **[Project Overview](docs/overview/)** - Vision, roadmap, and architecture
- **[Implementation Phases](docs/phases/)** - Completed development phases
- **[Technical Reference](docs/technical/)** - Deep technical documentation

## Notes

- Each environment runs in its own container with isolated workspace
- User IDs are unique per environment to avoid permission issues
- The base image is built once and reused by all environments
- Shared resources reduce duplication and improve consistency
EOF

# Create environment-specific README
for env in dev1 dev2; do
  cat > environments/${env}/README.md << EOF
# ${env} Environment

This is an isolated OpenCode development environment for ${env}.

## Quick Start

1. **Build the environment:**
   \`\`\`bash
   docker-compose build
   \`\`\`

2. **Start the environment:**
   \`\`\`bash
   docker-compose up -d
   \`\`\`

3. **Access the environment:**
   \`\`\`bash
   docker-compose exec opencode-${env} bash
   \`\`\`

4. **Stop the environment:**
   \`\`\`bash
   docker-compose down
   \`\`\`

## Configuration

- **User ID:** $(grep USER_ID .env | cut -d= -f2)
- **Group ID:** $(grep GROUP_ID .env | cut -d= -f2)
- **Container Name:** opencode-${env}
- **Hostname:** opencode-${env}
- **Workspace:** ./workspace/ (mounted to /home/dev/workspace)

## Files

- \`docker-compose.yml\` - Container configuration
- \`.env\` - Environment variables
- \`workspace/\` - Developer workspace (persistent)

## Network

This environment connects to the shared \`opencode-network\`.
Other environments can be accessed by hostname:
- \`opencode-dev1.opencode.local\`
- \`opencode-dev2.opencode.local\`

## Validation

Run validation from project root:
\`\`\`bash
./validate-environment.sh ${env}
\`\`\`

