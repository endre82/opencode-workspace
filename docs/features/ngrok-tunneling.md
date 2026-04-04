# ngrok Tunnel Management — Feature Documentation

**Status:** Implemented ✅  
**Feature:** On-demand ngrok tunneling for remote OpenCode and VSCode access  
**Release:** Recent  

## Overview

The ngrok tunneling feature enables users to expose their OpenCode server and VSCode (code-server) over the internet on-demand using ngrok's tunneling service. This is useful for remote development from any location.

### Key Characteristics

- **On-demand**: Tunnels start/stop via TUI (press `t` on Dashboard)
- **Free tier compatible**: Works with ngrok free plan (single tunnel at a time)
- **Automatic cleanup**: Orphaned processes killed on app exit
- **Security conscious**: Includes warnings about free tier bot scanning
- **Both services**: Tunnels OpenCode server (API + web UI) and VSCode (code-server)
- **URL copying**: One-click copy of public URLs + password to clipboard

## Implementation Details

### Files Modified

**New Files:**
- `envman/services/ngrok.py` — NgrokService class
- `envman/screens/modals/tunnel.py` — TunnelModal screen

**Modified Files:**
- `envman/screens/dashboard.py` — Added tunnel binding, column, action
- `envman/app.py` — Instantiate and cleanup NgrokService
- Root `AGENTS.md` — No longer contains user docs (see user guides instead)

### Architecture

```
┌─────────────────────┐
│   Dashboard TUI     │
│  Press 't' key     │
└──────────┬──────────┘
           │ action_tunnel()
           ↓
┌─────────────────────────┐
│   TunnelModal Screen    │
│  • Start Tunnel button  │
│  • Stop Tunnel button   │
│  • Copy URLs button     │
│  • Shows public URLs    │
└──────────┬──────────────┘
           │ NgrokService
           ↓
┌─────────────────────────────────────┐
│      NgrokService                   │
│  • Write ngrok config               │
│  • Spawn ngrok subprocess           │
│  • Poll http://127.0.0.1:4040/api   │
│  • Track tunneled env               │
│  • Kill process on cleanup          │
└──────────┬──────────────────────────┘
           │
           ↓
     [Host ngrok]
       (port 4040)
           │
      Tunnels to:
      • localhost:4096 (OpenCode)
      • localhost:8096 (VSCode)
           │
           ↓
    [Public ngrok URLs]
    (abc123.ngrok-free.app)
```

### NgrokService Class

**Location:** `envman/services/ngrok.py`

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `is_available()` | Check if ngrok binary installed |
| `start(env_name, opencode_port, vscode_port)` | Start tunnel, return public URLs |
| `stop()` | Kill ngrok process |
| `is_running()` | Check if tunnel active |
| `get_status()` | Get env name, URLs, PID |
| `cleanup()` | Called on app exit (atexit handler) |

**Features:**
- Auto-detects ngrok installation
- Enforces single-tunnel constraint (free tier)
- Polls ngrok API for URLs (10s timeout with 0.5s retry)
- Handles process lifecycle and cleanup
- Thread-safe subprocess management

### TunnelModal Screen

**Location:** `envman/screens/modals/tunnel.py`

**Features:**
- Status display (inactive/starting/active/error)
- Public URL display (OpenCode + VSCode)
- Copy to clipboard (includes password)
- Start/Stop buttons with async operations
- Free tier security warnings
- Real-time status updates

### Dashboard Integration

**Column:** 5th column shows "🔗" indicator when tunnel is active for that environment

**Binding:** Press `t` to open tunnel modal for selected environment

**Checks Before Opening:**
- Environment is running
- OpenCode server enabled and port configured
- VSCode server port configured

### Configuration

**Config Files Location:**
```
~/.local/share/opencode-workspace/ngrok/<environment-name>.yml
```

**Config Format:**
```yaml
version: 2
tunnels:
  opencode:
    addr: 4096
    proto: http
  vscode:
    addr: 8096
    proto: http
```

## Usage Workflow

1. Start an environment in Dashboard
2. Press `t` on that environment
3. TunnelModal opens, shows current status
4. Click "Start Tunnel"
5. Modal shows public URLs for OpenCode and VSCode
6. Click "Copy URLs" to get URLs + password
7. Share URLs with others for remote access
8. Click "Stop Tunnel" when done (or app exits auto-stops)

## Free Tier Limitations

### Constraints

⚠️ **Single Agent Limit**: Only one ngrok process runs at a time (free tier constraint)
- If you tunnel env A, then env B, tunnel A stops automatically

⚠️ **Random URLs**: Free tier generates random subdomains
- Example: `abc123-def456.ngrok-free.app`
- URLs change each time tunnel starts
- Gets scanned by bots within minutes

⚠️ **No OAuth**: No email verification or IP allowlisting
- Password auth is your only defense
- Interstitial warning page on first visit (helps filter bots)

### Security Mitigations

✓ **On-demand only**: Control exposure window (not always-on)  
✓ **Password protected**: Same `OPENCODE_SERVER_PASSWORD` as normal access  
✓ **WebUI not tunneled**: Admin interface stays internal  
✓ **Auto-cleanup**: Orphaned processes killed on exit  

**Recommendations:**
- Keep tunnels short-lived (only while actively working)
- Use strong passwords
- Monitor activity at `http://127.0.0.1:4040`
- Consider ngrok paid tier ($8/mo+) for OAuth and fixed domains

## API Reference

### ngrok Local API

NgrokService queries `http://127.0.0.1:4040/api/tunnels` to get public URLs.

**Response Example:**
```json
{
  "tunnels": [
    {
      "name": "opencode",
      "public_url": "https://abc123.ngrok-free.app",
      "proto": "http",
      "addr": "localhost:4096"
    },
    {
      "name": "vscode",
      "public_url": "https://def456.ngrok-free.app",
      "proto": "http",
      "addr": "localhost:8096"
    }
  ]
}
```

## Troubleshooting

### ngrok not installed
```
Error: "ngrok not installed. Install it with: snap install ngrok..."
```
**Fix:** Install ngrok
```bash
snap install ngrok
ngrok config add-authtoken <token>
```

### Could not reach ngrok API
```
Error: "Could not reach ngrok API (http://127.0.0.1:4040)"
```
**Cause:** ngrok process crashed or isn't running  
**Fix:** Stop tunnel and restart

### Tunnel URLs not appearing
```
Error: "Tunnel setup timed out after 10s..."
```
**Cause:** ngrok process died or port conflict  
**Fixes:**
- Check logs: `ps aux | grep ngrok`
- Kill stray ngrok: `pkill ngrok`
- Check port 4040 is free

### Port conflict
**Cause:** Another ngrok instance running  
**Fix:** `pkill ngrok` or use different user session

## Related Documentation

- **User Guide:** See `docs/guides/remote-dev-guide.md` for user-facing instructions
- **TUI Reference:** Press `?` in Dashboard for quick help
- **Namespace Sharing:** `docs/guides/remote-dev-guide.md` — sharing agents/skills

## Implementation Notes

- ngrok runs as host process (not containerized)
- Subprocess lifecycle managed with atexit handler
- Config written to `~/.local/share/opencode-workspace/ngrok/`
- Single tunnel enforced at service level
- Thread-safe subprocess management
