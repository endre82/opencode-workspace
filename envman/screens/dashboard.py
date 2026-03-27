"""Dashboard screen - main environment list view"""

import asyncio
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from envman.models.environment import Environment
from envman.services.docker import DockerService
from envman.services.discovery import DiscoveryService
from envman.utils.exceptions import DockerError
from envman.utils.exception_logger import set_context
from envman.utils.browser import open_url
from typing import List, Optional


class Dashboard(Screen):
    """Main dashboard screen showing all environments"""

    BINDINGS = [
        # Always visible
        Binding("n", "new_environment", "New"),
        Binding("R", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("question_mark", "show_help", "Help"),
        # Visible when environments exist (check_action controls this)
        Binding("s", "start_environment", "Start"),
        Binding("x", "stop_environment", "Stop"),
        Binding("l", "view_logs", "Logs"),
        Binding("c", "configure_environment", "Config"),
        Binding("d", "delete_environment", "Delete"),
        # Less common — work via keyboard but not cluttering the footer
        Binding("r", "restart_environment", "Restart", show=False),
        Binding("b", "build_environment", "Build", show=False),
        Binding("i", "inspect_environment", "Inspect", show=False),
        Binding("w", "open_opencode_web", "OpenCode Web", show=False),
        Binding("v", "open_vscode_web", "VSCode Web", show=False),
    ]

    def check_action(self, action: str, parameters: tuple) -> bool | None:
        """Hide env-specific bindings in the footer when the list is empty."""
        env_actions = {
            "start_environment", "stop_environment", "view_logs",
            "configure_environment", "delete_environment",
            "restart_environment", "build_environment", "inspect_environment",
            "open_opencode_web", "open_vscode_web",
        }
        if action in env_actions and not self.environments:
            return False  # disabled + hidden from footer
        return True

    def __init__(
        self,
        environments: List[Environment],
        docker_service: DockerService,
        discovery_service: DiscoveryService,
        workspace_root: Path
    ):
        super().__init__()
        self.environments = environments
        self.docker_service = docker_service
        self.discovery_service = discovery_service
        self.workspace_root = workspace_root

        set_context(screen="Dashboard")

    @property
    def current_env(self) -> Optional[Environment]:
        """Return the environment at the current cursor row, or None if list is empty."""
        if not self.environments:
            return None
        try:
            table = self.query_one("#env-table", DataTable)
            row = table.cursor_row
            if row is not None and 0 <= row < len(self.environments):
                return self.environments[row]
        except Exception:
            pass
        return None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="dashboard-container"):
            yield Static("Environments", id="title")
            yield DataTable(id="env-table")
            yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#env-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("Name", width=30)
        table.add_column("Status", width=15)
        table.add_column("Port", width=8)
        table.add_column("URL", width=40)

        self.refresh_table()
        self.update_status_bar()
        self.refresh_bindings()

        # Auto-refresh every 30 seconds
        self.set_interval(30, self._auto_refresh)

    def refresh_table(self) -> None:
        """Refresh the table with current environment data, preserving cursor position."""
        table = self.query_one("#env-table", DataTable)
        saved_row = table.cursor_row

        table.clear()

        if not self.environments:
            table.add_row(
                "[dim]No environments found — press [bold]n[/bold] to create one[/dim]",
                "", "", "",
            )
            return

        for env in self.environments:
            status_text = Text()
            status_text.append(env.status_icon + " ")
            status_text.append(env.status.capitalize())

            port_str = str(env.server_port) if env.server_port else "N/A"
            url = env.server_url if env.server_url else "N/A"

            table.add_row(
                env.name,
                status_text,
                port_str,
                url,
                key=env.name,
            )

        # Restore cursor position
        if saved_row is not None:
            try:
                max_row = len(self.environments) - 1
                table.move_cursor(row=min(saved_row, max_row))
            except Exception:
                pass

    def update_status_bar(self) -> None:
        running = sum(1 for e in self.environments if e.is_running)
        stopped = sum(1 for e in self.environments if e.is_stopped)
        total = len(self.environments)

        status_text = f"{total} environments | {running} running | {stopped} stopped"
        self.query_one("#status-bar", Static).update(status_text)

    # ─── helpers ───────────────────────────────────────────────────────────────

    def _require_env(self, action_name: str = "action") -> Optional[Environment]:
        """Return current_env, or show a warning and return None."""
        env = self.current_env
        if env is None:
            self.app.notify("No environment selected", severity="warning")
        return env

    def _require_running(self, env: Environment, action_name: str = "") -> bool:
        if not env.is_running:
            self.app.notify(
                f"{env.name} is not running",
                severity="warning",
            )
            return False
        return True

    # ─── actions ───────────────────────────────────────────────────────────────

    def action_new_environment(self) -> None:
        from envman.screens.creation.wizard import CreationWizard

        wizard = CreationWizard(
            docker_service=self.docker_service,
            discovery_service=self.discovery_service,
            workspace_root=self.workspace_root,
        )

        def on_wizard_close(result) -> None:
            self.action_refresh()

        self.app.push_screen(wizard, on_wizard_close)

    def action_start_environment(self) -> None:
        env = self._require_env("start")
        if env is None:
            return
        self.app.notify(f"Starting {env.name}...", timeout=2)
        self.run_worker(self._start_environment(env), exclusive=True)

    async def _start_environment(self, env: Environment) -> None:
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.start_container,
                str(env.path),
            )
            if success:
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Started {env.name}", severity="information")
            else:
                error_line = output.split("\n")[0] if output else "Unknown error"
                self.app.notify(
                    f"✗ Failed to start {env.name}: {error_line}",
                    severity="error",
                    timeout=5,
                )
        except DockerError as e:
            self.app.notify(f"✗ Error starting {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")

    def action_stop_environment(self) -> None:
        env = self._require_env("stop")
        if env is None:
            return
        self.app.notify(f"Stopping {env.name}...", timeout=2)
        self.run_worker(self._stop_environment(env), exclusive=True)

    async def _stop_environment(self, env: Environment) -> None:
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.stop_container,
                str(env.path),
            )
            if success:
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Stopped {env.name}", severity="information")
            else:
                error_line = output.split("\n")[0] if output else "Unknown error"
                self.app.notify(
                    f"✗ Failed to stop {env.name}: {error_line}",
                    severity="error",
                    timeout=5,
                )
        except DockerError as e:
            self.app.notify(f"✗ Error stopping {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")

    def action_restart_environment(self) -> None:
        env = self._require_env("restart")
        if env is None:
            return
        self.app.notify(f"Restarting {env.name}...", timeout=2)
        self.run_worker(self._restart_environment(env), exclusive=True)

    async def _restart_environment(self, env: Environment) -> None:
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.restart_container,
                str(env.path),
            )
            if success:
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Restarted {env.name}", severity="information")
            else:
                error_line = output.split("\n")[0] if output else "Unknown error"
                self.app.notify(
                    f"✗ Failed to restart {env.name}: {error_line}",
                    severity="error",
                    timeout=5,
                )
        except DockerError as e:
            self.app.notify(f"✗ Error restarting {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")

    def action_build_environment(self) -> None:
        env = self._require_env("build")
        if env is None:
            return
        self.app.notify(f"Building {env.name}... (this may take a while)", timeout=3)
        self.run_worker(self._build_environment(env), exclusive=True)

    async def _build_environment(self, env: Environment) -> None:
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.build_container,
                str(env.path),
            )
            if success:
                self.app.notify(f"✓ Built {env.name}", severity="information")
            else:
                error_line = output.split("\n")[0] if output else "Unknown error"
                self.app.notify(
                    f"✗ Failed to build {env.name}: {error_line}",
                    severity="error",
                    timeout=5,
                )
        except DockerError as e:
            self.app.notify(f"✗ Error building {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")

    def action_view_logs(self) -> None:
        env = self._require_env("logs")
        if env is None:
            return
        if not self._require_running(env, "logs"):
            return

        from envman.screens.logs import LogsScreen

        self.app.push_screen(
            LogsScreen(environment=env, docker_service=self.docker_service)
        )

    def action_inspect_environment(self) -> None:
        env = self._require_env("inspect")
        if env is None:
            return
        if env.status == "unknown":
            self.app.notify(f"{env.name} container not found", severity="warning")
            return

        from envman.screens.inspect import InspectScreen

        self.app.push_screen(
            InspectScreen(environment=env, docker_service=self.docker_service)
        )

    def action_configure_environment(self) -> None:
        env = self._require_env("configure")
        if env is None:
            return

        from envman.screens.config import ConfigScreen

        def on_config_close(result) -> None:
            self.action_refresh()

        self.app.push_screen(ConfigScreen(environment=env), on_config_close)

    def action_delete_environment(self) -> None:
        env = self._require_env("delete")
        if env is None:
            return

        from envman.screens.delete import DeleteEnvironmentScreen

        env_name = env.name

        def on_delete_close(deleted: bool) -> None:
            if deleted:
                self.environments = [e for e in self.environments if e.name != env_name]
                self.refresh_table()
                self.update_status_bar()
                self.refresh_bindings()
            else:
                self.action_refresh()

        self.app.push_screen(
            DeleteEnvironmentScreen(
                environment=env,
                docker_service=self.docker_service,
                discovery_service=self.discovery_service,
            ),
            on_delete_close,
        )

    def action_refresh(self) -> None:
        self.run_worker(self._refresh_environments(), exclusive=True)

    async def _refresh_environments(self) -> None:
        try:
            # Discover environments fresh from disk (picks up new ones too)
            new_envs = await asyncio.to_thread(
                self.discovery_service.discover_environments
            )

            # Refresh Docker status for each
            for env in new_envs:
                await asyncio.to_thread(env.refresh_status, self.docker_service)

            self.environments = new_envs
            self.refresh_table()
            self.update_status_bar()
            self.refresh_bindings()
        except Exception as e:
            self.app.notify(f"✗ Error refreshing: {e}", severity="error")

    async def _auto_refresh(self) -> None:
        """Silent background refresh (no notification)."""
        try:
            new_envs = await asyncio.to_thread(
                self.discovery_service.discover_environments
            )
            for env in new_envs:
                await asyncio.to_thread(env.refresh_status, self.docker_service)
            self.environments = new_envs
            self.refresh_table()
            self.update_status_bar()
            self.refresh_bindings()
        except Exception:
            pass  # Silent — don't spam the user every 30s on transient errors

    def action_open_opencode_web(self) -> None:
        env = self._require_env("open OpenCode web")
        if env is None:
            return
        if not self._require_running(env):
            return
        if not env.server_url:
            self.notify("Server URL not available", severity="error")
            return

        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(env.server_password)
                self.notify("Password copied to clipboard", severity="success", timeout=2)
            except Exception as e:
                self.notify(f"Failed to copy password: {e}", severity="warning")
        else:
            self.notify("Clipboard not available — password not copied", severity="warning")

        try:
            open_url(env.server_url)
            self.notify(f"Opening OpenCode at {env.server_url}", severity="information")
        except Exception as e:
            self.notify(f"Failed to open browser: {e}", severity="error")

    def action_open_vscode_web(self) -> None:
        env = self._require_env("open VSCode web")
        if env is None:
            return
        if not self._require_running(env):
            return
        if not env.code_server_url:
            self.notify("VSCode server URL not available", severity="error")
            return

        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(env.server_password)
                self.notify("Password copied to clipboard", severity="success", timeout=2)
            except Exception as e:
                self.notify(f"Failed to copy password: {e}", severity="warning")
        else:
            self.notify("Clipboard not available — password not copied", severity="warning")

        try:
            open_url(env.code_server_url)
            self.notify(f"Opening VSCode at {env.code_server_url}", severity="information")
        except Exception as e:
            self.notify(f"Failed to open browser: {e}", severity="error")

    def action_show_help(self) -> None:
        from envman.screens.modals.help import HelpModal
        self.app.push_screen(HelpModal())

    def action_quit(self) -> None:
        self.app.exit()
