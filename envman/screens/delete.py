"""Delete environment screen"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Input, Checkbox, Button
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
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

    /* Dialog fills 92% of width so long paths are never cut off */
    #delete-dialog {
        width: 92%;
        max-width: 110;
        height: auto;
        max-height: 90%;
        border: thick $error 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $error;
        height: 1;
        margin-bottom: 1;
    }

    #warning {
        width: 100%;
        content-align: center middle;
        color: $error;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }

    /* ── Always-removed info box ───────────────────────────────── */
    .info-box {
        border: solid $primary;
        padding: 0 1;
        margin-bottom: 1;
    }

    .info-item {
        height: 1;
        color: $text;
    }

    .safe-note {
        color: $success;
        text-style: bold;
        height: 1;
        margin-top: 1;
    }

    /* ── Optional deletions section ─────────────────────────────── */
    #optional-label {
        color: $text;
        text-style: bold;
        height: 1;
        margin-bottom: 0;
    }

    .opt-row {
        height: auto;
        margin-top: 1;
    }

    /* Path lines sit directly under their checkbox, indented */
    .path-line {
        color: $text-muted;
        text-style: italic;
        margin-left: 4;
        margin-top: 0;
        /* Allow wrapping so path is never truncated */
        width: 100%;
    }

    /* ── Confirmation ────────────────────────────────────────────── */
    #confirmation-section {
        margin-top: 1;
    }

    #confirmation-label {
        height: 1;
        margin-bottom: 0;
    }

    #confirmation-input {
        margin-top: 0;
    }

    /* ── Buttons ─────────────────────────────────────────────────── */
    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
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
        self.is_deleting = False

        set_context(screen="DeleteEnvironment", environment_name=self.environment.name)

    def compose(self) -> ComposeResult:
        yield Header()

        env = self.environment
        workspace_path  = env.path / "workspace"
        env_config_path = env.path / "opencode_config"

        with Container(id="delete-dialog"):

            yield Static(f"⚠️  Delete Environment: [bold]{env.name}[/bold]", id="title")
            yield Static("WARNING: This action cannot be undone!", id="warning")

            # ── What is always removed ─────────────────────────────────
            with Vertical(classes="info-box"):
                yield Static("Always removed:", classes="info-item")
                yield Static("  ✓  Docker container — stopped and removed", classes="info-item")
                yield Static("  ✓  Named Docker volumes (docker compose down --volumes)", classes="info-item")
                yield Static("  ✓  Container network attachment", classes="info-item")
                yield Static(
                    "  🛡  Global config, shared auth and host ~/.ssh are NEVER touched",
                    classes="safe-note",
                )

            # ── Optional disk deletions ────────────────────────────────
            yield Static("Optionally also delete from disk:", id="optional-label")

            with Vertical(classes="opt-row"):
                yield Checkbox("Delete workspace data", value=False, id="delete-workspace")
                yield Static(str(workspace_path), classes="path-line")

            with Vertical(classes="opt-row"):
                yield Checkbox("Delete environment config", value=False, id="delete-config")
                yield Static(str(env_config_path), classes="path-line")

            with Vertical(classes="opt-row"):
                yield Checkbox(
                    "Delete entire environment directory  (includes everything above)",
                    value=False,
                    id="delete-all",
                )
                yield Static(str(env.path), classes="path-line")

            # ── Confirmation input ─────────────────────────────────────
            with Vertical(id="confirmation-section"):
                yield Static(
                    f"Type [bold]{env.name}[/bold] to confirm deletion:",
                    id="confirmation-label",
                )
                yield Input(placeholder=env.name, id="confirmation-input")

            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Delete", variant="error",   id="delete-btn", disabled=True)

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#confirmation-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "confirmation-input":
            self.query_one("#delete-btn", Button).disabled = (
                event.value != self.environment.name
            )

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "delete-all":
            # "Delete all" supersedes the individual options
            for cb_id in ("delete-workspace", "delete-config"):
                self.query_one(f"#{cb_id}", Checkbox).disabled = event.value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "delete-btn":
            await self.perform_deletion()

    async def perform_deletion(self) -> None:
        if self.is_deleting:
            return

        self.is_deleting = True
        delete_btn = self.query_one("#delete-btn", Button)
        cancel_btn = self.query_one("#cancel-btn", Button)
        delete_btn.disabled = True
        cancel_btn.disabled = True

        try:
            delete_all       = self.query_one("#delete-all",        Checkbox).value
            delete_workspace = self.query_one("#delete-workspace",   Checkbox).value
            delete_config    = self.query_one("#delete-config",      Checkbox).value

            # Step 1: Stop running container
            if self.environment.is_running:
                self.notify("Stopping container...", severity="information")
                success, output = await asyncio.to_thread(
                    self.docker_service.stop_container, str(self.environment.path)
                )
                if not success:
                    self.notify(f"Failed to stop container: {output}", severity="error")
                    return

            # Step 2: Remove container + named volumes
            self.notify("Removing container...", severity="information")
            success, output = await asyncio.to_thread(
                self.docker_service.remove_container,
                str(self.environment.path),
                force=True,
                volumes=True,
            )
            if not success:
                self.notify(f"Failed to remove container: {output}", severity="error")
                return

            # Step 3: Optional disk deletions
            #
            # SAFETY: only paths that are children of environment.path are ever
            # touched here.  Global config (../shared/...) and shared auth
            # (../../shared/...) live OUTSIDE environment.path and are never
            # passed to rmtree.
            if delete_all:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_archive = (
                    self.environment.path.parent
                    / f"backup_{self.environment.name}_{timestamp}.tar.gz"
                )
                try:
                    import tarfile
                    with tarfile.open(backup_archive, "w:gz") as tar:
                        if self.environment.env_file_path.exists():
                            tar.add(self.environment.env_file_path, arcname=".env")
                        if self.environment.docker_compose_path.exists():
                            tar.add(self.environment.docker_compose_path, arcname="docker-compose.yml")
                    self.notify(f"Config backup: {backup_archive.name}", severity="information")
                except Exception as e:
                    self.notify(f"Backup failed (continuing): {e}", severity="warning")

                self.notify("Deleting environment directory...", severity="information")
                await asyncio.to_thread(shutil.rmtree, self.environment.path, ignore_errors=True)

            else:
                if delete_workspace:
                    workspace_dir = self.environment.path / "workspace"
                    if workspace_dir.exists():
                        self.notify("Deleting workspace data...", severity="information")
                        await asyncio.to_thread(shutil.rmtree, workspace_dir, ignore_errors=True)

                if delete_config:
                    config_dir = self.environment.path / "opencode_config"
                    if config_dir.exists():
                        self.notify("Deleting environment config...", severity="information")
                        await asyncio.to_thread(shutil.rmtree, config_dir, ignore_errors=True)

            # Success — dismiss first, then clean up state
            self.notify(
                f"✓ Environment '{self.environment.name}' deleted",
                severity="information",
                timeout=5,
            )
            self.is_deleting = False
            self.dismiss(True)
            return

        except DockerError as e:
            self.notify(f"Docker error: {e}", severity="error")
        except Exception as e:
            self.notify(f"Deletion failed: {e}", severity="error")

        # Only reached on failure — re-enable so user can retry or cancel
        self.is_deleting = False
        delete_btn.disabled = False
        cancel_btn.disabled = False

    def action_cancel(self) -> None:
        self.dismiss(False)
