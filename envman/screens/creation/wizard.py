"""Main creation wizard orchestrator"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Label, Input, RadioSet, RadioButton, Switch
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
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

    /* Tight top-level frame — every line matters on a 24-row terminal */
    #wizard-container {
        height: 100%;
        padding: 0 1;
    }

    #progress {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        height: 1;
        padding: 0;
        margin-bottom: 0;
    }

    #step-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        height: 1;
        padding: 0;
        margin-bottom: 0;
    }

    /* The scrollable content area — 1fr means it takes all remaining height */
    #step-content {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
        margin: 0;
    }

    #step-content-inner {
        height: auto;    /* grows to fit content — enables scrolling */
    }

    /* ── Generic form element spacing ───────────────────────────── */
    #step-content Label {
        height: 1;
        padding: 0;
        margin: 0;
        color: $text;
    }

    #step-content Input {
        margin-bottom: 0;
        height: 3;
    }

    #step-content Static {
        color: $text-muted;
        margin: 0;
        padding: 0;
    }

    /* ── Section headers ─────────────────────────────────────────── */
    .section-header {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-top: 1;
        margin-bottom: 0;
        text-style: bold;
        height: 1;
    }

    /* ── Inline error messages ───────────────────────────────────── */
    #error-name, #error-port, #error-step3, .error-message {
        color: $error;
        text-style: bold;
        height: 1;
        margin: 0;
        padding: 0;
    }

    /* ── Always-mounted labels ───────────────────────────────────── */
    .always-enabled {
        color: $success;
        text-style: bold;
        height: 1;
        margin: 0;
    }

    /* ── Compact mount rows (step 3) ────────────────────────────── */
    /*
     * Each optional mount is ONE Horizontal row:
     *   [Switch 8] [Label 15] [Input 1fr] [dest-hint 22]
     * This collapses 3 stacked widgets → 1 row (height 3 due to Input).
     */
    .mount-row {
        height: 3;
        margin-top: 0;
        margin-bottom: 0;
        align: left middle;
    }

    .mount-row Switch {
        width: 8;
        margin: 0 1 0 0;
    }

    .mount-label {
        width: 15;
        content-align: left middle;
        padding: 0;
        color: $text;
    }

    .mount-row Input {
        width: 1fr;
        margin: 0 1;
        height: 3;
    }

    .dest-hint {
        width: 22;
        color: $text-muted;
        text-style: italic;
        content-align: right middle;
        text-align: right;
    }

    .mount-row-disabled {
        opacity: 0.5;
    }

    /* ── Navigation bar ─────────────────────────────────────────── */
    #wizard-nav {
        height: 3;
        align: center middle;
        margin-top: 0;
    }

    #wizard-nav Button {
        margin: 0 1;
        min-width: 12;
    }

    /* ── Summary screen ─────────────────────────────────────────── */
    #summary-text {
        color: $text;
        background: $panel;
        padding: 1;
        border: solid $accent;
    }

    #summary-action {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-top: 1;
        height: 1;
    }

    /* ── Steps 1 & 2 spacing ────────────────────────────────────── */
    #workspace-help {
        color: $text-muted;
        text-style: italic;
        margin-top: 0;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        docker_service: DockerService,
        discovery_service: DiscoveryService,
        workspace_root: Path,
    ):
        super().__init__()
        self.docker_service = docker_service
        self.discovery_service = discovery_service
        self.workspace_root = workspace_root

        self.creation_service = CreationService(workspace_root)
        self.validation_service = ValidationService()

        self.current_step = 1
        self.total_steps = 4
        self.config: Dict[str, Any] = {}
        self.on_summary = False  # True while the review/summary screen is shown

        self._initialize_defaults()
        set_context(screen="CreationWizard", step=self.current_step)

    def _initialize_defaults(self) -> None:
        host_uid = os.getuid()
        host_gid = os.getgid()
        next_port = self.creation_service.find_next_available_port()

        self.config = {
            'name': '',
            'user_id': str(host_uid),
            'group_id': str(host_gid),
            'timezone': 'UTC',
            'workspace_type': 'isolated',
            'workspace_dir': './workspace',
            'mount_worktree': True,
            'worktree_dir': './workspace.worktrees',
            # OpenCode config mode: host, global, or project
            'opencode_config_mode': 'project',
            # OpenCode config path (fixed structure, not user-editable)
            'opencode_env_config': './opencode_config',
            # ssh_use_host: True = use host ~/.ssh, False = use ./ssh_config
            'ssh_use_host': True,
            'ssh_mode': 'default',  # kept in sync with ssh_use_host by save_current_step
            'ssh_host_path': str(Path.home() / '.ssh'),
            'ssh_project_path': './ssh_config',
            'server_port': str(next_port),
            'server_username': 'opencode',
            'server_password': self.creation_service.generate_random_password(),
        }

    # ─── Scaffold ──────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("", id="progress")
            yield Static("", id="step-title")
            with ScrollableContainer(id="step-content"):
                yield Vertical(id="step-content-inner")
            with Horizontal(id="wizard-nav"):
                yield Button("Cancel", id="btn-cancel", variant="error")
                yield Button("Back",   id="btn-back",   variant="default")
                yield Button("Next",   id="btn-next",   variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.update_progress()
        self.update_navigation()
        self.render_current_step()

    # ─── Progress & nav ────────────────────────────────────────────────────────

    def update_progress(self) -> None:
        label = (
            f"Step {self.total_steps} of {self.total_steps} — Review"
            if self.on_summary
            else f"Step {self.current_step} of {self.total_steps}"
        )
        self.query_one("#progress", Static).update(label)

    def update_navigation(self) -> None:
        back_btn = self.query_one("#btn-back", Button)
        next_btn = self.query_one("#btn-next", Button)

        back_btn.disabled = (self.current_step == 1 and not self.on_summary)

        if self.on_summary:
            next_btn.label = "Create"
            next_btn.variant = "success"
        elif self.current_step >= self.total_steps:
            next_btn.label = "Review"
            next_btn.variant = "primary"
        else:
            next_btn.label = "Next"
            next_btn.variant = "primary"

    # ─── Step renderers ────────────────────────────────────────────────────────

    def _render_step_1(self) -> Vertical:
        return Vertical(
            Label("Environment Name (required):"),
            Input(value=self.config.get('name', ''), placeholder="e.g. dev3, my-project", id="input-name"),
            Static("", id="error-name"),
            Label("User ID:"),
            Input(value=str(self.config['user_id']), placeholder="current user ID", id="input-user-id"),
            Label("Group ID:"),
            Input(value=str(self.config['group_id']), placeholder="current group ID", id="input-group-id"),
        )

    def _render_step_2(self) -> Vertical:
        isolated = self.config.get('workspace_type', 'isolated') == 'isolated'
        return Vertical(
            Label("Workspace Type:"),
            RadioSet(
                RadioButton("Isolated  ./workspace  (recommended)", value=isolated),
                RadioButton("External  (custom path)",              value=not isolated),
                id="workspace-type",
            ),
            Label("Workspace Path:"),
            Input(value=self.config['workspace_dir'], placeholder="./workspace or /path/to/external", id="input-workspace-path"),
            Static("Isolated mode creates the workspace inside the environment directory.", id="workspace-help"),
            Label("Worktree Directory:"),
            Horizontal(
                Switch(value=self.config['mount_worktree'], id="switch-worktree"),
                Label("Enable worktrees", classes="mount-label"),
                Input(value=self.config['worktree_dir'], placeholder="./workspace.worktrees", id="input-worktree-path"),
                Static("→ /home/dev/.local/share/opencode/worktree (rw)", classes="dest-hint"),
                id="row-worktree",
                classes="mount-row",
            ),
        )

    def _render_step_3(self) -> Vertical:
        """
        Step 3 — Volume Mounts.

        Layout goal: fit as much as possible on screen while keeping a clear
        scrollable area for the rest. Mount rows are single compact Horizontal
        rows with [Switch] [Label] [Input/Static] [→ destination].
        """
        return Vertical(
            # Inline error bar (hidden until validation fires)
            Static("", id="error-step3"),

            # ── SSH ──────────────────────────────────────────────────────
            Static("🔑 SSH Access (required)", classes="section-header"),
            Horizontal(
                Switch(value=self.config['ssh_use_host'], id="switch-ssh-host"),
                Label("Use host ~/.ssh", classes="mount-label"),
                Static("off → use ./ssh_config  →  /home/dev/.ssh (ro)", classes="dest-hint"),
                classes="mount-row",
                id="row-ssh",
            ),

            # ── Always mounted ───────────────────────────────────────────
            Static("📁 Always Mounted", classes="section-header"),
            Static("  ✓  WORKSPACE_DIR  →  /workspace  (rw)", classes="always-enabled"),
            # Env config is always mounted with fixed path
            Horizontal(
                Static("  ✓  ENV_CONFIG", classes="mount-label always-enabled"),
                Static(self.config['opencode_env_config'], classes="mount-label"),
                Static("→ /home/dev/.local/share/opencode (rw)", classes="dest-hint"),
                classes="mount-row",
            ),

            # ── OpenCode Config Source ──────────────────────────────────
            Static("⚙️  OpenCode Config Source", classes="section-header"),
            RadioSet(
                RadioButton("Host      — ~/.opencode/opencode.jsonc + auth.json  [read-only]", value=self.config['opencode_config_mode'] == 'host'),
                RadioButton("Global    — shared/config/opencode.jsonc + auth.json  [read-only]", value=self.config['opencode_config_mode'] == 'global'),
                RadioButton("Project   — ./opencode_project_config/opencode.jsonc  [read-write]", value=self.config['opencode_config_mode'] == 'project'),
                id="opencode-config-mode",
            ),
        )

    def _render_step_4(self) -> Vertical:
        return Vertical(
            Label("Server Port:"),
            Input(value=str(self.config['server_port']), placeholder="4100", id="input-port"),
            Static("", id="error-port"),
            Label("Server Username:"),
            Input(value=self.config['server_username'], placeholder="opencode", id="input-username"),
            Label("Server Password:"),
            Input(value=self.config['server_password'], password=True, placeholder="leave empty for random", id="input-password"),
            Button("Generate Random", id="btn-gen-password", variant="default"),
        )

    def _render_summary(self) -> Vertical:
        summary = self.creation_service.get_creation_summary(self.config)
        return Vertical(
            Static(summary, id="summary-text"),
            Static("Press 'Create' to create the environment.", id="summary-action"),
        )

    # ─── Rendering ─────────────────────────────────────────────────────────────

    def render_current_step(self) -> None:
        set_context(screen="CreationWizard", step=self.current_step)

        titles = {
            1: "Step 1: Basic Information",
            2: "Step 2: Workspace Configuration",
            3: "Step 3: Volume Mounts",
            4: "Step 4: Server Configuration",
        }
        self.query_one("#step-title", Static).update(titles.get(self.current_step, ""))

        content = self.query_one("#step-content-inner", Vertical)
        content.remove_children()

        renderers = {
            1: self._render_step_1,
            2: self._render_step_2,
            3: self._render_step_3,
            4: self._render_step_4,
        }
        renderer = renderers.get(self.current_step)
        if renderer:
            content.mount(renderer())

        if self.current_step == 2:
            self.app.call_later(self._initialize_step_2_states)
        elif self.current_step == 3:
            self.app.call_later(self._initialize_step_3_states)

        # Scroll back to top whenever step changes
        self.app.call_later(self._scroll_to_top)

    def _scroll_to_top(self) -> None:
        try:
            self.query_one("#step-content", ScrollableContainer).scroll_home(animate=False)
        except Exception:
            pass

    def show_summary(self) -> None:
        self.query_one("#step-title", Static).update("Review Configuration")
        content = self.query_one("#step-content-inner", Vertical)
        content.remove_children()
        content.mount(self._render_summary())
        self.on_summary = True
        self.update_progress()
        self.update_navigation()

    # ─── Switch state initialisation (step 3) ─────────────────────────────────

    def _initialize_step_2_states(self) -> None:
        """Disable worktree input if switch is off, on first render of step 2."""
        try:
            sw  = self.query_one("#switch-worktree", Switch)
            inp = self.query_one("#input-worktree-path",  Input)
            row = self.query_one("#row-worktree",    Horizontal)
            inp.disabled = not sw.value
            if not sw.value:
                row.add_class("mount-row-disabled")
        except Exception:
            pass

    def _initialize_step_3_states(self) -> None:
        """Initialize state for step 3 switches (SSH, worktree)."""
        # SSH switch state initialization (already handled by default value)
        try:
            sw  = self.query_one("#switch-ssh-host", Switch)
            row = self.query_one("#row-ssh",    Horizontal)
            if not sw.value:
                row.add_class("mount-row-disabled")
        except Exception:
            pass
        
        # Worktree switch state initialization
        try:
            sw  = self.query_one("#switch-worktree", Switch)
            inp = self.query_one("#input-worktree-path",  Input)
            row = self.query_one("#row-worktree",    Horizontal)
            inp.disabled = not sw.value
            if not sw.value:
                row.add_class("mount-row-disabled")
        except Exception:
            pass

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes for worktree."""
        if event.switch.id == "switch-worktree":
            try:
                inp = self.query_one("#input-worktree-path", Input)
                row = self.query_one("#row-worktree", Horizontal)
                inp.disabled = not event.value
                row.remove_class("mount-row-disabled") if event.value else row.add_class("mount-row-disabled")
            except Exception:
                pass

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle workspace type selection changes in step 2."""
        if event.radio_set.id != "workspace-type":
            return
        try:
            inp = self.query_one("#input-workspace-path", Input)
        except Exception:
            return
        
        if event.index == 1:  # External selected
            project_name = self.config.get('name', '')
            inp.value = str(Path.home() / 'workspace' / project_name) if project_name else str(Path.home() / 'workspace')
        else:  # Isolated selected (index 0)
            inp.value = './workspace'

    def on_input_changed(self, event: Input.Changed) -> None:
        """Auto-compute worktree path when workspace path changes."""
        if event.input.id != "input-workspace-path":
            return
        try:
            worktree_inp = self.query_one("#input-worktree-path", Input)
        except Exception:
            return
        
        workspace_val = event.value.strip()
        if workspace_val:
            worktree_inp.value = workspace_val.rstrip('/') + '.worktrees'
        else:
            worktree_inp.value = './workspace.worktrees'

    # ─── Navigation ────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-cancel":      self.action_cancel()
            case "btn-back":        self.go_back()
            case "btn-next":        self.go_next()
            case "btn-gen-password":self.generate_password()

    def go_next(self) -> None:
        if self.on_summary:
            self.app.call_later(self.create_environment)
            return
        if not self.validate_current_step():
            return
        self.save_current_step()
        if self.current_step >= self.total_steps:
            self.show_summary()
        else:
            self.current_step += 1
            self.render_current_step()
            self.update_progress()
            self.update_navigation()

    def go_back(self) -> None:
        if self.on_summary:
            self.on_summary = False
            self.current_step = self.total_steps
            self.render_current_step()
            self.update_progress()
            self.update_navigation()
        elif self.current_step > 1:
            self.current_step -= 1
            self.render_current_step()
            self.update_progress()
            self.update_navigation()

    # ─── Validation ────────────────────────────────────────────────────────────

    def validate_current_step(self) -> bool:
        match self.current_step:
            case 1: return self.validate_step_1()
            case 3: return self.validate_step_3()
            case 4: return self.validate_step_4()
        return True

    def validate_step_1(self) -> bool:
        name = self.query_one("#input-name", Input).value.strip()
        existing = self.creation_service.get_existing_environment_names()
        is_valid, error = self.validation_service.validate_env_name(name, existing)
        err_label = self.query_one("#error-name", Static)
        err_label.update(f"❌ {error}" if not is_valid else "")
        return is_valid

    def validate_step_3(self) -> bool:
        """Validate step 3 — volume mounts. RadioSet always has a value, so no validation needed."""
        err_label = self.query_one("#error-step3", Static)
        err_label.update("")
        return True

    def validate_step_4(self) -> bool:
        port = self.query_one("#input-port", Input).value.strip()
        used_ports = self.creation_service.get_used_ports()
        is_valid, error = self.validation_service.validate_port(port, used_ports)
        self.query_one("#error-port", Static).update(f"❌ {error}" if not is_valid else "")
        return is_valid

    # ─── Data collection ───────────────────────────────────────────────────────

    def save_current_step(self) -> None:
        match self.current_step:
            case 1:
                self.config['name'] = self.query_one("#input-name", Input).value.strip()
                try:
                    self.config['user_id'] = int(self.query_one("#input-user-id", Input).value.strip())
                except ValueError:
                    self.config['user_id'] = 1000
                try:
                    self.config['group_id'] = int(self.query_one("#input-group-id", Input).value.strip())
                except ValueError:
                    self.config['group_id'] = 1000

            case 2:
                radio = self.query_one("#workspace-type", RadioSet)
                self.config['workspace_type'] = 'isolated' if radio.pressed_index == 0 else 'external'
                self.config['workspace_dir'] = self.query_one("#input-workspace-path", Input).value.strip()
                self.config['mount_worktree'] = self.query_one("#switch-worktree", Switch).value
                self.config['worktree_dir'] = self.query_one("#input-worktree-path", Input).value.strip()

            case 3:
                # SSH: switch on = host ~/.ssh, switch off = ./ssh_config
                self.config['ssh_use_host'] = self.query_one("#switch-ssh-host", Switch).value
                self.config['ssh_mode'] = 'default' if self.config['ssh_use_host'] else 'project'
                self.config['ssh_host_path'] = str(Path.home() / '.ssh')
                self.config['ssh_project_path'] = './ssh_config'

                # OpenCode config mode (host, global, or project)
                radio = self.query_one("#opencode-config-mode", RadioSet)
                modes = ['host', 'global', 'project']
                self.config['opencode_config_mode'] = modes[radio.pressed_index]

            case 4:
                try:
                    self.config['server_port'] = int(self.query_one("#input-port", Input).value.strip())
                except ValueError:
                    self.config['server_port'] = 4100
                self.config['server_username'] = self.query_one("#input-username", Input).value.strip()
                password = self.query_one("#input-password", Input).value.strip()
                if password:
                    self.config['server_password'] = password

    # ─── Misc actions ──────────────────────────────────────────────────────────

    def generate_password(self) -> None:
        self.query_one("#input-password", Input).value = self.creation_service.generate_random_password()
        self.app.notify("Generated random password", severity="information")

    def action_cancel(self) -> None:
        self.app.pop_screen()

    async def create_environment(self) -> None:
        self.app.notify(f"Creating environment '{self.config['name']}'...", timeout=3)
        try:
            success, message = await asyncio.to_thread(
                self.creation_service.create_environment, self.config
            )
            if success:
                self.app.notify(f"✓ {message}", severity="information", timeout=5)
                self.app.pop_screen()
            else:
                self.app.notify(f"✗ {message}", severity="error", timeout=10)
        except Exception as e:
            self.app.notify(f"✗ Error: {e}", severity="error", timeout=10)
