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


@pytest.mark.skipif(not SVG.exists(), reason="world.svg asset not downloaded")
def test_render_heatmap_fills_country_with_brand_blue():
    """Regression: injected CSS must beat the SVG's own stylesheet.

    A single country at the max bucket renders at full opacity, so the
    output must contain pixels at (or antialiased near) brand #497dff.
    """
    import io

    from PIL import Image

    png = render_heatmap_png({"US": 5}, svg_path=SVG)
    img = Image.open(io.BytesIO(png)).convert("RGB")
    target = (0x49, 0x7D, 0xFF)
    colors = img.getcolors(maxcolors=1_000_000)
    assert colors is not None
    brand_pixels = 0
    for count, color in colors:
        assert isinstance(color, tuple)
        r, g, b = color
        if (
            abs(r - target[0]) <= 12
            and abs(g - target[1]) <= 12
            and abs(b - target[2]) <= 12
        ):
            brand_pixels += count
    assert brand_pixels > 500, f"expected brand-blue fill, found {brand_pixels} px"
