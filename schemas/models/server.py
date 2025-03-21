"""Server configuration schemas."""

from pydantic import model_validator

from schemas.base import BaseConfigModel


class KeepAlive(BaseConfigModel):
    """Keep-alive server configuration."""

    enabled: bool
    host: str
    port: str


class Server(BaseConfigModel):
    """Server configuration."""

    environment: str
    is_cloud_hosted: bool
    keep_alive: KeepAlive

    @model_validator(mode="after")
    def validate_environment(self):
        """Validate the environment field."""
        valid_environments = {"development", "production", "testing"}
        if self.environment not in valid_environments:
            raise ValueError(
                f"Invalid environment: {self.environment}. "
                f"Must be one of: {', '.join(valid_environments)}"
            )
        return self
