"""Dashboard screen - main environment list view"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container, Vertical
from textual.binding import Binding
from rich.text import Text

from envman.models.environment import Environment
from typing import List


class Dashboard(Screen):
    """Main dashboard screen showing all environments"""
    
    BINDINGS = [
        Binding("n", "new_environment", "New"),
        Binding("s", "start_environment", "Start"),
        Binding("x", "stop_environment", "Stop"),
        Binding("r", "restart_environment", "Restart"),
        Binding("b", "build_environment", "Build"),
        Binding("l", "view_logs", "Logs"),
        Binding("i", "inspect_environment", "Inspect"),
        Binding("c", "configure_environment", "Configure"),
        Binding("d", "delete_environment", "Delete"),
        Binding("R", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, environments: List[Environment]):
        super().__init__()
        self.environments = environments
        self.selected_env: Environment | None = None
    
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
        
        # Add columns
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
            # Format status with icon
            status_text = Text()
            status_text.append(env.status_icon + " ")
            status_text.append(env.status.capitalize())
            
            # Format port
            port_str = str(env.server_port) if env.server_port else "N/A"
            
            # Format URL
            url = env.server_url if env.server_url else "N/A"
            
            table.add_row(
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
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        env_name = event.row_key
        self.selected_env = next((e for e in self.environments if e.name == env_name), None)
    
    def action_new_environment(self) -> None:
        """Create new environment"""
        self.app.notify("Create new environment (not yet implemented)")
    
    def action_start_environment(self) -> None:
        """Start selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Starting {self.selected_env.name}...")
    
    def action_stop_environment(self) -> None:
        """Stop selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Stopping {self.selected_env.name}...")
    
    def action_restart_environment(self) -> None:
        """Restart selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Restarting {self.selected_env.name}...")
    
    def action_build_environment(self) -> None:
        """Build selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Building {self.selected_env.name}...")
    
    def action_view_logs(self) -> None:
        """View logs for selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Viewing logs for {self.selected_env.name}...")
    
    def action_inspect_environment(self) -> None:
        """Inspect selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Inspecting {self.selected_env.name}...")
    
    def action_configure_environment(self) -> None:
        """Configure selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Configuring {self.selected_env.name}...")
    
    def action_delete_environment(self) -> None:
        """Delete selected environment"""
        if not self.selected_env:
            self.app.notify("No environment selected", severity="warning")
            return
        self.app.notify(f"Delete {self.selected_env.name} (not yet implemented)")
    
    def action_refresh(self) -> None:
        """Refresh environment list"""
        self.app.notify("Refreshing...")
        # This will be implemented to reload from discovery service
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()
