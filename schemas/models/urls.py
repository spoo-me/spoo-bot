"""URL-related configuration schemas."""

from typing import Annotated
from pydantic import HttpUrl, field_validator

from schemas.base import BaseConfigModel
from schemas.validators import https_validator


class SocialShareUrls(BaseConfigModel):
    """Social media sharing URL configuration."""

    twitter: Annotated[str, HttpUrl]
    facebook: Annotated[str, HttpUrl]
    telegram: Annotated[str, HttpUrl]
    whatsapp: Annotated[str, HttpUrl]
    reddit: Annotated[str, HttpUrl]
    snapchat: Annotated[str, HttpUrl]

    @field_validator("*")
    @classmethod
    def validate_social_url_format(cls, v: str) -> str:
        # First validate HTTPS
        https_validator(v)

        # Then validate ending with '='
        url_str = str(v)
        if not url_str.endswith("="):
            raise ValueError(
                'Social share URLs must end with "=" for parameter appending'
            )
        return v


class Urls(BaseConfigModel):
    """URL configuration."""

    api_base: Annotated[str, HttpUrl]
    spoo_metrics: Annotated[str, HttpUrl]
    qr_api_base: Annotated[str, HttpUrl]
    charts_api_base: Annotated[str, HttpUrl]
    discord_invite: Annotated[str, HttpUrl]
    bot_invite: Annotated[str, HttpUrl]
    github: Annotated[str, HttpUrl]
    social_share: SocialShareUrls

    # Validate that all URLs use HTTPS
    @field_validator("*", mode="before")
    @classmethod
    def validate_https(cls, v: any) -> any:
        # skips the check for social_share which are already validated
        if not isinstance(v, str):
            return v

        https_validator(v)
        return v
