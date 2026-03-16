"""Environment discovery service"""

import os
from pathlib import Path
from typing import List, Optional

from envman.models.environment import Environment
from envman.services.config import ConfigService
from envman.services.docker import DockerService
from envman.utils.constants import (
    ENVIRONMENTS_DIR, 
    SKIP_DIRS, 
    CONTAINER_NAME_PREFIX,
    ENV_FILE,
    DOCKER_COMPOSE_FILE
)
from envman.utils.exceptions import EnvironmentNotFoundError


class DiscoveryService:
    """Service for discovering and loading environments"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize discovery service"""
        self.base_dir = base_dir or Path.cwd()
        self.environments_dir = self.base_dir / ENVIRONMENTS_DIR
        self.config_service = ConfigService()
        self.docker_service = DockerService()
    
    def discover_environments(self) -> List[Environment]:
        """Discover all environments in the environments directory"""
        environments = []
        
        if not self.environments_dir.exists():
            return environments
        
        for entry in self.environments_dir.iterdir():
            if not entry.is_dir():
                continue
            
            # Skip template and other special directories
            if entry.name in SKIP_DIRS:
                continue
            
            # Check if it has required files
            env_file = entry / ENV_FILE
            if not env_file.exists():
                continue
            
            try:
                env = self.load_environment(entry.name)
                if env:
                    environments.append(env)
            except Exception as e:
                print(f"Warning: Failed to load environment {entry.name}: {e}")
                continue
        
        return sorted(environments, key=lambda e: e.name)
    
    def load_environment(self, env_name: str) -> Optional[Environment]:
        """Load a specific environment by name"""
        env_path = self.environments_dir / env_name
        
        if not env_path.exists():
            raise EnvironmentNotFoundError(f"Environment not found: {env_name}")
        
        env_file = env_path / ENV_FILE
        if not env_file.exists():
            raise EnvironmentNotFoundError(f"Environment file not found: {env_file}")
        
        try:
            # Parse configuration
            config = self.config_service.parse_env_file(env_file)
            
            # Create environment object
            env = Environment(
                name=env_name,
                path=env_path,
            )
            
            # Populate from config
            self._populate_from_config(env, config)
            
            # Get Docker status
            env.status = self.docker_service.get_container_status(env.container_name)
            
            return env
        
        except Exception as e:
            print(f"Error loading environment {env_name}: {e}")
            return None
    
    def _populate_from_config(self, env: Environment, config: dict) -> None:
        """Populate environment object from configuration"""
        cs = self.config_service
        
        # Container info
        env.container_name = cs.get_str_value(
            config, "CONTAINER_NAME", 
            f"{CONTAINER_NAME_PREFIX}{env.name}"
        )
        env.hostname = cs.get_str_value(
            config, "HOSTNAME", 
            env.container_name
        )
        
        # User configuration
        env.user_id = cs.get_int_value(config, "USER_ID", 1000) or 1000
        env.group_id = cs.get_int_value(config, "GROUP_ID", 1000) or 1000
        env.timezone = cs.get_str_value(config, "TIMEZONE", "UTC")
        
        # Network
        env.network_name = cs.get_str_value(config, "NETWORK_NAME", "opencode-network")
        
        # Server configuration
        env.server_enabled = cs.get_bool_value(config, "OPENCODE_SERVER_ENABLED", False)
        env.server_host = cs.get_str_value(config, "OPENCODE_SERVER_HOST", "0.0.0.0")
        env.server_port = cs.get_int_value(config, "OPENCODE_SERVER_PORT")
        env.server_username = cs.get_str_value(config, "OPENCODE_SERVER_USERNAME", "opencode")
        env.server_password = cs.get_str_value(config, "OPENCODE_SERVER_PASSWORD", "")
        env.server_cors = cs.get_str_value(config, "OPENCODE_SERVER_CORS", "")
        
        # Volume configuration
        env.workspace_dir = cs.get_str_value(config, "WORKSPACE_DIR", "./workspace")
        env.global_config = cs.get_str_value(config, "GLOBAL_CONFIG", "")
        env.project_config = cs.get_str_value(config, "PROJECT_CONFIG", "")
        env.opencode_env_config = cs.get_str_value(config, "OPENCODE_ENV_CONFIG", "./opencode_config")
        env.worktree_dir = cs.get_str_value(config, "WORKTREE_DIR", "./worktree")
        
        # Volume mount flags
        env.mount_global_config = cs.get_bool_value(config, "MOUNT_GLOBAL_CONFIG", False)
        env.mount_project_config = cs.get_bool_value(config, "MOUNT_PROJECT_CONFIG", False)
        env.mount_opencode_env_config = cs.get_bool_value(config, "MOUNT_OPENCODE_ENV_CONFIG", True)
        
        # Resource limits
        env.memory_limit = cs.get_str_value(config, "MEMORY_LIMIT", "")
        env.cpu_limit = cs.get_str_value(config, "CPU_LIMIT", "")
        env.shm_size = cs.get_str_value(config, "SHM_SIZE", "")
        
        # Store full config for reference
        env.config = config
    
    def get_environment(self, env_name: str) -> Environment:
        """Get a specific environment (with error if not found)"""
        env = self.load_environment(env_name)
        if not env:
            raise EnvironmentNotFoundError(f"Failed to load environment: {env_name}")
        return env
    
    def environment_exists(self, env_name: str) -> bool:
        """Check if environment exists"""
        env_path = self.environments_dir / env_name
        env_file = env_path / ENV_FILE
        return env_path.exists() and env_file.exists()
    
    def refresh_environment(self, env: Environment) -> Optional[Environment]:
        """Refresh environment data (reload from disk and update status)"""
        return self.load_environment(env.name)
