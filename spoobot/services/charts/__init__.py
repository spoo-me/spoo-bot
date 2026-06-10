from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import httpx

if TYPE_CHECKING:
    from spoobot.config import Config


class ChartRenderer(Protocol):
    async def timeseries(
        self,
        title: str,
        points: list[tuple[str, int]],
        unique: list[tuple[str, int]] | None = None,
    ) -> bytes: ...
    async def breakdown(self, title: str, rows: list[tuple[str, int]]) -> bytes: ...
    async def country_heatmap(self, counts: dict[str, int]) -> bytes: ...
    async def close(self) -> None: ...


def build_renderer(kind: str, http: httpx.AsyncClient, cfg: Config) -> ChartRenderer:
    """`http` is an httpx.AsyncClient without base_url (the bot's misc client).

    Renderer modules import inside their branch so the optional htmlcards
    renderer never loads unless selected.
    """
    if kind == "quickchart":
        from spoobot.services.charts.quickchart import QuickChartRenderer

        return QuickChartRenderer(http, cfg)
    if kind == "htmlcards":
        from spoobot.services.charts.htmlcards import HtmlCardRenderer

        return HtmlCardRenderer(cfg)
    raise ValueError(f"unknown chart renderer: {kind}")
