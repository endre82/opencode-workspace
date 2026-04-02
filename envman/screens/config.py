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
from envman.services.creation import CreationService
from envman.utils.exceptions import ConfigurationError
from envman.utils.exception_logger import set_context
from envman.screens.modals.copy_command import CopyCommandModal
from envman.screens.modals.confirm import ConfirmDialog

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


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
        Binding("ctrl+k", "copy_command", "Copy Command"),
    ]

    def __init__(self, environment: Environment):
        super().__init__()
        self.environment = environment
        self.config_service = ConfigService()
        self.creation_service = CreationService(self.environment.path.parent.parent)
        self.original_config: Dict[str, Any] = {}
        self.has_changes = False

        set_context(screen="ConfigEditor", environment_name=self.environment.name)

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="config-container"):
            with Vertical(id="header-section"):
                yield Static(
                    f"[bold]Configuration Editor[/bold] - {self.environment.name}",
                    id="title",
                )
                yield Static(
                    f"Editing: {self.environment.env_file_path}",
                    id="subtitle",
                )

            with ScrollableContainer(id="form-container"):
                yield from self._create_form()

            with Horizontal(id="button-bar"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Reset", variant="default", id="btn-reset")
                yield Button("Backup", variant="default", id="btn-backup")
                yield Button("Copy Command", variant="success", id="btn-copy-command")
                yield Button("Migrate Mounts", variant="warning", id="btn-migrate-mounts")
                yield Button("Cancel", variant="default", id="btn-cancel")

        yield Footer()

    def _create_form(self) -> ComposeResult:
        # ── Server Configuration ─────────────────────────────────────────────
        yield Static("Server Configuration", classes="section-header")

        yield from self._create_form_group(
            "server-enabled",
            "Server Enabled:",
            Switch(value=False, id="input-server-enabled"),
            "Enable OpenCode server for remote connections",
        )
        yield from self._create_form_group(
            "server-host",
            "Server Host:",
            Input(value="0.0.0.0", placeholder="0.0.0.0", id="input-server-host"),
            "Host address for the server (0.0.0.0 for all interfaces)",
        )
        yield from self._create_form_group(
            "server-port",
            "Server Port:",
            Input(value="", placeholder="8080", id="input-server-port"),
            "Port number (1024-65535) for the server",
        )
        yield from self._create_form_group(
            "server-username",
            "Username:",
            Input(value="opencode", placeholder="opencode", id="input-server-username"),
            "Authentication username for server access",
        )
        yield from self._create_form_group(
            "server-password",
            "Password:",
            Input(value="", placeholder="", password=True, id="input-server-password"),
            "Authentication password for server access",
        )
        yield from self._create_form_group(
            "server-cors",
            "CORS Origins:",
            Input(value="", placeholder="*", id="input-server-cors"),
            "Comma-separated list of allowed CORS origins (* for all)",
        )

        # ── User Configuration ───────────────────────────────────────────────
        yield Static("User Configuration", classes="section-header")

        yield from self._create_form_group(
            "user-id",
            "User ID:",
            Input(value="1000", placeholder="1000", id="input-user-id"),
            "UID for container user (match host user for file permissions)",
        )
        yield from self._create_form_group(
            "group-id",
            "Group ID:",
            Input(value="1000", placeholder="1000", id="input-group-id"),
            "GID for container group (match host group for file permissions)",
        )
        yield from self._create_form_group(
            "timezone",
            "Timezone:",
            Input(value="UTC", placeholder="UTC", id="input-timezone"),
            "Timezone for container (e.g., America/New_York, Europe/London)",
        )

        # ── Container Configuration ──────────────────────────────────────────
        yield Static("Container Configuration", classes="section-header")

        yield from self._create_form_group(
            "container-name",
            "Container Name:",
            Input(value="", placeholder="opencode-env", id="input-container-name"),
            "Unique name for the Docker container",
        )
        yield from self._create_form_group(
            "hostname",
            "Hostname:",
            Input(value="", placeholder="opencode-container", id="input-hostname"),
            "Hostname inside the container",
        )

        # ── Volume Configuration ─────────────────────────────────────────────
        yield Static("Volume Configuration", classes="section-header")

        yield from self._create_form_group(
            "workspace-dir",
            "Workspace Directory:",
            Input(value="./workspace", placeholder="./workspace", id="input-workspace-dir"),
            "Path to workspace directory (relative or absolute)",
        )
        yield from self._create_form_group(
            "worktree-dir",
            "Worktree Directory:",
            Input(value="./worktree", placeholder="./worktree", id="input-worktree-dir"),
            "Path to worktree directory",
        )

        # ── OpenCode Config ──────────────────────────────────────────────────
        yield Static("OpenCode Config", classes="section-header")

        yield Label("Config Source:", classes="form-label")
        yield Static("(read-only — change requires environment recreation)", id="display-opencode-config-mode")
        yield Static("[dim]Mode and paths are set during environment creation[/dim]", classes="form-help")

        # ── Volume Mount Control ─────────────────────────────────────────────
        yield Static("Volume Mount Control", classes="section-header")

        yield Label("Enabled mounts:", classes="form-label")
        yield Checkbox("Mount Worktree Directory", value=True, id="check-mount-worktree")
        yield Static("[dim]Control which directories are mounted into the container[/dim]", classes="form-help")

        # ── Rebuild reminder ─────────────────────────────────────────────────
        yield Static(
            "\n[yellow]⚠ Changes require container rebuild to take effect.[/yellow]",
            classes="warning-text",
        )

    def _create_form_group(
        self,
        group_id: str,
        label: str,
        input_widget,
        help_text: str = "",
    ) -> ComposeResult:
        with Horizontal(classes="form-group", id=f"group-{group_id}"):
            yield Label(label, classes="form-label")
            input_widget.add_class("form-input")
            yield input_widget

        if help_text:
            yield Static(f"[dim]{help_text}[/dim]", classes="form-help")

    async def on_mount(self) -> None:
        await self._load_configuration()

    async def _load_configuration(self) -> None:
        try:
            env_path = self.environment.env_file_path
            if env_path.exists():
                self.original_config = await asyncio.to_thread(
                    self.config_service.parse_env_file, env_path
                )
            else:
                self.original_config = {}

            self._populate_form()
            self.notify("Configuration loaded", severity="information")

        except ConfigurationError as e:
            self.notify(f"Failed to load configuration: {e}", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {e}", severity="error")

    def _populate_form(self) -> None:
        config = self.original_config

        # Server
        if switch := self.query_one("#input-server-enabled", Switch):
            switch.value = self.config_service.get_bool_value(config, "OPENCODE_SERVER_ENABLED", False)

        self._set_input_value("input-server-host", config.get("OPENCODE_SERVER_HOST", "0.0.0.0"))
        self._set_input_value("input-server-port", config.get("OPENCODE_SERVER_PORT", ""))
        self._set_input_value("input-server-username", config.get("OPENCODE_SERVER_USERNAME", "opencode"))
        self._set_input_value("input-server-password", config.get("OPENCODE_SERVER_PASSWORD", ""))
        self._set_input_value("input-server-cors", config.get("OPENCODE_SERVER_CORS", ""))

        # User
        self._set_input_value("input-user-id", config.get("USER_ID", "1000"))
        self._set_input_value("input-group-id", config.get("GROUP_ID", "1000"))
        self._set_input_value("input-timezone", config.get("TIMEZONE", "UTC"))

        # Container
        self._set_input_value("input-container-name", config.get("CONTAINER_NAME", ""))
        self._set_input_value("input-hostname", config.get("HOSTNAME", ""))

        # Volumes
        self._set_input_value("input-workspace-dir", config.get("WORKSPACE_DIR", "./workspace"))
        self._set_input_value("input-worktree-dir", config.get("WORKTREE_DIR", "./worktree"))

        # OpenCode Config (read-only display)
        mode = config.get("OPENCODE_CONFIG_MODE", "project")
        jsonc_source = config.get("OPENCODE_JSONC_SOURCE", "./opencode_project_config/opencode.jsonc")
        try:
            if display := self.query_one("#display-opencode-config-mode", Static):
                display.update(f"{mode.upper()}: {jsonc_source}")
        except Exception:
            pass

        # Mount control
        if check := self.query_one("#check-mount-worktree", Checkbox):
            check.value = self.config_service.get_bool_value(config, "MOUNT_WORKTREE", True)

        # Reset change tracking after populating
        self.has_changes = False

    def _set_input_value(self, input_id: str, value: str) -> None:
        try:
            if input_widget := self.query_one(f"#{input_id}", Input):
                input_widget.value = str(value) if value else ""
        except Exception:
            pass

    def _get_input_value(self, input_id: str, default: str = "") -> str:
        try:
            if input_widget := self.query_one(f"#{input_id}", Input):
                return input_widget.value.strip()
        except Exception:
            pass
        return default

    def _get_switch_value(self, switch_id: str, default: bool = False) -> bool:
        try:
            if switch := self.query_one(f"#{switch_id}", Switch):
                return switch.value
        except Exception:
            pass
        return default

    def _get_checkbox_value(self, checkbox_id: str, default: bool = False) -> bool:
        try:
            if checkbox := self.query_one(f"#{checkbox_id}", Checkbox):
                return checkbox.value
        except Exception:
            pass
        return default

    def _collect_form_data(self) -> Dict[str, Any]:
        config = {}

        # Server
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

        # User
        config["USER_ID"] = self._get_input_value("input-user-id", "1000")
        config["GROUP_ID"] = self._get_input_value("input-group-id", "1000")
        config["TIMEZONE"] = self._get_input_value("input-timezone", "UTC")

        # Container
        container_name = self._get_input_value("input-container-name")
        if container_name:
            config["CONTAINER_NAME"] = container_name

        hostname = self._get_input_value("input-hostname")
        if hostname:
            config["HOSTNAME"] = hostname

        # Preserve NETWORK_NAME from original
        if "NETWORK_NAME" in self.original_config:
            config["NETWORK_NAME"] = self.original_config["NETWORK_NAME"]

        # Volumes
        config["WORKSPACE_DIR"] = self._get_input_value("input-workspace-dir", "./workspace")
        config["WORKTREE_DIR"] = self._get_input_value("input-worktree-dir", "./worktree")

        # Preserve OpenCode config mode and sources (read-only in this UI)
        if "OPENCODE_CONFIG_MODE" in self.original_config:
            config["OPENCODE_CONFIG_MODE"] = self.original_config["OPENCODE_CONFIG_MODE"]
        if "OPENCODE_JSONC_SOURCE" in self.original_config:
            config["OPENCODE_JSONC_SOURCE"] = self.original_config["OPENCODE_JSONC_SOURCE"]
        if "OPENCODE_AUTH_SOURCE" in self.original_config:
            config["OPENCODE_AUTH_SOURCE"] = self.original_config["OPENCODE_AUTH_SOURCE"]
        if "HOST_OPENCODE_JSONC" in self.original_config:
            config["HOST_OPENCODE_JSONC"] = self.original_config["HOST_OPENCODE_JSONC"]
        if "HOST_OPENCODE_AUTH" in self.original_config:
            config["HOST_OPENCODE_AUTH"] = self.original_config["HOST_OPENCODE_AUTH"]

        # Mount control
        config["MOUNT_WORKTREE"] = "true" if self._get_checkbox_value("check-mount-worktree") else "false"

        return config

    def _validate_configuration(self, config: Dict[str, Any]) -> tuple[bool, str]:
        server_port = config.get("OPENCODE_SERVER_PORT", "")
        if server_port:
            try:
                port = int(server_port)
                if port < 1024 or port > 65535:
                    return False, "Server port must be between 1024 and 65535"
            except ValueError:
                return False, "Server port must be a valid number"

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

        container_name = config.get("CONTAINER_NAME", "")
        if container_name and not all(c.isalnum() or c in "-_" for c in container_name):
            return False, "Container name can only contain alphanumeric characters, hyphens, and underscores"

        return True, ""

    async def _create_backup(self) -> Optional[Path]:
        try:
            env_path = self.environment.env_file_path
            if not env_path.exists():
                return None

            backups_dir = self.environment.path / "backups"
            await asyncio.to_thread(backups_dir.mkdir, parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backups_dir / f".env.backup.{timestamp}"
            await asyncio.to_thread(shutil.copy2, env_path, backup_path)

            return backup_path
        except Exception as e:
            self.notify(f"Failed to create backup: {e}", severity="error")
            return None

    async def _save_configuration(self) -> None:
        try:
            config = self._collect_form_data()

            valid, error_msg = self._validate_configuration(config)
            if not valid:
                self.notify(f"Validation failed: {error_msg}", severity="error")
                return

            backup_path = await self._create_backup()
            if backup_path:
                self.notify(f"Backup created: {backup_path.name}", severity="information")

            env_path = self.environment.env_file_path
            await asyncio.to_thread(
                self.config_service.write_env_file,
                env_path,
                config,
                backup=False,
            )

            self.original_config = config
            self.has_changes = False

            self.notify("Configuration saved successfully", severity="success")
            self.notify("⚠ Rebuild container for changes to take effect", severity="warning")

        except ConfigurationError as e:
            self.notify(f"Failed to save configuration: {e}", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {e}", severity="error")

    async def action_save(self) -> None:
        await self._save_configuration()

    async def action_reset(self) -> None:
        self._populate_form()
        self.notify("Form reset to original values", severity="information")

    async def action_backup(self) -> None:
        backup_path = await self._create_backup()
        if backup_path:
            self.notify(f"Backup created: {backup_path}", severity="success")
        else:
            self.notify("No configuration file to backup", severity="warning")

    def action_copy_command(self) -> None:
        config = self._collect_form_data()

        server_enabled = config.get("OPENCODE_SERVER_ENABLED", "false") == "true"
        if not server_enabled:
            self.notify("Server is not enabled. Enable it first to get connection command.", severity="warning")
            return

        server_port = config.get("OPENCODE_SERVER_PORT", "")
        if not server_port:
            self.notify("Server port is not configured. Set a port first.", severity="warning")
            return

        server_host = config.get("OPENCODE_SERVER_HOST", "0.0.0.0")
        host = "localhost" if server_host == "0.0.0.0" else server_host
        server_url = f"http://{host}:{server_port}"

        server_username = config.get("OPENCODE_SERVER_USERNAME", "opencode")
        server_password = config.get("OPENCODE_SERVER_PASSWORD", "")

        command = (
            f"OPENCODE_SERVER_USERNAME={server_username} "
            f"OPENCODE_SERVER_PASSWORD={server_password} "
            f"opencode attach {server_url}"
        )

        self.app.push_screen(
            CopyCommandModal(
                command=command,
                title="Remote Connection Command",
                message="Use this command from your local machine to connect to this OpenCode server:",
            )
        )

    async def action_migrate_mounts(self) -> None:
        success, message = await asyncio.to_thread(
            self.creation_service.migrate_plugins_skills,
            self.environment.path,
        )
        severity = "success" if success else "error"
        self.notify(message, severity=severity)

    def action_close(self) -> None:
        if self.has_changes:
            def on_confirm(confirmed: bool) -> None:
                if confirmed:
                    self.dismiss()

            self.app.push_screen(
                ConfirmDialog(
                    title="Unsaved Changes",
                    message="You have unsaved changes. Are you sure you want to close without saving?",
                    confirm_text="Discard Changes",
                    cancel_text="Keep Editing",
                ),
                on_confirm,
            )
        else:
            self.dismiss()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "btn-save":
            await self._save_configuration()
        elif button_id == "btn-reset":
            await self.action_reset()
        elif button_id == "btn-backup":
            await self.action_backup()
        elif button_id == "btn-copy-command":
            self.action_copy_command()
        elif button_id == "btn-migrate-mounts":
            await self.action_migrate_mounts()
        elif button_id == "btn-cancel":
            self.action_close()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.has_changes = True

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.has_changes = True

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.has_changes = True
