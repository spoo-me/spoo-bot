from typing import Dict, List, Optional, Annotated
from pydantic import (
    BaseModel,
    ValidationError,
    HttpUrl,
    Field,
    field_validator,
)
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
    count: Annotated[int, Field(gt=0)]
    seconds: Annotated[int, Field(gt=0, le=604800)]  # Max 1 week

    model_config = {
        "error_msg_templates": {
            "greater_than": "Value must be positive",
            "less_than_equal": "Cooldown duration cannot exceed 1 week (604800 seconds)"
        }
    }


# Chart Models
class ChartColors(BaseModel):
    platform: List[List[Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]]]
    browser: List[List[Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]]]
    referrer: List[List[Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]]]
    timeline: List[List[Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]]]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Colors must be in format 0xRRGGBB"
        }
    }

class ChartPadding(BaseModel):
    left: Annotated[int, Field(ge=0, le=100)]
    right: Annotated[int, Field(ge=0, le=100)]
    top: Annotated[int, Field(ge=0, le=100)]
    bottom: Annotated[int, Field(ge=0, le=100)]

    model_config = {
        "error_msg_templates": {
            "greater_than_equal": "Padding must be non-negative",
            "less_than_equal": "Padding cannot exceed 100 pixels"
        }
    }


class ChartStyle(BaseModel):
    background: Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{6}$")]
    grid_color: Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{6}$")]
    text_color: Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{6}$")]
    font_style: Annotated[str, Field(pattern=r'^(normal|italic|bold)$')]
    font_size: Annotated[int, Field(ge=8, le=72)]  # Reasonable font size range
    border_width: Annotated[int, Field(ge=0, le=10)]
    border_radius: Annotated[int, Field(ge=0, le=50)]
    line_tension: Annotated[float, Field(ge=0, le=1)]
    padding: ChartPadding

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": {
                "font_style": "Font style must be 'normal', 'italic', or 'bold'",
                "__default__": "Colors must be in format 0xRRGGBB"
            }
        }
    }


class ChartScales(BaseModel):
    grid_color: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]
    tick_color: Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{6}$")]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Colors must be in format 0xRRGGBB"
        }
    }


class ChartPluginTitle(BaseModel):
    color: Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{6}$")]
    font_style: Annotated[str, Field(pattern=r'^(normal|italic|bold)$')]
    font_size: Annotated[int, Field(ge=8, le=72)]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": {
                "font_style": "Font style must be 'normal', 'italic', or 'bold'",
                "__default__": "Colors must be in format 0xRRGGBB"
            }
        }
    }


class ChartPluginLegend(BaseModel):
    labels_color: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Colors must be in format 0xRRGGBB"
        }
    }


class ChartPlugins(BaseModel):
    title: ChartPluginTitle
    legend: ChartPluginLegend


class ChartHeatmap(BaseModel):
    dpi: Annotated[int, Field(ge=72, le=600)]  # Standard DPI range
    alpha: Annotated[float, Field(ge=0, le=1)]
    pad_inches: Annotated[float, Field(ge=0, le=2)]
    bbox_inches: Annotated[str, Field(pattern=r'^(tight|standard)$')]

    model_config = {
        "error_msg_templates": {
            "greater_than_equal": "Value must be at least {ge}",
            "less_than_equal": "Value cannot exceed {le}",
            "pattern_mismatch": "bbox_inches must be either 'tight' or 'standard'"
        }
    }

class Charts(BaseModel):
    colors: ChartColors
    style: ChartStyle
    scales: ChartScales
    plugins: ChartPlugins
    heatmap: ChartHeatmap


# UI Models
class UIColors(BaseModel):
    primary: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]
    success: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]
    error: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]
    warning: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]
    info: Annotated[str, Field(pattern=r'^0x[0-9a-fA-F]{6}$')]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "must be a hex color in format 0xRRGGBB"
        }
    }


class UIMessages(BaseModel):
    welcome: str
    bot_mention: str


class UI(BaseModel):
    colors: UIColors
    charts: Charts
    messages: UIMessages


# URL Models
class SocialShareUrls(BaseModel):
    twitter: HttpUrl
    facebook: HttpUrl
    telegram: HttpUrl
    whatsapp: HttpUrl
    reddit: HttpUrl
    snapchat: HttpUrl

    @field_validator('*')
    @classmethod
    def validate_social_url_format(cls, v: HttpUrl) -> HttpUrl:
        # Convert to string for manipulation
        url_str = str(v)
        if not url_str.endswith('='):
            raise ValueError('Social share URLs must end with "=" for parameter appending')
        return v


class Urls(BaseModel):
    api_base: HttpUrl
    spoo_metrics: HttpUrl
    qr_api_base: HttpUrl
    charts_api_base: HttpUrl
    discord_invite: HttpUrl
    bot_invite: HttpUrl
    github: HttpUrl
    social_share: SocialShareUrls

    @field_validator('*')
    @classmethod
    def must_be_https(cls, v: HttpUrl) -> HttpUrl:
        url_str = str(v)
        if not url_str.startswith('https://'):
            raise ValueError('All URLs must use HTTPS for security')
        return v


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
    welcome: Annotated[str, Field(pattern=r'^\d{17,19}$')]
    stats_clicks: Annotated[str, Field(pattern=r'^\d{17,19}$')]
    stats_shortlinks: Annotated[str, Field(pattern=r'^\d{17,19}$')]

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Channel IDs must be 17-19 digits"
        }
    }


class DiscordIds(BaseModel):
    parent_server: Annotated[str, Field(pattern=r'^\d{17,19}$')]
    channels: DiscordChannels

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Discord IDs must be 17-19 digits"
        }
    }


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
    command_prefix: Annotated[str, Field(min_length=1, max_length=3)]
    name: str
    description: str
    avatar_url: HttpUrl
    bot_id: Annotated[str, Field(pattern=r'^\d{17,19}$')]
    bot_token: str
    custom_status: str
    super_user_id: Annotated[str, Field(pattern=r'^\d{17,19}$')]
    emojis: BotEmojis

    @field_validator('command_prefix')
    @classmethod
    def validate_prefix_chars(cls, v: str) -> str:
        allowed = set('!@#$%^&*()_+-=[]{}|;:,.<>?/')
        if not all(c in allowed for c in v):
            raise ValueError('Command prefix must only contain special characters')
        return v

    model_config = {
        "error_msg_templates": {
            "pattern_mismatch": "Invalid Discord ID format (must be 17-19 digits)",
            "string_too_short": "Command prefix cannot be empty",
            "string_too_long": "Command prefix cannot exceed 3 characters"
        }
    }


# Assets Model
class Assets(BaseModel):
    ping_uri: HttpUrl
    waiting_gifs: List[HttpUrl]
    welcome_gifs: List[HttpUrl]

    @field_validator('waiting_gifs', 'welcome_gifs')
    @classmethod
    def validate_gif_urls(cls, urls: List[HttpUrl]) -> List[HttpUrl]:
        for url in urls:
            url_str = str(url)
            if not url_str.endswith('.gif'):
                raise ValueError('All animation URLs must end with .gif')
            if not url_str.startswith('https://'):
                raise ValueError('All URLs must use HTTPS for security')
        return urls

    @field_validator('ping_uri')
    @classmethod
    def validate_ping_url(cls, v: HttpUrl) -> HttpUrl:
        url_str = str(v)
        if not url_str.startswith('https://'):
            raise ValueError('All URLs must use HTTPS for security')
        return v

    model_config = {
        "error_msg_templates": {
            "type_error": "All URLs must be valid HTTPS URLs"
        }
    }

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
