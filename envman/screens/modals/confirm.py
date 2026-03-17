"""Confirmation dialog modal"""

from typing import Callable, Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, Checkbox, Static
from textual.containers import Container, Vertical, Horizontal, Center
from textual.binding import Binding


class ConfirmDialog(ModalScreen[bool]):
    """A modal confirmation dialog"""
    
    CSS = """
    ConfirmDialog {
        align: center middle;
    }
    
    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $warning;
        padding: 0 0 1 0;
    }
    
    #message {
        width: 100%;
        padding: 1 0;
    }
    
    #warning {
        width: 100%;
        content-align: center middle;
        color: $warning;
        text-style: bold;
        padding: 1 0;
    }
    
    #confirmation-input {
        margin: 1 0;
    }
    
    .checkbox-container {
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
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(
        self,
        title: str,
        message: str,
        warning: Optional[str] = None,
        require_confirmation: Optional[str] = None,
        checkboxes: Optional[list[tuple[str, str, bool]]] = None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Optional[Callable] = None,
    ):
        """
        Initialize confirmation dialog.
        
        Args:
            title: Dialog title
            message: Main message text
            warning: Optional warning text
            require_confirmation: If set, user must type this text to confirm
            checkboxes: List of (id, label, default) tuples for optional checkboxes
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            on_confirm: Optional callback when confirmed
        """
        super().__init__()
        self.title_text = title
        self.message_text = message
        self.warning_text = warning
        self.require_confirmation = require_confirmation
        self.checkboxes_data = checkboxes or []
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.on_confirm_callback = on_confirm
        self.checkbox_states: dict[str, bool] = {}
    
    def compose(self) -> ComposeResult:
        """Compose the dialog"""
        with Container(id="dialog"):
            yield Static(self.title_text, id="title")
            yield Static(self.message_text, id="message")
            
            if self.warning_text:
                yield Static(f"⚠️  {self.warning_text}", id="warning")
            
            # Add checkboxes if provided
            for checkbox_id, label, default in self.checkboxes_data:
                with Vertical(classes="checkbox-container"):
                    yield Checkbox(label, value=default, id=checkbox_id)
            
            # Add confirmation input if required
            if self.require_confirmation:
                yield Static(f"Type '{self.require_confirmation}' to confirm:", id="confirmation-label")
                yield Input(placeholder=self.require_confirmation, id="confirmation-input")
            
            with Horizontal(id="buttons"):
                yield Button(self.cancel_text, variant="default", id="cancel")
                yield Button(self.confirm_text, variant="error", id="confirm")
    
    def on_mount(self) -> None:
        """Focus the appropriate widget on mount"""
        if self.require_confirmation:
            self.query_one("#confirmation-input", Input).focus()
        else:
            self.query_one("#confirm", Button).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "confirm":
            if self._validate_confirmation():
                # Collect checkbox states
                for checkbox_id, _, _ in self.checkboxes_data:
                    checkbox = self.query_one(f"#{checkbox_id}", Checkbox)
                    self.checkbox_states[checkbox_id] = checkbox.value
                
                if self.on_confirm_callback:
                    self.on_confirm_callback(self.checkbox_states)
                
                self.dismiss(True)
            else:
                self.notify("Confirmation text does not match", severity="error")
    
    def _validate_confirmation(self) -> bool:
        """Validate confirmation input if required"""
        if not self.require_confirmation:
            return True
        
        input_widget = self.query_one("#confirmation-input", Input)
        return input_widget.value == self.require_confirmation
    
    def action_cancel(self) -> None:
        """Handle cancel action"""
        self.dismiss(False)
    
    def get_checkbox_states(self) -> dict[str, bool]:
        """Get the states of all checkboxes"""
        return self.checkbox_states
