"""Render identical sample data through both chart renderers.

Usage:
    uv sync --group cards && uv run playwright install chromium
    uv run python scripts/chart_bakeoff.py
Outputs PNGs into ./bakeoff/ — open them side by side and pick a winner.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from spoobot.config import load_config
from spoobot.infrastructure.http import create_client
from spoobot.services.charts import build_renderer

TIMESERIES = [
    (f"Jun {d:02d}", v)
    for d, v in enumerate(
        [3, 7, 4, 12, 18, 11, 25, 31, 22, 40, 38, 52, 47, 61], start=1
    )
]
UNIQUE = [(label, max(1, int(v * 0.7))) for label, v in TIMESERIES]
BROWSERS = [
    ("Chrome", 312),
    ("Safari", 144),
    ("Firefox", 89),
    ("Edge", 41),
    ("Other", 17),
]
COUNTRIES = {"US": 220, "IN": 180, "DE": 95, "GB": 70, "BR": 40, "JP": 22}


async def main() -> None:
    out = Path("bakeoff")
    out.mkdir(exist_ok=True)
    cfg = load_config()
    client = create_client()
    try:
        for kind in ("quickchart", "htmlcards"):
            renderer = build_renderer(kind, client, cfg)
            try:
                (out / f"{kind}-timeseries.png").write_bytes(
                    await renderer.timeseries(
                        "Clicks over time — bakeoff", TIMESERIES, UNIQUE
                    )
                )
                (out / f"{kind}-breakdown.png").write_bytes(
                    await renderer.breakdown("Browsers — bakeoff", BROWSERS)
                )
                (out / f"{kind}-heatmap.png").write_bytes(
                    await renderer.country_heatmap(COUNTRIES)
                )
                print(f"{kind}: 3 charts written")
            finally:
                await renderer.close()
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
