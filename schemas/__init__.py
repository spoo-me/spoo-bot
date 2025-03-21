"""Schema definitions for SpooBot configuration.

This package contains all the Pydantic models used for configuration validation.
"""

# Base classes and utilities
from schemas.base import BaseConfigModel
from schemas.exceptions import (
    ConfigError,
    ConfigNotFoundError,
    ConfigValidationError,
    EnvironmentVariableError,
)
from schemas.validators import (
    HexColorField,
    RgbColorField,
    DiscordIdField,
    FontStyleField,
    RangeField,
    https_validator,
)

# Models
from schemas.models import (
    Bot,
    BotEmojis,
    Discord,
    DiscordIds,
    DiscordChannels,
    Urls,
    SocialShareUrls,
    UI,
    UIColors,
    UIMessages,
    Server,
    KeepAlive,
    Charts,
    ChartColors,
    ChartStyle,
    ChartPadding,
    ChartScales,
    ChartPlugins,
    ChartPluginTitle,
    ChartPluginLegend,
    ChartHeatmap,
    Assets,
    Command,
    CommandParameter,
    CommandCooldown,
    Cooldowns,
)

__all__: list[str] = [
    # Base and exceptions
    "BaseConfigModel",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "EnvironmentVariableError",
    # Field types and validators
    "HexColorField",
    "RgbColorField",
    "DiscordIdField",
    "FontStyleField",
    "RangeField",
    "https_validator",
    # Models
    "Bot",
    "BotEmojis",
    "Discord",
    "DiscordIds",
    "DiscordChannels",
    "Urls",
    "SocialShareUrls",
    "UI",
    "UIColors",
    "UIMessages",
    "Server",
    "KeepAlive",
    "Charts",
    "ChartColors",
    "ChartStyle",
    "ChartPadding",
    "ChartScales",
    "ChartPlugins",
    "ChartPluginTitle",
    "ChartPluginLegend",
    "ChartHeatmap",
    "Assets",
    "Command",
    "CommandParameter",
    "CommandCooldown",
    "Cooldowns",
]
