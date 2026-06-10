"""Renderer B: HTML/CSS cards screenshot by a persistent headless Chromium.

Requires the optional dependency group:  uv sync --group cards
and a one-time:  uv run playwright install chromium
"""

from __future__ import annotations

import asyncio
import html
from pathlib import Path
from typing import TYPE_CHECKING

from spoobot.services.charts.heatmap import render_heatmap_png

if TYPE_CHECKING:
    from playwright.async_api import Browser, Playwright

    from spoobot.config import Config

_TEMPLATE = Path("spoobot/templates/cards/stats-card.html")
_SVG = Path("spoobot/templates/cards/world.svg")


def _bars_html(rows: list[tuple[str, int]]) -> str:
    hi = max((v for _, v in rows), default=1) or 1
    out = []
    for label, value in rows[:10]:
        pct = int(value / hi * 100)
        out.append(
            f'<div class="bar"><div class="label">{html.escape(label)}</div>'
            f'<div class="track"><div class="fill" style="width:{pct}%"></div></div>'
            f'<div class="val">{value:,}</div></div>'
        )
    return "".join(out)


def _numbers_html(pairs: list[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="num"><b>{html.escape(v)}</b><span>{html.escape(k)}</span></div>'
        for k, v in pairs
    )


class HtmlCardRenderer:
    def __init__(self, cfg: Config) -> None:
        self._sem = asyncio.Semaphore(2)
        self._browser: Browser | None = None
        self._pw: Playwright | None = None

    async def _ensure_browser(self) -> Browser:
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(args=["--no-sandbox"])
        return self._browser

    async def _shoot(self, html_doc: str) -> bytes:
        browser = await self._ensure_browser()
        async with self._sem:
            page = await browser.new_page(viewport={"width": 800, "height": 10})
            try:
                await page.set_content(html_doc, wait_until="load")
                return await page.screenshot(full_page=True, type="png")
            finally:
                await page.close()

    async def _card(
        self, title: str, numbers: list[tuple[str, str]], rows: list[tuple[str, int]]
    ) -> bytes:
        doc = (
            _TEMPLATE.read_text(encoding="utf-8")
            .replace("{{title}}", html.escape(title))
            .replace("{{numbers}}", _numbers_html(numbers))
            .replace("{{bars}}", _bars_html(rows))
        )
        return await self._shoot(doc)

    async def timeseries(
        self,
        title: str,
        points: list[tuple[str, int]],
        unique: list[tuple[str, int]] | None = None,
    ) -> bytes:
        total = sum(v for _, v in points)
        numbers = [("clicks", f"{total:,}")]
        if unique:
            numbers.append(("unique", f"{sum(v for _, v in unique):,}"))
        return await self._card(title, numbers, points)

    async def breakdown(self, title: str, rows: list[tuple[str, int]]) -> bytes:
        return await self._card(title, [("total", f"{sum(v for _, v in rows):,}")], rows)

    async def country_heatmap(self, counts: dict[str, int]) -> bytes:
        return await asyncio.to_thread(render_heatmap_png, counts, svg_path=_SVG)

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()
