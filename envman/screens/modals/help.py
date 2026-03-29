"""Help / keyboard shortcuts modal"""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding


_SECTION_STYLE = "bold white on $primary"
_KEY_STYLE = "bold $accent"
_DIM = "dim"


def _row(key: str, desc: str, key2: str = "", desc2: str = "") -> str:
    """Build one formatted help row (up to two key/desc pairs)."""
    left = f"  [{_KEY_STYLE}]{key:<5}[/]  {desc:<26}"
    if key2:
        right = f"[{_KEY_STYLE}]{key2:<5}[/]  {desc2}"
    else:
        right = ""
    return left + right


class HelpModal(ModalScreen[None]):
    """Full keyboard-shortcut reference, opened with '?'."""

    CSS = """
    HelpModal {
        align: center middle;
    }

    #help-dialog {
        width: 66;
        height: auto;
        border: round $primary;
        background: $surface;
        padding: 0;
    }

    #help-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1 2;
    }

    .help-section-label {
        width: 100%;
        background: $panel;
        color: $text-muted;
        text-style: bold;
        padding: 0 2;
        margin-top: 1;
    }

    .help-row {
        width: 100%;
        padding: 0 2;
        height: 1;
    }

    #help-footer {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        padding: 1 2;
        margin-top: 1;
        border-top: solid $primary;
    }

    #close-btn {
        margin: 1 2;
        width: 100%;
        align-horizontal: center;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("?", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Static("⌨  Keyboard Shortcuts", id="help-title")

            # ── Navigation & global ──────────────────────────────────────────
            yield Static(" GLOBAL ", classes="help-section-label")
            yield Static(_row("↑ ↓", "Navigate rows",       "R",  "Refresh list"), classes="help-row")
            yield Static(_row("n",   "New environment",      "q",  "Quit"), classes="help-row")
            yield Static(_row("?",   "This help screen"), classes="help-row")

            # ── Environment actions ──────────────────────────────────────────
            yield Static(" ENVIRONMENT  (acts on highlighted row) ", classes="help-section-label")
            yield Static(_row("s",   "Start",                "x",  "Stop"), classes="help-row")
            yield Static(_row("r",   "Restart",              "b",  "Build / rebuild image"), classes="help-row")
            yield Static(_row("l",   "View logs",            "i",  "Inspect container"), classes="help-row")
            yield Static(_row("c",   "Configure (.env)",     "d",  "Delete"), classes="help-row")

            # ── Web UI ───────────────────────────────────────────────────────
            yield Static(" WEB UI  (environment must be running) ", classes="help-section-label")
            yield Static(_row("w",   "Open OpenCode web UI",  "v",  "Open VSCode web UI"), classes="help-row")
            yield Static(_row("C",   "Copy remote connect cmd"), classes="help-row")
            yield Static(
                "       [dim]w/v copy the server password to clipboard automatically[/dim]",
                classes="help-row",
            )

            yield Static("Press [bold]Escape[/bold] or [bold]?[/bold] to close", id="help-footer")

    def on_mount(self) -> None:
        # Nothing to focus — user just reads and presses Escape
        pass

    def on_key(self, event) -> None:
        """Close on any key that isn't a navigation key."""
        if event.key not in ("up", "down", "tab", "shift+tab"):
            self.dismiss()

    def action_close(self) -> None:
        self.dismiss()
