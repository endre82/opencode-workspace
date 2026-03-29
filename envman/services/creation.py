"""Environment creation service"""

import os
import re
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
            
            # Create project config directory and file if in project mode
            mode = config.get('opencode_config_mode', 'project')
            if mode == 'project':
                project_config_dir = env_dir / "opencode_project_config"
                project_config_dir.mkdir(exist_ok=True)
                # Create empty opencode.jsonc for project mode
                project_jsonc = project_config_dir / "opencode.jsonc"
                if not project_jsonc.exists():
                    project_jsonc.write_text('{}')
            
            # Create worktree directory if mounting is enabled
            if config.get('mount_worktree') and config.get('worktree_dir'):
                worktree_path = Path(config['worktree_dir']).expanduser()
                if not worktree_path.is_absolute():
                    worktree_path = env_dir / worktree_path
                worktree_path.mkdir(parents=True, exist_ok=True)
            
            # Create shared directories if needed
            (self.shared_dir / "config").mkdir(parents=True, exist_ok=True)
            (self.shared_dir / "models").mkdir(parents=True, exist_ok=True)
            (self.shared_dir / "auth").mkdir(parents=True, exist_ok=True)
            
            # Create global opencode.jsonc and auth.json if in global mode
            if mode == 'global':
                global_jsonc = self.shared_dir / "config" / "opencode.jsonc"
                if not global_jsonc.exists():
                    global_jsonc.write_text('{}')
                global_auth = self.shared_dir / "auth" / "auth.json"
                if not global_auth.exists():
                    global_auth.write_text('{}')
            
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
        
        # Build replacements list
        replacements = [
            ('USER_ID=1000', f'USER_ID={int(config["user_id"])}'),
            ('GROUP_ID=1000', f'GROUP_ID={int(config["group_id"])}'),
            ('TIMEZONE=UTC', f'TIMEZONE={config.get("timezone", "UTC")}'),
            ('OPENCODE_SERVER_PORT=4096', f'OPENCODE_SERVER_PORT={int(config["server_port"])}'),
            ('OPENCODE_SERVER_USERNAME=opencode', f'OPENCODE_SERVER_USERNAME={config["server_username"]}'),
            ('CODE_SERVER_PORT=8096', f'CODE_SERVER_PORT={int(config["server_port"]) + 4000}'),
            ('WEBUI_PORT=9096', f'WEBUI_PORT={int(config["server_port"]) + 5000}'),
            ('WORKSPACE_DIR=./workspace', f'WORKSPACE_DIR={config["workspace_dir"]}'),
            ('WORKTREE_DIR=${WORKSPACE_DIR}.worktrees', f'WORKTREE_DIR={config.get("worktree_dir", "./workspace.worktrees")}'),
            ('SSH_MODE=default', f'SSH_MODE={ssh_mode}'),
            ('SSH_HOST_PATH=/home/endre/.ssh', f'SSH_HOST_PATH={config.get("ssh_host_path", str(Path.home() / ".ssh"))}'),
            ('SSH_PROJECT_PATH=./ssh_config', f'SSH_PROJECT_PATH={config.get("ssh_project_path", "./ssh_config")}'),
            ('SSH_CONFIG=/home/endre/.ssh', f'SSH_CONFIG={ssh_config_path}'),
            # OpenCode Config Mode
            ('OPENCODE_CONFIG_MODE=project', f'OPENCODE_CONFIG_MODE={config.get("opencode_config_mode", "project")}'),
            ('OPENCODE_ENV_CONFIG=./opencode_config', f'OPENCODE_ENV_CONFIG=./opencode_config'),  # always ./opencode_config
            ('HOST_OPENCODE_JSONC=/home/endre/.opencode/opencode.jsonc', f'HOST_OPENCODE_JSONC={str(Path.home() / ".opencode" / "opencode.jsonc")}'),
            ('HOST_OPENCODE_AUTH=/home/endre/.local/share/opencode/auth.json', f'HOST_OPENCODE_AUTH={str(Path.home() / ".local" / "share" / "opencode" / "auth.json")}'),
        ]
        
        # Add mode-specific sources
        mode = config.get('opencode_config_mode', 'project')
        if mode == 'host':
            replacements.append(('OPENCODE_JSONC_SOURCE=./opencode_project_config/opencode.jsonc', f'OPENCODE_JSONC_SOURCE={str(Path.home() / ".opencode" / "opencode.jsonc")}'))
            replacements.append(('OPENCODE_AUTH_SOURCE=', f'OPENCODE_AUTH_SOURCE={str(Path.home() / ".local" / "share" / "opencode" / "auth.json")}'))
        elif mode == 'global':
            replacements.append(('OPENCODE_JSONC_SOURCE=./opencode_project_config/opencode.jsonc', 'OPENCODE_JSONC_SOURCE=../../shared/config/opencode.jsonc'))
            replacements.append(('OPENCODE_AUTH_SOURCE=', 'OPENCODE_AUTH_SOURCE=../../shared/auth/auth.json'))
        else:  # project
            replacements.append(('OPENCODE_JSONC_SOURCE=./opencode_project_config/opencode.jsonc', 'OPENCODE_JSONC_SOURCE=./opencode_project_config/opencode.jsonc'))
            replacements.append(('OPENCODE_AUTH_SOURCE=', 'OPENCODE_AUTH_SOURCE='))
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Handle passwords with regex to avoid substring collisions:
        # "CODE_SERVER_PASSWORD=" is a substring of "OPENCODE_SERVER_PASSWORD=",
        # so we use regex patterns to match only at the start of lines.
        server_password = config["server_password"]
        content = re.sub(r'^OPENCODE_SERVER_PASSWORD=.*$', f'OPENCODE_SERVER_PASSWORD={server_password}', content, flags=re.MULTILINE)
        content = re.sub(r'^CODE_SERVER_PASSWORD=.*$', f'CODE_SERVER_PASSWORD={server_password}', content, flags=re.MULTILINE)
        
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
        
        # Uncomment OpenCode config mounts based on mode
        mode = config.get('opencode_config_mode', 'project')
        
        if mode in ('host', 'global'):
            # Uncomment both :ro lines (config and auth files)
            content = content.replace(
                '      # - ${OPENCODE_JSONC_SOURCE}:/home/dev/.opencode/opencode.jsonc:ro',
                '      - ${OPENCODE_JSONC_SOURCE}:/home/dev/.opencode/opencode.jsonc:ro'
            )
            content = content.replace(
                '      # - ${OPENCODE_AUTH_SOURCE}:/home/dev/.local/share/opencode/auth.json:ro',
                '      - ${OPENCODE_AUTH_SOURCE}:/home/dev/.local/share/opencode/auth.json:ro'
            )
        else:  # project mode
            # Uncomment :rw line (config file only, auth is in env data dir)
            content = content.replace(
                '      # - ${OPENCODE_JSONC_SOURCE}:/home/dev/.opencode/opencode.jsonc:rw',
                '      - ${OPENCODE_JSONC_SOURCE}:/home/dev/.opencode/opencode.jsonc:rw'
            )
        
        # Uncomment worktree mount if enabled
        if config.get('mount_worktree', False):
            content = content.replace(
                '      # - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw',
                '      - ${WORKTREE_DIR}:/home/dev/.local/share/opencode/worktree:rw'
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
        lines.append("OpenCode Configuration:")
        mode = config.get('opencode_config_mode', 'project')
        lines.append(f"  Mode: {mode.upper()}")
        
        if mode == 'host':
            lines.append(f"    Config: ~/.opencode/opencode.jsonc (ro)")
            lines.append(f"    Auth: ~/.local/share/opencode/auth.json (ro)")
        elif mode == 'global':
            lines.append(f"    Config: ../../shared/config/opencode.jsonc (ro)")
            lines.append(f"    Auth: ../../shared/auth/auth.json (ro)")
        else:  # project
            lines.append(f"    Config: ./opencode_project_config/opencode.jsonc (rw)")
            lines.append(f"    Auth: inside env data directory (rw)")
        
        lines.append("")
        lines.append("Volume Mounts:")
        lines.append("  Always mounted:")
        lines.append(f"    ✓ WORKSPACE_DIR → /workspace (rw)")
        lines.append(f"    ✓ ENV_CONFIG (./opencode_config) → /home/dev/.local/share/opencode (rw)")
        
        # Optional mounts
        if config.get('mount_worktree'):
            worktree_path = config.get('worktree_dir', './workspace.worktrees')
            lines.append(f"    ✓ WORKTREE_DIR: {worktree_path} → /home/dev/.local/share/opencode/worktree (rw)")
        else:
            lines.append(f"    ✗ WORKTREE_DIR")
        
        lines.append("")
        lines.append("Server Configuration:")
        lines.append(f"  Port:     {config['server_port']}")
        lines.append(f"  Username: {config['server_username']}")
        lines.append(f"  Password: {'*' * len(config['server_password'])}")
        
        return "\n".join(lines)
