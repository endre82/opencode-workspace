"""Main Textual application"""

from pathlib import Path
from textual.app import App
from textual.widgets import Header, Footer

from envman.screens.dashboard import Dashboard
from envman.services.discovery import DiscoveryService
from envman.services.docker import DockerService
from envman.utils.exceptions import DockerError


class EnvironmentManagerApp(App):
    """OpenCode Environment Manager TUI Application"""
    
    CSS = """
    #dashboard-container {
        height: 100%;
        padding: 1;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }
    
    #env-table {
        height: 1fr;
        border: solid $primary;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
        margin-top: 1;
    }
    
    DataTable {
        height: 100%;
    }
    
    DataTable > .datatable--header {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    DataTable > .datatable--cursor {
        background: $secondary;
    }
    """
    
    TITLE = "OpenCode Environment Manager"
    SUB_TITLE = "Manage your development environments"
    
    def __init__(self, base_dir: Path | None = None):
        super().__init__()
        self.base_dir = base_dir or Path.cwd()
        self.discovery_service: DiscoveryService | None = None
        self.docker_service: DockerService | None = None
    
    def on_mount(self) -> None:
        """Initialize services and load environments"""
        try:
            # Initialize services
            self.docker_service = DockerService()
            self.discovery_service = DiscoveryService(self.base_dir)
            
            # Discover environments
            environments = self.discovery_service.discover_environments()
            
            if not environments:
                self.notify(
                    "No environments found. Create one with the creation wizard.",
                    severity="information",
                    timeout=5
                )
            
            # Show dashboard
            self.push_screen(Dashboard(environments))
        
        except DockerError as e:
            self.notify(
                f"Docker error: {e}",
                severity="error",
                timeout=10
            )
            self.exit(1)
        
        except Exception as e:
            self.notify(
                f"Failed to initialize: {e}",
                severity="error",
                timeout=10
            )
            self.exit(1)


def run_app(base_dir: Path | None = None) -> None:
    """Run the TUI application"""
    app = EnvironmentManagerApp(base_dir)
    app.run()
