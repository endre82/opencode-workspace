# OpenCode Workspace — Architecture Reference

This document is a technical reference for understanding the complete architecture of OpenCode Workspace. Written for developers maintaining or extending the system.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────┐                │
│  │  TUI Application  (envman/app.py)               │                │
│  │  ┌─────────────┐  ┌──────────────┐              │                │
│  │  │ Dashboard   │  │ Creation     │              │                │
│  │  │ screen      │  │ Wizard       │              │                │
│  │  │             │  │ (4 steps)    │              │                │
│  │  └─────────────┘  └──────────────┘              │                │
│  │  ┌─────────────┐  ┌──────────────┐              │                │
│  │  │ Config      │  │ Logs screen  │              │                │
│  │  │ screen      │  │              │              │                │
│  │  └─────────────┘  └──────────────┘              │                │
│  │                                                  │                │
│  │  Services (discovery, docker, ngrok, config)   │                │
│  └─────────────────────────────────────────────────┘                │
│                            │                                         │
│  ┌────────────────────────┼────────────────────────┐                │
│  │                        │                        │                │
│  ▼                        ▼                        ▼                │
│ Docker daemon      ~/.opencode/         ~/.local/share/             │
│                    plugins/             opencode-workspace/         │
│                    skills/              logs/exceptions.log         │
│                    extensions/          ngrok/                      │
│                    User/                settings.json               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
           │
           │  docker compose, environment variables
           │
    ┌──────┴──────────────────────────────────────────┐
    │                                                   │
    ▼                                                   ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│   Docker Network             │  │  Shared Host Directory        │
│   opencode-network           │  │  ./shared/                    │
│   (bridge driver)            │  │                               │
└──────────────────────────────┘  │  • config/                    │
    │                             │  • auth/                      │
    ├─────────────┬───────────┐   │  • models/                    │
    │             │           │   │  • vscode/extensions          │
    ▼             ▼           ▼   │  • vscode/User                │
 ┌────────────┐ ┌────────────┐  │  • namespaces/                │
 │ Container  │ │ Container  │ ...└──────────────────────────────┘
 │  (env-1)   │ │  (env-2)   │
 │            │ │            │
 │ • opencode │ │ • opencode │
 │   server   │ │   server   │
 │ • code-srv │ │ • code-srv │
 │ • webui    │ │ • webui    │
 │ • meridian │ │ • meridian │  (optional)
 │   (opt)    │ │   (opt)    │
 └────────────┘ └────────────┘
