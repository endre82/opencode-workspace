"""Exception logging system for OpenCode Workspace TUI

This module provides comprehensive exception logging with automatic context capture.
It logs all uncaught exceptions to a JSON file with full stack traces, system info,
and contextual information (current screen, step, action, etc.).

Usage:
    1. Call install_global_hook() once at app startup
    2. Use set_context() in screens to update current context
    3. Exceptions are automatically logged to ~/.local/share/opencode-workspace/logs/exceptions.log

Example:
    from envman.utils.exception_logger import install_global_hook, set_context
    
    # In app initialization
    install_global_hook()
    
    # In screen on_mount()
    set_context(screen="Dashboard")
    
    # In wizard step changes
    set_context(screen="CreationWizard", step=2)
    
    # In button handlers (optional)
    set_context(user_action="clicked_next_button")
"""

import sys
import json
import threading
import traceback
import platform
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from logging.handlers import RotatingFileHandler
import logging


# Thread-local storage for context information
_context = threading.local()

# Lock for thread-safe file writing
_write_lock = threading.Lock()

# Logger instance
_logger: Optional[logging.Logger] = None

# Flag to track if hook is installed
_hook_installed = False


def set_context(**kwargs) -> None:
    """Set context information for exception logging.
    
    Args:
        screen: Current screen name (e.g., "Dashboard", "CreationWizard")
        step: Current step number (for wizards)
        user_action: Last user action (e.g., "clicked_next_button")
        environment_name: Current environment being operated on
        **kwargs: Any other context fields to store
    
    Example:
        set_context(screen="CreationWizard", step=1)
        set_context(user_action="clicked_create_button", environment_name="myenv")
    """
    if not hasattr(_context, 'data'):
        _context.data = {}
    
    _context.data.update(kwargs)


def clear_context() -> None:
    """Clear all context information."""
    if hasattr(_context, 'data'):
        _context.data = {}


def get_context() -> dict[str, Any]:
    """Get current context information.
    
    Returns:
        Dictionary of current context data
    """
    if not hasattr(_context, 'data'):
        _context.data = {}
    
    return _context.data.copy()


def _collect_system_info() -> dict[str, Any]:
    """Collect system and environment information.
    
    Returns:
        Dictionary containing:
        - python_version: Python version string
        - platform: Platform/OS information
        - docker_available: Whether Docker is accessible
        - docker_version: Docker version if available
    """
    system_info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "docker_available": False,
        "docker_version": None
    }
    
    # Check Docker availability (don't crash if Docker check fails)
    try:
        from envman.services.docker import DockerService
        docker_service = DockerService()
        system_info["docker_available"] = True
        
        # Try to get Docker version
        try:
            client = docker_service.client
            version_info = client.version()
            system_info["docker_version"] = version_info.get("Version", "unknown")
        except Exception:
            pass  # Docker is available but can't get version
            
    except Exception:
        pass  # Docker not available or import failed
    
    return system_info


def _format_stack_trace(tb: Any) -> list[dict[str, Any]]:
    """Format traceback into structured list.
    
    Args:
        tb: Traceback object
    
    Returns:
        List of stack frame dictionaries with file, line, function, and code
    """
    frames = []
    
    for frame_summary in traceback.extract_tb(tb):
        frames.append({
            "file": frame_summary.filename,
            "line": frame_summary.lineno,
            "function": frame_summary.name,
            "code": frame_summary.line
        })
    
    return frames


def _get_log_file_path() -> Path:
    """Get the path to the exception log file.
    
    Returns:
        Path to exceptions.log in the OpenCode workspace logs directory
    """
    # Use home directory to find OpenCode workspace
    home = Path.home()
    log_dir = home / ".local" / "share" / "opencode-workspace" / "logs"
    
    # Create directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir / "exceptions.log"


def _init_logger() -> logging.Logger:
    """Initialize the rotating file logger.
    
    Returns:
        Configured logger instance with rotating file handler
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Create logger
    logger = logging.getLogger("envman.exceptions")
    logger.setLevel(logging.ERROR)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    # Create rotating file handler (10MB max, 5 backup files)
    log_path = _get_log_file_path()
    handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # No formatting - we'll write raw JSON
    handler.setFormatter(logging.Formatter('%(message)s'))
    
    logger.addHandler(handler)
    _logger = logger
    
    return logger


def _write_exception(exc_type: type, exc_value: BaseException, exc_tb: Any) -> None:
    """Write exception information to log file as JSON.
    
    Args:
        exc_type: Exception type/class
        exc_value: Exception instance
        exc_tb: Traceback object
    """
    try:
        # Initialize logger if needed
        logger = _init_logger()
        
        # Build exception log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "exception_type": exc_type.__name__,
            "exception_message": str(exc_value),
            "stack_trace": _format_stack_trace(exc_tb) if exc_tb else [],
            "context": get_context(),
            "system_info": _collect_system_info(),
            "process_info": {
                "pid": sys.argv[0] if sys.argv else "unknown",
                "cwd": str(Path.cwd())
            }
        }
        
        # Write as single-line JSON
        with _write_lock:
            logger.error(json.dumps(log_entry))
        
    except Exception as e:
        # If logging fails, write to stderr but don't crash the app
        print(f"Exception logger failed: {e}", file=sys.stderr)


def _exception_hook(exc_type: type, exc_value: BaseException, exc_tb: Any) -> None:
    """Global exception hook that logs exceptions and calls original hook.
    
    This replaces sys.excepthook to intercept all uncaught exceptions.
    
    Args:
        exc_type: Exception type/class
        exc_value: Exception instance
        exc_tb: Traceback object
    """
    # Log the exception
    _write_exception(exc_type, exc_value, exc_tb)
    
    # Call the original exception hook to maintain default behavior
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def install_global_hook() -> None:
    """Install global exception hook to capture all uncaught exceptions.
    
    This should be called once at application startup, typically in the
    main app __init__ method.
    
    Example:
        from envman.utils.exception_logger import install_global_hook
        
        class EnvironmentManagerApp(App):
            def __init__(self):
                super().__init__()
                install_global_hook()
    """
    global _hook_installed
    
    if _hook_installed:
        return
    
    # Replace sys.excepthook with our logging hook
    sys.excepthook = _exception_hook
    _hook_installed = True


class exception_context:
    """Context manager for manual exception logging.
    
    Use this to wrap code blocks where you want to log exceptions
    but also handle them locally.
    
    Example:
        with exception_context(screen="Dashboard", user_action="refresh"):
            # Code that might raise exceptions
            refresh_environments()
    """
    
    def __init__(self, **context_kwargs):
        """Initialize context manager with context information.
        
        Args:
            **context_kwargs: Context fields to set (screen, step, action, etc.)
        """
        self.context = context_kwargs
        self.previous_context = None
    
    def __enter__(self):
        """Enter context: save previous context and set new one."""
        self.previous_context = get_context()
        set_context(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        """Exit context: restore previous context and log exception if any.
        
        Returns:
            False to propagate the exception (don't suppress it)
        """
        # Log exception if one occurred
        if exc_type is not None:
            _write_exception(exc_type, exc_value, exc_tb)
        
        # Restore previous context
        clear_context()
        if self.previous_context:
            set_context(**self.previous_context)
        
        # Don't suppress the exception
        return False
