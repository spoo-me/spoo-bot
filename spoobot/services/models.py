from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class ShortUrl(_Model):
    alias: str
    short_url: str
    long_url: str
    created_at: int = 0
    status: str = "ACTIVE"


class AliasCheck(_Model):
    available: bool
    reason: str | None = None  # "length" | "format" | "taken" | None


class UrlListItem(_Model):
    id: str
    alias: str
    short_url: str = ""
    long_url: str
    status: str = "ACTIVE"
    total_clicks: int = 0
    created_at: int | None = None
    password_set: bool = False
    max_clicks: int | None = None
    domain: str | None = None


class UrlPage(_Model):
    items: list[UrlListItem]
    page: int
    page_size: int = Field(alias="pageSize")
    total: int
    has_next: bool = Field(alias="hasNext")


class StatsSummary(_Model):
    total_clicks: int = 0
    unique_clicks: int = 0
    first_click: str | None = None
    last_click: str | None = None
    avg_redirection_time: float = 0.0


class StatsResult(_Model):
    scope: str
    group_by: list[str] = []
    timezone: str = "UTC"
    summary: StatsSummary
    # dynamic keys: "{metric}_by_{dimension}" -> list of datapoint dicts
    metrics: dict[str, list[dict[str, Any]]] = {}
    short_code: str | None = None

    def series(self, metric: str, dimension: str) -> list[tuple[str, int]]:
        """Return [(label, value)] for e.g. metric='clicks', dimension='browser'."""
        rows = self.metrics.get(f"{metric}_by_{dimension}", [])
        out: list[tuple[str, int]] = []
        for row in rows:
            label = str(row.get(dimension, "unknown"))
            out.append((label, int(row.get(metric, 0))))
        return out


class SiteMetrics(_Model):
    total_clicks: int = Field(alias="total-clicks", default=0)
    total_shortlinks: int = Field(alias="total-shortlinks", default=0)


class SpooProfile(_Model):
    email: str
    email_verified: bool = False
    user_name: str = ""
    plan: str = "FREE"


class TokenPair(_Model):
    access_token: str
    refresh_token: str


class DeviceTokenGrant(_Model):
    access_token: str
    refresh_token: str
    user: SpooProfile | None = None


class ExportFile(_Model):
    filename: str
    content: bytes
