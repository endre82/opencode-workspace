# OpenCode Workspace TUI - Installation Guide

Complete guide for installing the TUI system-wide with the `oc-workspace-tui` command.

## Quick Install

```bash
# From the opencode-workspace directory
./install-envman-tui.sh
```

That's it! The installer will:
- ✅ Check all prerequisites
- ✅ Create isolated Python virtual environment
- ✅ Install all dependencies
- ✅ Create system-wide `oc-workspace-tui` command
- ✅ Update your shell profile (PATH)
- ✅ Verify installation

## What Gets Installed

### Installation Structure

```
$HOME/
├── .local/
│   ├── bin/
│   │   └── oc-workspace-tui          # Main executable command
│   └── share/
│       └── opencode-workspace/
│           ├── venv/                 # Python virtual environment
│           ├── envman/               # TUI application
│           ├── opencode-connect.sh   # Connection helper
│           ├── config.json           # Installation metadata
│           ├── installation-log.txt  # Installation log
│           ├── workspace-root        # Workspace path reference
│           ├── uninstall.sh          # Uninstaller
│           └── backup/               # Shell profile backups
│
└── .opencode-workspace.conf          # Configuration file
```

### Disk Space

- **Total:** ~200MB
  - Python venv: ~150MB
  - Dependencies: ~50MB
  - Application files: <1MB

## Prerequisites

### Required

- **Python 3.8+** with venv module
  ```bash
  # Ubuntu/Debian
  sudo apt install python3 python3-venv python3-pip
  
  # macOS
  brew install python3
  
  # Verify
  python3 --version
  ```

- **Docker** (for environment management)
  ```bash
  # Verify Docker is installed and running
  docker --version
  docker ps
  
  # If permission errors, add user to docker group
  sudo usermod -aG docker $USER
  newgrp docker
  ```

### Optional but Recommended

- **Git** (for workspace detection)
- **curl** or **wget** (for remote installation)

## Installation Methods

### Method 1: Local Installation (Recommended)

If you already have the workspace cloned:

```bash
cd /path/to/opencode-workspace
./install-envman-tui.sh
```

### Method 2: Remote Installation (Coming Soon)

One-line installation from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/opencode-workspace/main/install-envman-tui.sh | bash
```

### Method 3: Custom Workspace Path

Install from a different location:

```bash
cd /path/to/workspace
./install-envman-tui.sh
```

The installer will auto-detect the workspace root.

## Installation Process

### Step-by-Step Walkthrough

**1. Preflight Checks**
```
✓ Python 3.12.3 found
✓ Python venv module available
✓ Docker 29.2.1 found
✓ Docker daemon is accessible
✓ Workspace root found: /home/user/opencode-workspace
✓ No existing installation found
✓ Write access to /home/user/.local
✓ Can create /home/user/.local/bin
```

**2. Installation Plan**
```
Workspace Root:    /home/user/opencode-workspace
Install Location:  /home/user/.local/share/opencode-workspace
Command Location:  /home/user/.local/bin/oc-workspace-tui
Disk Space:        ~200MB (for venv + dependencies)

Proceed with installation? [Y/n]:
```

**3. Installation Steps**
```
▶ Creating installation directories
  ✓ Created /home/user/.local/share/opencode-workspace
  ✓ Created /home/user/.local/bin

▶ Creating Python virtual environment
  ✓ Virtual environment created
  ✓ pip upgraded

▶ Installing Python dependencies
  ✓ Dependencies installed
  ✓ textual installed
  ✓ docker-py installed
  ✓ python-dotenv installed
  ✓ pyyaml installed

▶ Copying application files
  ✓ envman package copied
  ✓ opencode-connect.sh copied
  ✓ Application files copied

▶ Creating oc-workspace-tui command
  ✓ Created /home/user/.local/bin/oc-workspace-tui

▶ Updating shell profiles
  Will update: ~/.bashrc
  Proceed with updating shell profiles? [Y/n]: y
  ✓ Updated /home/user/.bashrc
  ✓ Shell profiles updated

▶ Creating configuration file
  ✓ Created /home/user/.opencode-workspace.conf

▶ Creating uninstall script
  ✓ Created uninstall.sh

▶ Verifying installation
  ✓ Virtual environment activates successfully
  ✓ TUI imports work correctly
  ✓ oc-workspace-tui is executable
  ✓ Workspace detection works from /tmp
  ✓ Installation verified
```

**4. Post-Installation**
```
╔══════════════════════════════════════════════════════════════════════╗
║                   ✓ Installation Complete!                          ║
╚══════════════════════════════════════════════════════════════════════╝

