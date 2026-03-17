# Phase 5: Environment Management

**Status:** ✅ Complete  
**Version:** 1.0.0  
**Date:** March 17, 2026

## Overview

Phase 5 adds comprehensive environment management features to the OpenCode Workspace TUI, completing the core functionality set with 4 essential screens for monitoring, configuring, and maintaining development environments.

## Features

### 1. Logs Viewer 📄

View, search, and export container logs in real-time.

**Access:** Dashboard → Select environment → Press `l`

#### Capabilities
- **Real-time Streaming:** Follow mode auto-scrolls new logs as they appear
- **Search:** Find specific log entries with regex support and highlighting
- **Filter by Level:** Show only INFO, WARN, ERROR, or DEBUG messages
- **Export:** Save logs to timestamped files for sharing or archiving
- **Clear Display:** Clear the log view without affecting container logs
- **Historical Logs:** Scroll through logs with keyboard or mouse

#### Use Cases
- **Debugging:** Search for errors or specific events
- **Monitoring:** Watch logs in real-time during development
- **Troubleshooting:** Export logs for bug reports
- **Analysis:** Filter by severity to focus on important messages

#### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Esc` | Close logs viewer |
| `e` | Export logs to file |
| `f` | Toggle follow mode |
| `c` | Clear log display |
| `/` | Focus search input |

#### Screenshots
```
┌─ Logs: my-environment ─────────────────────────────────────┐
│ Follow: ON  │  Filter: ALL  │  Search: [_______]  │  Export│
├────────────────────────────────────────────────────────────┤
│ 2026-03-17 12:00:01 [INFO] Server starting on port 8080... │
│ 2026-03-17 12:00:02 [INFO] Workspace loaded: /workspace    │
│ 2026-03-17 12:00:03 [WARN] Config file not found          │
│ 2026-03-17 12:00:04 [INFO] Server ready for connections    │
│ 2026-03-17 12:00:05 [ERROR] Failed to load plugin: xyz    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Inspect Environment 🔍

Inspect detailed container information and resource usage.

**Access:** Dashboard → Select environment → Press `i`

#### Capabilities
- **Container Details:** ID, name, image, created date, platform
- **Configuration:** Environment variables, labels, working directory, command
- **Network Settings:** Port mappings, IP addresses, gateway, network mode
- **Volume Mounts:** Source paths, mount points, permissions (rw/ro)
- **Resource Usage:** CPU, memory, disk I/O, network I/O (running containers only)
- **State Information:** Status, uptime, restart count, exit code
- **Tree Navigation:** Expand/collapse sections to explore data
- **Refresh:** Update data on demand to see current stats

#### Use Cases
- **Configuration Review:** Verify environment variables and settings
- **Network Debugging:** Check port mappings and IP addresses
- **Volume Verification:** Confirm mounted paths and permissions
- **Performance Monitoring:** Track CPU and memory usage
- **Troubleshooting:** Inspect container state and restart history

#### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Esc` | Close inspect screen |
| `r` | Refresh data |
| `e` | Expand all tree nodes |
| `c` | Collapse all tree nodes |
| `↑↓` | Navigate tree |
| `Enter` | Expand/collapse node |

#### Tree Structure
```
Container: opencode-my-env
├─ Details
│  ├─ ID: abc123...
│  ├─ Name: opencode-my-env
│  ├─ Image: opencode/workspace:latest
│  ├─ Created: 2026-03-17 10:00:00
│  └─ Platform: linux/amd64
├─ Configuration
│  ├─ Environment Variables
│  │  ├─ OPENCODE_SERVER_PORT=8080
│  │  ├─ USER_ID=1000
│  │  └─ TIMEZONE=UTC
│  ├─ Labels
│  └─ Command: /bin/bash -c "start.sh"
├─ Network Settings
│  ├─ Ports: 8080:8080
│  ├─ IP Address: 172.17.0.2
│  └─ Gateway: 172.17.0.1
├─ Volume Mounts
│  ├─ ./workspace → /workspace (rw)
│  ├─ ~/.config/opencode → /config (ro)
│  └─ ./opencode_config → /env_config (rw)
├─ Resource Usage
│  ├─ CPU: 5.2%
│  ├─ Memory: 512MB / 2GB (25%)
│  ├─ Disk Read: 100KB/s
│  └─ Network RX: 50KB/s
└─ State
   ├─ Status: running
   ├─ Running for: 2h 15m
   └─ Restart Count: 0
```