```

**Key insight:** The TUI runs on the host and orchestrates Docker containers. Each container is isolated but shares certain resources (plugins, skills, VS Code extensions) and optional configuration (OpenCode config, auth credentials).

---

## Repository Layout

```
opencode-workspace/
│
├── envman.py                           # Entry point: run TUI
├── requirements.txt                    # Python dependencies
│
├── envman/                             # TUI application package
│   ├── app.py                          # Main Textual app, service initialization
│   ├── models/
│   │   └── environment.py              # Environment data model (name, status, ports, mounts)
│   ├── services/
│   │   ├── discovery.py                # Scans ./environments/, loads .env files, creates Environment objs
│   │   ├── docker.py                   # Docker client wrapper (status, start, stop, logs)
│   │   ├── creation.py                 # Creates env from template, substitutes variables
│   │   ├── config.py                   # Reads/writes .env files, parses key=value
│   │   ├── ngrok.py                    # Starts/stops ngrok process, polls 4040 API
│   │   ├── validation.py               # Input validation for wizard
│   │   └── logs.py                     # Container log streaming
│   ├── screens/
│   │   ├── dashboard.py                # Main env list, status, action menu
│   │   ├── creation/
│   │   │   └── wizard.py               # 4-step creation flow (name, workspace, mounts, server)
│   │   ├── config.py                   # Edit .env form, save to disk
│   │   ├── inspect.py                  # Container details (image, ports, networks)
│   │   ├── logs.py                     # Live log streaming with tail
│   │   ├── delete.py                   # Confirmation + docker compose down --volumes
│   │   └── modals/
│   │       ├── help.py                 # Keyboard shortcut reference
│   │       ├── copy_command.py         # Copy paste remote attach command
│   │       ├── tunnel.py               # ngrok tunnel UI
│   │       ├── confirm.py              # Generic yes/no dialog
│   │       └── progress.py             # Spinner during async tasks
│   ├── utils/
│   │   ├── exception_logger.py         # Global hook, JSON logging to ~/.local/share/opencode-workspace/logs/
│   │   ├── constants.py                # Shared constants (status values, port ranges, skip dirs)
│   │   ├── browser.py                  # Open URLs in default browser
│   │   └── exceptions.py               # Custom exception types
│   └── webui/
│       ├── app.py                      # FastAPI app (runs inside container)
│       ├── config.py                   # WebUI config (env vars, paths)
│       └── auth.py                     # HTTP Basic auth
│
├── base/                               # Docker base image (shared by all containers)
│   ├── Dockerfile                      # Ubuntu 24.04, dev user, Node.js, OpenCode, code-server
│   └── config/
│       ├── entrypoint.sh               # Container startup: code-srv → webui → meridian → opencode
│       └── healthcheck.sh              # Container health check
│
├── environments/                       # Per-environment directories
│   ├── template/
│   │   ├── .env.template               # Variable template for .env
│   │   └── docker-compose.yml.template # Variable template for docker-compose.yml
│   ├── my-project/
│   │   ├── workspace/                  # Project files (mounted to /workspace in container)
│   │   ├── opencode_config/            # Environment config data (mounted to ~/.local/share/opencode)
│   │   ├── opencode_project_config/    # Optional: project-mode opencode.jsonc (mounted rw)
│   │   ├── .env                        # Generated from template during creation
│   │   ├── docker-compose.yml          # Generated from template during creation
│   │   └── backups/                    # Config backups (created by ConfigScreen)
│   └── another-project/
│       └── (same structure)
│
├── shared/                             # Resources shared across all environments
│   ├── config/
│   │   └── opencode.jsonc              # Global OpenCode config (used in 'global' mode)
│   ├── auth/
│   │   └── auth.json                   # Shared auth credentials
│   ├── models/                         # (future) shared model cache
│   ├── namespaces/
│   │   └── global/                     # Shared namespace config
│   └── vscode/
│       ├── extensions/                 # Shared VS Code extensions (mounted rw)
│       └── User/                       # Shared VS Code user settings (mounted rw)
│
├── docs/
│   ├── README.md                       # Documentation index
│   ├── architecture/
│   │   └── README.md                   # This file
│   ├── features/                       # Feature implementation docs
│   ├── guides/                         # User guides
│   ├── bugfixes/                       # Bug fix technical docs
│   └── summaries/                      # Quick reference docs
│
├── tests/                              # Test scripts
│   ├── test_wizard.py
│   └── test_wizard_simple.py
│
└── scripts/                            # Utility scripts
```

---

## Host-Side Component Map

| Module | Responsibility | Notes |
|--------|------------------|-------|
| `app.py` | App lifecycle, service init, error handling | Initializes Docker, discovery, ngrok services; installs global exception hook |
| `models/environment.py` | Data model for an environment | Immutable snapshot: name, status, ports, mounts, config paths |
| `services/discovery.py` | Scans `./environments/`, loads `.env`, creates `Environment` objects | Called on app start and on refresh; skips `template`, `shared`, special dirs |
| `services/docker.py` | Docker client (via `docker-py` SDK) | `get_status()`, `start_container()`, `stop_container()`, `get_logs()`, `inspect_container()` |
| `services/creation.py` | Creates new environment from template | Substitutes `{{ENV_NAME}}` and all config vars; calls `_create_env_file()` and `_create_compose_file()` |
| `services/config.py` | Parses `.env` files (key=value lines) | Read mode: splits on `=`, handles quoted values; Write mode: preserves format |
| `services/ngrok.py` | Manages ngrok tunnel process | Writes per-service config to `~/.local/share/opencode-workspace/ngrok/`; polls `http://127.0.0.1:4040/api/tunnels` |
| `services/validation.py` | Input validation (name, port, etc.) | Called by wizard and config screen |
| `services/logs.py` | Container log streaming | Generator that yields log lines as they arrive |
| `screens/dashboard.py` | Main environment list, status, actions | Shows running/stopped status; action menu (s/x/l/c/d/t); 30-second auto-refresh |
| `screens/creation/wizard.py` | 4-step environment creation UI | Step 1: basic info; Step 2: workspace; Step 3: mounts; Step 4: server config; summary review |
| `screens/config.py` | Edit `.env` file via form | Loads current config; displays as editable form; save + backup on write |
| `screens/inspect.py` | Show container details (image, networks, ports, volumes) | Read-only inspection |
| `screens/logs.py` | Stream container logs in a scrollable pane | Real-time as container outputs |
| `screens/delete.py` | Confirmation dialog + `docker compose down --volumes` | Deletes dir if you confirm |
| `screens/modals/help.py` | Keyboard shortcut reference modal | Displayed by `?` key |
| `screens/modals/tunnel.py` | UI to start ngrok tunnel, display public URL | Modal with copy button |
| `utils/exception_logger.py` | Global hook, JSON logging to disk | Every uncaught exception logged to `~/.local/share/opencode-workspace/logs/exceptions.log` |
| `utils/constants.py` | Shared constants | Status values, port ranges, skip directories, status icons |
| `webui/app.py` | FastAPI app (runs *inside* each container) | Mounted read-only from host; shows service status, logs |

