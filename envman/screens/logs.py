"""Logs viewer screen"""

import asyncio
from pathlib import Path
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, RichLog, Static, Input, Select, Button, Switch
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from rich.text import Text

from envman.models.environment import Environment
from envman.services.docker import DockerService
from envman.services.logs import LogService
from envman.utils.exceptions import DockerError
from envman.utils.exception_logger import set_context


class LogsScreen(Screen):
    """Logs viewer screen with search, filter, and export"""
    
    CSS = """
    LogsScreen {
        layout: vertical;
    }
    
    #logs-container {
        height: 100%;
        width: 100%;
    }
    
    #toolbar {
        dock: top;
        height: 3;
        background: $panel;
        padding: 0 1;
    }
    
    #log-viewer {
        height: 1fr;
        border: solid $primary;
        scrollbar-gutter: stable;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
    }
    
    Select {
        width: 15;
        margin: 0 1;
    }
    
    Input {
        width: 30;
        margin: 0 1;
    }
    
    Switch {
        margin: 0 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("e", "export", "Export"),
        Binding("f", "toggle_follow", "Toggle Follow"),
        Binding("c", "clear_logs", "Clear"),
        Binding("/", "focus_search", "Search"),
    ]
    
    def __init__(
        self,
        environment: Environment,
        docker_service: DockerService,
    ):
        super().__init__()
        self.environment = environment
        self.docker_service = docker_service
        self.log_service = LogService()
        self.log_lines: list[str] = []
        self.filtered_lines: list[str] = []
        self.is_following = False
        self.follow_task: asyncio.Task | None = None
        self.current_filter = "ALL"
        self.current_search = ""
        
        # Set context early so it's available during compose()
        set_context(screen="LogsViewer", environment_name=self.environment.name)
    
    def compose(self) -> ComposeResult:
        """Compose the logs viewer UI"""
        yield Header()
        
        with Container(id="logs-container"):
            with Horizontal(id="toolbar"):
                yield Select(
                    options=[
                        ("All Levels", "ALL"),
                        ("Info", "INFO"),
                        ("Warning", "WARN"),
                        ("Error", "ERROR"),
                        ("Debug", "DEBUG"),
                    ],
                    value="ALL",
                    id="filter-select",
                )
                yield Input(placeholder="Search logs...", id="search-input")
                yield Switch(value=False, id="follow-switch")
                yield Static("Follow", id="follow-label")
                yield Button("Export", variant="primary", id="export-btn")
                yield Button("Clear", variant="default", id="clear-btn")
            
            yield RichLog(id="log-viewer", wrap=True, highlight=True, markup=True)
            yield Static("", id="status-bar")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup the logs viewer when mounted"""
        self.load_initial_logs()
        self.update_status()
    
    def on_unmount(self) -> None:
        """Cleanup when unmounting"""
        if self.follow_task and not self.follow_task.done():
            self.follow_task.cancel()
    
    def load_initial_logs(self) -> None:
        """Load initial logs from container"""
        log_viewer = self.query_one("#log-viewer", RichLog)
        
        try:
            # Get last 500 lines
            logs = self.docker_service.get_logs(self.environment.container_name, tail=500)
            self.log_lines = logs.splitlines() if logs else []
            self.apply_filters()
            
            # Display filtered logs
            for line in self.filtered_lines:
                self._append_log_line(line)
            
            # Auto-scroll to bottom
            log_viewer.scroll_end(animate=False)
            
            if not self.log_lines:
                log_viewer.write("No logs available")
        
        except DockerError as e:
            log_viewer.write(f"[red]Error loading logs: {e}[/red]")
            self.notify(f"Failed to load logs: {e}", severity="error")
    
    def apply_filters(self) -> None:
        """Apply current filter and search to log lines"""
        # Start with all lines
        filtered = self.log_lines.copy()
        
        # Apply level filter
        if self.current_filter and self.current_filter != "ALL":
            filtered = self.log_service.filter_by_level(filtered, self.current_filter)
        
        # Apply search
        if self.current_search:
            filtered = self.log_service.search_logs(filtered, self.current_search, case_sensitive=False)
        
        self.filtered_lines = filtered
    
    def refresh_logs(self) -> None:
        """Refresh the log display with current filters"""
        log_viewer = self.query_one("#log-viewer", RichLog)
        log_viewer.clear()
        
        self.apply_filters()
        
        for line in self.filtered_lines:
            self._append_log_line(line)
        
        # Auto-scroll to bottom
        log_viewer.scroll_end(animate=False)
        
        self.update_status()
    
    def _append_log_line(self, line: str) -> None:
        """Append a log line with appropriate formatting"""
        log_viewer = self.query_one("#log-viewer", RichLog)
        
        # Get color based on log level
        color = self.log_service.get_log_color(line)
        
        # Highlight search term if present
        if self.current_search:
            line = self.log_service.highlight_search_term(line, self.current_search)
        
        # Create styled text
        if color and color != "white":
            log_viewer.write(f"[{color}]{line}[/{color}]")
        else:
            log_viewer.write(line)
    
    async def start_following(self) -> None:
        """Start following logs in real-time"""
        if self.is_following:
            return
        
        self.is_following = True
        self.follow_task = asyncio.create_task(self._follow_logs())
        self.update_status()
    
    async def stop_following(self) -> None:
        """Stop following logs"""
        self.is_following = False
        if self.follow_task and not self.follow_task.done():
            self.follow_task.cancel()
            try:
                await self.follow_task
            except asyncio.CancelledError:
                pass
        self.update_status()
    
    async def _follow_logs(self) -> None:
        """Follow logs in real-time (async task)"""
        try:
            # Use asyncio.to_thread for the blocking log streaming
            def stream_logs_sync():
                try:
                    for line in self.docker_service.stream_logs(self.environment.container_name, tail=0):
                        if not self.is_following:
                            break
                        line = line.strip()
                        if line:
                            self.log_lines.append(line)
                            # Check if line passes filters
                            if self._line_matches_filters(line):
                                self.filtered_lines.append(line)
                                self.call_from_thread(self._append_log_line, line)
                                self.call_from_thread(self.update_status)
                except Exception as e:
                    self.call_from_thread(self.notify, f"Log streaming stopped: {e}", severity="warning")
            
            await asyncio.to_thread(stream_logs_sync)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.notify(f"Error following logs: {e}", severity="error")
        finally:
            self.is_following = False
            self.update_status()
    
    def _line_matches_filters(self, line: str) -> bool:
        """Check if a line matches current filters"""
        # Use LogService for level filtering (same logic as batch apply_filters)
        if self.current_filter and self.current_filter != "ALL":
            filtered = self.log_service.filter_by_level([line], self.current_filter)
            if not filtered:
                return False

        # Check search filter
        if self.current_search:
            if self.current_search.lower() not in line.lower():
                return False

        return True
    
    def update_status(self) -> None:
        """Update the status bar"""
        status_bar = self.query_one("#status-bar", Static)
        
        total = len(self.log_lines)
        filtered = len(self.filtered_lines)
        follow_status = "Following" if self.is_following else "Paused"
        
        status = f"Lines: {filtered}/{total} | Filter: {self.current_filter} | {follow_status}"
        if self.current_search:
            status += f" | Search: '{self.current_search}'"
        
        status_bar.update(status)
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter selection change"""
        if event.select.id == "filter-select":
            self.current_filter = str(event.value)
            self.refresh_logs()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input change"""
        if event.input.id == "search-input":
            self.current_search = event.value
            self.refresh_logs()
    
    async def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle follow switch toggle"""
        if event.switch.id == "follow-switch":
            if event.value:
                await self.start_following()
            else:
                await self.stop_following()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "export-btn":
            self.action_export()
        elif event.button.id == "clear-btn":
            self.action_clear_logs()
    
    def action_close(self) -> None:
        """Close the logs viewer"""
        self.app.pop_screen()
    
    def action_export(self) -> None:
        """Export logs to file"""
        try:
            # Create logs directory in environment
            logs_dir = self.environment.path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_{self.environment.name}_{timestamp}.log"
            output_path = logs_dir / filename
            
            # Export filtered logs
            if self.log_service.export_logs(self.filtered_lines, output_path):
                self.notify(f"Logs exported to {output_path}", severity="information")
            else:
                self.notify("Failed to export logs", severity="error")
        
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")
    
    async def action_toggle_follow(self) -> None:
        """Toggle follow mode"""
        switch = self.query_one("#follow-switch", Switch)
        switch.value = not switch.value
    
    def action_clear_logs(self) -> None:
        """Clear the log display"""
        log_viewer = self.query_one("#log-viewer", RichLog)
        log_viewer.clear()
        self.log_lines.clear()
        self.filtered_lines.clear()
        self.update_status()
        self.notify("Logs cleared", severity="information")
    
    def action_focus_search(self) -> None:
        """Focus the search input"""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