---

### 3. Configure Environment ⚙️

Edit environment configuration with form-based interface and validation.

**Access:** Dashboard → Select environment → Press `c`

#### Capabilities
- **Form-Based Editor:** Easy-to-use form with organized sections
- **Input Validation:** Automatic validation of ports, IDs, and names
- **Automatic Backup:** Creates timestamped backup before saving
- **Reset Form:** Discard changes and restore original values
- **Manual Backup:** Save backup without applying changes
- **Rebuild Warning:** Reminds you to rebuild after config changes

#### Configuration Sections

##### Server Configuration
Configure OpenCode server settings for remote connections.

| Field | Description | Example |
|-------|-------------|---------|
| Server Enabled | Enable/disable server | ON/OFF |
| Server Host | Bind address | 0.0.0.0 |
| Server Port | Port number (1024-65535) | 8080 |
| Username | Auth username | opencode |
| Password | Auth password | ******** |
| CORS Origins | Allowed origins | * |

##### User Configuration
Match container user with host user for file permissions.

| Field | Description | Example |
|-------|-------------|---------|
| User ID | UID in container | 1000 |
| Group ID | GID in container | 1000 |
| Timezone | Container timezone | America/New_York |

##### Container Configuration
Container identity and network settings.

| Field | Description | Example |
|-------|-------------|---------|
| Container Name | Unique container name | opencode-my-env |
| Hostname | Container hostname | my-workspace |

##### Volume Configuration
Control mounted directories and paths.

| Field | Description | Example |
|-------|-------------|---------|
| Workspace Directory | Main workspace path | ./workspace |
| Global Config | Global OpenCode config | ~/.config/opencode |
| Project Config | Project-specific config | ./.opencode |
| Environment Config | Environment config path | ./opencode_config |

**Mount Control Checkboxes:**
- [x] Mount Global Config
- [x] Mount Project Config
- [x] Mount Environment Config

##### Resource Limits (Experimental)
⚠️ **Note:** Resource limits are currently commented out in the UI due to experimental status. Edit `.env` directly if needed.

Fields (when enabled):
- Memory Limit (e.g., 2g, 512m)
- CPU Limit (e.g., 2, 0.5)
- Shared Memory (e.g., 64m, 128m)

#### Validation Rules

The config editor validates input to prevent errors:

| Field | Rule | Error Example |
|-------|------|---------------|
| Server Port | 1024-65535 | "Port must be between 1024 and 65535" |
| User ID | Non-negative integer | "User ID must be non-negative" |
| Group ID | Non-negative integer | "Group ID must be non-negative" |
| Container Name | Alphanumeric, `-`, `_` only | "Container name can only contain alphanumeric characters, hyphens, and underscores" |

#### Backup Location
Backups are saved to: `<environment_path>/backups/.env.backup.<timestamp>`

Example: `backups/.env.backup.20260317_120000`

#### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Esc` | Close without saving |
| `Ctrl+S` | Save configuration |
| `Ctrl+R` | Reset form |
| `Ctrl+B` | Create backup |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |

#### Workflow
1. Select environment in dashboard
2. Press `c` to open config editor
3. Make changes to form fields
4. Press `Ctrl+S` or click "Save" button
5. Automatic backup created
6. Configuration saved to `.env` file
7. Rebuild warning displayed
8. Rebuild container for changes to take effect

---

### 4. Delete Environment 🗑️

Safely delete environments with confirmation and backup.

**Access:** Dashboard → Select environment → Press `d`

#### Safety Features
- **Name Verification:** Must type environment name to confirm
- **Automatic Backup:** Creates archive before deletion
- **Container Stop:** Gracefully stops container before removal
- **Selective Deletion:** Choose what to delete
- **Progress Notifications:** Shows deletion progress

#### Deletion Options

| Option | Effect |
|--------|--------|
| Delete workspace files | Removes `./workspace` directory |
| Delete configuration files | Removes `.env` and `docker-compose.yml` |
| Delete all | Removes entire environment directory |

#### Backup Location
Backup archives are saved to: `<environment_path>/backups/backup-<timestamp>.tar.gz`

Example: `backups/backup-20260317-120000.tar.gz`

#### Workflow
1. Select environment in dashboard
2. Press `d` to open delete screen
3. Read warning message carefully
4. Type environment name exactly in input field
5. Select deletion options:
   - [ ] Delete workspace files
   - [ ] Delete configuration files
   - [ ] Delete all (entire directory)
