"""Custom exceptions for the environment manager"""


class EnvironmentError(Exception):
    """Base exception for environment-related errors"""
    pass


class EnvironmentNotFoundError(EnvironmentError):
    """Environment does not exist"""
    pass


class EnvironmentAlreadyExistsError(EnvironmentError):
    """Environment already exists"""
    pass


class ConfigurationError(EnvironmentError):
    """Configuration file error"""
    pass


class DockerError(EnvironmentError):
    """Docker operation error"""
    pass


class ValidationError(EnvironmentError):
    """Validation error"""
    pass


class PortConflictError(EnvironmentError):
    """Port already in use"""
    pass
