"""Assets configuration schemas."""

from typing import List, Annotated
from pydantic import HttpUrl, field_validator

from schemas.base import BaseConfigModel
from schemas.validators import https_validator


class Assets(BaseConfigModel):
    """Assets configuration."""

    ping_uri: Annotated[str, HttpUrl]
    waiting_gifs: List[Annotated[str, HttpUrl]]
    welcome_gifs: List[Annotated[str, HttpUrl]]

    @field_validator("ping_uri")
    @classmethod
    def validate_ping_url(cls, v: str) -> str:
        return https_validator(v)

    @field_validator("waiting_gifs", "welcome_gifs")
    @classmethod
    def validate_gif_urls(cls, urls: List[str]) -> List[str]:
        for url in urls:
            # Validate HTTPS
            https_validator(url)

            # Validate GIF extension
            url_str = str(url)
            base_url: str = url_str.split("?")[0]  # Remove query parameters

            if not (base_url.endswith(".gif") or base_url.endswith(".webp")):
                raise ValueError("All animation URLs must end with .gif or .webp")

        return urls
