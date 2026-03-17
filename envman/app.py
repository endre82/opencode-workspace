"""Main Textual application"""

from pathlib import Path
from textual.app import App
from textual.widgets import Header, Footer

from envman.screens.dashboard import Dashboard
from envman.services.discovery import DiscoveryService
from envman.services.docker import DockerService
from envman.utils.exceptions import DockerError
from envman.utils.exception_logger import install_global_hook


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
    
    /* Wizard Styles */
    #wizard-container {
        height: 100%;
        padding: 2;
    }
    
    #progress {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }
    
    #step-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding: 1;
        margin-bottom: 2;
    }
    
    #step-content {
        height: 1fr;
        border: solid $primary;
        padding: 2;
        margin-bottom: 1;
    }
    
    #step-content Label {
        margin-bottom: 1;
        color: $text;
    }
    
    #step-content Input {
        margin-bottom: 2;
    }
    
    #step-content Static {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #error-name, #error-port {
        color: $error;
        text-style: bold;
        margin-top: 0;
        margin-bottom: 1;
    }
    
    #wizard-nav {
        height: 3;
        align: center middle;
    }
    
    #wizard-nav Button {
        margin: 0 1;
        min-width: 12;
    }
    
    #summary-text {
        color: $text;
        background: $panel;
        padding: 2;
        border: solid $accent;
    }
    
    #summary-action {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-top: 1;
    }
    
    #workspace-help {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }
    """
    
    TITLE = "OpenCode Environment Manager"
    SUB_TITLE = "Manage your development environments"
    
    def __init__(self, base_dir: Path | None = None):
        super().__init__()
        # Install global exception logger
        install_global_hook()
        self.base_dir = base_dir or Path.cwd()
        self.discovery_service: DiscoveryService | None = None
        self.docker_service: DockerService | None = None
    
    def on_error(self, event) -> None:
        """Handle Textual app-level errors and log them."""
        from envman.utils.exception_logger import log_textual_exception
        
        # Log the exception with app-level context
        log_textual_exception(
            event.exception,
            context={"screen": "App", "app_state": "error_handler"}
        )
        
        # Allow default error handling to continue
        # This ensures the error is still displayed to the user
        return super().on_error(event)
    
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
            
            # Show dashboard with services
            self.push_screen(
                Dashboard(
                    environments, 
                    self.docker_service, 
                    self.discovery_service,
                    self.base_dir
                )
            )
        
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
