# Exception Logging System

## Overview
The OpenCode Workspace TUI includes a comprehensive exception logging system that automatically captures all uncaught exceptions with full context. This enables AI agents to debug and fix issues with complete information.

## Log File Location
```
~/.local/share/opencode-workspace/logs/exceptions.log
```

## Log Format
Each exception is logged as a single-line JSON object with the following structure:

```json
{
  "timestamp": "2026-03-17T00:59:12.386334",
  "exception_type": "ValueError",
  "exception_message": "invalid literal for int() with base 10: 'not_a_number'",
  "stack_trace": [
    {
      "file": "/path/to/file.py",
      "line": 123,
      "function": "function_name",
      "code": "problematic_code_line"
    }
  ],
  "context": {
    "screen": "CreationWizard",
    "step": 1,
    "user_action": "clicked_next_button",
    "environment_name": "myenv"
  },
  "system_info": {
    "python_version": "3.12.3",
    "platform": "Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39",
    "docker_available": true,
    "docker_version": "24.0.7"
  },
  "process_info": {
    "pid": "app.py",
    "cwd": "/home/endre/opencode-workspace"
  }
}
```

## Key Features
- **Automatic Capture**: Global exception hook catches all uncaught exceptions
- **Rich Context**: Includes screen, step, user action, environment name
- **Full Stack Traces**: Multi-level stack traces with file paths and line numbers
- **System Information**: Python version, platform, Docker status
- **JSON Format**: Single-line JSON for easy parsing by AI
- **Log Rotation**: 10MB max per file, keeps 5 backup files
- **Thread-Safe**: Uses locks for concurrent writes
- **Fail-Safe**: Logger failures won't crash the app

## How It Works
1. **Global Hook**: `install_global_hook()` replaces `sys.excepthook` at app startup
2. **Context Tracking**: Screens call `set_context()` in `on_mount()` methods
3. **Automatic Logging**: When an exception occurs, the hook:
   - Gathers current context from thread-local storage
   - Collects system information
   - Formats stack trace
   - Writes JSON entry to log file
   - Calls original exception hook (so app behavior is unchanged)

## Integration Points
- **App Initialization**: `envman/app.py` calls `install_global_hook()` in `__init__`
- **Screen Context**: All screens call `set_context()` in `on_mount()`:
  - `Dashboard`: `set_context(screen="Dashboard")`
  - `CreationWizard`: `set_context(screen="CreationWizard", step=1)`
  - `LogsScreen`: `set_context(screen="LogsViewer", environment_name=...)`
  - `InspectScreen`: `set_context(screen="InspectEnvironment", environment_name=...)`
  - `ConfigScreen`: `set_context(screen="ConfigEditor", environment_name=...)`
  - `DeleteScreen`: `set_context(screen="DeleteEnvironment", environment_name=...)`

## Using the Exception Logger
**For AI Agents (Debugging):**
When a user reports an issue, simply ask them to:
1. Reproduce the error
2. Check the exception log: `cat ~/.local/share/opencode-workspace/logs/exceptions.log`
3. Provide the latest JSON entry

**For Development:**
```python
from envman.utils.exception_logger import install_global_hook, set_context

# Install at app startup
install_global_hook()

# Set context in screens
set_context(screen="Dashboard")

# Set context with step changes
set_context(screen="CreationWizard", step=2)

# Set context for user actions
set_context(user_action="clicked_create_button", environment_name="myenv")
```

## Manual Exception Logging
For caught exceptions that you want to log but handle locally:
```python
from envman.utils.exception_logger import exception_context

with exception_context(screen="Dashboard", user_action="refresh"):
    # Code that might raise exceptions
    refresh_environments()
```

## Testing the Logger
```bash
# Test with a simple exception
python3 -c "
import sys
sys.path.insert(0, '/home/endre/.local/share/opencode-workspace')
from envman.utils.exception_logger import install_global_hook, set_context
install_global_hook()
set_context(screen='TestScreen', step=1)
x = 1 / 0  # This will be logged
"

# View the log
cat ~/.local/share/opencode-workspace/logs/exceptions.log | tail -1 | python3 -m json.tool
```

## Benefits for AI Debugging
When a user says "fix the exception", the AI has access to:
- **Exact error message** and exception type
- **Full stack trace** showing where it happened
- **User context**: What screen/step they were on
- **Action context**: What triggered the exception
- **System environment**: Python version, Docker status, etc.
- **Process info**: Working directory, PID

This eliminates the need for back-and-forth questions about:
- "What were you doing when it crashed?"
- "What error message did you see?"
- "What version are you running?"
- "Can you show me the full traceback?"

## File Structure
```
envman/utils/exception_logger.py  # Main logging implementation
envman/app.py                     # Global hook installation
envman/screens/*.py               # Context tracking in screens
~/.local/share/opencode-workspace/logs/exceptions.log  # Log file
```

## Notes
- The logger creates the log directory automatically if it doesn't exist
- Log rotation creates backup files: `exceptions.log.1`, `.log.2`, etc.
- Each log entry is a single line for easy `tail -f` monitoring
- JSON format ensures structured data for AI parsing
- Context is thread-local, so it works with async operations