Installation Details:
  • Workspace:   /home/user/opencode-workspace
  • Install Dir: /home/user/.local/share/opencode-workspace
  • Command:     /home/user/.local/bin/oc-workspace-tui
  • Config:      /home/user/.opencode-workspace.conf

Shell Profiles Updated:
  • /home/user/.bashrc

⚠️  Reload your shell to use the new command:
    source ~/.bashrc

Quick Start:
  oc-workspace-tui              # Launch TUI
  oc-workspace-tui list         # List environments
  oc-workspace-tui --help       # Show help

Launch TUI now? [Y/n]:
```

## Using oc-workspace-tui

### Basic Commands

**Launch TUI Dashboard:**
```bash
oc-workspace-tui
# or
oc-workspace-tui dashboard
```

**List Environments:**
```bash
oc-workspace-tui list
```
Output:
```
Environments (4):
  🟢 vienna-agentic-vibes         Port: 4100  Status: running
  🔴 test-env                     Port: 4097  Status: stopped
  🟢 code-reviewing-framework     Port: 4107  Status: running
  🔴 build-test-env               Port: 4099  Status: stopped
```

**Show Status Summary:**
```bash
oc-workspace-tui status
```
Output:
```
Total: 4 | Running: 2 | Stopped: 2
```

**Quick Connect:**
```bash
oc-workspace-tui connect vienna-agentic-vibes
```

**View Logs:**
```bash
oc-workspace-tui logs vienna-agentic-vibes
```

**Open Shell:**
```bash
oc-workspace-tui shell vienna-agentic-vibes
```

**Create Environment:**
```bash
oc-workspace-tui create my-new-env
```

**Show Configuration:**
```bash
oc-workspace-tui config
```

**Show Help:**
```bash
oc-workspace-tui --help
```

### Advanced Usage

**Use Different Workspace:**
```bash
oc-workspace-tui --workspace ~/another-workspace list
```

**Set Workspace via Environment Variable:**
```bash
export OPENCODE_WORKSPACE=~/my-workspace
oc-workspace-tui list
```

**Call from Anywhere:**
```bash
cd /tmp
oc-workspace-tui status  # Still finds your workspace!
```

## Workspace Detection

The tool automatically finds your workspace using this priority order:

1. **--workspace flag:** `oc-workspace-tui --workspace /path/to/workspace`
2. **OPENCODE_WORKSPACE env var:** `export OPENCODE_WORKSPACE=/path`
3. **Config file:** `~/.opencode-workspace.conf`
4. **Installation reference:** `~/.local/share/opencode-workspace/workspace-root`
5. **Directory walk-up:** Look for `environments/` and `envman/` directories
6. **Git root:** Use git repository root if inside a repo

## Troubleshooting

### Command not found: oc-workspace-tui

**Problem:** Shell can't find the command after installation.

**Solution:**
```bash
# Reload your shell
source ~/.bashrc  # or ~/.zshrc

# Or start a new terminal session

# Verify PATH includes ~/.local/bin
echo $PATH | grep ".local/bin"

# If not, manually add to your shell profile:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Could not detect workspace root

**Problem:** Tool can't find the workspace directory.

**Solutions:**
```bash
# Option 1: Use --workspace flag
oc-workspace-tui --workspace /path/to/workspace list

# Option 2: Set environment variable
export OPENCODE_WORKSPACE=/path/to/workspace
oc-workspace-tui list

# Option 3: Run from workspace directory
cd /path/to/workspace
oc-workspace-tui list

# Option 4: Update config file
vim ~/.opencode-workspace.conf
# Change "workspace_root" to correct path
```

### Virtual environment not found

**Problem:** Installation corrupted or deleted.

**Solution:**
```bash
# Reinstall
cd /path/to/opencode-workspace
./install-envman-tui.sh

# Choose option 2 (Reinstall) if prompted
```

### Import errors or missing packages

**Problem:** Python dependencies not installed correctly.

**Solution:**
```bash
# Activate venv and reinstall dependencies
source ~/.local/share/opencode-workspace/venv/bin/activate
pip install -r /path/to/workspace/requirements.txt

# Or reinstall TUI
./install-envman-tui.sh
# Choose option 1 (Upgrade) or 3 (Repair)
```

### Docker permission errors

**Problem:** Cannot access Docker daemon.

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Or restart your session
```

### Shell profile not updated

**Problem:** Installer didn't modify shell profile.

**Solution:**
```bash
# Manually add to your shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Updating

