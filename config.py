"""Configuration module for SpooBot.

This module provides access to the application configuration through a single import point.
Configuration is loaded from a TOML file and validated using Pydantic schemas.
"""

import os
import tomli
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

from pydantic import ValidationError

from schemas.exceptions import (
    ConfigError,
    ConfigNotFoundError,
    ConfigValidationError,
    EnvironmentVariableError,
)

from schemas.models import (
    Bot,
    Discord,
    Urls,
    UI,
    Server,
    Assets,
    Command,
    Cooldowns,
)
from schemas.base import BaseConfigModel

# Load environment variables
load_dotenv(override=True)


class Config(BaseConfigModel):
    """Main configuration class that combines all sub-schemas."""

    bot: Bot
    discord: Discord
    urls: Urls
    ui: UI
    server: Server
    assets: Assets
    commands: Dict[str, Command]
    cooldowns: Cooldowns


def replace_env_vars(value: str) -> str:
    """Replace environment variables in string values.

    Args:
        value: The value to process for environment variables.

    Returns:
        The processed value with environment variables replaced.

    Raises:
        EnvironmentVariableError: If a required environment variable is not set.
    """
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        env_value = os.getenv(env_var)
        if env_value is None:
            raise EnvironmentVariableError(
                f"Required environment variable '{env_var}' is not set"
            )
        return env_value
    return value


def process_dict(d: dict) -> dict:
    """Recursively process dictionary to replace environment variables.

    Args:
        d: The dictionary to process.

    Returns:
        The processed dictionary with environment variables replaced.

    Raises:
        EnvironmentVariableError: If a required environment variable is not set.
    """
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = process_dict(v)
        elif isinstance(v, list):
            result[k] = [
                process_dict(x) if isinstance(x, dict) else replace_env_vars(x)
                for x in v
            ]
        else:
            try:
                result[k] = replace_env_vars(v)
            except EnvironmentVariableError as e:
                raise EnvironmentVariableError(f"Error in '{k}': {str(e)}")
    return result


def load_config() -> Config:
    """Load and parse the TOML configuration file with error handling.

    Returns:
        A validated Config object.

    Raises:
        ConfigNotFoundError: If the configuration file is missing.
        ConfigError: If there's an error parsing the TOML file.
        EnvironmentVariableError: If required environment variables are missing.
        ConfigValidationError: If configuration validation fails.
    """
    config_path = Path("config.toml")

    # Check if config file exists
    if not config_path.exists():
        template_path = Path("config.template.toml")
        if template_path.exists():
            raise ConfigNotFoundError(
                "config.toml not found. Please copy config.template.toml to config.toml "
                "and fill in the required values."
            )
        raise ConfigNotFoundError(
            "Neither config.toml nor config.template.toml found. "
            "Please ensure at least one configuration file exists."
        )

    try:
        # Read and parse TOML file
        with open(config_path, "rb") as f:
            toml_dict = tomli.load(f)
    except tomli.TOMLDecodeError as e:
        raise ConfigError(f"Error parsing config.toml: {str(e)}")

    try:
        # Process environment variables
        processed_dict = process_dict(toml_dict)
    except EnvironmentVariableError as e:
        raise EnvironmentVariableError(f"Environment variable error: {str(e)}")

    try:
        # Create and validate config object
        return Config(**processed_dict)
    except ValidationError as e:
        # Format validation errors for better readability
        errors = []
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            errors.append(f"{location}: {error['msg']}")

        raise ConfigValidationError(
            "Configuration validation failed:\n" + "\n".join(errors)
        )


# Create a global config instance with error handling
try:
    config: Config = load_config()
except ConfigError as e:
    print(f"Configuration Error: {str(e)}")
    raise SystemExit(1)


# Export only what's needed
__all__: list[str] = [
    "config",
    "Config",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "EnvironmentVariableError",
]
