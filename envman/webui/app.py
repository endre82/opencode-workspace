"""
FastAPI application for per-environment web management UI.

This web UI runs inside each environment container and provides:
- Dashboard showing service status (OpenCode, code-server)
- Service management (restart services)
- Log viewing
- Environment information

Note: This manages services WITHIN the container, not the Docker container itself.
"""
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasicCredentials

from .config import config
from .auth import security, require_auth


# Create FastAPI app
app = FastAPI(
    title=f"OpenCode Environment Manager - {config.ENV_NAME}",
    description="Web UI for managing this OpenCode environment",
    version="0.1.0",
    docs_url="/api/docs" if config.DEBUG else None,
    redoc_url="/api/redoc" if config.DEBUG else None,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


def get_service_status(service_name: str) -> Dict[str, Any]:
    """
    Check if a service is running by checking its process.
    Returns status information.
    """
    try:
        # Check if process is running using pgrep
        result = subprocess.run(
            ["pgrep", "-f", service_name],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        is_running = result.returncode == 0
        pid = result.stdout.strip() if is_running else None
        
        return {
            "name": service_name,
            "status": "running" if is_running else "stopped",
            "pid": pid,
            "checked_at": datetime.now().isoformat()
        }
    except subprocess.TimeoutExpired:
        return {
            "name": service_name,
            "status": "unknown",
            "pid": None,
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "name": service_name,
            "status": "error",
            "pid": None,
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }


def get_log_tail(log_file: str, lines: int = 100) -> Optional[str]:
    """Get last N lines from a log file."""
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), log_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security)
):
    """Main dashboard page."""
    require_auth(credentials)
    
    # Get service statuses
    opencode_status = get_service_status("opencode serve")
    codeserver_status = get_service_status("code-server")
    
    context = {
        "request": request,
        "env_name": config.ENV_NAME,
        "container_name": config.CONTAINER_NAME,
        "opencode_port": config.OPENCODE_PORT,
        "codeserver_port": config.CODESERVER_PORT,
        "webui_port": config.PORT,
        "opencode_status": opencode_status,
        "codeserver_status": codeserver_status,
        "username": credentials.username,
    }
    
    return templates.TemplateResponse("dashboard.html", context)


@app.get("/api/status")
async def get_status(credentials: HTTPBasicCredentials = Depends(security)):
    """Get overall environment status."""
    require_auth(credentials)
    
    opencode_status = get_service_status("opencode serve")
    codeserver_status = get_service_status("code-server")
    
    return {
        "environment": config.ENV_NAME,
        "container": config.CONTAINER_NAME,
        "services": {
            "opencode": opencode_status,
            "codeserver": codeserver_status,
        },
        "ports": {
            "opencode": config.OPENCODE_PORT,
            "codeserver": config.CODESERVER_PORT,
            "webui": config.PORT,
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/services/{service_name}/restart")
async def restart_service(
    service_name: str,
    credentials: HTTPBasicCredentials = Depends(security)
):
    """
    Restart a service.
    Note: This is a placeholder. Service management would require supervisord or similar.
    """
    require_auth(credentials)
    
    if service_name not in ["opencode", "codeserver"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # TODO: Implement actual service restart via supervisord
    # For now, return a message indicating this feature is coming
    return {
        "success": False,
        "message": "Service restart not yet implemented. Use container restart instead.",
        "service": service_name
    }


@app.get("/api/logs/{service_name}")
async def get_logs(
    service_name: str,
    lines: int = 100,
    credentials: HTTPBasicCredentials = Depends(security)
):
    """Get logs for a service."""
    require_auth(credentials)
    
    if service_name not in ["opencode", "codeserver"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Map service names to log file paths
    log_paths = {
        "opencode": "/var/log/opencode.log",
        "codeserver": "/var/log/code-server.log",
    }
    
    log_content = get_log_tail(log_paths.get(service_name, ""), lines)
    
    if log_content is None:
        return {
            "success": False,
            "message": f"Could not read logs for {service_name}",
            "logs": ""
        }
    
    return {
        "success": True,
        "service": service_name,
        "lines": lines,
        "logs": log_content
    }


@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)."""
    return {
        "status": "healthy",
        "service": "webui",
        "environment": config.ENV_NAME,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "envman.webui.app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