### Check for Updates

```bash
oc-workspace-tui --version
```

### Upgrade Installation

```bash
cd /path/to/opencode-workspace
git pull  # Get latest changes
./install-envman-tui.sh
# Choose option 1 (Upgrade)
```

### Repair Installation

```bash
./install-envman-tui.sh
# Choose option 3 (Repair)
```

## Uninstallation

### Method 1: Using the Command

```bash
oc-workspace-tui --uninstall
```

### Method 2: Manual Uninstall Script

```bash
bash ~/.local/share/opencode-workspace/uninstall.sh
```

### What Gets Removed

- ✅ `~/.local/share/opencode-workspace/` (entire installation)
- ✅ `~/.local/bin/oc-workspace-tui` (command)
- ✅ `~/.opencode-workspace.conf` (config file)

### What Gets Preserved

- ⚠️ Shell profile modifications (manual removal needed)
- ✅ Backups in installation directory (until you delete it)

### Manual Cleanup

To remove PATH modifications:

```bash
# Edit your shell profile
vim ~/.bashrc  # or ~/.zshrc

# Remove these lines:
# Added by OpenCode Workspace TUI installer
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
```

## Shell Profile Updates

The installer automatically updates your shell profile to add `~/.local/bin` to PATH.

### Supported Shells

- **bash** → Updates `~/.bashrc`
- **zsh** → Updates `~/.zshrc`
- **fish** → Updates `~/.config/fish/config.fish`
- **sh** → Updates `~/.profile`

### Backups

Original shell profiles are backed up to:
```
~/.local/share/opencode-workspace/backup/
├── bashrc.backup
├── zshrc.backup
└── ...
```

### Manual Rollback

```bash
# Restore from backup
cp ~/.local/share/opencode-workspace/backup/bashrc.backup ~/.bashrc
source ~/.bashrc
```

## Multiple Workspaces

You can work with multiple OpenCode workspaces:

### Option 1: Use --workspace Flag

```bash
oc-workspace-tui --workspace ~/workspace1 list
oc-workspace-tui --workspace ~/workspace2 status
```

### Option 2: Use Environment Variable

```bash
# Switch workspaces on-the-fly
export OPENCODE_WORKSPACE=~/workspace1
oc-workspace-tui list

export OPENCODE_WORKSPACE=~/workspace2
oc-workspace-tui list
```

### Option 3: Update Config File

```bash
# Edit config to change default workspace
vim ~/.opencode-workspace.conf
# Change "workspace_root" value
```

## Configuration File

Location: `~/.opencode-workspace.conf`

Format:
```json
{
  "workspace_root": "/home/user/opencode-workspace",
  "version": "1.0.0",
  "installed_at": "2026-03-16T14:45:00Z",
  "venv_path": "/home/user/.local/share/opencode-workspace/venv",
  "install_base": "/home/user/.local/share/opencode-workspace"
}
```

You can manually edit this file to change the workspace root or other settings.

## FAQ

### Q: Do I need sudo for installation?

**A:** No! Installation is user-level (`~/.local/`), no sudo required.

### Q: Can I install for all users?

**A:** Currently only user-level installation is supported. System-wide installation (/opt) may be added in the future.

### Q: Does it work on macOS?

**A:** Yes! The installer should work on macOS with Python 3.8+ and Docker Desktop.

### Q: Does it work on Windows?

**A:** Windows is not officially supported. Use WSL2 (Windows Subsystem for Linux) instead.

### Q: Can I use system Python instead of venv?

**A:** Not recommended. The venv isolates dependencies and prevents conflicts.

### Q: What if I already have an older installation?

**A:** The installer detects existing installations and offers upgrade/reinstall/repair options.

### Q: Can I install to a custom location?

**A:** The current installer uses `~/.local/` by default. You can modify the script to use a different path.

### Q: How do I update to the latest version?

**A:** Pull latest changes (`git pull`) and run the installer again. Choose "Upgrade" option.

## Support

**Installation Logs:**
```bash
cat ~/.local/share/opencode-workspace/installation-log.txt
```

**Debug Mode:**
```bash
bash -x ./install-envman-tui.sh
```

**Report Issues:**
- Check TUI-README.md troubleshooting section
- Review installation log
- Report issues with full log output

---

**Next Steps:**
- See [QUICKSTART.md](QUICKSTART.md) for usage examples
- See [TUI-README.md](TUI-README.md) for complete TUI documentation
- Run `oc-workspace-tui --help` for command reference
