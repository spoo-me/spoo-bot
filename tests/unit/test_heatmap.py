from __future__ import annotations

from pathlib import Path

import pytest

from spoobot.services.charts.heatmap import build_country_css, render_heatmap_png

SVG = Path("spoobot/templates/cards/world.svg")


def test_build_country_css_buckets_opacity():
    css = build_country_css({"US": 100, "IN": 10})
    assert ".us" in css and ".in" in css
    assert "fill:#497dff" in css


@pytest.mark.skipif(not SVG.exists(), reason="world.svg asset not downloaded")
def test_render_heatmap_produces_png():
    png = render_heatmap_png({"US": 5, "DE": 2}, svg_path=SVG)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
