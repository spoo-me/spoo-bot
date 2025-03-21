"""Bot configuration schemas."""

from typing import Annotated
from pydantic import HttpUrl, Field

from schemas.base import BaseConfigModel
from schemas.validators import DiscordIdField


class BotEmojis(BaseConfigModel):
    """Bot emoji configuration."""

    twitter: Annotated[str, DiscordIdField("Twitter emoji")]
    facebook: Annotated[str, DiscordIdField("Facebook emoji")]
    telegram: Annotated[str, DiscordIdField("Telegram emoji")]
    whatsapp: Annotated[str, DiscordIdField("WhatsApp emoji")]
    reddit: Annotated[str, DiscordIdField("Reddit emoji")]
    snapchat: Annotated[str, DiscordIdField("Snapchat emoji")]
    git: Annotated[str, DiscordIdField("GitHub emoji")]
    spoo: Annotated[str, DiscordIdField("Spoo emoji")]


class Bot(BaseConfigModel):
    """Main bot configuration."""

    command_prefix: Annotated[
        str, Field(pattern=r"^[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/]{1,3}$")
    ]
    name: str
    description: Annotated[
        str, Field(min_length=1, max_length=190)
    ]  # 190 is the max length for Discord bot description
    avatar_url: Annotated[str, HttpUrl]
    bot_id: Annotated[str, DiscordIdField("Bot ID")]
    bot_token: Annotated[
        str, Field(pattern=r"^([MN][\w-]{23,25})\.([\w-]{6})\.([\w-]{27,39})$")
    ]
    custom_status: Annotated[
        str, Field(max_length=128)
    ]  # 128 is the max length for Discord custom status, empty status is allowed
    super_user_id: Annotated[str, DiscordIdField("Super user ID")]
    emojis: BotEmojis
