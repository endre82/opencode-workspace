"""Progress dialog modal"""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, ProgressBar, Label
from textual.containers import Container, Vertical


class ProgressDialog(ModalScreen[None]):
    """A modal progress dialog"""
    
    CSS = """
    ProgressDialog {
        align: center middle;
    }
    
    #dialog {
        width: 50;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        padding: 0 0 1 0;
    }
    
    #status {
        width: 100%;
        content-align: center middle;
        padding: 1 0;
    }
    
    #progress {
        width: 100%;
        margin: 1 0;
    }
    """
    
    def __init__(self, title: str, initial_status: str = "Processing..."):
        """
        Initialize progress dialog.
        
        Args:
            title: Dialog title
            initial_status: Initial status message
        """
        super().__init__()
        self.title_text = title
        self.status_text = initial_status
    
    def compose(self) -> ComposeResult:
        """Compose the dialog"""
        with Container(id="dialog"):
            yield Static(self.title_text, id="title")
            yield Static(self.status_text, id="status")
            yield ProgressBar(id="progress", show_eta=False)
    
    def update_status(self, status: str) -> None:
        """Update the status message"""
        status_widget = self.query_one("#status", Static)
        status_widget.update(status)
    
    def update_progress(self, current: float, total: float) -> None:
        """
        Update progress bar.
        
        Args:
            current: Current progress value
            total: Total progress value
        """
        progress_bar = self.query_one("#progress", ProgressBar)
        progress_bar.update(progress=current, total=total)
    
    def set_indeterminate(self) -> None:
        """Set progress bar to indeterminate mode"""
        progress_bar = self.query_one("#progress", ProgressBar)
        progress_bar.update(total=None)
