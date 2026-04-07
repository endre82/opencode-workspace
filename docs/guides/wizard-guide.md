# Environment Creation Wizard - User Guide

## Quick Start

Launch the TUI and press `n` to create a new environment:

```bash
oc-workspace-tui
# Press 'n' when dashboard loads
```

## Wizard Steps

### Step 1: Basic Information

**Environment Name** (required)
- Must be unique
- Only alphanumeric, hyphens, and underscores
- Examples: `dev3`, `my-project`, `code_review`
- Real-time validation shows errors immediately

**User ID / Group ID**
- Defaults to your host user (1000:1000 typically)
- Important: Must match host to avoid permission issues
- Usually you don't need to change these

**Timezone**
- Defaults to UTC
- Can be changed to match your local timezone

### Step 2: Workspace Configuration

**Workspace Type:**
- **Isolated (Recommended)**: Creates `./workspace` inside environment directory
  - Best for most use cases
  - Each environment has its own separate workspace
  - Example: `environments/dev3/workspace/`

- **External**: Use a custom path
  - For sharing workspaces across environments
  - Must provide full path (e.g., `~/my-project`)

**Workspace Path:**
- Auto-filled based on type selection
- For isolated: `./workspace`
- For external: Specify your path

### Step 3: Volume Mounts

Configure which OpenCode configurations to mount:

**GLOBAL_CONFIG** (Optional)
- Mount shared OpenCode config from host
- Path: `../shared/config/.opencode`
- Use when: You want to share API keys, preferences across all environments
- Mounted as: Read-only

**PROJECT_CONFIG** (Optional)
- Mount project-specific `.opencode` directory
- Path: `./opencode_project_config`
- Use when: You have project-level prompts, workflows
- Mounted as: Read-write

**OPENCODE_ENV_CONFIG** (Always Enabled)
- Per-environment OpenCode data and cache
- Path: `./opencode_config`
- Stores: Conversation history, settings, extensions
- Mounted as: Read-write

**Recommendation:** For most cases, just use the defaults (OPENCODE_ENV_CONFIG only). This follows the vienna-agentic-vibes pattern.

### Step 4: Server Configuration

**Server Port**
- Auto-detected next available port (e.g., 4101)
- Must be unique across all environments
- Range: 1024-65535
- Real-time validation checks for conflicts

**Server Username**
- Defaults to `opencode`
- Used for server authentication
- Must be at least 3 characters

**Server Password**
- Auto-generated 16-character secure password
- Click "Generate Random" for new password
- Must be at least 8 characters
- Note: Save this password if you need to connect remotely

### Step 5: Review & Create

**Review Screen**
- Shows all your configuration choices
- Double-check everything before creating
- Press "Create" to proceed
- Press "Back" to make changes
- Press "Cancel" (or ESC) to abort

**Creation Process**
- Creates environment directory structure
- Generates `.env` file from template
- Generates `docker-compose.yml` from template
- Creates all required subdirectories
- **Automatically builds and starts the container** (`docker compose up -d --build`)
- Shows progress notifications during build and start
- Returns to dashboard when complete (with running or stopped status)

## Navigation

- **Next**: Proceed to next step (validates current step first)
- **Back**: Return to previous step (disabled on Step 1)
- **Cancel**: Exit wizard without creating (ESC key)
- **Tab / Shift+Tab**: Navigate between input fields
- **Enter**: Submit current field / press focused button
- **Space**: Toggle switches (for volume mounts)

## Validation Errors

**Common Errors:**

1. **"Environment name already exists"**
   - Choose a different name
   - Check existing environments in dashboard

2. **"Port already in use"**
   - Wizard will suggest next available port
   - Manually enter a different port

3. **"Invalid environment name"**
   - Use only letters, numbers, hyphens, underscores
   - No spaces or special characters

4. **"Password too short"**
   - Minimum 8 characters
   - Use "Generate Random" button for secure password

## After Creation

The wizard automatically builds and starts your environment! You'll see progress notifications:

1. **"Creating environment..."** - File scaffolding
2. **"Building and starting container..."** - Docker build and startup in progress
3. **"✓ Container started"** - Your environment is now running (or error if build failed)

Once created, the environment appears in the dashboard:

- **Status**: Running (green circle) if build succeeded, Stopped (red) if build failed
- **Port**: Your configured port
- **Actions Available**:
  - `s` - Start environment (fast start, no rebuild)
  - `b` - Rebuild environment (rebuilds if Dockerfile changed)
  - `x` - Stop environment
  - `r` - Restart environment
  - `l` - View logs
  - `i` - Inspect details

**Next Steps:**
1. Environment is ready to use if build succeeded ✓
2. If build failed, check logs with `l` and retry with `b`
3. Connect: Use the server URL shown in dashboard
4. To rebuild after code changes, press `b` then `s`

## Tips

1. **Use Default Values**: The wizard pre-fills smart defaults. In most cases, you only need to provide a name.

2. **Port Selection**: Let the wizard auto-detect the next port. Manual port entry is only needed for specific requirements.

3. **Password Management**: The generated password is shown in the summary. Copy it if you need remote access. It's also saved in the `.env` file.

4. **Volume Mounts**: Start simple with just OPENCODE_ENV_CONFIG. Add GLOBAL_CONFIG later if you need shared configuration.

5. **Workspace Isolation**: Use isolated workspace (`./workspace`) unless you specifically need to share a workspace across environments.

## Troubleshooting

**Wizard doesn't launch:**
- Check that you're on the dashboard screen
- Press `n` (not Shift+N)
- Check for error notifications at bottom of screen

**Creation fails:**
- Check disk space in workspace directory
- Verify you have write permissions
- Check that Docker is running
- View error message in notification

**Port conflict despite validation:**
- Another process may have started using the port
- Try a different port manually
- Check with: `netstat -tuln | grep <port>`

**Permission errors after creation:**
- Verify USER_ID and GROUP_ID match your host user
- Check with: `id -u` and `id -g` on host
- Rebuild environment if needed

## Examples

**Example 1: Quick Development Environment**
```
Step 1: Name: dev3, UID: 1000, GID: 1000
Step 2: Isolated workspace (./workspace)
Step 3: Use defaults (OPENCODE_ENV_CONFIG only)
Step 4: Port: 4101 (auto), User: opencode, Password: (generated)
```

**Example 2: Shared Configuration Environment**
```
Step 1: Name: shared-config-dev, UID: 1000, GID: 1000
Step 2: Isolated workspace
Step 3: Enable GLOBAL_CONFIG, use defaults for others
Step 4: Port: 4102 (auto), User: opencode, Password: (generated)
```

**Example 3: Project-Specific Environment**
```
Step 1: Name: my-project, UID: 1000, GID: 1000
Step 2: External workspace: ~/projects/my-project
Step 3: Enable PROJECT_CONFIG
Step 4: Port: 4200, User: admin, Password: (custom)
```

## Advanced

**Manual Configuration:**
After creation, you can manually edit:
- `.env` file in environment directory
- `docker-compose.yml` in environment directory
- Remember to rebuild after manual changes: Press `b` in dashboard

**Template Customization:**
Edit templates in `environments/template/`:
- `.env.template`
- `docker-compose.yml.template`

Changes affect all future environment creations.

---

**Need Help?** Check the main documentation or AGENTS.md for more details.
