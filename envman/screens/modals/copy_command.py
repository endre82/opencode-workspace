"""Copy command modal dialog"""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class CopyCommandModal(ModalScreen[None]):
    """A modal dialog to display and copy connection command"""
    
    CSS = """
    CopyCommandModal {
        align: center middle;
    }
    
    #dialog {
        width: 80;
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
    
    #message {
        width: 100%;
        padding: 1 0;
        color: $text-muted;
    }
    
    #command-container {
        width: 100%;
        border: solid $primary;
        background: $panel;
        padding: 1;
        margin: 1 0;
    }
    
    #command {
        width: 100%;
        color: $accent;
        text-style: bold;
    }
    
    #hint {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        padding: 1 0;
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
        Binding("ctrl+c", "copy", "Copy"),
    ]
    
    def __init__(
        self,
        command: str,
        title: str = "Connection Command",
        message: Optional[str] = None,
    ):
        """
        Initialize copy command modal.
        
        Args:
            command: The command to display and copy
            title: Modal title
            message: Optional message to display above the command
        """
        super().__init__()
        self.command = command
        self.title_text = title
        self.message_text = message or "Use this command to connect to the remote OpenCode server:"
    
    def compose(self) -> ComposeResult:
        """Compose the dialog"""
        with Container(id="dialog"):
            yield Static(self.title_text, id="title")
            yield Static(self.message_text, id="message")
            
            # Command display
            with Vertical(id="command-container"):
                yield Static(self.command, id="command")
            
            if not CLIPBOARD_AVAILABLE:
                yield Static(
                    "⚠ Clipboard support not available. Please copy manually.",
                    id="hint"
                )
            else:
                yield Static(
                    "Press Ctrl+C to copy, or click the Copy button below",
                    id="hint"
                )
            
            with Horizontal(id="buttons"):
                if CLIPBOARD_AVAILABLE:
                    yield Button("Copy to Clipboard", variant="primary", id="copy")
                yield Button("Close", variant="default", id="close")
    
    def on_mount(self) -> None:
        """Focus the copy button on mount"""
        if CLIPBOARD_AVAILABLE:
            try:
                self.query_one("#copy", Button).focus()
            except Exception:
                self.query_one("#close", Button).focus()
        else:
            self.query_one("#close", Button).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "copy":
            self.action_copy()
        elif event.button.id == "close":
            self.action_close()
    
    def action_copy(self) -> None:
        """Copy command to clipboard"""
        if not CLIPBOARD_AVAILABLE:
            self.notify("Clipboard support not available", severity="error")
            return
        
        try:
            pyperclip.copy(self.command)
            self.notify("✓ Copied to clipboard", severity="success", timeout=2)
        except Exception as e:
            self.notify(f"Failed to copy: {e}", severity="error")
    
    def action_close(self) -> None:
        """Close the modal"""
        self.dismiss()
