# Web Management UI Guide

The Web Management UI provides a browser-based dashboard for monitoring and managing your OpenCode environment.

## Overview

Each environment includes a lightweight web interface that runs inside the container, providing:

- **Real-time service status** monitoring (OpenCode Server, code-server)
- **Service information** (PIDs, ports, last check times)
- **Quick access links** to OpenCode API docs and VSCode
- **Environment details** (name, container, ports)
- **Auto-refreshing dashboard** (updates every 5 seconds)
- **Mobile-responsive design** optimized for phones and tablets

## Features

### ✅ What It Does

- **Monitor Services**: View real-time status of OpenCode and code-server
- **Quick Access**: Direct links to VSCode, OpenCode API docs, and the Web UI itself
- **Environment Info**: See container name, environment name, and all port assignments
- **Secure Access**: Basic Auth using same credentials as OpenCode server
- **Mobile Friendly**: Responsive design works on laptop, tablet, or phone

### ⚠️ What It Doesn't Do (Yet)

- **Service Control**: Cannot start/stop/restart services (requires supervisord)
- **Log Viewing**: Cannot view service logs through UI (coming in future updates)
- **Docker Management**: Cannot manage the Docker container itself (use TUI or CLI)

## Accessing the Web UI

### Port Assignment

The Web UI follows the port offset pattern:

```
BASE_PORT       → OpenCode Server  (e.g., 4100)
BASE_PORT+4000  → code-server      (e.g., 8100)
BASE_PORT+5000  → Web UI           (e.g., 9100)
```

### Find Your Web UI Port

1. **Check environment creation output**:
   ```bash
   # During creation, you'll see:
   Access your environment:
     Web Management UI: http://localhost:9100
   ```

2. **Check .env file**:
   ```bash
   cd environments/your-env-name
   grep WEBUI_PORT .env
   ```

3. **Use the TUI**:
   ```bash
   ./envman.py
   # Navigate to your environment to see all ports
   ```

### Login Credentials

The Web UI uses the same authentication as your OpenCode server:

- **Username**: Value of `OPENCODE_SERVER_USERNAME` (default: `opencode`)
- **Password**: Value of `OPENCODE_SERVER_PASSWORD`

You set these during environment creation.

## Using the Dashboard

### Main Dashboard

The dashboard shows three main sections:

#### 1. Services Status

Displays real-time status of each service:

- **OpenCode Server**: Shows if running, port, PID, last check time
- **code-server**: Shows if running, port, PID, last check time

Status indicators:
- 🟢 **RUNNING**: Service is active
- 🔴 **STOPPED**: Service is not running
- 🟡 **UNKNOWN**: Status cannot be determined

Auto-refreshes every 5 seconds via HTMX.

#### 2. Access Ports

Quick access cards for each service:

- **OpenCode API**: Port number and link to API documentation
- **VSCode (code-server)**: Port number and link to open VSCode
- **Web Management UI**: Port number (current page)

Click the "→ Open" links to launch each service in a new tab.

#### 3. Environment Information

Details about your environment:

- **Environment Name**: Your environment identifier
- **Container Name**: Docker container name
- **Web UI Version**: Current version of the Web UI

## Configuration

### Environment Variables

Configure the Web UI in your environment's `.env` file:

```bash
# Web Management UI Configuration
WEBUI_ENABLED=true          # Enable/disable Web UI
WEBUI_PORT=9096            # Port for Web UI (auto-assigned)
WEBUI_HOST=0.0.0.0         # Bind address (0.0.0.0 for all interfaces)
ENV_NAME=your-env-name     # Environment name (displayed in UI)
```

### Docker Compose

The Web UI is automatically configured in `docker-compose.yml`:

```yaml
ports:
  - "${WEBUI_PORT}:${WEBUI_PORT}"

environment:
  - WEBUI_ENABLED=${WEBUI_ENABLED:-true}
  - WEBUI_PORT=${WEBUI_PORT:-9096}
  - WEBUI_HOST=${WEBUI_HOST:-0.0.0.0}
  - CONTAINER_NAME=${CONTAINER_NAME}
  - ENV_NAME=${ENV_NAME}

volumes:
  # Mount envman package for Web UI access
  - ../../envman:/home/dev/envman:ro
```

### Disabling the Web UI

To disable the Web UI for a specific environment:

