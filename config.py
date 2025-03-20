from typing import Dict, List, Optional
from pydantic import BaseModel, ValidationError
import tomli
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)


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


# Parameter Models
class CommandParameter(BaseModel):
    name: str
    description: str
    emoji: str


# Command Models
class Command(BaseModel):
    id: str
    emoji: str
    description: str
    parameters: Optional[List[CommandParameter]] = None


class CommandCooldown(BaseModel):
    count: int
    seconds: int


# Chart Models
class ChartColors(BaseModel):
    platform: List[List[str]]
    browser: List[List[str]]
    referrer: List[List[str]]
    timeline: List[List[str]]


class ChartPadding(BaseModel):
    left: int
    right: int
    top: int
    bottom: int


class ChartStyle(BaseModel):
    background: str
    grid_color: str
    text_color: str
    font_style: str
    font_size: int
    border_width: int
    border_radius: int
    line_tension: float
    padding: ChartPadding


class ChartScales(BaseModel):
    grid_color: str
    tick_color: str


class ChartPluginTitle(BaseModel):
    color: str
    font_style: str
    font_size: int


class ChartPluginLegend(BaseModel):
    labels_color: str


class ChartPlugins(BaseModel):
    title: ChartPluginTitle
    legend: ChartPluginLegend


class ChartHeatmap(BaseModel):
    dpi: int
    alpha: float
    pad_inches: float
    bbox_inches: str


class Charts(BaseModel):
    colors: ChartColors
    style: ChartStyle
    scales: ChartScales
    plugins: ChartPlugins
    heatmap: ChartHeatmap


# UI Models
class UIColors(BaseModel):
    primary: str
    success: str
    error: str
    warning: str
    info: str


class UIMessages(BaseModel):
    welcome: str
    bot_mention: str


class UI(BaseModel):
    colors: UIColors
    charts: Charts
    messages: UIMessages


# URL Models
class SocialShareUrls(BaseModel):
    twitter: str
    facebook: str
    telegram: str
    whatsapp: str
    reddit: str
    snapchat: str


class Urls(BaseModel):
    api_base: str
    spoo_metrics: str
    qr_api_base: str
    charts_api_base: str
    discord_invite: str
    bot_invite: str
    github: str
    social_share: SocialShareUrls


# Server Models
class KeepAlive(BaseModel):
    enabled: bool
    host: str
    port: str


class Server(BaseModel):
    environment: str
    is_cloud_hosted: bool
    keep_alive: KeepAlive

    def validate_environment(self):
        valid_environments = {"development", "production", "testing"}
        if self.environment not in valid_environments:
            raise ValueError(
                f"Invalid environment: {self.environment}. Must be one of: {', '.join(valid_environments)}"
            )
        return True


# Discord Models
class DiscordChannels(BaseModel):
    welcome: str
    stats_clicks: str
    stats_shortlinks: str


class DiscordIds(BaseModel):
    parent_server: str
    channels: DiscordChannels


class Discord(BaseModel):
    ids: DiscordIds


# Bot Models
class BotEmojis(BaseModel):
    twitter: str
    facebook: str
    telegram: str
    whatsapp: str
    reddit: str
    snapchat: str
    git: str
    spoo: str


class Bot(BaseModel):
    command_prefix: str
    name: str
    description: str
    avatar_url: str
    bot_id: str
    bot_token: str
    custom_status: str
    super_user_id: str
    emojis: BotEmojis


# Assets Model
class Assets(BaseModel):
    ping_uri: str
    waiting_gifs: List[str]
    welcome_gifs: List[str]


# Cooldowns Model
class Cooldowns(BaseModel):
    short_term: CommandCooldown
    medium_term: CommandCooldown
    long_term: CommandCooldown


# Main Config Model
class Config(BaseModel):
    bot: Bot
    discord: Discord
    urls: Urls
    ui: UI
    server: Server
    assets: Assets
    commands: Dict[str, Command]
    cooldowns: Cooldowns  # Changed from commands_cooldowns to cooldowns


def replace_env_vars(value: str) -> str:
    """Replace environment variables in string values."""
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
    """Recursively process dictionary to replace environment variables."""
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
    """Load and parse the TOML configuration file with error handling."""
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
        config = Config(**processed_dict)

        # Additional validation
        config.server.validate_environment()

        return config
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
    config = load_config()
except ConfigError as e:
    print(f"Configuration Error: {str(e)}")
    raise SystemExit(1)

# Export only what's needed
__all__ = [
    "config",
    "Config",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "EnvironmentVariableError",
]
