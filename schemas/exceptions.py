"""Exceptions for configuration validation errors."""


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is missing."""

    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""

    pass


class EnvironmentVariableError(ConfigError):
    """Raised when required environment variables are missing."""

    pass
