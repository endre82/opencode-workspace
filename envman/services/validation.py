"""Input validation utilities for environment creation"""

import re
from pathlib import Path
from typing import Tuple, Optional


class ValidationService:
    """Service for validating user input"""
    
    @staticmethod
    def validate_env_name(name: str, existing_names: list[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate environment name
        Returns: (is_valid, error_message)
        """
        if not name:
            return False, "Environment name is required"
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters"
        
        if len(name) > 50:
            return False, "Name must be 50 characters or less"
        
        # Allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, "Name can only contain letters, numbers, hyphens, and underscores"
        
        # Check if name already exists
        if name.lower() in [n.lower() for n in existing_names]:
            return False, f"Environment '{name}' already exists"
        
        # Reserved names
        reserved = ['template', 'shared', 'base']
        if name.lower() in reserved:
            return False, f"'{name}' is a reserved name"
        
        return True, None
    
    @staticmethod
    def validate_user_id(value: str) -> Tuple[bool, Optional[str]]:
        """Validate USER_ID"""
        if not value:
            return False, "USER_ID is required"
        
        try:
            uid = int(value)
            if uid < 1:
                return False, "USER_ID must be greater than 0"
            if uid > 65535:
                return False, "USER_ID must be 65535 or less"
            return True, None
        except ValueError:
            return False, "USER_ID must be a number"
    
    @staticmethod
    def validate_group_id(value: str) -> Tuple[bool, Optional[str]]:
        """Validate GROUP_ID"""
        if not value:
            return False, "GROUP_ID is required"
        
        try:
            gid = int(value)
            if gid < 1:
                return False, "GROUP_ID must be greater than 0"
            if gid > 65535:
                return False, "GROUP_ID must be 65535 or less"
            return True, None
        except ValueError:
            return False, "GROUP_ID must be a number"
    
    @staticmethod
    def validate_port(value: str, used_ports: list[int]) -> Tuple[bool, Optional[str]]:
        """Validate server port"""
        if not value:
            return False, "Port is required"
        
        try:
            port = int(value)
            if port < 1024:
                return False, "Port must be 1024 or higher"
            if port > 65535:
                return False, "Port must be 65535 or less"
            if port in used_ports:
                return False, f"Port {port} is already in use"
            return True, None
        except ValueError:
            return False, "Port must be a number"
    
    @staticmethod
    def validate_username(value: str) -> Tuple[bool, Optional[str]]:
        """Validate server username"""
        if not value:
            return False, "Username is required"
        
        if len(value) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(value) > 32:
            return False, "Username must be 32 characters or less"
        
        # Allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_password(value: str, allow_empty: bool = True) -> Tuple[bool, Optional[str]]:
        """Validate server password"""
        if not value and not allow_empty:
            return False, "Password is required"
        
        if value and len(value) < 6:
            return False, "Password must be at least 6 characters"
        
        return True, None
    
    @staticmethod
    def validate_path(value: str, must_exist: bool = False, must_not_exist: bool = False) -> Tuple[bool, Optional[str]]:
        """Validate filesystem path"""
        if not value:
            return False, "Path is required"
        
        try:
            path = Path(value).expanduser()
            
            if must_exist and not path.exists():
                return False, f"Path does not exist: {value}"
            
            if must_not_exist and path.exists():
                return False, f"Path already exists: {value}"
            
            # Check if parent directory exists (for new paths)
            if must_not_exist and not path.parent.exists():
                return False, f"Parent directory does not exist: {path.parent}"
            
            return True, None
        except Exception as e:
            return False, f"Invalid path: {e}"
    
    @staticmethod
    def sanitize_env_name(name: str) -> str:
        """Sanitize environment name to safe format"""
        # Replace invalid characters with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        return sanitized.lower()
