"""Dashboard screen - main environment list view"""

import asyncio
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual.worker import Worker, WorkerState
from rich.text import Text
from textual.message import Message

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
from typing import List


class Dashboard(Screen):
    """Main dashboard screen showing all environments"""
    
    # All bindings (always active - Textual requires static binding registration)
    BINDINGS = [
        Binding("enter", "select_environment", "Select"),
        Binding("space", "select_environment", "Select"),
        Binding("n", "new_environment", "New"),
        Binding("R", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("s", "start_environment", "Start"),
        Binding("x", "stop_environment", "Stop"),
        Binding("r", "restart_environment", "Restart"),
        Binding("b", "build_environment", "Build"),
        Binding("l", "view_logs", "Logs"),
        Binding("i", "inspect_environment", "Inspect"),
        Binding("c", "configure_environment", "Configure"),
        Binding("d", "delete_environment", "Delete"),
        Binding("w", "open_opencode_web", "OpenCode Web"),
        Binding("v", "open_vscode_web", "VSCode Web"),
    ]
    
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
        self.selected_env: Environment | None = None
        
        # Set context early so it's available during compose()
        set_context(screen="Dashboard")
    
    def compose(self) -> ComposeResult:
        """Compose the dashboard UI"""
        yield Header()
        
        with Container(id="dashboard-container"):
            yield Static("Environments", id="title")
            yield DataTable(id="env-table")
            yield Static("", id="status-bar")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup the table when mounted"""
        table = self.query_one("#env-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Add columns - selection column first
        table.add_column("", width=3)  # Selection indicator column
        table.add_column("Name", width=30)
        table.add_column("Status", width=15)
        table.add_column("Port", width=8)
        table.add_column("URL", width=30)
        
        # Populate rows
        self.refresh_table()
        
        # Update status bar
        self.update_status_bar()
    
    def refresh_table(self) -> None:
        """Refresh the table with current environment data"""
        table = self.query_one("#env-table", DataTable)
        table.clear()
        
        for env in self.environments:
            # Selection indicator
            selection_indicator = "✓" if self.selected_env and env.name == self.selected_env.name else ""
            
            # Format status with icon
            status_text = Text()
            status_text.append(env.status_icon + " ")
            status_text.append(env.status.capitalize())
            
            # Format port
            port_str = str(env.server_port) if env.server_port else "N/A"
            
            # Format URL
            url = env.server_url if env.server_url else "N/A"
            
            table.add_row(
                selection_indicator,
                env.name,
                status_text,
                port_str,
                url,
                key=env.name
            )
    
    def update_status_bar(self) -> None:
        """Update the status bar with summary info"""
        running = sum(1 for e in self.environments if e.is_running)
        stopped = sum(1 for e in self.environments if e.is_stopped)
        total = len(self.environments)
        
        status_text = f"{total} environments | {running} running | {stopped} stopped"
        
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(status_text)
    
    def update_bindings(self) -> None:
        """Update footer bindings based on selection state"""
        # Note: All bindings are always active. This method kept for compatibility
        # but no longer dynamically changes bindings since Textual requires static registration.
        # Actions already check selection state and show warnings if needed.
        pass
    
    def _toggle_environment_selection(self, env: Environment) -> None:
        """Toggle selection of the given environment"""
        # Save current cursor position before refresh
        table = self.query_one("#env-table", DataTable)
        saved_cursor_row = table.cursor_row
        
        if self.selected_env and self.selected_env.name == env.name:
            # Deselect if clicking same environment
            self.selected_env = None
            self.refresh_table()
            self.update_bindings()
            self.app.notify("Deselected", severity="information", timeout=2)
        else:
            # Select new environment (or switch from previous)
            self.selected_env = env
            self.refresh_table()
            self.update_bindings()
            self.app.notify(f"Selected: {env.name}", severity="information", timeout=2)
        
        # Restore cursor position after refresh
        if saved_cursor_row is not None:
            try:
                table.move_cursor(row=saved_cursor_row)
            except (AttributeError, Exception):
                # Fallback if move_cursor doesn't exist
                try:
                    table.cursor_row = saved_cursor_row
                except Exception:
                    pass
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle mouse click or row activation"""
        env_name = event.row_key
        clicked_env = next((e for e in self.environments if e.name == env_name), None)
        if clicked_env:
            self._toggle_environment_selection(clicked_env)
    
    def action_select_environment(self) -> None:
        """Toggle selection of the focused environment (Space/Enter)"""
        table = self.query_one("#env-table", DataTable)
        
        try:
            cursor_row = table.cursor_row
            if cursor_row is not None and cursor_row < len(self.environments):
                focused_env = self.environments[cursor_row]
                self._toggle_environment_selection(focused_env)
        except Exception as e:
            self.app.notify(f"Selection error: {e}", severity="error")
    
    def action_new_environment(self) -> None:
        """Create new environment"""
        from envman.screens.creation.wizard import CreationWizard
        
        wizard = CreationWizard(
            docker_service=self.docker_service,
            discovery_service=self.discovery_service,
            workspace_root=self.workspace_root
        )
        
        # Push wizard screen, refresh when it closes
        def on_wizard_close(result) -> None:
            self.action_refresh()
        
        self.app.push_screen(wizard, on_wizard_close)
    
    def action_start_environment(self) -> None:
        """Start selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        self.app.notify(f"Starting {self.selected_env.name}...", timeout=2)
        self.run_worker(self._start_environment(self.selected_env), exclusive=True)
    
    async def _start_environment(self, env: Environment) -> None:
        """Worker to start environment"""
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.start_container, 
                str(env.path)
            )
            
            if success:
                # Update status
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Started {env.name}", severity="information")
            else:
                # Show first line of error
                error_line = output.split('\n')[0] if output else "Unknown error"
                self.app.notify(f"✗ Failed to start {env.name}: {error_line}", severity="error", timeout=5)
        
        except DockerError as e:
            self.app.notify(f"✗ Error starting {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")
    
    def action_stop_environment(self) -> None:
        """Stop selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        self.app.notify(f"Stopping {self.selected_env.name}...", timeout=2)
        self.run_worker(self._stop_environment(self.selected_env), exclusive=True)
    
    async def _stop_environment(self, env: Environment) -> None:
        """Worker to stop environment"""
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.stop_container,
                str(env.path)
            )
            
            if success:
                # Update status
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Stopped {env.name}", severity="information")
            else:
                error_line = output.split('\n')[0] if output else "Unknown error"
                self.app.notify(f"✗ Failed to stop {env.name}: {error_line}", severity="error", timeout=5)
        
        except DockerError as e:
            self.app.notify(f"✗ Error stopping {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")
    
    def action_restart_environment(self) -> None:
        """Restart selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        self.app.notify(f"Restarting {self.selected_env.name}...", timeout=2)
        self.run_worker(self._restart_environment(self.selected_env), exclusive=True)
    
    async def _restart_environment(self, env: Environment) -> None:
        """Worker to restart environment"""
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.restart_container,
                str(env.path)
            )
            
            if success:
                # Update status
                env.refresh_status(self.docker_service)
                self.refresh_table()
                self.update_status_bar()
                self.app.notify(f"✓ Restarted {env.name}", severity="information")
            else:
                error_line = output.split('\n')[0] if output else "Unknown error"
                self.app.notify(f"✗ Failed to restart {env.name}: {error_line}", severity="error", timeout=5)
        
        except DockerError as e:
            self.app.notify(f"✗ Error restarting {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")
    
    def action_build_environment(self) -> None:
        """Build selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        self.app.notify(f"Building {self.selected_env.name}... (this may take a while)", timeout=3)
        self.run_worker(self._build_environment(self.selected_env), exclusive=True)
    
    async def _build_environment(self, env: Environment) -> None:
        """Worker to build environment"""
        try:
            success, output = await asyncio.to_thread(
                self.docker_service.build_container,
                str(env.path)
            )
            
            if success:
                self.app.notify(f"✓ Built {env.name}", severity="information")
            else:
                error_line = output.split('\n')[0] if output else "Unknown error"
                self.app.notify(f"✗ Failed to build {env.name}: {error_line}", severity="error", timeout=5)
        
        except DockerError as e:
            self.app.notify(f"✗ Error building {env.name}: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"✗ Unexpected error: {e}", severity="error")
    
    def action_view_logs(self) -> None:
        """View logs for selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        # Check if container is running
        if not self.selected_env.is_running:
            self.app.notify(f"{self.selected_env.name} is not running", severity="warning")
            return
        
        from envman.screens.logs import LogsScreen
        
        logs_screen = LogsScreen(
            environment=self.selected_env,
            docker_service=self.docker_service
        )
        
        self.app.push_screen(logs_screen)
    
    def action_inspect_environment(self) -> None:
        """Inspect selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        # Check if container exists
        if self.selected_env.status == "unknown":
            self.app.notify(f"{self.selected_env.name} container not found", severity="warning")
            return
        
        from envman.screens.inspect import InspectScreen
        
        inspect_screen = InspectScreen(
            environment=self.selected_env,
            docker_service=self.docker_service
        )
        
        self.app.push_screen(inspect_screen)
    
    def action_configure_environment(self) -> None:
        """Configure selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        from envman.screens.config import ConfigScreen
        
        config_screen = ConfigScreen(environment=self.selected_env)
        
        # Refresh when config screen closes (in case changes were made)
        def on_config_close(result) -> None:
            self.action_refresh()
        
        self.app.push_screen(config_screen, on_config_close)
    
    def action_delete_environment(self) -> None:
        """Delete selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        
        from envman.screens.delete import DeleteEnvironmentScreen
        
        # Capture the environment name for the closure
        env_name = self.selected_env.name
        
        delete_screen = DeleteEnvironmentScreen(
            environment=self.selected_env,
            docker_service=self.docker_service,
            discovery_service=self.discovery_service
        )
        
        # Refresh environment list when delete screen closes
        def on_delete_close(deleted: bool) -> None:
            if deleted:
                # Remove from list and refresh
                self.environments = [e for e in self.environments if e.name != env_name]
                self.selected_env = None
                self.refresh_table()
                self.update_status_bar()
            else:
                # Just refresh status in case container was stopped
                self.action_refresh()
        
        self.app.push_screen(delete_screen, on_delete_close)
    
    def action_refresh(self) -> None:
        """Refresh environment list"""
        self.app.notify("Refreshing...", timeout=1)
        self.run_worker(self._refresh_environments(), exclusive=True)
    
    async def _refresh_environments(self) -> None:
        """Worker to refresh all environments"""
        try:
            # Refresh status for all environments
            for env in self.environments:
                await asyncio.to_thread(env.refresh_status, self.docker_service)
            
            # Update UI
            self.refresh_table()
            self.update_status_bar()
            self.app.notify("✓ Refreshed", severity="information", timeout=2)
        
        except Exception as e:
            self.app.notify(f"✗ Error refreshing: {e}", severity="error")
    
    def action_open_opencode_web(self) -> None:
        """Open OpenCode web interface in browser"""
        if not self.selected_env:
            self.notify("No environment selected", severity="warning")
            return
        
        if not self.selected_env.is_running:
            self.notify("Environment is not running", severity="warning")
            return
        
        if not self.selected_env.server_url:
            self.notify("Server URL not available", severity="error")
            return
        
        # Copy password to clipboard
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(self.selected_env.server_password)
                self.notify("Password copied to clipboard", severity="success", timeout=2)
            except Exception as e:
                self.notify(f"Failed to copy password: {e}", severity="error")
        else:
            self.notify("Clipboard not available - password not copied", severity="warning")
        
        # Open browser
        try:
            open_url(self.selected_env.server_url)
            self.notify(f"Opening OpenCode at {self.selected_env.server_url}", severity="information")
        except Exception as e:
            self.notify(f"Failed to open browser: {e}", severity="error")
    
    def action_open_vscode_web(self) -> None:
        """Open VSCode web interface in browser"""
        if not self.selected_env:
            self.notify("No environment selected", severity="warning")
            return
        
        if not self.selected_env.is_running:
            self.notify("Environment is not running", severity="warning")
            return
        
        if not self.selected_env.code_server_url:
            self.notify("VSCode server URL not available", severity="error")
            return
        
        # Copy password to clipboard
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(self.selected_env.server_password)
                self.notify("Password copied to clipboard", severity="success", timeout=2)
            except Exception as e:
                self.notify(f"Failed to copy password: {e}", severity="error")
        else:
            self.notify("Clipboard not available - password not copied", severity="warning")
        
        # Open browser
        try:
            open_url(self.selected_env.code_server_url)
            self.notify(f"Opening VSCode at {self.selected_env.code_server_url}", severity="information")
        except Exception as e:
            self.notify(f"Failed to open browser: {e}", severity="error")
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()
