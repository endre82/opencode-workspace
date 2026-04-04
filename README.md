# OpenCode Workspace

A **management system for multiple isolated development environments**, each running AI-assisted coding in a containerized workspace.

Think of it as a **personal developer laptop farm** — easily create, manage, and switch between different development environments, each with its own OpenCode instance, VSCode, and workspace. Work on multiple projects simultaneously without interference, or spin up fresh environments for experimentation.

## The Problem It Solves

- **No more conflicts**: Multiple projects can coexist without fighting over dependencies, config, or extensions
- **Easy context switching**: Work on a different project in seconds (just start a new environment)
- **Clean isolation**: Accidentally break something? Delete the environment and start fresh
- **Remote access**: Code from anywhere on your network (browser-based VSCode)
- **Hands-off management**: Simple terminal UI (or command line) to create, start, stop, and manage everything

## Key Features

- **🌐 Browser-based coding** — VSCode in your browser, access from any device on your network
- **🖥️ Simple management** — Terminal UI to create, start, stop, and delete environments with a few keypresses
- **🔒 Full isolation** — Each environment has its own workspace, settings, and AI assistant
- **🚀 Instant setup** — Create a new environment in minutes with an interactive wizard
- **📊 Live monitoring** — Dashboard shows status of all environments at a glance
- **🔐 Secure local network** — Access from any device on your LAN with password protection
- **📦 Shared resources** — Settings, plugins, and credentials can be shared across environments

## 🎨 [Visual Overview](overview.html)

Want to see the architecture and vision in an interactive visualization? **[Open the fancy overview →](overview.html)**

## Quick Start

### 1. Install and Launch

```bash
pip install --user -r requirements.txt
./envman.py
```

This opens a terminal dashboard. Press `n` to create a new environment.

### 2. Create an Environment

The interactive wizard will ask for:
- Name (e.g., `my-project`)
- Ports (auto-assigned)
- Workspace location (optional)
- OpenCode configuration mode

### 3. Start Coding

Press `s` to start the environment, then:
- Press `w` to open the OpenCode web UI
- Press `v` to open VSCode in your browser
- Or SSH in with the connection command

## Dashboard Commands

From the environment list, just press a key:

| Key | Action |
|-----|--------|
| `n` | Create new environment |
| `s` | Start environment |
| `x` | Stop environment |
| `r` | Restart |
| `b` | Build/rebuild |
| `l` | View live logs |
| `c` | Edit configuration |
| `d` | Delete environment |
| `w` | Open OpenCode web UI |
| `v` | Open VSCode in browser |
| `?` | Help |

## What's Inside Each Environment

Each environment is a containerized workspace containing:
- **OpenCode** — an AI coding assistant
- **VSCode** — accessible in your browser for remote coding
- **Linux shell** — for command-line tools
- **Your workspace** — isolated project files that persist between restarts
- **Shared config** — optional shared settings, plugins, and credentials across all environments

## Common Workflows

### Work on Multiple Projects
```
1. Create environment "project-a" → do work → stop it
2. Create environment "project-b" → do work → stop it
3. Switch back to "project-a" → start it → continue work
```

### Experiment Safely
```
1. Create "experiment" environment
2. Try something risky
3. If it breaks → delete environment → recreate clean copy
```

### Share Tools Across Projects
```
1. Install a plugin or skill once in shared location
2. All environments automatically have access
3. Update once, used everywhere
```

### Collaborate Remotely
```
1. Peer connects to your environment's VSCode URL
2. They can code in real-time in their browser
3. No installation needed on their machine
```

## Managing Multiple Environments

The dashboard shows all your environments at once:
- ✅ **Running** environments (green)
- ⏸️ **Stopped** environments (gray)
- 🔗 **Tunneled** environments (with public internet access)

Switch between any of them instantly by pressing `s` (start) or `x` (stop).

## Documentation

- **New to this?** → [QUICKSTART.md](docs/user-guides/QUICKSTART.md)
- **Want remote access?** → [REMOTE_DEV_GUIDE.md](docs/user-guides/REMOTE_DEV_GUIDE.md)
- **Terminal UI guide** → [TUI-README.md](docs/user-guides/TUI-README.md)
- **Full docs** → [docs/README.md](docs/README.md)

## Project Structure

```
opencode-workspace/
├── envman.py                 # Terminal UI application
├── requirements.txt          # Python dependencies
├── base/                     # Docker base image (shared by all environments)
│
├── environments/             # Your development environments live here
│   ├── template/            # Template used when creating new environments
│   ├── my-project/          # Each environment has:
│   │   ├── workspace/       #   - workspace/ (your project files)
│   │   ├── opencode_config/ #   - config/ (AI assistant settings)
│   │   ├── docker-compose.yml
│   │   └── .env
│   ├── another-project/
│   └── ...
│
├── shared/                   # Resources shared across all environments
│   ├── config/              # Shared OpenCode configuration
│   └── auth/                # Shared credentials (optional)
│
└── docs/                     # Documentation

## How It Works

### Each Environment is Isolated

When you create a new environment (e.g., "my-project"), the system:
1. Creates a new folder in `environments/my-project/`
2. Sets up a containerized Linux workspace
3. Installs OpenCode AI assistant in the container
4. Sets up VSCode access in your browser
5. Assigns unique ports so environments don't conflict

### Everything is Self-Contained

Your project files stay in `environments/my-project/workspace/`. When you delete an environment, everything goes away cleanly. No leftover config or dependencies affecting other projects.

### Shared Configuration (Optional)

You can optionally share things across environments:
- **OpenCode config**: Same AI settings in all environments
- **Credentials**: One set of API keys used by all environments
- **Plugins & Skills**: Install tools once, use everywhere

## Getting Help

The dashboard has a built-in help screen — just press `?` while the TUI is running.

For more detailed information, see:
- **Quick tutorial**: [QUICKSTART.md](docs/user-guides/QUICKSTART.md)
- **Remote development guide**: [REMOTE_DEV_GUIDE.md](docs/user-guides/REMOTE_DEV_GUIDE.md)
- **Full documentation**: [docs/README.md](docs/README.md)

## Troubleshooting

### "Port already in use" error
Each environment needs its own port. The system auto-assigns them, but if you create too many, you might run out. Solution: Delete unused environments, or manually assign different ports in configuration.

### Can't access VSCode in browser
Make sure the environment is running (press `s` to start). Get the URL from the dashboard or press `v` to open it.

### Changes aren't persisting
Make sure you're editing files in the `workspace/` folder (it's the mounted directory). Files outside that folder won't persist between container restarts.

### Need to reset an environment
Press `d` to delete it (you'll be asked for confirmation), then `n` to create a new one with the same name.

