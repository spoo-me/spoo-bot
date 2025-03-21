"""Discord-related configuration schemas."""

from typing import Annotated

from schemas.base import BaseConfigModel
from schemas.validators import DiscordIdField


class DiscordChannels(BaseConfigModel):
    """Discord channel configuration."""

    welcome: Annotated[str, DiscordIdField("Welcome channel ID")]
    stats_clicks: Annotated[str, DiscordIdField("Stats clicks channel ID")]
    stats_shortlinks: Annotated[str, DiscordIdField("Stats shortlinks channel ID")]


class DiscordIds(BaseConfigModel):
    """Discord IDs configuration."""

    parent_server: Annotated[str, DiscordIdField("Parent server ID")]
    channels: DiscordChannels


class Discord(BaseConfigModel):
    """Main Discord configuration."""

    ids: DiscordIds