---

## Environment Lifecycle

```
CREATE (wizard)
   │
   ├─ User selects name (Step 1)
   ├─ User selects workspace type (Step 2)
   ├─ User selects volume mounts (Step 3)
   ├─ User configures server (Step 4)
   │
   ├─ Creation service validates
   ├─ mkdir ./environments/<name>/
   ├─ mkdir ./environments/<name>/workspace/ (if isolated)
   ├─ mkdir ./environments/<name>/opencode_config/
   │
   ├─ Substitute template variables
   ├─ Write .env file
   ├─ Write docker-compose.yml file
   │
   └─ Environment created ✅ (stopped state)
      │
      ▼
BUILD (optional, automatic on first start or on-demand)
   │
   ├─ docker compose build
   ├─ Base image + layer caching
   │
   └─ Image built ✅
      │
      ▼
START (s key)
   │
   ├─ docker compose up -d
   ├─ Container starts
   ├─ entrypoint.sh runs as dev user:
   │  ├─ Start code-server on $CODE_SERVER_PORT
   │  ├─ Start Web UI on $WEBUI_PORT
   │  ├─ Setup ~/.claude-local overlay (if MERIDIAN_ENABLED)
   │  ├─ Start Meridian proxy on port 3456 (if MERIDIAN_ENABLED)
   │  └─ Start OpenCode server on $OPENCODE_SERVER_PORT
   │
   ├─ Docker health check polls every 30s
   │
   └─ Container running ✅
      │
      ├─ (various operations: view logs, edit config, etc.)
      │
      ▼
STOP (x key)
   │
   ├─ docker compose down (stops + removes container)
   ├─ Volumes persist
   │
   └─ Container stopped ✅
      │
      ├─ (can start again)
      │
      ▼
DELETE (d key)
   │
   ├─ Confirmation dialog
   ├─ docker compose down --volumes
   ├─ rm -rf ./environments/<name>/
   │
   └─ Environment deleted ✅ (no recovery)
```

---

## Configuration System

### Three OpenCode Config Modes

When creating an environment (Step 3 of wizard), you choose where OpenCode reads its configuration:

#### 1. **Host Mode** (read-only)
- **Config source:** `~/.opencode/opencode.jsonc`
- **Auth source:** `~/.local/share/opencode/auth.json`
- **Mount:** Both mounted read-only into container
- **Use case:** One personal config, used by all environments
- **Mutable:** Changes on host are immediately visible in container; you edit on host, not in UI
- **.env entries:**
  ```
  OPENCODE_CONFIG_MODE=host
  OPENCODE_JSONC_SOURCE=~/.opencode/opencode.jsonc
  OPENCODE_AUTH_SOURCE=~/.local/share/opencode/auth.json
  ```

