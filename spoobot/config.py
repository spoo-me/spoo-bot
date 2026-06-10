"""TOML + ${ENV} configuration, validated with pydantic.

Layout mirrors config.template.toml. Unknown keys are rejected so typos
surface at startup, not at first use.
"""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError

_ENV_RE = re.compile(r"^\$\{([A-Z0-9_]+)\}$")


class ConfigError(Exception):
    """Raised for any configuration problem (missing file/env, bad values)."""


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BotSection(_Model):
    command_prefix: str = "$"
    name: str = "SpooBot"
    description: str = ""
    bot_token: str
    custom_status: str = ""
    super_user_id: str
    parent_server_id: str = ""


class EmojiSection(_Model):
    twitter: str = ""
    facebook: str = ""
    telegram: str = ""
    whatsapp: str = ""
    reddit: str = ""
    snapchat: str = ""
    git: str = ""
    spoo: str = ""


class SpooSection(_Model):
    api_base: str = "https://spoo.me"
    qr_api_base: str = "https://qr.spoo.me"


class AuthSection(_Model):
    app_id: str = "spoo-discord"
    state_secret: str = Field(min_length=32)
    vault_key: str  # Fernet key (44-char urlsafe base64)
    vault_path: str = "data/vault.sqlite3"
    link_ttl_seconds: int = 600


class WebSection(_Model):
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 9274
    public_callback_url: str = "https://discord-bot.spoo.me/callback"


class ChartsSection(_Model):
    renderer: Literal["quickchart", "htmlcards"] = "quickchart"
    quickchart_url: str = "https://quickchart.io"


class CooldownTier(_Model):
    count: int
    seconds: int


class CooldownsSection(_Model):
    short_term: CooldownTier = CooldownTier(count=1, seconds=10)
    medium_term: CooldownTier = CooldownTier(count=5, seconds=60)
    long_term: CooldownTier = CooldownTier(count=200, seconds=86400)


class ChannelsSection(_Model):
    welcome: str = ""
    stats_clicks: str = ""
    stats_shortlinks: str = ""


class UrlsSection(_Model):
    discord_invite: str = "https://spoo.me/discord"
    bot_invite: str = ""
    github: str = "https://github.com/spoo-me/spoo-bot"
    dashboard_apps: str = "https://spoo.me/dashboard/apps"


class Config(_Model):
    bot: BotSection
    emojis: EmojiSection = EmojiSection()
    spoo: SpooSection = SpooSection()
    auth: AuthSection
    web: WebSection
    charts: ChartsSection = ChartsSection()
    cooldowns: CooldownsSection = CooldownsSection()
    channels: ChannelsSection = ChannelsSection()
    urls: UrlsSection = UrlsSection()


def _interpolate(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _interpolate(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate(v) for v in value]
    if isinstance(value, str):
        m = _ENV_RE.match(value)
        if m:
            name = m.group(1)
            env = os.getenv(name)
            if env is None:
                raise ConfigError(f"environment variable {name} is not set")
            return env
    return value


def load_config(path: str | Path = "config.toml") -> Config:
    load_dotenv()
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p} (copy config.template.toml)")
    with p.open("rb") as f:
        raw = tomllib.load(f)
    try:
        return Config.model_validate(_interpolate(raw))
    except ValidationError as exc:
        raise ConfigError(str(exc)) from exc