6. Click "Delete" button
7. Container stopped (if running)
8. Backup created automatically
9. Selected files/directories deleted
10. Environment removed from dashboard

#### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Esc` | Cancel and close |
| `Tab` | Navigate options |
| `Space` | Toggle checkbox |
| `Enter` | Confirm deletion (if name verified) |

#### Warning Display
```
┌─ Delete Environment: my-environment ───────────────────────┐
│                                                             │
│  ⚠️  WARNING: This action cannot be undone!                │
│                                                             │
│  To confirm deletion, type the environment name below:     │
│                                                             │
│  Environment name: [_____________________]                 │
│                                                             │
│  What would you like to delete?                            │
│                                                             │
│  [ ] Delete workspace files (./workspace)                  │
│  [ ] Delete configuration files (.env, docker-compose.yml) │
│  [ ] Delete all (entire environment directory)             │
│                                                             │
│  A backup will be created before deletion in:              │
│  /path/to/env/backups/backup-YYYYMMDD-HHMMSS.tar.gz       │
│                                                             │
│  [Cancel]                              [Delete]            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Workflows

### Workflow 1: Debug Application Issues
1. **View Logs** (`l`) - Check for error messages
2. **Search Logs** (`/`) - Find specific errors
3. **Export Logs** (`e`) - Save for bug report
4. **Inspect Environment** (`i`) - Verify configuration
5. **Check Resources** - Monitor CPU/memory in inspect screen

### Workflow 2: Modify Configuration
1. **Configure** (`c`) - Open config editor
2. **Change Settings** - Update port, timezone, etc.
3. **Save** (`Ctrl+S`) - Apply changes (backup created automatically)
4. **Build** (`b`) - Rebuild container with new config
5. **View Logs** (`l`) - Verify container starts correctly
6. **Inspect** (`i`) - Confirm new settings applied

### Workflow 3: Clean Up Environment
1. **Stop** (`x`) - Stop running container
2. **Inspect** (`i`) - Review what will be deleted
3. **Configure** (`c`) - Backup config if needed
4. **Delete** (`d`) - Remove environment
5. **Verify Backup** - Check `/backups/` directory

### Workflow 4: Monitor Performance
1. **Start** (`s`) - Start environment
2. **Inspect** (`i`) - Open inspect screen
3. **Check Resources** - Review CPU, memory, disk I/O
4. **Refresh** (`r`) - Update stats periodically
5. **View Logs** (`l`) - Check for performance warnings

---

## Tips and Best Practices

### Logs Viewer
- **Use Follow Mode** for real-time monitoring during development
- **Filter by Level** to focus on errors when debugging
- **Export Logs** before troubleshooting to have a reference
- **Search with Regex** for powerful log analysis (e.g., `error|fail|exception`)

### Inspect Screen
- **Refresh Regularly** when monitoring resource usage
- **Collapse Sections** you don't need to reduce clutter
- **Check Network Settings** when having connection issues
- **Verify Volume Mounts** when files aren't accessible

### Config Editor
- **Backup Before Changes** - Use `Ctrl+B` before experimenting
- **Match Host UID/GID** - Set User ID and Group ID to match your host user for proper file permissions
- **Use Meaningful Names** - Container and hostname should be descriptive
- **Test After Changes** - Always rebuild and test after config changes

### Delete Environment
- **Backup First** - Create manual backup before deletion if concerned
- **Be Selective** - Only delete what you need to (workspace vs config)
- **Check Backups** - Verify backup archives are created successfully
- **Review Inspect Screen** - Understand what you're deleting before proceeding

---

## Keyboard Reference

| Key | Screen | Action |
|-----|--------|--------|
| `l` | Dashboard | Open Logs Viewer |
| `i` | Dashboard | Open Inspect Environment |
| `c` | Dashboard | Open Configure Environment |
| `d` | Dashboard | Open Delete Environment |
| `Esc` | Any screen | Close current screen |
| `r` | Inspect/Logs | Refresh data |
| `e` | Logs | Export logs to file |
| `f` | Logs | Toggle follow mode |
| `/` | Logs | Focus search input |
| `Ctrl+S` | Config | Save configuration |
| `Ctrl+R` | Config | Reset form |
| `Ctrl+B` | Config | Create backup |

---

## File Locations

### Configuration Files
- **Environment File:** `<env_path>/.env`
- **Docker Compose:** `<env_path>/docker-compose.yml`

### Backup Files
- **Config Backups:** `<env_path>/backups/.env.backup.<timestamp>`
- **Deletion Backups:** `<env_path>/backups/backup-<timestamp>.tar.gz`

### Log Files
- **Container Logs:** Managed by Docker (use logs viewer to access)
- **Exported Logs:** `<env_path>/logs-export-<timestamp>.txt` (or user-specified path)

---

## Troubleshooting

### "No environment selected" Warning
**Problem:** Trying to use a feature without selecting an environment.  
**Solution:** Click on an environment row in the dashboard to select it.

### "Container not running" Warning
**Problem:** Trying to view logs on a stopped container.  
**Solution:** Start the container first with `s` key.

### "Container not found" Warning
**Problem:** Trying to inspect a non-existent container.  
**Solution:** Build the container first with `b` key.

### Config Save Fails
**Problem:** Validation error when saving configuration.  
**Solution:** Check error message, correct invalid field (port out of range, invalid characters in name, etc.).

### Logs Not Appearing
**Problem:** Logs viewer is empty or not updating.  
**Solution:**
1. Verify container is running (`i` to inspect)
2. Check if container has any logs (may be silent)
3. Try refreshing (`r` key)

### Resource Stats Not Showing
**Problem:** Resource usage section is empty in inspect screen.  
**Solution:** Resource stats only available for running containers. Start the container first.

### Deletion Fails
**Problem:** Delete operation fails or hangs.  
**Solution:**
1. Ensure container is stopped first (will auto-stop, but may take time)
2. Check file permissions on environment directory
3. Verify no processes have files open in the environment

---

## API Reference

### DockerService Extensions

```python
# Stream logs from container
for log_line in docker_service.stream_logs(
    container_name="opencode-my-env",
    follow=True,
    tail=100
):
    print(log_line)

