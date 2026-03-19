"""Environment creation service"""

import os
import shutil
import secrets
from pathlib import Path
from typing import Dict, Any, Tuple, List

from envman.utils.exceptions import ConfigurationError


class CreationService:
    """Service for creating new environments"""
    
    def __init__(self, workspace_root: Path):
        """Initialize with workspace root directory"""
        self.workspace_root = workspace_root
        self.environments_dir = workspace_root / "environments"
        self.template_dir = self.environments_dir / "template"
        self.shared_dir = workspace_root / "shared"
    
    def get_existing_environment_names(self) -> List[str]:
        """Get list of existing environment names"""
        if not self.environments_dir.exists():
            return []
        
        names = []
        for item in self.environments_dir.iterdir():
            if item.is_dir() and item.name not in ['template', 'shared']:
                names.append(item.name)
        return names
    
    def get_used_ports(self) -> List[int]:
        """Get list of ports already in use by environments"""
        used_ports = []
        
        if not self.environments_dir.exists():
            return used_ports
        
        for env_dir in self.environments_dir.iterdir():
            if not env_dir.is_dir() or env_dir.name in ['template', 'shared']:
                continue
            
            env_file = env_dir / ".env"
            if env_file.exists():
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('OPENCODE_SERVER_PORT='):
                                port_str = line.split('=')[1].strip()
                                try:
                                    used_ports.append(int(port_str))
                                except ValueError:
                                    pass
                except Exception:
                    pass
        
        return used_ports
    
    def find_next_available_port(self, starting_port: int = 4100) -> int:
        """Find the next available port"""
        used_ports = self.get_used_ports()
        port = starting_port
        
        while port in used_ports:
            port += 1
        
        return port
    
    def generate_random_password(self, length: int = 16) -> str:
        """Generate a random password"""
        return secrets.token_urlsafe(length)[:length]
    
    def create_environment(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create new environment with given configuration
        
        Args:
            config: Configuration dictionary with all settings
        
        Returns:
            (success, message) tuple
        """
        env_name = config['name']
        env_dir = self.environments_dir / env_name
        
        try:
            # Validate template exists
            if not self.template_dir.exists():
                return False, f"Template directory not found: {self.template_dir}"
            
            env_template = self.template_dir / ".env.template"
            compose_template = self.template_dir / "docker-compose.yml.template"
            
            if not env_template.exists():
                return False, f"Template .env file not found: {env_template}"
            
            if not compose_template.exists():
                return False, f"Template docker-compose.yml not found: {compose_template}"
            
            # Create directory structure
            env_dir.mkdir(parents=True, exist_ok=False)
            (env_dir / "workspace").mkdir(exist_ok=True)
            (env_dir / "opencode_config").mkdir(exist_ok=True)
            
            # Create shared directories if needed
            (self.shared_dir / "config").mkdir(parents=True, exist_ok=True)
            (self.shared_dir / "models").mkdir(parents=True, exist_ok=True)
            
            # Copy and process .env template
            self._create_env_file(env_dir / ".env", env_template, env_name, config)
            
            # Copy and process docker-compose.yml template
            self._create_compose_file(
                env_dir / "docker-compose.yml",
                compose_template,
                env_name,
                config
            )
            
            return True, f"Environment '{env_name}' created successfully"
        
        except FileExistsError:
            return False, f"Environment '{env_name}' already exists"
        except Exception as e:
            # Clean up on error
            if env_dir.exists():
                try:
                    shutil.rmtree(env_dir)
                except Exception:
                    pass
            return False, f"Failed to create environment: {e}"
    
    def _create_env_file(self, target_path: Path, template_path: Path, env_name: str, config: Dict[str, Any]) -> None:
        """Create .env file from template"""
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Replace template variables
        content = content.replace('{{ENV_NAME}}', env_name)
        
        # Determine SSH configuration
        ssh_mode = config.get("ssh_mode", "default")
        if ssh_mode == "default":
            ssh_config_path = config.get("ssh_host_path", str(Path.home() / ".ssh"))
        else:  # project mode
            ssh_config_path = config.get("ssh_project_path", "./ssh_config")
        
        # Replace configuration values
        replacements = {
            'USER_ID=1000': f'USER_ID={int(config["user_id"])}',
            'GROUP_ID=1000': f'GROUP_ID={int(config["group_id"])}',
            'TIMEZONE=UTC': f'TIMEZONE={config.get("timezone", "UTC")}',
            'CONTAINER_NAME=opencode-{{ENV_NAME}}': f'CONTAINER_NAME=opencode-{env_name}',
            'HOSTNAME=opencode-{{ENV_NAME}}': f'HOSTNAME=opencode-{env_name}',
            'OPENCODE_SERVER_PORT=4096': f'OPENCODE_SERVER_PORT={int(config["server_port"])}',
            'OPENCODE_SERVER_USERNAME=opencode': f'OPENCODE_SERVER_USERNAME={config["server_username"]}',
            'OPENCODE_SERVER_PASSWORD=': f'OPENCODE_SERVER_PASSWORD={config["server_password"]}',
            'WORKSPACE_DIR=./workspace': f'WORKSPACE_DIR={config["workspace_dir"]}',
            'GLOBAL_CONFIG=../shared/config/.opencode': f'GLOBAL_CONFIG={config.get("global_config", "../shared/config/.opencode")}',
            'PROJECT_CONFIG=./opencode_project_config': f'PROJECT_CONFIG={config.get("project_config", "./opencode_project_config")}',
            'OPENCODE_ENV_CONFIG=./opencode_config': f'OPENCODE_ENV_CONFIG={config.get("opencode_env_config", "./opencode_config")}',
            'WORKTREE_DIR=./worktree': f'WORKTREE_DIR={config.get("worktree_dir", "./worktree")}',
            'SHARED_AUTH_CONFIG=../../shared/auth/auth.json': f'SHARED_AUTH_CONFIG={config.get("shared_auth_config", "../../shared/auth/auth.json")}',
            'MOUNT_GLOBAL_CONFIG=false': f'MOUNT_GLOBAL_CONFIG={str(config.get("mount_global_config", False)).lower()}',
            'MOUNT_PROJECT_CONFIG=false': f'MOUNT_PROJECT_CONFIG={str(config.get("mount_project_config", False)).lower()}',
            'MOUNT_OPENCODE_ENV_CONFIG=true': f'MOUNT_OPENCODE_ENV_CONFIG={str(config.get("mount_opencode_env_config", True)).lower()}',
            'MOUNT_SHARED_AUTH=true': f'MOUNT_SHARED_AUTH={str(config.get("mount_shared_auth", True)).lower()}',
            'SSH_MODE=default': f'SSH_MODE={ssh_mode}',
            'SSH_HOST_PATH=/home/endre/.ssh': f'SSH_HOST_PATH={config.get("ssh_host_path", str(Path.home() / ".ssh"))}',
            'SSH_PROJECT_PATH=./ssh_config': f'SSH_PROJECT_PATH={config.get("ssh_project_path", "./ssh_config")}',
            'SSH_CONFIG=/home/endre/.ssh': f'SSH_CONFIG={ssh_config_path}',
        }
        
        # Calculate code-server port (server_port + 4000)
        code_server_port = int(config["server_port"]) + 4000
        replacements['CODE_SERVER_PORT=8096'] = f'CODE_SERVER_PORT={code_server_port}'
        replacements['CODE_SERVER_PASSWORD='] = f'CODE_SERVER_PASSWORD={config["server_password"]}'
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(target_path, 'w') as f:
            f.write(content)
    
    def _create_compose_file(self, target_path: Path, template_path: Path, env_name: str, config: Dict[str, Any]) -> None:
        """Create docker-compose.yml from template"""
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Replace template variables
        content = content.replace('{{ENV_NAME}}', env_name)
        
        # SSH mount is always active (mandatory) - no conditional handling needed
        # The template already has it uncommented
        
        # Uncomment volume mounts based on configuration
        if config.get('mount_global_config', False):
            content = content.replace(
                '      # - ${GLOBAL_CONFIG}:/home/dev/.config/opencode:ro',
                '      - ${GLOBAL_CONFIG}:/home/dev/.config/opencode:ro'
            )
        
        if config.get('mount_project_config', False):
            content = content.replace(
                '      # - ${PROJECT_CONFIG}:/home/dev/workspace/.opencode:rw',
                '      - ${PROJECT_CONFIG}:/home/dev/workspace/.opencode:rw'
            )
        
        if config.get('mount_worktree', False):
            content = content.replace(
                '      # - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw',
                '      - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw'
            )
        
        if config.get('mount_shared_auth', True):
            content = content.replace(
                '      # - ${SHARED_AUTH_CONFIG}:/home/dev/.local/share/opencode/auth.json:ro',
                '      - ${SHARED_AUTH_CONFIG}:/home/dev/.local/share/opencode/auth.json:ro'
            )
        
        with open(target_path, 'w') as f:
            f.write(content)
    
    def get_creation_summary(self, config: Dict[str, Any]) -> str:
        """Generate a summary of the configuration"""
        lines = []
        lines.append("Configuration Summary:")
        lines.append("")
        lines.append(f"Environment Name: {config['name']}")
        lines.append("")
        lines.append("User Configuration:")
        lines.append(f"  USER_ID:  {config['user_id']}")
        lines.append(f"  GROUP_ID: {config['group_id']}")
        lines.append("")
        lines.append("Workspace:")
        lines.append(f"  Type: {config.get('workspace_type', 'Isolated')}")
        lines.append(f"  Path: {config['workspace_dir']}")
        lines.append("")
        lines.append("SSH Configuration:")
        ssh_mode = config.get("ssh_mode", "default")
        if ssh_mode == "default":
            ssh_path = config.get('ssh_host_path', str(Path.home() / '.ssh'))
            lines.append(f"  Mode: Default (using host ~/.ssh)")
            lines.append(f"  Source: {ssh_path}")
            lines.append(f"  Destination: /home/dev/.ssh (ro)")
        else:
            ssh_path = config.get('ssh_project_path', './ssh_config')
            lines.append(f"  Mode: Project-Based")
            lines.append(f"  Source: {ssh_path}")
            lines.append(f"  Destination: /home/dev/.ssh (ro)")
        lines.append("")
        lines.append("Volume Mounts:")
        lines.append("  Always mounted:")
        lines.append(f"    ✓ WORKSPACE_DIR → /workspace (rw)")
        env_config = config.get('opencode_env_config', './opencode_config')
        lines.append(f"    ✓ OPENCODE_ENV_CONFIG: {env_config} → /home/dev/.opencode (rw)")
        
        # Optional mounts
        optional_enabled = []
        optional_disabled = []
        
        if config.get('mount_global_config'):
            global_path = config.get('global_config', '../shared/config/.opencode')
            optional_enabled.append(f"    ✓ GLOBAL_CONFIG: {global_path} → /home/dev/.config/opencode (ro)")
        else:
            optional_disabled.append("    ✗ GLOBAL_CONFIG")
        
        if config.get('mount_project_config'):
            project_path = config.get('project_config', './opencode_project_config')
            optional_enabled.append(f"    ✓ PROJECT_CONFIG: {project_path} → /home/dev/workspace/.opencode (rw)")
        else:
            optional_disabled.append("    ✗ PROJECT_CONFIG")
        
        if config.get('mount_worktree'):
            worktree_path = config.get('worktree_dir', './worktree')
            optional_enabled.append(f"    ✓ WORKTREE_DIR: {worktree_path} → /home/dev/.local/share/opencode/worktree (rw)")
        else:
            optional_disabled.append("    ✗ WORKTREE_DIR")
        
        if config.get('mount_shared_auth', True):
            optional_enabled.append(f"    ✓ SHARED_AUTH: ../../shared/auth/auth.json → /home/dev/.local/share/opencode/auth.json (ro)")
        else:
            optional_disabled.append("    ✗ SHARED_AUTH")
        
        if optional_enabled:
            lines.append("  Optional (enabled):")
            lines.extend(optional_enabled)
        
        if optional_disabled:
            lines.append("  Optional (disabled):")
            lines.extend(optional_disabled)
        
        lines.append("")
        lines.append("Server Configuration:")
        lines.append(f"  Port:     {config['server_port']}")
        lines.append(f"  Username: {config['server_username']}")
        lines.append(f"  Password: {'*' * len(config['server_password'])}")
        
        return "\n".join(lines)