#### 2. **Global Mode** (read-only)
- **Config source:** `./shared/config/opencode.jsonc`
- **Auth source:** `./shared/auth/auth.json`
- **Mount:** Both mounted read-only into container
- **Use case:** Shared workspace config across all environments
- **Mutable:** Shared by all envs; edit in `./shared/config/` on host
- **.env entries:**
  ```
  OPENCODE_CONFIG_MODE=global
  OPENCODE_JSONC_SOURCE=../../shared/config/opencode.jsonc
  OPENCODE_AUTH_SOURCE=../../shared/auth/auth.json
  ```

#### 3. **Project Mode** (read-write)
- **Config source:** `./environments/<name>/opencode_project_config/opencode.jsonc`
- **Auth source:** Inside container data dir (not shared)
- **Mount:** Config mounted read-write; auth stored per-env
- **Use case:** Per-environment configuration, can diverge across envs
- **Mutable:** Can edit via `ConfigScreen` or directly on host
- **.env entries:**
  ```
  OPENCODE_CONFIG_MODE=project
  OPENCODE_JSONC_SOURCE=./opencode_project_config/opencode.jsonc
  OPENCODE_AUTH_SOURCE=
  ```

### Variable Substitution Pipeline

**Wizard** → **CreationService** → **.env.template** → **.env**

1. User fills wizard form (name, ports, workspace type, etc.)
2. `CreationService.create_environment(config: Dict)` called with form data
3. `.env.template` is read
4. All `old_value=...` lines replaced with `new_value=...` via:
   - Direct string replacement for most values (e.g., `USER_ID=1000` → `USER_ID=1001`)
   - Regex with `re.MULTILINE` for values that could be substrings (e.g., `CODE_SERVER_PASSWORD=` is a substring of `OPENCODE_SERVER_PASSWORD=`)
5. Result written to `.env` in the environment directory

**Key keys in `.env`:**

| Key | Who sets it | When mutable | Notes |
|-----|-------------|--------------|-------|
| `USER_ID`, `GROUP_ID` | Wizard Step 1 | ConfigScreen | Must rebuild to take effect |
| `WORKSPACE_DIR` | Wizard Step 2 | ConfigScreen | Relative or absolute path |
| `WORKTREE_DIR` | Wizard Step 2 | ConfigScreen | Optional; toggle in Step 3 |
| `SSH_MODE`, `SSH_CONFIG` | Wizard Step 3 | ConfigScreen (read-only) | 'default' or 'project' |
| `OPENCODE_CONFIG_MODE`, `OPENCODE_JSONC_SOURCE` | Wizard Step 3 | Not mutable in UI | Set at creation; changing requires recreation |
| `OPENCODE_SERVER_PORT` | Wizard Step 4, auto-assigned | ConfigScreen | Must rebuild to take effect |
| `OPENCODE_SERVER_USERNAME`, `OPENCODE_SERVER_PASSWORD` | Wizard Step 4 | ConfigScreen | Can be changed any time |
| `MERIDIAN_ENABLED` | Wizard Step 3 | ConfigScreen (read-only) | Set at creation; affects mounts |
| `VSCODE_PROFILE_SHARING` | Wizard Step 3 | ConfigScreen (read-only) | Set at creation; default true |

---

## Volume Mount Map

Every mount in `docker-compose.yml`:

| Source (Host) | Container Destination | Mode | Always On? | Feature | Notes |
|---|---|---|---|---|---|
| `/etc/localtime` | `/etc/localtime` | ro | ✅ | System | Timezone sync |
| `${WORKSPACE_DIR}` | `/home/dev/workspace` | rw | ✅ | Core | Project files |
| `${OPENCODE_ENV_CONFIG}` (e.g., `./opencode_config`) | `/home/dev/.local/share/opencode` | rw | ✅ | Core | Container-specific config data |
| `../../base/config/entrypoint.sh` | `/entrypoint.sh` | ro | ✅ | Core | Startup script |
| `../../base/config/healthcheck.sh` | `/healthcheck.sh` | ro | ✅ | Core | Health check script |
| `../../envman` | `/home/dev/envman` | ro | ✅ | Web UI | FastAPI app (host-side mounted) |
| `${NAMESPACE_GLOBAL_DIR}` | `/home/dev/.opencode/namespaces/global` | ro | ✅ | Core | OpenCode namespace config |
| `${OPENCODE_PLUGINS_DIR}` (e.g., `~/.opencode/plugins`) | `/home/dev/.opencode/plugins` | ro | ✅ | Plugins | Shared plugins across envs |
| `${OPENCODE_SKILLS_DIR}` (e.g., `~/.opencode/skills`) | `/home/dev/.opencode/skills` | ro | ✅ | Skills | Shared skills across envs |
| `${SSH_CONFIG}` (from SSH_MODE) | `/home/dev/.ssh` | ro | ✅ | SSH | Git/SSH access |
| `${MERIDIAN_DIR}` | `/opt/meridian` | ro | ❌ | Meridian | `@rynfar/meridian` npm package (Meridian_ENABLED=true) |
| `${CLAUDE_AUTH_DIR}` (e.g., `~/.claude`) | `/home/dev/.claude` | ro | ❌ | Meridian | Claude auth (read-only overlay) |
| `${OPENCODE_JSONC_SOURCE}` (host or global mode) | `/home/dev/.opencode/opencode.jsonc` | ro | ❌ | Config | Host or global mode only |
| `${OPENCODE_AUTH_SOURCE}` (host or global mode) | `/home/dev/.local/share/opencode/auth.json` | ro | ❌ | Config | Host or global mode only |
| `${OPENCODE_JSONC_SOURCE}` (project mode) | `/home/dev/.opencode/opencode.jsonc` | rw | ❌ | Config | Project mode only |
| `${WORKTREE_DIR}` | `/home/dev/.local/share/opencode/worktree` | rw | ❌ | Worktrees | Mounted only if enabled in Step 3 |
| `${VSCODE_SHARED_EXTENSIONS_DIR}` (e.g., `shared/vscode/extensions`) | `/home/dev/.local/share/code-server/extensions` | rw | ❌ | VS Code | Shared VS Code extensions (enabled by default) |
| `${VSCODE_SHARED_USER_DIR}` (e.g., `shared/vscode/User`) | `/home/dev/.local/share/code-server/User` | rw | ❌ | VS Code | Shared VS Code settings (enabled by default) |

---

## Port Allocation

Every container gets three ports (all configurable, but following a predictable pattern):

```
Base port: OPENCODE_SERVER_PORT = N  (e.g., 4100, 4101, 4102, ...)
  ├─ 4100 (OpenCode server)
  ├─ 8100 (code-server / VSCode, = N+4000)
  └─ 9100 (Web UI, = N+5000)

Next env: N+1 (e.g., 4101)
  ├─ 4101 (OpenCode server)
  ├─ 8101 (code-server / VSCode)
  └─ 9101 (Web UI)
```

**Port assignment algorithm:**
1. `CreationService.get_used_ports()` scans all `.env` files for existing `OPENCODE_SERVER_PORT=...`
2. `CreationService.find_next_available_port()` starts at 4096, increments until a free port is found
3. All three ports are auto-assigned based on this base port

**Why this scheme:**
- Default base 4096 leaves 1–4095 for system and other apps
- Up to 100 environments before hitting 5000 (arbitrary limit; expandable)
- Formula is simple and predictable for debugging

---

## In-Container Startup Sequence

When container starts, `entrypoint.sh` runs as the `dev` user (not root) and follows this order:

```
1. INITIALIZE DIRECTORIES
   └─ mkdir -p ~/.local/share/opencode ~/.config/code-server

2. START CODE-SERVER (VSCode in browser)
   ├─ if CODE_SERVER_ENABLED=true
   ├─ Generate ~/.config/code-server/config.yaml
   ├─ nohup code-server /home/dev/workspace > ~/.local/share/opencode/code-server.log 2>&1 &
   └─ Log output to ~/.local/share/opencode/code-server.log

3. START WEB MANAGEMENT UI (FastAPI)
   ├─ if WEBUI_ENABLED=true
   ├─ Export WEBUI_HOST, WEBUI_PORT, ENV_NAME, CONTAINER_NAME
   ├─ nohup python3 -m envman.webui.app > ~/.local/share/opencode/webui.log 2>&1 &
   └─ Log output to ~/.local/share/opencode/webui.log

4. SETUP CLAUDE CONFIG OVERLAY (for Meridian session persistence)
   ├─ if MERIDIAN_ENABLED=true
   ├─ mkdir -p ~/.claude-local
   ├─ cp -a ~/.claude/. ~/.claude-local/   (initial copy)
   ├─ ln -sf ~/.claude/.credentials.json ~/.claude-local/.credentials.json   (symlink for sync)
   ├─ export CLAUDE_CONFIG_DIR=/home/dev/.claude-local   (tell SDK to use overlay)
   └─ Reason: ~/.claude is mounted read-only; overlay is writable for session persistence

5. START MERIDIAN PROXY (in-container Anthropic API proxy)
   ├─ if MERIDIAN_ENABLED=true
   ├─ Check /opt/meridian/dist/cli.js exists
   ├─ nohup node /opt/meridian/dist/cli.js > ~/.local/share/opencode/meridian.log 2>&1 &
   ├─ Listens on port 3456 (CLAUDE_PROXY_PORT)
   └─ Log output to ~/.local/share/opencode/meridian.log

6. START OPENCODE SERVER
   ├─ if OPENCODE_SERVER_ENABLED=true
   ├─ Build command: opencode serve --hostname $OPENCODE_SERVER_HOST --port $OPENCODE_SERVER_PORT
   ├─ Optional --cors flag if OPENCODE_SERVER_CORS is set
   ├─ Run in background (& at end)
   ├─ Wait 5 seconds for startup
   ├─ Verify with curl to /global/health endpoint
   └─ Log to console (captured by docker logs)

7. KEEP CONTAINER ALIVE
   └─ tail -f /dev/null   (prevents container from exiting)
```

**Key points:**
- All long-running processes started in background (`nohup ... &`)
- Logs captured to `~/.local/share/opencode/` for inspection via `logs.py`
- `CLAUDE_CONFIG_DIR` environment variable essential for Meridian session persistence
- entrypoint runs as `dev` user (set in `docker-compose.yml` via `user:` directive)
- No `chown` commands in entrypoint (already run as correct user)

---

## Optional Features Reference

### Meridian Proxy (in-container Anthropic API proxy)

**What it does:**
- Intercepts Anthropic API calls (e.g., from `opencode serve`) to a local HTTP endpoint
- Forwards them through Claude's authentication (reading `~/.claude/` credentials)
- Allows OpenCode to use Claude without hardcoding API keys

**Configuration:**
- **Wizard Step 3:** Toggle switch "In-container" under "Anthropic Proxy (Meridian)"
- **If enabled:**
  - `.env` variables: `MERIDIAN_ENABLED=true`, `MERIDIAN_DIR=/path/to/meridian`, `CLAUDE_AUTH_DIR=~/.claude`
  - `docker-compose.yml` mounts: `/opt/meridian`, `~/.claude` (both read-only)
  - `entrypoint.sh`: Sets up `~/.claude-local` overlay, starts `node /opt/meridian/dist/cli.js`
  - Listens on `http://127.0.0.1:3456`

**Session persistence pattern (overlay):**
```
Host:                     Container:
~/.claude/ (ro)    ┐
                   ├──→ /home/dev/.claude (mounted ro)
                   │    └─ Can't persist token refreshes
                   │
                   └──→ /home/dev/.claude-local (writable overlay)
                        ├─ cp -a ~/.claude/. (initial sync)
                        └─ ln -sf ~/.claude/.credentials.json (symlink for token sync)
```

**Why the overlay:** Claude SDK subprocess runs in container and needs to refresh auth tokens. Since `/home/dev/.claude` is read-only, we create a writable `~/.claude-local` and symlink the credentials file so token updates on host are visible to container.

**Discovery:**
- `CreationService.resolve_meridian_dir()` calls `npm root -g` to find `@rynfar/meridian` package location
- If not found, wizard shows warning; you must set `MERIDIAN_DIR` manually in `.env` after creation

---

### VS Code Profile Sharing (shared extensions + settings)

**What it does:**
- Shares VS Code extensions across all environments (install once, use everywhere)
- Shares VS Code user settings and keybindings (same config in all envs)

