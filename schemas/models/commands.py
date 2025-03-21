"""Command and cooldown configuration schemas."""

from typing import List, Optional, Annotated
from pydantic import Field

from schemas.base import BaseConfigModel
from schemas.validators import RangeField, DiscordIdField


class CommandParameter(BaseConfigModel):
    """Command parameter configuration."""

    name: str
    description: str
    emoji: str


class Command(BaseConfigModel):
    """Command configuration."""

    id: Annotated[str, DiscordIdField("Command ID")]
    emoji: str
    description: Annotated[
        str, Field(min_length=1, max_length=100)
    ]  # 100 is the max length for Discord command description
    parameters: Optional[List[CommandParameter]] = None


class CommandCooldown(BaseConfigModel):
    """Command cooldown configuration."""

    count: Annotated[
        int, RangeField(gt=0, description="Number of uses before cooldown")
    ]
    seconds: Annotated[
        int, RangeField(gt=0, le=604800, description="Cooldown duration in seconds")
    ]


class Cooldowns(BaseConfigModel):
    """Cooldown configuration for different command types."""

    short_term: CommandCooldown
    medium_term: CommandCooldown
    long_term: CommandCooldown