```bash
# In your environment's .env file
WEBUI_ENABLED=false

# Restart container
docker compose down
docker compose up -d
```

## API Endpoints

The Web UI exposes several API endpoints you can use programmatically:

### GET /health

Health check endpoint (no authentication required).

```bash
curl http://localhost:9096/health
```

Response:
```json
{
  "status": "healthy",
  "service": "webui",
  "environment": "my-env",
  "timestamp": "2026-03-16T23:47:03.496436"
}
```

### GET /api/status

Get comprehensive environment status (requires authentication).

```bash
curl -u opencode:yourpassword http://localhost:9096/api/status
```

Response:
```json
{
  "environment": "my-env",
  "container": "opencode-my-env",
  "services": {
    "opencode": {
      "name": "opencode serve",
      "status": "running",
      "pid": "123",
      "checked_at": "2026-03-16T23:47:07.731976"
    },
    "codeserver": {
      "name": "code-server",
      "status": "running",
      "pid": "456",
      "checked_at": "2026-03-16T23:47:07.735927"
    }
  },
  "ports": {
    "opencode": 4100,
    "codeserver": 8100,
    "webui": 9100
  },
  "timestamp": "2026-03-16T23:47:07.735949"
}
```

### GET /api/logs/{service_name}

Get recent logs for a service (requires authentication).

```bash
# Get OpenCode logs
curl -u opencode:yourpassword http://localhost:9096/api/logs/opencode?lines=50

# Get code-server logs
curl -u opencode:yourpassword http://localhost:9096/api/logs/codeserver?lines=100
```

## Troubleshooting

### Web UI Not Starting

1. **Check if enabled**:
   ```bash
   grep WEBUI_ENABLED environments/your-env/.env
   ```

2. **Check logs**:
   ```bash
   docker compose logs | grep -i webui
   # Or check inside container:
   docker compose exec opencode-your-env cat /home/dev/.local/share/opencode/webui.log
   ```

3. **Check if port is available**:
   ```bash
   netstat -tuln | grep 9096
   ```

4. **Restart container**:
   ```bash
   docker compose restart
   ```

### Cannot Access Web UI

1. **Verify service is running**:
   ```bash
   curl http://localhost:9096/health
   ```

2. **Check credentials**:
   ```bash
   grep OPENCODE_SERVER_USERNAME environments/your-env/.env
   grep OPENCODE_SERVER_PASSWORD environments/your-env/.env
   ```

3. **Check browser console** for authentication issues

4. **Try different browser** (clear cache/cookies if needed)

### Wrong Port Displayed

If the API shows incorrect port numbers:

1. **Check environment variables are set**:
   ```bash
   docker compose exec opencode-your-env env | grep -E "OPENCODE_SERVER_PORT|CODESERVER_PORT|WEBUI_PORT"
   ```

2. **Verify .env file**:
   ```bash
   cat environments/your-env/.env | grep -E "_PORT"
   ```

3. **Restart container** after fixing .env:
   ```bash
   docker compose down
   docker compose up -d
   ```

## Architecture

The Web UI is built with:

- **FastAPI**: Python web framework
- **Uvicorn**: ASGI server
- **Jinja2**: Template engine
- **HTMX**: Dynamic HTML updates without JavaScript
- **Alpine.js**: Minimal JavaScript for interactivity

Key design decisions:

- **Per-environment service**: Each container runs its own Web UI
- **Read-only mount**: The `envman` package is mounted read-only from host
- **Basic Auth**: Uses same credentials as OpenCode server
- **Lightweight**: Minimal dependencies, fast startup
- **Mobile-first**: Responsive design for all devices

## Future Enhancements

Planned features for future releases:

- ✨ Service restart functionality (requires supervisord integration)
- 📊 Real-time log viewing with filtering
- 📈 Resource usage metrics (CPU, memory, disk)
- 🔔 Service health alerts
- ⚙️ Environment configuration editor
- 🔄 Container management (start/stop/restart)

## Related Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [REMOTE_DEV_GUIDE.md](REMOTE_DEV_GUIDE.md) - Remote development with code-server
- [TUI-README.md](TUI-README.md) - Terminal UI application guide
- [Main README](../../README.md) - Project overview

---

**Need help?** Check the troubleshooting section above or consult the main [README](../../README.md).
