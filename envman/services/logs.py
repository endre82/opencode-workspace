"""Log service for log streaming, filtering, and export"""

import re
from pathlib import Path
from typing import Generator, Optional
from datetime import datetime


class LogService:
    """Service for log operations"""
    
    LOG_LEVELS = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "FATAL"]
    
    def __init__(self):
        """Initialize log service"""
        pass
    
    @staticmethod
    def filter_by_level(log_lines: list[str], level: Optional[str] = None) -> list[str]:
        """
        Filter log lines by log level.
        
        Args:
            log_lines: List of log lines
            level: Log level to filter by (INFO, WARN, ERROR, etc.)
        
        Returns:
            Filtered list of log lines
        """
        if not level or level.upper() == "ALL":
            return log_lines
        
        level_upper = level.upper()
        filtered = []
        
        for line in log_lines:
            # Check if line contains the log level
            line_upper = line.upper()
            if level_upper in line_upper:
                filtered.append(line)
        
        return filtered
    
    @staticmethod
    def search_logs(log_lines: list[str], search_term: str, case_sensitive: bool = False, regex: bool = False) -> list[str]:
        """
        Search log lines for a term.
        
        Args:
            log_lines: List of log lines
            search_term: Term to search for
            case_sensitive: Whether search should be case-sensitive
            regex: Whether search_term is a regex pattern
        
        Returns:
            Filtered list of log lines matching the search
        """
        if not search_term:
            return log_lines
        
        filtered = []
        
        if regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_term, flags)
                for line in log_lines:
                    if pattern.search(line):
                        filtered.append(line)
            except re.error:
                # Invalid regex, fall back to literal search
                return LogService.search_logs(log_lines, search_term, case_sensitive, regex=False)
        else:
            if case_sensitive:
                for line in log_lines:
                    if search_term in line:
                        filtered.append(line)
            else:
                search_lower = search_term.lower()
                for line in log_lines:
                    if search_lower in line.lower():
                        filtered.append(line)
        
        return filtered
    
    @staticmethod
    def highlight_search_term(line: str, search_term: str, case_sensitive: bool = False) -> str:
        """
        Highlight search term in line using rich markup.
        
        Args:
            line: Log line
            search_term: Term to highlight
            case_sensitive: Whether matching should be case-sensitive
        
        Returns:
            Line with highlighted search term
        """
        if not search_term:
            return line
        
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            # Escape special regex characters if not using regex mode
            escaped_term = re.escape(search_term)
            pattern = re.compile(f"({escaped_term})", flags)
            return pattern.sub(r"[bold yellow]\1[/bold yellow]", line)
        except re.error:
            return line
    
    @staticmethod
    def export_logs(log_lines: list[str], output_path: Path) -> bool:
        """
        Export log lines to a file.
        
        Args:
            log_lines: List of log lines to export
            output_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_lines))
            return True
        except Exception as e:
            print(f"Failed to export logs: {e}")
            return False
    
    @staticmethod
    def get_log_color(line: str) -> str:
        """
        Get color for log line based on log level.
        
        Args:
            line: Log line
        
        Returns:
            Color name for the line
        """
        line_upper = line.upper()
        
        if "ERROR" in line_upper or "FATAL" in line_upper or "CRITICAL" in line_upper:
            return "red"
        elif "WARN" in line_upper:
            return "yellow"
        elif "DEBUG" in line_upper:
            return "dim"
        else:
            return "white"
    
    @staticmethod
    def rotate_logs(log_file: Path, max_size_mb: int = 10, max_files: int = 5) -> bool:
        """
        Rotate log file if it exceeds max size.
        
        Args:
            log_file: Path to log file
            max_size_mb: Maximum file size in MB before rotation
            max_files: Maximum number of rotated files to keep
        
        Returns:
            True if rotation occurred, False otherwise
        """
        try:
            if not log_file.exists():
                return False
            
            # Check file size
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb < max_size_mb:
                return False
            
            # Rotate existing files
            for i in range(max_files - 1, 0, -1):
                old_file = log_file.with_suffix(f"{log_file.suffix}.{i}")
                new_file = log_file.with_suffix(f"{log_file.suffix}.{i + 1}")
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)
            
            # Rotate current file
            rotated_file = log_file.with_suffix(f"{log_file.suffix}.1")
            if rotated_file.exists():
                rotated_file.unlink()
            log_file.rename(rotated_file)
            
            return True
        except Exception as e:
            print(f"Failed to rotate logs: {e}")
            return False
    
    @staticmethod
    def cleanup_old_logs(logs_dir: Path, days: int = 30) -> int:
        """
        Clean up old log files.
        
        Args:
            logs_dir: Directory containing log files
            days: Delete files older than this many days
        
        Returns:
            Number of files deleted
        """
        try:
            if not logs_dir.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Failed to cleanup old logs: {e}")
            return 0
