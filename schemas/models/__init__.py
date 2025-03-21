"""Models package for SpooBot schemas.

This package contains all Pydantic models that represent configuration entities.
"""

# Bot related models
from schemas.models.bot import Bot, BotEmojis

# Discord related models
from schemas.models.discord import Discord, DiscordIds, DiscordChannels

# URL related models
from schemas.models.urls import Urls, SocialShareUrls

# UI related models
from schemas.models.ui import UI, UIColors, UIMessages

# Server related models
from schemas.models.server import Server, KeepAlive

# Chart related models
from schemas.models.charts import (
    Charts,
    ChartColors,
    ChartStyle,
    ChartPadding,
    ChartScales,
    ChartPlugins,
    ChartPluginTitle,
    ChartPluginLegend,
    ChartHeatmap,
)

# Assets related models
from schemas.models.assets import Assets

# Command related models
from schemas.models.commands import (
    Command,
    CommandParameter,
    CommandCooldown,
    Cooldowns,
)

__all__: list[str] = [
    # Bot related
    "Bot",
    "BotEmojis",
    # Discord related
    "Discord",
    "DiscordIds",
    "DiscordChannels",
    # URL related
    "Urls",
    "SocialShareUrls",
    # UI related
    "UI",
    "UIColors",
    "UIMessages",
    # Server related
    "Server",
    "KeepAlive",
    # Chart related
    "Charts",
    "ChartColors",
    "ChartStyle",
    "ChartPadding",
    "ChartScales",
    "ChartPlugins",
    "ChartPluginTitle",
    "ChartPluginLegend",
    "ChartHeatmap",
    # Assets related
    "Assets",
    # Command related
    "Command",
    "CommandParameter",
    "CommandCooldown",
    "Cooldowns",
]
