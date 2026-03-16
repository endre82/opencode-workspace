"""
Configuration for the Web UI application.
"""
import os
from pathlib import Path


class Config:
    """Web UI configuration."""
    
    # Server settings
    HOST = os.getenv("WEBUI_HOST", "0.0.0.0")
    PORT = int(os.getenv("WEBUI_PORT", "9096"))
    
    # Authentication (matches OpenCode server)
    USERNAME = os.getenv("OPENCODE_SERVER_USERNAME", "opencode")
    PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD", "")
    
    # Environment info
    ENV_NAME = os.getenv("ENV_NAME", "unknown")
    CONTAINER_NAME = os.getenv("CONTAINER_NAME", "unknown")
    
    # Service ports
    OPENCODE_PORT = int(os.getenv("OPENCODE_SERVER_PORT", "4096"))
    CODESERVER_PORT = int(os.getenv("CODESERVER_PORT", "8096"))
    
    # Paths
    BASE_DIR = Path(__file__).parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    STATIC_DIR = BASE_DIR / "static"
    
    # Application settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD = False  # Disable auto-reload in production


config = Config()
