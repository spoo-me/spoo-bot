from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import httpx

from spoobot.infrastructure.http import raise_for_status_mapped
from spoobot.services.charts.heatmap import render_heatmap_png

if TYPE_CHECKING:
    from spoobot.config import Config

DARK_BG = "rgb(32, 34, 37)"
GRID = "rgb(46, 48, 53)"
TEXT = "rgb(255, 255, 255)"
SERIES_COLORS = [
    ("rgba(75, 192, 192, 0.15)", "rgb(75, 192, 192)"),
    ("rgba(85, 52, 235, 0.25)", "rgb(85, 52, 235)"),
]


def build_chart_config(
    *, kind: str, title: str, labels: list[str], datasets: list[tuple[str, list[int]]]
) -> dict[str, Any]:
    ds: list[dict[str, Any]] = []
    for i, (name, data) in enumerate(datasets):
        fill, line = SERIES_COLORS[i % len(SERIES_COLORS)]
        ds.append(
            {
                "label": name,
                "data": data,
                "backgroundColor": fill,
                "borderColor": line,
                "borderWidth": 2,
                "tension": 0.5,
                "fill": kind == "line",
            }
        )
    axis = {"grid": {"color": GRID}, "ticks": {"color": TEXT}}
    return {
        "type": kind,
        "data": {"labels": labels, "datasets": ds},
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": title,
                    "color": TEXT,
                    "font": {"size": 20, "weight": "bold"},
                },
                "legend": {"labels": {"color": TEXT}},
            },
            "scales": {"x": axis, "y": axis},
        },
    }


class QuickChartRenderer:
    """Renderer A: chart.js via QuickChart /chart endpoint (POST → PNG)."""

    def __init__(self, http: httpx.AsyncClient, cfg: Config) -> None:
        self._http = http  # the bot's misc client (no base_url) — absolute URL below
        self._base = cfg.charts.quickchart_url.rstrip("/")
        self._svg_path = "spoobot/templates/cards/world.svg"

    async def _render(self, config: dict[str, Any]) -> bytes:
        body = {
            "chart": config,
            "width": 800,
            "height": 400,
            "backgroundColor": DARK_BG,
            "format": "png",
            "version": "4",
        }
        resp = await self._http.post(f"{self._base}/chart", json=body)
        raise_for_status_mapped(resp)
        return resp.content

    async def timeseries(
        self,
        title: str,
        points: list[tuple[str, int]],
        unique: list[tuple[str, int]] | None = None,
    ) -> bytes:
        labels = [label for label, _ in points]
        datasets = [("Clicks", [v for _, v in points])]
        if unique:
            datasets.append(("Unique clicks", [v for _, v in unique]))
        return await self._render(
            build_chart_config(
                kind="line", title=title, labels=labels, datasets=datasets
            )
        )

    async def breakdown(self, title: str, rows: list[tuple[str, int]]) -> bytes:
        labels = [label for label, _ in rows]
        return await self._render(
            build_chart_config(
                kind="bar",
                title=title,
                labels=labels,
                datasets=[("Clicks", [v for _, v in rows])],
            )
        )

    async def country_heatmap(self, counts: dict[str, int]) -> bytes:
        return await asyncio.to_thread(
            render_heatmap_png, counts, svg_path=self._svg_path
        )

    async def close(self) -> None:
        return None
