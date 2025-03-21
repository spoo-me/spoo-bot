"""Base models and common configuration for all schema models."""

from pydantic import BaseModel, ConfigDict

HEX_COLOR_PATTERN = r"^0x[0-9a-fA-F]{6}$"
RGB_COLOR_PATTERN = r"^rgba?\((\d{1,3},\s*){2}\d{1,3},?\s*(0|1|0?\.\d+)?\)$"
DISCORD_ID_PATTERN = r"^\d{17,19}$"
FONT_STYLE_PATTERN = r"^(normal|italic|bold)$"


class BaseConfigModel(BaseModel):
    """Base model with common configuration for all schema models."""

    model_config: ConfigDict = {"extra": "forbid", "validate_assignment": True}
