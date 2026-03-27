"""Main creation wizard orchestrator"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Label, Input, RadioSet, RadioButton, Switch
from textual.containers import Container, Vertical, Horizontal, Center, ScrollableContainer
from textual.binding import Binding

from envman.services.creation import CreationService
from envman.services.validation import ValidationService
from envman.services.discovery import DiscoveryService
from envman.services.docker import DockerService
from envman.utils.exception_logger import set_context


class CreationWizard(Screen):
    """Multi-step environment creation wizard"""
    
    CSS = """
    CreationWizard {
        layout: vertical;
    }
    
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
        scrollbar-gutter: stable;
    }
    
    #step-content-inner {
        height: auto;
    }
    
    #step-content Label {
        margin-bottom: 0;
        color: $text;
    }
    
    #step-content Input {
        margin-bottom: 1;
    }
    
    #step-content Static {
        color: $text-muted;
        margin-bottom: 0;
    }
    
    .section-header {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-top: 1;
        margin-bottom: 0;
        text-style: bold;
    }
    
    .mount-hint {
        color: $text-muted;
        text-style: italic;
        margin-top: 0;
        margin-bottom: 1;
    }
    
    .always-enabled {
        color: $success;
        text-style: bold;
        margin-bottom: 0;
    }
    
    .mount-row-disabled {
        opacity: 0.5;
    }
    
    #error-name, #error-port, .error-message {
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
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(
        self,
        docker_service: DockerService,
        discovery_service: DiscoveryService,
        workspace_root: Path
    ):
        super().__init__()
        self.docker_service = docker_service
        self.discovery_service = discovery_service
        self.workspace_root = workspace_root
        
        # Services
        self.creation_service = CreationService(workspace_root)
        self.validation_service = ValidationService()
        
        # Wizard state
        self.current_step = 1
        self.total_steps = 4
        self.config: Dict[str, Any] = {}
        self.creating = False  # Flag for when we're on summary screen
        
        # Initialize config with defaults
        self._initialize_defaults()
        
        # Set context early so it's available during compose()
        set_context(screen="CreationWizard", step=self.current_step)
    
    def _initialize_defaults(self) -> None:
        """Initialize configuration with default values"""
        # Get host UID/GID
        host_uid = os.getuid()
        host_gid = os.getgid()
        
        # Get next available port
        next_port = self.creation_service.find_next_available_port()
        
        self.config = {
            'name': '',
            'user_id': str(host_uid),
            'group_id': str(host_gid),
            'timezone': 'UTC',
            'workspace_type': 'isolated',
            'workspace_dir': './workspace',
            'mount_global_config': False,
            'mount_project_config': False,
            'mount_opencode_env_config': True,
            'mount_worktree': True,
            'mount_shared_auth': True,
            'global_config': '../shared/config/.opencode',
            'project_config': './opencode_project_config',
            'opencode_env_config': './opencode_config',
            'worktree_dir': './worktree',
            'shared_auth_config': '../../shared/auth/auth.json',
            'ssh_mode': 'default',
            'ssh_host_path': str(Path.home() / '.ssh'),
            'ssh_project_path': './ssh_config',
            'server_port': str(next_port),
            'server_username': 'opencode',
            'server_password': self.creation_service.generate_random_password(),
        }
    
    def compose(self) -> ComposeResult:
        """Compose the wizard UI"""
        yield Header()
        
        with Container(id="wizard-container"):
            # Progress indicator
            yield Static("", id="progress")
            
            # Step title
            yield Static("", id="step-title")
            
            # Step content (scrollable, will be populated in on_mount)
            with ScrollableContainer(id="step-content"):
                yield Vertical(id="step-content-inner")
            
            # Navigation buttons
            with Horizontal(id="wizard-nav"):
                yield Button("Cancel", id="btn-cancel", variant="error")
                yield Button("Back", id="btn-back", variant="default")
                yield Button("Next", id="btn-next", variant="primary")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup when wizard is mounted"""
        self.update_progress()
        self.update_navigation()
        self.render_current_step()  # Populate first step after elements exist
    
    def update_progress(self) -> None:
        """Update progress indicator"""
        progress = self.query_one("#progress", Static)
        progress.update(f"Step {self.current_step} of {self.total_steps}")
    
    def update_navigation(self) -> None:
        """Update navigation button states"""
        back_btn = self.query_one("#btn-back", Button)
        next_btn = self.query_one("#btn-next", Button)
        
        # Disable back on first step
        back_btn.disabled = (self.current_step == 1)
        
        # Change "Next" to "Create" on last step
        if self.current_step == self.total_steps:
            next_btn.label = "Review"
        else:
            next_btn.label = "Next"
    
    def _render_step_1(self) -> Container:
        """Render Step 1: Basic Info"""
        return Vertical(
            Label("Environment Name (required):"),
            Input(
                value=self.config.get('name', ''),
                placeholder="e.g., dev3, my-project",
                id="input-name"
            ),
            Static("", id="error-name"),
            Label("\nUser ID:"),
            Input(
                value=str(self.config['user_id']),
                placeholder="Default: current user ID",
                id="input-user-id"
            ),
            Label("\nGroup ID:"),
            Input(
                value=str(self.config['group_id']),
                placeholder="Default: current group ID",
                id="input-group-id"
            ),
        )
    
    def _render_step_2(self) -> Container:
        """Render Step 2: Workspace Configuration"""
        return Vertical(
            Label("Workspace Type:"),
            RadioSet(
                RadioButton("Isolated (./workspace) - Recommended", value=True),
                RadioButton("External (custom path)"),
                id="workspace-type"
            ),
            Label("\nWorkspace Path:"),
            Input(
                value=self.config['workspace_dir'],
                placeholder="./workspace or /path/to/external",
                id="input-workspace-path"
            ),
            Static("Isolated: Creates workspace inside environment directory", id="workspace-help"),
        )
    
    def _render_step_3(self) -> Container:
        """Render Step 3: Volume Mounts"""
        return Vertical(
            # Section 1: SSH Access (Mandatory)
            Static("🔑 SSH Access (Required)", classes="section-header"),
            Horizontal(
                Label("SSH Mode:"),
                RadioSet(
                    RadioButton("Host ~/.ssh", value=(self.config['ssh_mode'] == 'default')),
                    RadioButton("Project ./ssh_config", value=(self.config['ssh_mode'] == 'project')),
                    id="ssh-mode"
                ),
            ),
            Static("→ /home/dev/.ssh (ro)", classes="mount-hint"),
            
            # Section 2: Always Mounted
            Static("📁 Always Mounted", classes="section-header"),
            Static("✓ WORKSPACE_DIR → /workspace (rw)", classes="always-enabled"),
            Static("✓ OPENCODE_ENV_CONFIG", classes="always-enabled"),
            Input(
                value=self.config['opencode_env_config'],
                placeholder="./opencode_config",
                id="input-env-path"
            ),
            Static("→ /home/dev/.opencode (rw)", classes="mount-hint"),
            
            # Section 3: Optional Configuration Mounts
            Static("⚙️ Optional Config Mounts", classes="section-header"),
            Horizontal(
                Label("Mount GLOBAL_CONFIG:"),
                Switch(value=self.config['mount_global_config'], id="switch-global"),
                id="row-global"
            ),
            Input(
                value=self.config['global_config'],
                placeholder="../shared/config/.opencode",
                id="input-global-path"
            ),
            Static("→ /home/dev/.opencode-shared (ro)", classes="mount-hint"),
            
            Horizontal(
                Label("Mount PROJECT_CONFIG:"),
                Switch(value=self.config['mount_project_config'], id="switch-project"),
                id="row-project"
            ),
            Input(
                value=self.config['project_config'],
                placeholder="./opencode_project_config",
                id="input-project-path"
            ),
            Static("→ /home/dev/.opencode-project (rw)", classes="mount-hint"),
            
            Horizontal(
                Label("Mount WORKTREE_DIR:"),
                Switch(value=self.config['mount_worktree'], id="switch-worktree"),
                id="row-worktree"
            ),
            Input(
                value=self.config['worktree_dir'],
                placeholder="./worktree",
                id="input-worktree-path"
            ),
            Static("→ /home/dev/worktree (rw)", classes="mount-hint"),
            
            # Section 4: Shared Authentication
            Static("🔐 Shared Authentication", classes="section-header"),
            Horizontal(
                Label("Mount SHARED_AUTH:"),
                Switch(value=self.config['mount_shared_auth'], id="switch-shared-auth"),
                id="row-shared-auth"
            ),
            Static("Path: ../../shared/auth/auth.json", classes="mount-hint"),
            Static("→ /home/dev/.opencode/auth.json (ro)", classes="mount-hint"),
        )
    
    def _render_step_4(self) -> Container:
        """Render Step 4: Server Configuration"""
        return Vertical(
            Label("Server Port:"),
            Input(
                value=str(self.config['server_port']),
                placeholder="4100",
                id="input-port"
            ),
            Static("", id="error-port"),
            Label("\nServer Username:"),
            Input(
                value=self.config['server_username'],
                placeholder="opencode",
                id="input-username"
            ),
            Label("\nServer Password:"),
            Input(
                value=self.config['server_password'],
                password=True,
                placeholder="Leave empty for random",
                id="input-password"
            ),
            Button("Generate Random", id="btn-gen-password", variant="default"),
        )
    
    def _render_summary(self) -> Container:
        """Render summary screen"""
        summary = self.creation_service.get_creation_summary(self.config)
        
        return Vertical(
            Static(summary, id="summary-text"),
            Static("\n"),
            Static("Press 'Create' to create the environment.", id="summary-action"),
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "btn-cancel":
            self.action_cancel()
        elif button_id == "btn-back":
            self.go_back()
        elif button_id == "btn-next":
            self.go_next()
        elif button_id == "btn-gen-password":
            self.generate_password()
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggle events"""
        switch_id = event.switch.id
        is_enabled = event.value
        
        # Map switches to their corresponding inputs and rows
        switch_input_map = {
            "switch-global": ("input-global-path", "row-global"),
            "switch-project": ("input-project-path", "row-project"),
            "switch-worktree": ("input-worktree-path", "row-worktree"),
        }
        
        if switch_id in switch_input_map:
            input_id, row_id = switch_input_map[switch_id]
            
            # Enable/disable the input
            try:
                input_widget = self.query_one(f"#{input_id}", Input)
                input_widget.disabled = not is_enabled
                
                # Add/remove disabled styling to the row
                row_widget = self.query_one(f"#{row_id}", Horizontal)
                if is_enabled:
                    row_widget.remove_class("mount-row-disabled")
                else:
                    row_widget.add_class("mount-row-disabled")
            except Exception:
                pass  # Widget may not exist yet
    
    def go_next(self) -> None:
        """Go to next step"""
        # If we're on summary screen, create the environment
        if self.creating:
            self.app.call_later(self.create_environment)
            return
        
        # Validate current step
        if not self.validate_current_step():
            return
        
        # Save current step data
        self.save_current_step()
        
        # Check if we're at the last step
        if self.current_step >= self.total_steps:
            # Show summary and create
            self.show_summary()
        else:
            # Move to next step
            self.current_step += 1
            self.render_current_step()
            self.update_progress()
            self.update_navigation()
    
    def go_back(self) -> None:
        """Go to previous step"""
        # If we're on summary screen, go back to step 4
        if self.creating:
            self.creating = False
            self.current_step = self.total_steps
            self.render_current_step()
            self.update_progress()
            self.update_navigation()
            # Reset Next button styling
            next_btn = self.query_one("#btn-next", Button)
            next_btn.label = "Review"
            next_btn.remove_class("success")
            next_btn.add_class("primary")
        elif self.current_step > 1:
            self.current_step -= 1
            self.render_current_step()
            self.update_progress()
            self.update_navigation()
    
    def validate_current_step(self) -> bool:
        """Validate current step inputs"""
        if self.current_step == 1:
            return self.validate_step_1()
        elif self.current_step == 3:
            return self.validate_step_3()
        elif self.current_step == 4:
            return self.validate_step_4()
        return True
    
    def validate_step_1(self) -> bool:
        """Validate step 1 inputs"""
        name_input = self.query_one("#input-name", Input)
        name = name_input.value.strip()
        
        # Validate environment name
        existing_names = self.creation_service.get_existing_environment_names()
        is_valid, error = self.validation_service.validate_env_name(name, existing_names)
        
        error_label = self.query_one("#error-name", Static)
        if not is_valid:
            error_label.update(f"❌ {error}")
            return False
        
        error_label.update("")
        return True
    
    def validate_step_3(self) -> bool:
        """Validate step 3 mount inputs"""
        errors = []
        
        # Check OPENCODE_ENV_CONFIG (always required)
        env_path = self.query_one("#input-env-path", Input).value.strip()
        if not env_path:
            errors.append("OPENCODE_ENV_CONFIG path is required")
        
        # Check optional mounts that are enabled
        mount_validations = [
            ("switch-global", "input-global-path", "GLOBAL_CONFIG"),
            ("switch-project", "input-project-path", "PROJECT_CONFIG"),
            ("switch-worktree", "input-worktree-path", "WORKTREE_DIR"),
        ]
        
        for switch_id, input_id, mount_name in mount_validations:
            try:
                switch = self.query_one(f"#{switch_id}", Switch)
                if switch.value:
                    input_widget = self.query_one(f"#{input_id}", Input)
                    if not input_widget.value.strip():
                        errors.append(f"{mount_name} is enabled but path is empty")
            except Exception:
                pass
        
        # Display errors if any
        if errors:
            self.app.notify(f"❌ Validation errors:\n" + "\n".join(f"  • {err}" for err in errors), severity="error", timeout=10)
            return False
        
        return True
    
    def validate_step_4(self) -> bool:
        """Validate step 4 inputs"""
        port_input = self.query_one("#input-port", Input)
        port = port_input.value.strip()
        
        # Validate port
        used_ports = self.creation_service.get_used_ports()
        is_valid, error = self.validation_service.validate_port(port, used_ports)
        
        error_label = self.query_one("#error-port", Static)
        if not is_valid:
            error_label.update(f"❌ {error}")
            return False
        
        error_label.update("")
        return True
    
    def save_current_step(self) -> None:
        """Save current step data to config"""
        if self.current_step == 1:
            self.config['name'] = self.query_one("#input-name", Input).value.strip()
            # Convert user_id and group_id to integers
            try:
                self.config['user_id'] = int(self.query_one("#input-user-id", Input).value.strip())
            except ValueError:
                self.config['user_id'] = 1000
            try:
                self.config['group_id'] = int(self.query_one("#input-group-id", Input).value.strip())
            except ValueError:
                self.config['group_id'] = 1000
        
        elif self.current_step == 2:
            radio = self.query_one("#workspace-type", RadioSet)
            self.config['workspace_type'] = 'isolated' if radio.pressed_index == 0 else 'external'
            self.config['workspace_dir'] = self.query_one("#input-workspace-path", Input).value.strip()
        
        elif self.current_step == 3:
            # Save SSH configuration
            radio = self.query_one("#ssh-mode", RadioSet)
            self.config['ssh_mode'] = 'default' if radio.pressed_index == 0 else 'project'
            self.config['ssh_host_path'] = str(Path.home() / '.ssh')
            self.config['ssh_project_path'] = './ssh_config'
            
            # Save volume mount configuration
            self.config['mount_global_config'] = self.query_one("#switch-global", Switch).value
            self.config['mount_project_config'] = self.query_one("#switch-project", Switch).value
            self.config['global_config'] = self.query_one("#input-global-path", Input).value.strip()
            self.config['project_config'] = self.query_one("#input-project-path", Input).value.strip()
            self.config['opencode_env_config'] = self.query_one("#input-env-path", Input).value.strip()
            self.config['mount_worktree'] = self.query_one("#switch-worktree", Switch).value
            self.config['worktree_dir'] = self.query_one("#input-worktree-path", Input).value.strip()
            self.config['mount_shared_auth'] = self.query_one("#switch-shared-auth", Switch).value
        
        elif self.current_step == 4:
            # Convert server_port to integer
            try:
                self.config['server_port'] = int(self.query_one("#input-port", Input).value.strip())
            except ValueError:
                self.config['server_port'] = 4100
            self.config['server_username'] = self.query_one("#input-username", Input).value.strip()
            password = self.query_one("#input-password", Input).value.strip()
            if password:
                self.config['server_password'] = password
    
    def render_current_step(self) -> None:
        """Render the current step"""
        # Update context with current step
        set_context(screen="CreationWizard", step=self.current_step)
        
        # Update step title
        step_title = self.query_one("#step-title", Static)
        if self.current_step == 1:
            step_title.update("Step 1: Basic Information")
        elif self.current_step == 2:
            step_title.update("Step 2: Workspace Configuration")
        elif self.current_step == 3:
            step_title.update("Step 3: Volume Mounts")
        elif self.current_step == 4:
            step_title.update("Step 4: Server Configuration")
        
        # Update content (now targeting the inner vertical container)
        content_container = self.query_one("#step-content-inner", Vertical)
        content_container.remove_children()
        
        if self.current_step == 1:
            content_container.mount(self._render_step_1())
        elif self.current_step == 2:
            content_container.mount(self._render_step_2())
        elif self.current_step == 3:
            content_container.mount(self._render_step_3())
            # Initialize disabled states for step 3
            self.app.call_later(self._initialize_step_3_states)
        elif self.current_step == 4:
            content_container.mount(self._render_step_4())
    
    def _initialize_step_3_states(self) -> None:
        """Initialize disabled states for step 3 inputs based on switch values"""
        switch_input_map = {
            "switch-global": ("input-global-path", "row-global"),
            "switch-project": ("input-project-path", "row-project"),
            "switch-worktree": ("input-worktree-path", "row-worktree"),
        }
        
        for switch_id, (input_id, row_id) in switch_input_map.items():
            try:
                switch = self.query_one(f"#{switch_id}", Switch)
                input_widget = self.query_one(f"#{input_id}", Input)
                row_widget = self.query_one(f"#{row_id}", Horizontal)
                
                # Set initial disabled state
                input_widget.disabled = not switch.value
                if not switch.value:
                    row_widget.add_class("mount-row-disabled")
            except Exception:
                pass  # Widget may not exist yet
    
    def show_summary(self) -> None:
        """Show summary and create environment"""
        # Update title
        step_title = self.query_one("#step-title", Static)
        step_title.update("Review Configuration")
        
        # Update content (now targeting the inner vertical container)
        content_container = self.query_one("#step-content-inner", Vertical)
        content_container.remove_children()
        content_container.mount(self._render_summary())
        
        # Update button
        next_btn = self.query_one("#btn-next", Button)
        next_btn.label = "Create"
        next_btn.remove_class("primary")
        next_btn.add_class("success")
        
        # Override next button behavior
        self.creating = True
    
    def generate_password(self) -> None:
        """Generate random password"""
        password = self.creation_service.generate_random_password()
        password_input = self.query_one("#input-password", Input)
        password_input.value = password
        self.app.notify("Generated random password", severity="information")
    
    def action_cancel(self) -> None:
        """Cancel wizard and return to dashboard"""
        self.app.pop_screen()
    
    async def create_environment(self) -> None:
        """Create the environment"""
        self.app.notify(f"Creating environment '{self.config['name']}'...", timeout=3)
        
        try:
            success, message = await asyncio.to_thread(
                self.creation_service.create_environment,
                self.config
            )
            
            if success:
                self.app.notify(f"✓ {message}", severity="information", timeout=5)
                # Close wizard and refresh dashboard
                self.app.pop_screen()
            else:
                self.app.notify(f"✗ {message}", severity="error", timeout=10)
        
        except Exception as e:
            self.app.notify(f"✗ Error: {e}", severity="error", timeout=10)
