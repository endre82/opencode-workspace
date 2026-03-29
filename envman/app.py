"""Main Textual application"""

import json
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
    
    @property
    def _settings_path(self) -> Path:
        """Path to the settings file"""
        return Path.home() / ".local" / "share" / "opencode-workspace" / "settings.json"
    
    def _load_settings(self) -> dict:
        """Load settings from disk, return empty dict if not found or invalid"""
        try:
            if self._settings_path.exists():
                with open(self._settings_path, "r") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {}
    
    def _save_settings(self, settings: dict) -> None:
        """Save settings to disk"""
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._settings_path, "w") as f:
                json.dump(settings, f)
        except IOError:
            pass
    
    def watch_theme(self, new_theme: str) -> None:
        """Save theme preference when user changes it"""
        settings = self._load_settings()
        settings["theme"] = new_theme
        self._save_settings(settings)
    
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
            # Restore theme preference
            settings = self._load_settings()
            if "theme" in settings:
                try:
                    self.theme = settings["theme"]
                except Exception:
                    pass  # Invalid theme name, use default
            
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
