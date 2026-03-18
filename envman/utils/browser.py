"""WSL-aware browser utility for opening URLs in the system default browser"""

import subprocess
import webbrowser
from typing import Optional


def is_wsl() -> bool:
    """
    Detect if running on Windows Subsystem for Linux (WSL).
    
    Returns:
        bool: True if running on WSL, False otherwise
    """
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            return 'microsoft' in version_info or 'wsl' in version_info
    except (FileNotFoundError, PermissionError):
        return False


def open_url(url: str) -> bool:
    """
    Open a URL in the system default browser, with WSL support.
    
    On WSL, this will open the URL in the Windows host's default browser
    instead of an X11 browser within WSL.
    
    Args:
        url: The URL to open
        
    Returns:
        bool: True if the URL was opened successfully, False otherwise
        
    Raises:
        Exception: If all methods of opening the browser fail
    """
    if is_wsl():
        return _open_url_wsl(url)
    else:
        return _open_url_standard(url)


def _open_url_wsl(url: str) -> bool:
    """
    Open a URL on WSL using Windows commands.
    
    Tries multiple methods in order of preference:
    1. cmd.exe /c start (most compatible)
    2. powershell.exe Start-Process (modern alternative)
    3. explorer.exe (fallback)
    4. Standard webbrowser module (last resort)
    
    Args:
        url: The URL to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Method 1: cmd.exe with start command (most reliable)
    try:
        # The empty string "" after start is the window title (required when URL contains special chars)
        subprocess.run(
            ['cmd.exe', '/c', 'start', '""', url],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Method 2: PowerShell Start-Process
    try:
        subprocess.run(
            ['powershell.exe', '-c', f'Start-Process "{url}"'],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Method 3: explorer.exe (works for URLs too)
    try:
        subprocess.run(
            ['explorer.exe', url],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Method 4: Fallback to standard webbrowser (may open X11 browser)
    try:
        webbrowser.open(url)
        return True
    except Exception:
        pass
    
    # All methods failed
    raise Exception(
        "Failed to open browser. Tried cmd.exe, powershell.exe, explorer.exe, and webbrowser module."
    )


def _open_url_standard(url: str) -> bool:
    """
    Open a URL using the standard Python webbrowser module.
    
    This is used on non-WSL systems (native Linux, macOS, etc.)
    
    Args:
        url: The URL to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        raise Exception(f"Failed to open browser: {e}")
