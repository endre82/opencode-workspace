# Remote Development Guide

Welcome to the OpenCode Remote Development Platform! This guide covers the new features for remote development with code-server (VSCode in browser) and namespace-based agent/skill sharing.

## 🎯 Overview

This platform enables:
- **Remote IDE Access**: Full VSCode experience in your browser
- **Isolated Environments**: Each developer gets their own containerized workspace
- **Shared Resources**: Team-wide agents, skills, and workflows via namespaces
- **Local Network Access**: Access environments from any device on your LAN
- **Centralized Management**: TUI and CLI tools for environment management

## 🚀 Quick Start

### Create Your First Environment

```bash
# 1. Create a new environment
./scripts/create-environment.sh my-project

# 2. Build the environment
cd environments/my-project
docker compose build

# 3. Start the environment
docker compose up -d

# 4. Access VSCode in browser
# Open: http://localhost:8096
# Password: (shown during environment creation)
```

That's it! You now have a full development environment accessible from any browser.

## 🌐 Remote Access

### Access from Your Browser

Once your environment is running:

1. **Local Access**: `http://localhost:8096`
2. **From Other Devices on LAN**:
   - Find your server IP: `ip addr show`
   - Access from tablet/laptop: `http://192.168.1.100:8096`
   - Use the same password

### Multiple Environments

Each environment gets its own ports:

| Environment | OpenCode API | code-server (VSCode) |
|------------|--------------|---------------------|
| env1       | 4100         | 8100                |
| env2       | 4101         | 8101                |
| env3       | 4102         | 8102                |

Pattern: code-server port = OpenCode port + 4000

### Mobile Access

Access your development environment from tablets or phones:

1. Connect to same WiFi network
2. Open browser on mobile device
3. Navigate to `http://<server-ip>:8096`
4. Enter password
5. Full VSCode experience on mobile!

**Tip**: Add bookmark to home screen for quick access.

## 📦 Namespace System

Namespaces allow sharing agents, skills, workflows, and context across all environments.

### Directory Structure

```
shared/namespaces/
├── global/                    # Available to all environments
│   ├── agents/               # Shared OpenCode agents
│   ├── skills/               # Shared OpenCode skills
│   ├── workflows/            # Team workflows and checklists
│   └── context/              # Knowledge base and documentation
│
└── README.md                 # Namespace documentation
```

### What Goes in Each Namespace Directory?

