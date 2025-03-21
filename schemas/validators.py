"""Custom field types and validators for configuration schemas."""

from typing import Any, Optional, Union
from pydantic import Field, HttpUrl

# Import constants from base.py
from schemas.base import (
    HEX_COLOR_PATTERN,
    RGB_COLOR_PATTERN,
    DISCORD_ID_PATTERN,
    FONT_STYLE_PATTERN,
)


def HexColorField(description: str = "Hex color code") -> Any:
    """Field for hex color values in format 0xRRGGBB."""
    return Field(pattern=HEX_COLOR_PATTERN, description=description)


def RgbColorField(description: str = "RGB color code") -> Any:
    """Field for RGB color values in format rgba(r, g, b, a)."""
    return Field(pattern=RGB_COLOR_PATTERN, description=description)


def DiscordIdField(description: str = "Discord ID") -> Any:
    """Field for Discord IDs (17-19 digits)."""
    return Field(pattern=DISCORD_ID_PATTERN, description=description)


def FontStyleField(description: str = "Font style") -> Any:
    """Field for font style values (normal, italic, bold)."""
    return Field(pattern=FONT_STYLE_PATTERN, description=description)


def RangeField(
    ge: Optional[Union[int, float]] = None,
    gt: Optional[Union[int, float]] = None,
    le: Optional[Union[int, float]] = None,
    lt: Optional[Union[int, float]] = None,
    description: str = "",
) -> Any:
    """Field for numeric ranges with consistent validation."""
    return Field(ge=ge, gt=gt, le=le, lt=lt, description=description)


def https_validator(url: HttpUrl) -> HttpUrl:
    """Validate that a URL uses HTTPS."""
    url_str = str(url)
    if not url_str.startswith("https://"):
        raise ValueError("URL must use HTTPS for security")
    return url
