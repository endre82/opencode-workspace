"""Tunnel management modal"""

import asyncio

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from envman.models.environment import Environment
from envman.services.ngrok import NgrokService
from envman.utils.browser import open_url


class TunnelModal(ModalScreen[None]):
    """Modal dialog for managing ngrok tunnels per-service"""
    
    CSS = """
    TunnelModal {
        align: center middle;
    }
    
    #dialog {
        width: 100;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        padding: 0 0 1 0;
    }
    
    #warning {
        width: 100%;
        border: solid $warning;
        background: $boost;
        padding: 1;
        margin: 1 0;
        color: $warning;
    }
    
    .service-box {
        width: 100%;
        border: solid $primary;
        background: $panel;
        padding: 1;
        margin: 0 0 1 0;
    }
    
    .service-title {
        width: 100%;
        color: $primary;
        text-style: bold;
        height: auto;
        margin: 0 0 1 0;
    }
    
    .service-status {
        width: 100%;
        color: $accent;
        height: auto;
        margin: 0 0 1 0;
    }
    
    .service-buttons {
        width: 100%;
        height: auto;
    }
    
    #password-section {
        width: 100%;
        border: solid $success;
        background: $panel;
        padding: 1;
        margin: 1 0;
    }
    
    .password-label {
        width: 100%;
        color: $text-muted;
        text-style: italic;
        height: auto;
        margin: 0 0 1 0;
    }
    
    .password-value {
        width: 100%;
        color: $accent;
        text-style: bold;
        height: auto;
        margin: 0 0 1 0;
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
        Binding("escape", "close", "Close"),
    ]
    
    def __init__(
        self,
        environment: Environment,
        ngrok_service: NgrokService,
    ):
        """
        Initialize tunnel modal.
        
        Args:
            environment: The environment to tunnel
            ngrok_service: The ngrok service instance
        """
        super().__init__()
        self.environment = environment
        self.ngrok_service = ngrok_service
        self.is_starting_opencode = False
        self.is_starting_vscode = False
        self.is_stopping = False
    
    def compose(self) -> ComposeResult:
        """Compose the dialog"""
        with Container(id="dialog"):
            yield Static(f"🔗 Tunnel: {self.environment.name}", id="title")
            
            yield Static(
                "⚠️  ngrok free tier: starting one service stops the other. "
                "Each start generates a new random URL.",
                id="warning"
            )
            
            # OpenCode service
            with Vertical(classes="service-box"):
                yield Label("OpenCode Server", classes="service-title")
                yield Label(id="opencode-status", classes="service-status")
                with Horizontal(classes="service-buttons"):
                    yield Button("Start Tunnel", id="start-opencode", variant="primary")
                    yield Button("🌐 Open & Copy", id="open-opencode", disabled=True, variant="success")
                    yield Button("Stop", id="stop-opencode", disabled=True, variant="warning")
            
            # VSCode service
            with Vertical(classes="service-box"):
                yield Label("VSCode", classes="service-title")
                yield Label(id="vscode-status", classes="service-status")
                with Horizontal(classes="service-buttons"):
                    yield Button("Start Tunnel", id="start-vscode", variant="primary")
                    yield Button("🌐 Open & Copy", id="open-vscode", disabled=True, variant="success")
                    yield Button("Stop", id="stop-vscode", disabled=True, variant="warning")
            
            # Password section
            with Vertical(id="password-section"):
                yield Label("Password", classes="password-label")
                yield Label(id="password-display", classes="password-value")
                yield Button("📋 Copy Password", id="copy-password", disabled=True, variant="default")
            
            # Bottom buttons
            with Horizontal(id="buttons"):
                yield Button("Close", variant="default", id="close")
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        self.query_one("#close", Button).focus()
        self._update_display()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "start-opencode":
            self.run_worker(self._start_tunnel("opencode"), exclusive=True)
        elif button_id == "start-vscode":
            self.run_worker(self._start_tunnel("vscode"), exclusive=True)
        elif button_id == "stop-opencode":
            self.run_worker(self._stop_tunnel(), exclusive=True)
        elif button_id == "stop-vscode":
            self.run_worker(self._stop_tunnel(), exclusive=True)
        elif button_id == "open-opencode":
            self._open_service("opencode")
        elif button_id == "open-vscode":
            self._open_service("vscode")
        elif button_id == "copy-password":
            self._copy_password()
        elif button_id == "close":
            self.action_close()
    
    async def _start_tunnel(self, service: str) -> None:
        """Start tunnel for the specified service"""
        if service == "opencode":
            if self.is_starting_opencode:
                return
            self.is_starting_opencode = True
        else:
            if self.is_starting_vscode:
                return
            self.is_starting_vscode = True
        
        self._disable_buttons()
        
        try:
            # Check ngrok installation
            if not self.ngrok_service.is_available():
                self.app.notify(
                    "ngrok not installed. Install: snap install ngrok",
                    severity="error",
                    timeout=5,
                )
                return
            
            # Check if a different service is already tunneled
            status = self.ngrok_service.get_status()
            if status and status["service"] != service:
                self.app.notify(
                    f"Stopping tunnel for {status['service']}...",
                    severity="information",
                    timeout=2,
                )
                await asyncio.to_thread(self.ngrok_service.stop)
            
            self.app.notify(
                f"Starting tunnel for {service}...",
                severity="information",
                timeout=2,
            )
            
            # Start tunnel
            port = self.environment.server_port if service == "opencode" else self.environment.code_server_port
            url = await asyncio.to_thread(
                self.ngrok_service.start,
                self.environment.name,
                service,
                port,
            )
            
            self.app.notify(
                f"✓ Tunnel started for {service}",
                severity="success",
                timeout=3,
            )
        
        except RuntimeError as e:
            self.app.notify(
                f"✗ Failed to start tunnel: {e}",
                severity="error",
                timeout=5,
            )
        except Exception as e:
            self.app.notify(
                f"✗ Unexpected error: {e}",
                severity="error",
                timeout=5,
            )
        finally:
            self.is_starting_opencode = False
            self.is_starting_vscode = False
            self._update_display()
    
    async def _stop_tunnel(self) -> None:
        """Stop the current tunnel"""
        if self.is_stopping:
            return
        
        self.is_stopping = True
        self._disable_buttons()
        
        try:
            self.app.notify(
                "Stopping tunnel...",
                severity="information",
                timeout=2,
            )
            
            await asyncio.to_thread(self.ngrok_service.stop)
            
            self.app.notify(
                "✓ Tunnel stopped",
                severity="success",
                timeout=2,
            )
        
        except Exception as e:
            self.app.notify(
                f"✗ Failed to stop tunnel: {e}",
                severity="error",
                timeout=5,
            )
        finally:
            self.is_stopping = False
            self._update_display()
    
    def _open_service(self, service: str) -> None:
        """Open service URL and copy password to clipboard"""
        status = self.ngrok_service.get_status()
        if not status or status["service"] != service:
            self.app.notify(f"No tunnel URL available for {service}", severity="warning", timeout=2)
            return
        
        url = status.get("url")
        if not url:
            self.app.notify(f"{service} URL not found", severity="warning", timeout=2)
            return
        
        # Copy password
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(self.environment.server_password)
                self.app.notify("Password copied to clipboard", severity="success", timeout=2)
            except Exception as e:
                self.app.notify(f"Failed to copy password: {e}", severity="warning", timeout=2)
        
        # Open URL
        try:
            open_url(url)
            self.app.notify(f"Opening {service.capitalize()} at {url}", severity="information")
        except Exception as e:
            self.app.notify(f"Failed to open browser: {e}", severity="error", timeout=2)
    
    def _copy_password(self) -> None:
        """Copy password to clipboard"""
        if not CLIPBOARD_AVAILABLE:
            self.app.notify(
                "Clipboard not available",
                severity="warning",
                timeout=2,
            )
            return
        
        try:
            pyperclip.copy(self.environment.server_password)
            self.app.notify(
                "✓ Password copied to clipboard",
                severity="success",
                timeout=2,
            )
        except Exception as e:
            self.app.notify(f"Failed to copy: {e}", severity="error", timeout=2)
    
    def _update_display(self) -> None:
        """Update display based on tunnel status"""
        status = self.ngrok_service.get_status()
        
        # Update OpenCode service display
        oc_status_label = self.query_one("#opencode-status", Label)
        oc_start_btn = self.query_one("#start-opencode", Button)
        oc_open_btn = self.query_one("#open-opencode", Button)
        oc_stop_btn = self.query_one("#stop-opencode", Button)
        
        # Update VSCode service display
        vs_status_label = self.query_one("#vscode-status", Label)
        vs_start_btn = self.query_one("#start-vscode", Button)
        vs_open_btn = self.query_one("#open-vscode", Button)
        vs_stop_btn = self.query_one("#stop-vscode", Button)
        
        # Update password section
        copy_pwd_btn = self.query_one("#copy-password", Button)
        password_display = self.query_one("#password-display", Label)
        
        # Disable all buttons during operations
        if self.is_starting_opencode or self.is_starting_vscode or self.is_stopping:
            oc_start_btn.disabled = True
            oc_open_btn.disabled = True
            oc_stop_btn.disabled = True
            vs_start_btn.disabled = True
            vs_open_btn.disabled = True
            vs_stop_btn.disabled = True
            copy_pwd_btn.disabled = True
        else:
            # Update buttons based on tunnel status
            if status and status["service"] == "opencode":
                # OpenCode active
                oc_start_btn.disabled = True
                oc_open_btn.disabled = False
                oc_stop_btn.disabled = False
                oc_status_label.update(f"🔗 {status['url']}")
                
                # VSCode inactive
                vs_start_btn.disabled = False
                vs_open_btn.disabled = True
                vs_stop_btn.disabled = True
                vs_status_label.update("⚪ Not tunneled")
                
                copy_pwd_btn.disabled = False
            elif status and status["service"] == "vscode":
                # OpenCode inactive
                oc_start_btn.disabled = False
                oc_open_btn.disabled = True
                oc_stop_btn.disabled = True
                oc_status_label.update("⚪ Not tunneled")
                
                # VSCode active
                vs_start_btn.disabled = True
                vs_open_btn.disabled = False
                vs_stop_btn.disabled = False
                vs_status_label.update(f"🔗 {status['url']}")
                
                copy_pwd_btn.disabled = False
            else:
                # No tunnel active
                oc_start_btn.disabled = False
                oc_open_btn.disabled = True
                oc_stop_btn.disabled = True
                oc_status_label.update("⚪ Not tunneled")
                
                vs_start_btn.disabled = False
                vs_open_btn.disabled = True
                vs_stop_btn.disabled = True
                vs_status_label.update("⚪ Not tunneled")
                
                copy_pwd_btn.disabled = True
        
        # Update password display
        if status:
            password_display.update("••••••••")
        else:
            password_display.update("—")
    
    def _disable_buttons(self) -> None:
        """Disable all control buttons"""
        self.query_one("#start-opencode", Button).disabled = True
        self.query_one("#open-opencode", Button).disabled = True
        self.query_one("#stop-opencode", Button).disabled = True
        self.query_one("#start-vscode", Button).disabled = True
        self.query_one("#open-vscode", Button).disabled = True
        self.query_one("#stop-vscode", Button).disabled = True
        self.query_one("#copy-password", Button).disabled = True
    
    def action_close(self) -> None:
        """Close the modal"""
        self.dismiss()
