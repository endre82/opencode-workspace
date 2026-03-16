"""
Basic authentication middleware for the Web UI.
Uses the same credentials as the OpenCode server.
"""
import secrets
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import config


security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Verify username and password against configured values.
    Uses constant-time comparison to prevent timing attacks.
    """
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        config.USERNAME.encode("utf8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        config.PASSWORD.encode("utf8")
    )
    
    return correct_username and correct_password


def require_auth(credentials: HTTPBasicCredentials) -> str:
    """
    Require authentication for protected routes.
    Raises HTTPException if credentials are invalid.
    Returns username if valid.
    """
    if not config.PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server not configured with password",
        )
    
    if not verify_credentials(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username