**Configuration:**
- **Wizard Step 3:** Toggle switch "Share profile" under "VS Code Profile"
- **Default:** Enabled (toggle to disable for per-environment extensions)
- **If enabled:**
  - `.env` variables: `VSCODE_PROFILE_SHARING=true`, `VSCODE_SHARED_EXTENSIONS_DIR=../../shared/vscode/extensions`, `VSCODE_SHARED_USER_DIR=../../shared/vscode/User`
  - `docker-compose.yml` mounts: both as read-write
  - `shared/vscode/extensions/` → `/home/dev/.local/share/code-server/extensions`
  - `shared/vscode/User/` → `/home/dev/.local/share/code-server/User`
  - Created by `CreationService.create_environment()` if not already present

**Behavior:**
- When you install an extension in one environment's VS Code, it goes to `shared/vscode/extensions/`
- Other environments automatically have that extension (same mount point)
- Disabling the toggle makes each environment have its own extensions (per-env `~/.local/share/code-server/extensions`)

---

### ngrok Tunneling (on-demand internet access)

**What it does:**
- Creates a public HTTPS tunnel to your local OpenCode or VS Code server
- Allows remote access from anywhere on the internet
- Free tier: one tunnel at a time

**Configuration:**
- **From dashboard:** Select environment, press `t`, choose service (OpenCode or VSCode), click "Start Tunnel"
- **NgrokService:**
  - `is_available()`: checks if `ngrok` binary exists in `$PATH`
  - `start(env_name, service, port)`: writes config, starts process, polls API
  - `stop()`: terminates process
  - `get_status()`: returns current tunnel info (env_name, service, URL, PID)

**Process lifecycle:**
```
start(env_name="my-proj", service="opencode", port=4100)
   │
   ├─ Write ~/.local/share/opencode-workspace/ngrok/my-proj-opencode.yml
   │  (contains: tunnels.opencode.addr=4100, tunnels.opencode.proto=http)
   │
   ├─ Spawn: ngrok start --all --config ~/.config/ngrok/ngrok.yml --config ~/.local/share/.../ngrok/my-proj-opencode.yml
   │  (--all loads all tunnels in all config files)
   │
   ├─ Store process object and metadata (env_name, service, PID)
   │
   ├─ Poll http://127.0.0.1:4040/api/tunnels until tunnel appears
   │  (ngrok API endpoint; returns JSON with public_url)
   │
   ├─ Extract public URL: https://abc.ngrok-free.app
   │
   └─ Display in TUI modal; user can copy
```

**Stopping:** `stop()` terminates process; metadata cleared.

**Free tier limitation:** One tunnel at a time. If you try to tunnel a different service, the old one is stopped first.

---

## Exception Logging System

**Location:** `~/.local/share/opencode-workspace/logs/exceptions.log`

**Format:** Each line is a single JSON object:
```json
{
  "timestamp": "2026-03-17T00:59:12.386334",
  "exception_type": "ValueError",
  "exception_message": "invalid literal...",
  "stack_trace": [{"file": "...", "line": 123, "function": "func", "code": "..."}],
  "context": {"screen": "Dashboard", "step": 1, "user_action": "clicked_refresh"},
  "system_info": {"python_version": "3.12", "platform": "Linux-..."},
  "process_info": {"pid": "app.py", "cwd": "/home/endre/opencode-workspace"}
}
```

**How to use:**
1. User encounters an exception; TUI catches it and logs to disk
2. Run: `cat ~/.local/share/opencode-workspace/logs/exceptions.log | tail -1 | python3 -m json.tool`
3. Full stack trace, context, and environment info available for debugging

**Context tracking:**
- `set_context(screen="Dashboard")` sets thread-local context
- Called in `on_mount()` of every screen
- Automatically included in exception log

---

## Summary

The OpenCode Workspace architecture follows a **host-TUI + containerized-workspaces** pattern:

1. **Host side:** Python/Textual TUI manages discovery, creation, and orchestration of Docker containers
2. **Container runtime:** Ubuntu 24.04 with dev user, OpenCode, VSCode in browser, optional Meridian proxy
3. **Configuration:** Three modes (host/global/project) + template substitution pipeline
4. **Volumes:** Shared resources (plugins, skills, VS Code profile) + isolated per-env config
5. **Ports:** Auto-assigned formula-based allocation (base N, N+4000, N+5000)
6. **Services:** code-server, Web UI, Meridian (optional), OpenCode server started in sequence by entrypoint.sh

This design enables **isolated development environments with shared tooling and configuration**.
