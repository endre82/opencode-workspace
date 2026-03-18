"""Environment model class"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class Environment:
    """Represents an OpenCode development environment"""
    
    # Basic information
    name: str
    path: Path
    
    # Container information
    container_name: str = ""
    hostname: str = ""
    
    # Status
    status: str = "unknown"
    
    # User configuration
    user_id: int = 1000
    group_id: int = 1000
    timezone: str = "UTC"
    
    # Network
    network_name: str = "opencode-network"
    
    # Server configuration
    server_enabled: bool = False
    server_host: str = "0.0.0.0"
    server_port: Optional[int] = None
    server_username: str = "opencode"
    server_password: str = ""
    server_cors: str = ""
    
    # Volume configuration
    workspace_dir: str = "./workspace"
    global_config: str = ""
    project_config: str = ""
    opencode_env_config: str = "./opencode_config"
    worktree_dir: str = "./worktree"
    shared_auth_config: str = "../../shared/auth/auth.json"
    
    # Volume mount flags
    mount_global_config: bool = False
    mount_project_config: bool = False
    mount_opencode_env_config: bool = True
    mount_shared_auth: bool = True
    
    # Resource limits
    memory_limit: str = ""
    cpu_limit: str = ""
    shm_size: str = ""
    
    # Additional metadata
    config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def env_file_path(self) -> Path:
        """Path to .env file"""
        return self.path / ".env"
    
    @property
    def docker_compose_path(self) -> Path:
        """Path to docker-compose.yml file"""
        return self.path / "docker-compose.yml"
    
    @property
    def server_url(self) -> str:
        """Server URL for connection"""
        if not self.server_enabled or not self.server_port:
            return ""
        host = "localhost" if self.server_host == "0.0.0.0" else self.server_host
        return f"http://{host}:{self.server_port}"
    
    @property
    def connection_command(self) -> str:
        """Full connection command"""
        if not self.server_enabled or not self.server_port:
            return ""
        
        return (
            f"OPENCODE_SERVER_USERNAME={self.server_username} "
            f"OPENCODE_SERVER_PASSWORD={self.server_password} "
            f"opencode attach {self.server_url}"
        )
    
    @property
    def is_running(self) -> bool:
        """Check if environment is running"""
        return self.status == "running"
    
    @property
    def is_stopped(self) -> bool:
        """Check if environment is stopped"""
        return self.status == "stopped"
    
    @property
    def status_icon(self) -> str:
        """Get status icon"""
        from envman.utils.constants import STATUS_ICONS
        return STATUS_ICONS.get(self.status, "⚪")
    
    def refresh_status(self, docker_service) -> None:
        """Refresh the environment status from Docker"""
        from envman.services.docker import DockerService
        if isinstance(docker_service, DockerService):
            self.status = docker_service.get_container_status(self.container_name)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.status})"
    
    def __repr__(self) -> str:
        return f"Environment(name={self.name!r}, status={self.status!r}, port={self.server_port})"
