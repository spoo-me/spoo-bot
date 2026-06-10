from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Protocol

import httpx

if TYPE_CHECKING:
    from spoobot.config import Config


class ChartRenderer(Protocol):
    async def timeseries(self, title: str, points: list[tuple[str, int]],
                         unique: list[tuple[str, int]] | None = None) -> bytes: ...
    async def breakdown(self, title: str, rows: list[tuple[str, int]]) -> bytes: ...
    async def country_heatmap(self, counts: dict[str, int]) -> bytes: ...
    async def close(self) -> None: ...


def build_renderer(kind: str, http: httpx.AsyncClient, cfg: Config) -> ChartRenderer:
    """`http` is an httpx.AsyncClient without base_url (the bot's misc client).

    Renderer modules are imported lazily (importlib) — they land in Tasks 16/17.
    """
    if kind == "quickchart":
        module = import_module("spoobot.services.charts.quickchart")
        return module.QuickChartRenderer(http, cfg)
    if kind == "htmlcards":
        module = import_module("spoobot.services.charts.htmlcards")
        return module.HtmlCardRenderer(cfg)
    raise ValueError(f"unknown chart renderer: {kind}")