# Inspect container
data = docker_service.inspect_container("opencode-my-env")
if data:
    print(f"Container ID: {data['Id']}")
    print(f"Status: {data['State']['Status']}")

# Get resource stats
stats = docker_service.get_container_stats("opencode-my-env")
if stats:
    print(f"CPU: {stats['cpu_percent']}%")
    print(f"Memory: {stats['memory_usage']}")

# Remove container and volumes
success, output = docker_service.remove_container(
    env_path="/path/to/env",
    volumes=True
)
```

### LogService Methods

```python
from envman.services.logs import LogService

log_service = LogService()

# Filter logs by level
errors = log_service.filter_by_level(logs, "ERROR")

# Search logs
matches = log_service.search_logs(logs, r"error|fail")

# Highlight search term
from rich.text import Text
highlighted = log_service.highlight_search_term(
    "Error: Connection failed",
    "error"
)

# Export logs
log_service.export_logs(logs, Path("/path/to/export.txt"))

# Rotate logs
log_service.rotate_logs(
    log_file=Path("/path/to/app.log"),
    max_size_mb=10,
    backup_count=5
)

# Cleanup old logs
removed = log_service.cleanup_old_logs(
    logs_dir=Path("/path/to/logs"),
    days=30
)
```

---

## Related Documentation

- [Phase 1: Base System](phase1-base-system.md) - Environment discovery and listing
- [Phase 3: Container Operations](phase3-container-ops.md) - Start/stop/restart/build
- [Phase 4: Creation Wizard](phase4-creation-wizard.md) - Create new environments
- [Testing Guide](../testing/phase5-test-plan.md) - Comprehensive test plan
- [Implementation Summary](../summaries/phase5-implementation-summary.md) - Technical details

---

## Changelog

### Version 1.0.0 (March 17, 2026)
- ✅ Added Logs Viewer screen with search, filter, and export
- ✅ Added Inspect Environment screen with tree navigation
- ✅ Added Configure Environment screen with form-based editor
- ✅ Added Delete Environment screen with safety features
- ✅ Created modal dialog components (ConfirmDialog, ProgressDialog)
- ✅ Extended DockerService with 4 new methods
- ✅ Created LogService for log management
- ✅ Updated dashboard to integrate all new screens

---

## Support

For issues, questions, or feature requests related to Phase 5 features, please:
1. Check this documentation first
2. Review the test plan for common scenarios
3. Check the troubleshooting section
4. File an issue with reproduction steps

---

**Phase 5 Status:** ✅ **Complete and Ready for Production**
