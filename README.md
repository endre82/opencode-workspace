# OpenCode Workspace Environments

Separated development environments for OpenCode with Ubuntu 24.04.

## Project Structure

```
opencode-workspace/
├── base/              # Shared base image configuration
├── environments/      # Individual developer environments
│   ├── dev1/         # Developer 1 environment
│   ├── dev2/         # Developer 2 environment
│   └── template/     # Template for new environments
└── shared/           # Shared resources
```

## Quick Start

1. **Setup shared network:**
   ```bash
   ./setup-network.sh
   ```

2. **Build base image:**
   ```bash
   cd base
   docker build -t opencode-base:latest .
   ```

3. **Build and start an environment:**
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
- `opencode-network` - Shared Docker network for inter-container communication

## Volume Mounts

Each environment mounts:
- `./workspace` → `/home/dev/workspace` (read-write, isolated)
- `~/.config/opencode` → `/home/dev/.config/opencode` (read-only, host config)
- `./opencode_config` → `/home/dev/.local/share/opencode` (read-write, per-environment)
- `/etc/localtime` → `/etc/localtime` (read-only, time sync)

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

