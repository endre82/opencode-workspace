"""Configuration editor screen"""

import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Input, Button, Switch, Label, Checkbox
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding
from rich.text import Text

from envman.models.environment import Environment
from envman.services.config import ConfigService
from envman.utils.exceptions import ConfigurationError
from envman.utils.exception_logger import set_context


class ConfigScreen(Screen):
    """Configuration editor screen for .env file"""
    
    CSS = """
    ConfigScreen {
        layout: vertical;
    }
    
    #config-container {
        height: 100%;
        width: 100%;
    }
    
    #header-section {
        dock: top;
        height: auto;
        background: $panel;
        padding: 1 2;
        border-bottom: solid $primary;
    }
    
    #form-container {
        height: 1fr;
        border: solid $primary;
        padding: 1 2;
    }
    
    #button-bar {
        dock: bottom;
        height: 3;
        background: $panel;
        padding: 0 2;
        align-horizontal: center;
    }
    
    .section-header {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-top: 1;
        text-style: bold;
    }
    
    .form-group {
        height: auto;
        margin: 0 0 1 0;
    }
    
    .form-label {
        width: 30;
        color: $text-muted;
        content-align: right middle;
        margin-right: 1;
    }
    
    .form-input {
        width: 50;
    }
    
    .form-help {
        color: $text-muted;
        text-style: italic;
        margin-left: 31;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    .warning-text {
        color: $warning;
        text-style: bold;
        padding: 1;
        background: $panel;
        margin: 1 0;
    }
    
    Checkbox {
        margin-left: 31;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("ctrl+b", "backup", "Backup"),
    ]
    
    def __init__(self, environment: Environment):
        super().__init__()
        self.environment = environment
        self.config_service = ConfigService()
        self.original_config: Dict[str, Any] = {}
        self.has_changes = False
    
    def compose(self) -> ComposeResult:
        """Compose the config editor UI"""
        yield Header()
        
        with Container(id="config-container"):
            # Header section
            with Vertical(id="header-section"):
                yield Static(
                    f"[bold]Configuration Editor[/bold] - {self.environment.name}",
                    id="title"
                )
                yield Static(
                    f"Editing: {self.environment.env_file_path}",
                    id="subtitle"
                )
            
            # Form container
            with ScrollableContainer(id="form-container"):
                yield self._create_form()
            
            # Button bar
            with Horizontal(id="button-bar"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Reset", variant="default", id="btn-reset")
                yield Button("Backup", variant="default", id="btn-backup")
                yield Button("Cancel", variant="default", id="btn-cancel")
        
        yield Footer()
    
    def _create_form(self) -> ComposeResult:
        """Create form inputs for configuration"""
        
        # Server Configuration Section
        yield Static("Server Configuration", classes="section-header")
        
        yield from self._create_form_group(
            "server-enabled",
            "Server Enabled:",
            Switch(value=False, id="input-server-enabled"),
            "Enable OpenCode server for remote connections"
        )
        
        yield from self._create_form_group(
            "server-host",
            "Server Host:",
            Input(value="0.0.0.0", placeholder="0.0.0.0", id="input-server-host"),
            "Host address for the server (0.0.0.0 for all interfaces)"
        )
        
        yield from self._create_form_group(
            "server-port",
            "Server Port:",
            Input(value="", placeholder="8080", id="input-server-port"),
            "Port number (1024-65535) for the server"
        )
        
        yield from self._create_form_group(
            "server-username",
            "Username:",
            Input(value="opencode", placeholder="opencode", id="input-server-username"),
            "Authentication username for server access"
        )
        
        yield from self._create_form_group(
            "server-password",
            "Password:",
            Input(value="", placeholder="", password=True, id="input-server-password"),
            "Authentication password for server access"
        )
        
        yield from self._create_form_group(
            "server-cors",
            "CORS Origins:",
            Input(value="", placeholder="*", id="input-server-cors"),
            "Comma-separated list of allowed CORS origins (* for all)"
        )
        
        # User Configuration Section
        yield Static("User Configuration", classes="section-header")
        
        yield from self._create_form_group(
            "user-id",
            "User ID:",
            Input(value="1000", placeholder="1000", id="input-user-id"),
            "UID for container user (match host user for file permissions)"
        )
        
        yield from self._create_form_group(
            "group-id",
            "Group ID:",
            Input(value="1000", placeholder="1000", id="input-group-id"),
            "GID for container group (match host group for file permissions)"
        )
        
        yield from self._create_form_group(
            "timezone",
            "Timezone:",
            Input(value="UTC", placeholder="UTC", id="input-timezone"),
            "Timezone for container (e.g., America/New_York, Europe/London)"
        )
        
        # Container Configuration Section
        yield Static("Container Configuration", classes="section-header")
        
        yield from self._create_form_group(
            "container-name",
            "Container Name:",
            Input(value="", placeholder="opencode-env", id="input-container-name"),
            "Unique name for the Docker container"
        )
        
        yield from self._create_form_group(
            "hostname",
            "Hostname:",
            Input(value="", placeholder="opencode-container", id="input-hostname"),
            "Hostname inside the container"
        )
        
        # Volume Configuration Section
        yield Static("Volume Configuration", classes="section-header")
        
        yield from self._create_form_group(
            "workspace-dir",
            "Workspace Directory:",
            Input(value="./workspace", placeholder="./workspace", id="input-workspace-dir"),
            "Path to workspace directory (relative or absolute)"
        )
        
        yield from self._create_form_group(
            "global-config",
            "Global Config:",
            Input(value="", placeholder="~/.config/opencode", id="input-global-config"),
            "Path to global OpenCode config (leave empty to skip)"
        )
        
        yield from self._create_form_group(
            "project-config",
            "Project Config:",
            Input(value="", placeholder="./.opencode", id="input-project-config"),
            "Path to project-specific config (leave empty to skip)"
        )
        
        yield from self._create_form_group(
            "opencode-env-config",
            "Environment Config:",
            Input(value="./opencode_config", placeholder="./opencode_config", id="input-opencode-env-config"),
            "Path to environment-specific config"
        )
        
        # Mount Control
        yield Label("Volume Mount Control:", classes="form-label")
        yield Checkbox("Mount Global Config", value=False, id="check-mount-global")
        yield Checkbox("Mount Project Config", value=False, id="check-mount-project")
        yield Checkbox("Mount Environment Config", value=True, id="check-mount-opencode-env")
        yield Static("Control which config directories are mounted", classes="form-help")
        
        # Resource Limits Section (Commented out as per requirements)
        yield Static("Resource Limits [dim](Experimental - Use with caution)[/dim]", classes="section-header")
        yield Static(
            "[yellow]⚠ Resource limits are experimental and may cause container startup issues.[/yellow]",
            classes="warning-text"
        )
        
        # Comment: Uncomment these fields when resource limits are stable
        # yield from self._create_form_group(
        #     "memory-limit",
        #     "Memory Limit:",
        #     Input(value="", placeholder="2g", id="input-memory-limit"),
        #     "Memory limit (e.g., 512m, 2g, 4g) - leave empty for no limit"
        # )
        #
        # yield from self._create_form_group(
        #     "cpu-limit",
        #     "CPU Limit:",
        #     Input(value="", placeholder="2", id="input-cpu-limit"),
        #     "CPU cores limit (e.g., 0.5, 1, 2) - leave empty for no limit"
        # )
        #
        # yield from self._create_form_group(
        #     "shm-size",
        #     "Shared Memory:",
        #     Input(value="", placeholder="64m", id="input-shm-size"),
        #     "Shared memory size (e.g., 64m, 128m) - leave empty for default"
        # )
        
        yield Static(
            "[dim]Note: Resource limits are currently disabled. Edit .env directly if needed.[/dim]",
            classes="form-help"
        )
        
        # Rebuild warning
        yield Static(
            "\n[yellow]⚠ Changes require container rebuild to take effect.[/yellow]",
            classes="warning-text"
        )
    
    def _create_form_group(
        self,
        group_id: str,
        label: str,
        input_widget,
        help_text: str = ""
    ) -> ComposeResult:
        """Create a form group with label, input, and help text"""
        with Horizontal(classes="form-group", id=f"group-{group_id}"):
            yield Label(label, classes="form-label")
            input_widget.add_class("form-input")
            yield input_widget
        
        if help_text:
            yield Static(f"[dim]{help_text}[/dim]", classes="form-help")
    
    async def on_mount(self) -> None:
        """Load configuration when screen mounts"""
        set_context(screen="ConfigEditor", environment_name=self.environment.name)
        await self._load_configuration()
    
    async def _load_configuration(self) -> None:
        """Load configuration from .env file"""
        try:
            # Load .env file
            env_path = self.environment.env_file_path
            if env_path.exists():
                self.original_config = await asyncio.to_thread(
                    self.config_service.parse_env_file,
                    env_path
                )
            else:
                self.original_config = {}
            
            # Populate form fields
            self._populate_form()
            
            self.notify("Configuration loaded", severity="information")
        
        except ConfigurationError as e:
            self.notify(f"Failed to load configuration: {e}", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {e}", severity="error")
    
    def _populate_form(self) -> None:
        """Populate form fields with loaded configuration"""
        config = self.original_config
        
        # Server configuration
        if switch := self.query_one("#input-server-enabled", Switch):
            switch.value = self.config_service.get_bool_value(config, "OPENCODE_SERVER_ENABLED", False)
        
        self._set_input_value("input-server-host", config.get("OPENCODE_SERVER_HOST", "0.0.0.0"))
        self._set_input_value("input-server-port", config.get("OPENCODE_SERVER_PORT", ""))
        self._set_input_value("input-server-username", config.get("OPENCODE_SERVER_USERNAME", "opencode"))
        self._set_input_value("input-server-password", config.get("OPENCODE_SERVER_PASSWORD", ""))
        self._set_input_value("input-server-cors", config.get("OPENCODE_SERVER_CORS", ""))
        
        # User configuration
        self._set_input_value("input-user-id", config.get("USER_ID", "1000"))
        self._set_input_value("input-group-id", config.get("GROUP_ID", "1000"))
        self._set_input_value("input-timezone", config.get("TIMEZONE", "UTC"))
        
        # Container configuration
        self._set_input_value("input-container-name", config.get("CONTAINER_NAME", ""))
        self._set_input_value("input-hostname", config.get("HOSTNAME", ""))
        
        # Volume configuration
        self._set_input_value("input-workspace-dir", config.get("WORKSPACE_DIR", "./workspace"))
        self._set_input_value("input-global-config", config.get("GLOBAL_CONFIG", ""))
        self._set_input_value("input-project-config", config.get("PROJECT_CONFIG", ""))
        self._set_input_value("input-opencode-env-config", config.get("OPENCODE_ENV_CONFIG", "./opencode_config"))
        
        # Mount control
        if check := self.query_one("#check-mount-global", Checkbox):
            check.value = self.config_service.get_bool_value(config, "MOUNT_GLOBAL_CONFIG", False)
        if check := self.query_one("#check-mount-project", Checkbox):
            check.value = self.config_service.get_bool_value(config, "MOUNT_PROJECT_CONFIG", False)
        if check := self.query_one("#check-mount-opencode-env", Checkbox):
            check.value = self.config_service.get_bool_value(config, "MOUNT_OPENCODE_ENV_CONFIG", True)
        
        # Resource limits (commented out)
        # self._set_input_value("input-memory-limit", config.get("MEMORY_LIMIT", ""))
        # self._set_input_value("input-cpu-limit", config.get("CPU_LIMIT", ""))
        # self._set_input_value("input-shm-size", config.get("SHM_SIZE", ""))
    
    def _set_input_value(self, input_id: str, value: str) -> None:
        """Set input value safely"""
        try:
            if input_widget := self.query_one(f"#{input_id}", Input):
                input_widget.value = str(value) if value else ""
        except Exception:
            pass  # Widget not found or error setting value
    
    def _get_input_value(self, input_id: str, default: str = "") -> str:
        """Get input value safely"""
        try:
            if input_widget := self.query_one(f"#{input_id}", Input):
                return input_widget.value.strip()
        except Exception:
            pass
        return default
    
    def _get_switch_value(self, switch_id: str, default: bool = False) -> bool:
        """Get switch value safely"""
        try:
            if switch := self.query_one(f"#{switch_id}", Switch):
                return switch.value
        except Exception:
            pass
        return default
    
    def _get_checkbox_value(self, checkbox_id: str, default: bool = False) -> bool:
        """Get checkbox value safely"""
        try:
            if checkbox := self.query_one(f"#{checkbox_id}", Checkbox):
                return checkbox.value
        except Exception:
            pass
        return default
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Collect all form data into a configuration dictionary"""
        config = {}
        
        # Server configuration
        config["OPENCODE_SERVER_ENABLED"] = "true" if self._get_switch_value("input-server-enabled") else "false"
        config["OPENCODE_SERVER_HOST"] = self._get_input_value("input-server-host", "0.0.0.0")
        
        server_port = self._get_input_value("input-server-port")
        if server_port:
            config["OPENCODE_SERVER_PORT"] = server_port
        
        config["OPENCODE_SERVER_USERNAME"] = self._get_input_value("input-server-username", "opencode")
        
        server_password = self._get_input_value("input-server-password")
        if server_password:
            config["OPENCODE_SERVER_PASSWORD"] = server_password
        
        server_cors = self._get_input_value("input-server-cors")
        if server_cors:
            config["OPENCODE_SERVER_CORS"] = server_cors
        
        # User configuration
        config["USER_ID"] = self._get_input_value("input-user-id", "1000")
        config["GROUP_ID"] = self._get_input_value("input-group-id", "1000")
        config["TIMEZONE"] = self._get_input_value("input-timezone", "UTC")
        
        # Container configuration
        container_name = self._get_input_value("input-container-name")
        if container_name:
            config["CONTAINER_NAME"] = container_name
        
        hostname = self._get_input_value("input-hostname")
        if hostname:
            config["HOSTNAME"] = hostname
        
        # Network configuration
        if "NETWORK_NAME" in self.original_config:
            config["NETWORK_NAME"] = self.original_config["NETWORK_NAME"]
        
        # Volume configuration
        config["WORKSPACE_DIR"] = self._get_input_value("input-workspace-dir", "./workspace")
        
        global_config = self._get_input_value("input-global-config")
        if global_config:
            config["GLOBAL_CONFIG"] = global_config
        
        project_config = self._get_input_value("input-project-config")
        if project_config:
            config["PROJECT_CONFIG"] = project_config
        
        config["OPENCODE_ENV_CONFIG"] = self._get_input_value("input-opencode-env-config", "./opencode_config")
        
        worktree_dir = self.original_config.get("WORKTREE_DIR", "./worktree")
        config["WORKTREE_DIR"] = worktree_dir
        
        # Mount control
        config["MOUNT_GLOBAL_CONFIG"] = "true" if self._get_checkbox_value("check-mount-global") else "false"
        config["MOUNT_PROJECT_CONFIG"] = "true" if self._get_checkbox_value("check-mount-project") else "false"
        config["MOUNT_OPENCODE_ENV_CONFIG"] = "true" if self._get_checkbox_value("check-mount-opencode-env") else "false"
        
        # Resource limits (commented out)
        # memory_limit = self._get_input_value("input-memory-limit")
        # if memory_limit:
        #     config["MEMORY_LIMIT"] = memory_limit
        #
        # cpu_limit = self._get_input_value("input-cpu-limit")
        # if cpu_limit:
        #     config["CPU_LIMIT"] = cpu_limit
        #
        # shm_size = self._get_input_value("input-shm-size")
        # if shm_size:
        #     config["SHM_SIZE"] = shm_size
        
        return config
    
    def _validate_configuration(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """Validate configuration values"""
        
        # Validate server port
        server_port = config.get("OPENCODE_SERVER_PORT", "")
        if server_port:
            try:
                port = int(server_port)
                if port < 1024 or port > 65535:
                    return False, "Server port must be between 1024 and 65535"
            except ValueError:
                return False, "Server port must be a valid number"
        
        # Validate user/group IDs
        try:
            user_id = int(config.get("USER_ID", "1000"))
            if user_id < 0:
                return False, "User ID must be non-negative"
        except ValueError:
            return False, "User ID must be a valid number"
        
        try:
            group_id = int(config.get("GROUP_ID", "1000"))
            if group_id < 0:
                return False, "Group ID must be non-negative"
        except ValueError:
            return False, "Group ID must be a valid number"
        
        # Validate container name
        container_name = config.get("CONTAINER_NAME", "")
        if container_name and not all(c.isalnum() or c in "-_" for c in container_name):
            return False, "Container name can only contain alphanumeric characters, hyphens, and underscores"
        
        # Validate resource limits (if uncommented)
        # memory_limit = config.get("MEMORY_LIMIT", "")
        # if memory_limit:
        #     if not re.match(r'^\d+[kmg]$', memory_limit.lower()):
        #         return False, "Memory limit must be in format: 512m, 2g, etc."
        #
        # cpu_limit = config.get("CPU_LIMIT", "")
        # if cpu_limit:
        #     try:
        #         cpu = float(cpu_limit)
        #         if cpu <= 0:
        #             return False, "CPU limit must be positive"
        #     except ValueError:
        #         return False, "CPU limit must be a valid number"
        
        return True, ""
    
    async def _create_backup(self) -> Optional[Path]:
        """Create backup of .env file in /backups/ directory"""
        try:
            env_path = self.environment.env_file_path
            if not env_path.exists():
                return None
            
            # Create backups directory
            backups_dir = self.environment.path / "backups"
            await asyncio.to_thread(backups_dir.mkdir, parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backups_dir / f".env.backup.{timestamp}"
            
            # Copy file
            await asyncio.to_thread(shutil.copy2, env_path, backup_path)
            
            return backup_path
        
        except Exception as e:
            self.notify(f"Failed to create backup: {e}", severity="error")
            return None
    
    async def _save_configuration(self) -> None:
        """Save configuration to .env file"""
        try:
            # Collect form data
            config = self._collect_form_data()
            
            # Validate configuration
            valid, error_msg = self._validate_configuration(config)
            if not valid:
                self.notify(f"Validation failed: {error_msg}", severity="error")
                return
            
            # Create backup
            backup_path = await self._create_backup()
            if backup_path:
                self.notify(f"Backup created: {backup_path.name}", severity="information")
            
            # Save configuration
            env_path = self.environment.env_file_path
            await asyncio.to_thread(
                self.config_service.write_env_file,
                env_path,
                config,
                backup=False  # We already created backup above
            )
            
            # Update original config
            self.original_config = config
            self.has_changes = False
            
            self.notify("Configuration saved successfully", severity="success")
            self.notify("⚠ Rebuild container for changes to take effect", severity="warning")
        
        except ConfigurationError as e:
            self.notify(f"Failed to save configuration: {e}", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {e}", severity="error")
    
    async def action_save(self) -> None:
        """Save configuration (Ctrl+S)"""
        await self._save_configuration()
    
    async def action_reset(self) -> None:
        """Reset form to original values (Ctrl+R)"""
        self._populate_form()
        self.has_changes = False
        self.notify("Form reset to original values", severity="information")
    
    async def action_backup(self) -> None:
        """Create backup without saving (Ctrl+B)"""
        backup_path = await self._create_backup()
        if backup_path:
            self.notify(f"Backup created: {backup_path}", severity="success")
        else:
            self.notify("No configuration file to backup", severity="warning")
    
    def action_close(self) -> None:
        """Close the screen (Escape)"""
        if self.has_changes:
            # TODO: Show confirmation dialog
            pass
        self.dismiss()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "btn-save":
            await self._save_configuration()
        elif button_id == "btn-reset":
            await self.action_reset()
        elif button_id == "btn-backup":
            await self.action_backup()
        elif button_id == "btn-cancel":
            self.action_close()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Track changes to form"""
        self.has_changes = True
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Track changes to switches"""
        self.has_changes = True
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Track changes to checkboxes"""
        self.has_changes = True