**agents/**: Custom OpenCode agents for specialized tasks
- `code-reviewer/` - Automated code review agent
- `test-writer/` - Test generation agent
- `docs-generator/` - Documentation agent

**skills/**: Reusable instruction sets and workflows
- `refactoring/` - Code refactoring guides
- `debugging/` - Debugging procedures
- `optimization/` - Performance optimization

**workflows/**: Team processes and checklists
- `pr-checklist.md` - Pull request checklist
- `deployment.md` - Deployment procedure
- `code-review.md` - Code review guidelines

**context/**: Shared knowledge and documentation
- `architecture.md` - System architecture
- `coding-standards.md` - Team coding conventions
- `glossary.md` - Domain terminology

### Using Namespaces

Namespaces are automatically mounted in all environments at:
```
/home/dev/.opencode/namespaces/global/
```

Reference them in OpenCode conversations:
```
"Review my code following our code-review workflow"
"Use the refactoring skill to improve this function"
"Generate documentation using our docs-generator agent"
```

### Creating Shared Resources

1. **Add an agent**:
   ```bash
   mkdir -p shared/namespaces/global/agents/my-agent
   # Create agent.yaml and documentation
   ```

2. **Add a skill**:
   ```bash
   mkdir -p shared/namespaces/global/skills/my-skill
   # Create SKILL.md with instructions
   ```

3. **Add a workflow**:
   ```bash
   touch shared/namespaces/global/workflows/my-workflow.md
   # Document the workflow
   ```

4. **Restart environments** to pick up changes:
   ```bash
   docker compose restart
   ```

See detailed documentation in each namespace subdirectory README.

## 🛠️ Environment Configuration

### Environment Variables (.env)

Each environment has its own `.env` file:

```bash
# User Configuration
USER_ID=1000
GROUP_ID=1000

# Server Ports
OPENCODE_SERVER_PORT=4100
CODE_SERVER_PORT=8100

# Authentication
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=your-secure-password

# code-server Settings
CODE_SERVER_ENABLED=true
CODE_SERVER_AUTH=password
CODE_SERVER_DISABLE_TELEMETRY=true

# Namespace Mounting
MOUNT_NAMESPACE_GLOBAL=true
```

### Customizing code-server

Edit your environment's `.env`:

```bash
# Disable password (local only!)
CODE_SERVER_AUTH=none

# Use different port
CODE_SERVER_PORT=9000

# Disable code-server entirely
CODE_SERVER_ENABLED=false
```

Then restart: `docker compose restart`

### Installing VSCode Extensions

Extensions can be installed via:

1. **code-server UI**: Extensions panel (Ctrl+Shift+X)
2. **CLI inside container**:
   ```bash
   docker compose exec <container> bash
   code-server --install-extension ms-python.python
   ```
3. **Pre-install in base image**: Edit `base/Dockerfile`

## 💡 Use Cases

### Scenario 1: Tablet Developer

**Situation**: You want to code from your iPad while traveling.

**Solution**:
1. Ensure environment is running on your server
2. Connect iPad to same network (or VPN)
3. Open Safari/Chrome on iPad
4. Navigate to `http://server-ip:8096`
5. Full development environment on tablet!

**Benefits**:
- No local development setup needed
- Full VSCode experience
- Access your project files
- Run tests and builds server-side

### Scenario 2: Team Collaboration

**Situation**: Your team wants to share code review agents and workflows.

**Solution**:
1. Create agents in `shared/namespaces/global/agents/`
2. Document workflows in `shared/namespaces/global/workflows/`
3. All team members' environments auto-mount these
4. Everyone uses same agents and follows same workflows

**Benefits**:
- Consistent code review standards
- Shared best practices
- Reusable workflows
- Version controlled via Git

### Scenario 3: Remote Pair Programming

**Situation**: Two developers working on same codebase remotely.

**Solution**:
1. Create shared environment
2. Both access via code-server URL
3. Use tmux/screen for shared terminal
4. Or use code-server's Live Share-like features

**Benefits**:
- Same environment, no "works on my machine"
- Shared context
- Real-time collaboration

### Scenario 4: Centralized AI Subscription

**Situation**: Small team wants to share one AI API subscription.

**Solution**:
1. Configure OpenCode API keys in shared config
2. All environments use same subscription
3. Optional: Add usage tracking (future feature)

**Benefits**:
- Cost savings
- Centralized billing
- Simplified management

## 🌍 Internet Access via ngrok

Want to work from anywhere? Use ngrok tunneling to expose your environments over the internet on-demand.

### Quick Setup

1. **Install ngrok**:
   ```bash
   snap install ngrok
   ngrok config add-authtoken <your-free-token>
   ```
   Get a free token at [ngrok.com/signup](https://ngrok.com/signup)

2. **Start an environment** and press `t` in Dashboard

3. **Click "Start Tunnel"** in the modal

4. **Copy the public URLs** (includes password)

5. **Share URLs** with others to access from anywhere

6. Click **"Stop Tunnel"** when done

### How It Works

ngrok creates a secure tunnel from your local machine to a public URL:

```
Your Environment (localhost:4096, 8096)
           ↓
       [ngrok]
           ↓
    Public Internet
           ↓
    https://abc123.ngrok-free.app
           ↓
   Remote Users
```

Both OpenCode server and VSCode are tunneled. WebUI stays internal (admin only).

### Free Tier Security ⚠️

The free ngrok tier has tradeoffs:

| Feature | Free | Paid |
|---------|------|------|
| Public URLs | Random (change each restart) | Fixed subdomains |
| Bot Scanning | ⚠️ URLs scanned within minutes | ✅ IP allowlisting |
| Authentication | Password auth only | + Email verification (OAuth) |
| Cost | Free | $8+/month |

**Real Security:** Your password is the only defense. ngrok's interstitial warning page helps filter bots, but random URLs get scanned.

**Best Practice:** Keep tunnels short-lived (only while actively working), use strong passwords, and monitor activity at `http://127.0.0.1:4040`.

### Use Cases

**Scenario 1: Code Review on Tablet**
- Start environment at desk
- Tunnel to public URL
- Access from iPad anywhere
- Stop tunnel when done

**Scenario 2: Pair Programming (Remote)**
- Both open same public URL
- Both see same password-protected code-server
- Real-time collaboration

**Scenario 3: Sharing Work in Progress**
- Quick demo to non-technical stakeholder
- No setup needed on their end
- Just copy/paste URL

### Troubleshooting

- **"ngrok not installed"** → Run `snap install ngrok`
- **"Tunnel URLs not appearing"** → Check ngrok: `ps aux | grep ngrok`
- **"Could not reach ngrok API"** → ngrok crashed; stop and restart tunnel
- **Monitor activity** → Open `http://127.0.0.1:4040` while tunnel is active

### Alternatives for Production

For production internet access, consider:
- **Traefik reverse proxy** — Load balancing, SSL termination
- **Let's Encrypt** — Free SSL certificates
- **2FA/OAuth** — Email-based login
- **Rate limiting** — Prevent brute force attacks

See feature docs: `docs/features/ngrok-tunneling.md`

## 🔒 Security Considerations

### Local Network Only (Default)

Default configuration is for **local network access only**:
- ✅ Safe for home/office WiFi
- ✅ Password protected
- ⚠️ **Do NOT expose directly to internet** (use ngrok tunneling instead)

### Password Management

1. **Strong Passwords**: Use generated passwords (default)
   ```bash
   # Generated during environment creation
   SERVER_PASSWORD=$(openssl rand -base64 12)
   ```

2. **Unique Per Environment**: Each environment should have different password

3. **Rotate Regularly**: Change passwords periodically
   ```bash
   # Edit .env file
   OPENCODE_SERVER_PASSWORD=new-password
   CODE_SERVER_PASSWORD=new-password
   
   # Restart
   docker compose restart
   ```

### Internet Access Security

For remote internet access:
- Use **ngrok tunneling** (recommended for on-demand, temporary access)
- Keep tunnels **short-lived** (only while working)
- Monitor activity at ngrok's dashboard
- Consider **ngrok paid tier** for production use (fixed domains, OAuth, IP allowlisting)
- Or set up **reverse proxy + SSL** (Traefik, Nginx) for permanent internet exposure

See `docs/features/ngrok-tunneling.md` for detailed ngrok documentation.

## 📊 Monitoring and Logs

### Check Environment Status

```bash
# Using TUI
./envman.py

# Using CLI
docker compose ps

# Check logs
docker compose logs -f
```

### code-server Logs

```bash
# View code-server logs
docker compose exec <container> cat /home/dev/.local/share/opencode/code-server.log

# Follow logs in real-time
docker compose exec <container> tail -f /home/dev/.local/share/opencode/code-server.log
```

### OpenCode Logs

```bash
# OpenCode server logs
docker compose logs -f
```

## 🐛 Troubleshooting

### code-server Won't Start

1. **Check port not in use**:
   ```bash
   sudo netstat -tlnp | grep 8096
   ```

2. **Check logs**:
   ```bash
   docker compose logs | grep code-server
   ```

3. **Verify configuration**:
   ```bash
   docker compose exec <container> cat /home/dev/.config/code-server/config.yaml
   ```

### Can't Access from Other Devices

1. **Firewall blocking**:
   ```bash
   sudo ufw status
   sudo ufw allow 8096/tcp
   ```

2. **Wrong IP address**: Find correct IP
   ```bash
   ip addr show
   ```

3. **Container not listening on 0.0.0.0**:
   Check `.env` has `CODE_SERVER_HOST=0.0.0.0`

### Namespace Not Visible

1. **Check mount**:
   ```bash
   docker compose exec <container> ls /home/dev/.opencode/namespaces/global
   ```

2. **Verify .env setting**:
   ```bash
   grep MOUNT_NAMESPACE_GLOBAL .env
   ```

3. **Restart container**:
   ```bash
   docker compose restart
   ```

### Password Not Working

1. **Check .env file**:
   ```bash
   grep PASSWORD .env
   ```

2. **Regenerate password**:
   ```bash
   # Edit .env
   CODE_SERVER_PASSWORD=$(openssl rand -base64 12)
   # Restart
   docker compose restart
   ```

## 📚 Additional Resources

- [Main README](../../README.md) - Project overview
- [QUICKSTART Guide](QUICKSTART.md) - Quick setup instructions
- [TUI Documentation](TUI-README.md) - Terminal UI guide
- [AGENTS.md](../technical/AGENTS.md) - Detailed technical documentation

### Namespace Documentation

- [Namespace System Overview](../../shared/namespaces/README.md)
- [Agents Guide](../../shared/namespaces/global/agents/README.md)
- [Skills Guide](../../shared/namespaces/global/skills/README.md)
- [Workflows Guide](../../shared/namespaces/global/workflows/README.md)
- [Context Guide](../../shared/namespaces/global/context/README.md)

## 🎉 What's Next?

Now that you have remote development set up:

1. **Create your first environment**
2. **Access it from browser**
3. **Try accessing from tablet/phone**
4. **Create team workflows in namespaces**
5. **Share agents with your team**

### Future Enhancements (Roadmap)

**Phase 2**: Web Management UI
- Visual dashboard for all environments
- Real-time log viewer
- Environment creation wizard
- Namespace management UI

**Phase 3**: Internet Access
- Traefik reverse proxy
- SSL certificates
- Domain-based routing
- Enhanced security (2FA, rate limiting)

**Phase 4**: Advanced Features
- Environment templates marketplace
- AI usage tracking
- Collaborative sessions
- Snapshot/restore

See `IMPLEMENTATION_ROADMAP.md` for detailed plans.

## 💬 Feedback

This is a new feature! We'd love your feedback:

- What works well?
- What's confusing?
- What features would you like to see?
- Any bugs or issues?

Open an issue or contribute improvements!

---

**Happy Remote Coding! 🚀**
