"""Delete environment screen"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Input, Checkbox, Button
from textual.containers import Container, Vertical, Horizontal, Center
from textual.binding import Binding

from envman.models.environment import Environment
from envman.services.docker import DockerService
from envman.services.discovery import DiscoveryService
from envman.utils.exceptions import DockerError
from envman.utils.exception_logger import set_context


class DeleteEnvironmentScreen(Screen):
    """Delete environment with confirmation and optional data cleanup"""
    
    CSS = """
    DeleteEnvironmentScreen {
        align: center middle;
    }
    
    #delete-dialog {
        width: 70;
        height: auto;
        border: thick $error 80%;
        background: $surface;
        padding: 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $error;
        padding: 0 0 1 0;
    }
    
    #warning {
        width: 100%;
        content-align: center middle;
        color: $error;
        text-style: bold;
        padding: 1 0;
    }
    
    #message {
        width: 100%;
        padding: 1 0;
    }
    
    .info-box {
        border: solid $primary;
        padding: 1;
        margin: 1 0;
    }
    
    .checkbox-container {
        padding: 0.5 0;
    }
    
    #confirmation-section {
        padding: 1 0;
    }
    
    #confirmation-input {
        margin: 1 0;
    }
    
    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 0 0 0;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(
        self,
        environment: Environment,
        docker_service: DockerService,
        discovery_service: DiscoveryService,
    ):
        super().__init__()
        self.environment = environment
        self.docker_service = docker_service
        self.discovery_service = discovery_service
        self.delete_workspace = False
        self.delete_config = False
        self.is_deleting = False
    
    def compose(self) -> ComposeResult:
        """Compose the deletion dialog"""
        yield Header()
        
        with Container(id="delete-dialog"):
            yield Static(f"⚠️  Delete Environment: {self.environment.name}", id="title")
            
            yield Static("WARNING: This action cannot be undone!", id="warning")
            
            yield Static(
                "This will permanently delete the following:",
                id="message"
            )
            
            with Vertical(classes="info-box"):
                yield Static("✓ Docker container (stopped and removed)", classes="info-item")
                yield Static("✓ Container volumes", classes="info-item")
                yield Static("✓ Network connections", classes="info-item")
            
            with Vertical(id="optional-deletions"):
                yield Static("Optionally delete (check to remove):")
                
                with Vertical(classes="checkbox-container"):
                    workspace_path = str(self.environment.path / "workspace")
                    yield Checkbox(
                        f"Delete workspace data ({workspace_path})",
                        value=False,
                        id="delete-workspace"
                    )
                
                with Vertical(classes="checkbox-container"):
                    config_path = str(self.environment.path / "opencode_config")
                    yield Checkbox(
                        f"Delete configuration ({config_path})",
                        value=False,
                        id="delete-config"
                    )
                
                with Vertical(classes="checkbox-container"):
                    yield Checkbox(
                        f"Delete entire environment directory ({self.environment.path})",
                        value=False,
                        id="delete-all"
                    )
            
            with Vertical(id="confirmation-section"):
                yield Static(
                    f"Type the environment name '{self.environment.name}' to confirm deletion:",
                    id="confirmation-label"
                )
                yield Input(
                    placeholder=self.environment.name,
                    id="confirmation-input"
                )
            
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Delete", variant="error", id="delete-btn", disabled=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Focus the confirmation input on mount"""
        set_context(screen="DeleteEnvironment", environment_name=self.environment.name)
        self.query_one("#confirmation-input", Input).focus()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Enable delete button when confirmation matches"""
        if event.input.id == "confirmation-input":
            delete_btn = self.query_one("#delete-btn", Button)
            delete_btn.disabled = (event.value != self.environment.name)
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes"""
        if event.checkbox.id == "delete-all":
            # If "delete all" is checked, disable individual options
            workspace_cb = self.query_one("#delete-workspace", Checkbox)
            config_cb = self.query_one("#delete-config", Checkbox)
            
            if event.value:
                workspace_cb.disabled = True
                config_cb.disabled = True
            else:
                workspace_cb.disabled = False
                config_cb.disabled = False
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "delete-btn":
            await self.perform_deletion()
    
    async def perform_deletion(self) -> None:
        """Perform the actual deletion"""
        if self.is_deleting:
            return
        
        self.is_deleting = True
        
        # Disable buttons during deletion
        delete_btn = self.query_one("#delete-btn", Button)
        cancel_btn = self.query_one("#cancel-btn", Button)
        delete_btn.disabled = True
        cancel_btn.disabled = True
        
        try:
            # Get deletion options
            delete_all = self.query_one("#delete-all", Checkbox).value
            delete_workspace = self.query_one("#delete-workspace", Checkbox).value
            delete_config = self.query_one("#delete-config", Checkbox).value
            
            # Create backup directory
            backups_dir = self.environment.path / "backups"
            backups_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Step 1: Stop container if running
            if self.environment.is_running:
                self.notify("Stopping container...", severity="information")
                success, output = await asyncio.to_thread(
                    self.docker_service.stop_container,
                    str(self.environment.path)
                )
                if not success:
                    self.notify(f"Failed to stop container: {output}", severity="error")
                    return
            
            # Step 2: Remove container
            self.notify("Removing container...", severity="information")
            success, output = await asyncio.to_thread(
                self.docker_service.remove_container,
                str(self.environment.path),
                force=True,
                volumes=True
            )
            
            if not success:
                self.notify(f"Failed to remove container: {output}", severity="error")
                return
            
            # Step 3: Delete directories based on user selection
            if delete_all:
                # Delete entire environment directory
                self.notify("Deleting entire environment directory...", severity="information")
                
                # Create a backup of important files first
                backup_archive = backups_dir.parent / f"backup_{self.environment.name}_{timestamp}.tar.gz"
                try:
                    import tarfile
                    with tarfile.open(backup_archive, "w:gz") as tar:
                        # Backup .env and docker-compose.yml
                        if self.environment.env_file_path.exists():
                            tar.add(self.environment.env_file_path, arcname=".env")
                        if self.environment.docker_compose_path.exists():
                            tar.add(self.environment.docker_compose_path, arcname="docker-compose.yml")
                    
                    self.notify(f"Backup created: {backup_archive}", severity="information")
                except Exception as e:
                    self.notify(f"Backup failed (continuing anyway): {e}", severity="warning")
                
                # Delete the directory
                await asyncio.to_thread(shutil.rmtree, self.environment.path, ignore_errors=True)
                
            else:
                # Selective deletion
                if delete_workspace:
                    workspace_dir = self.environment.path / "workspace"
                    if workspace_dir.exists():
                        self.notify("Deleting workspace data...", severity="information")
                        await asyncio.to_thread(shutil.rmtree, workspace_dir, ignore_errors=True)
                
                if delete_config:
                    config_dir = self.environment.path / "opencode_config"
                    if config_dir.exists():
                        self.notify("Deleting configuration...", severity="information")
                        await asyncio.to_thread(shutil.rmtree, config_dir, ignore_errors=True)
            
            # Success!
            self.notify(
                f"Environment '{self.environment.name}' deleted successfully",
                severity="information",
                timeout=5
            )
            
            # Close this screen and refresh dashboard
            self.dismiss(True)
        
        except DockerError as e:
            self.notify(f"Docker error: {e}", severity="error")
        except Exception as e:
            self.notify(f"Deletion failed: {e}", severity="error")
        finally:
            self.is_deleting = False
            delete_btn.disabled = False
            cancel_btn.disabled = False
    
    def action_cancel(self) -> None:
        """Cancel deletion"""
        self.dismiss(False)
