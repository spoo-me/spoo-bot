"""Country heatmap: static SVG + injected CSS fills, rasterized by resvg.

The .fmbot pattern (research §5.1): zero geo libraries. world.svg has
country <g> elements classed with ISO-3166 alpha-2 codes (lowercase).
"""

from __future__ import annotations

from pathlib import Path

import resvg_py

BRAND_FILL = "#497dff"
_BUCKETS = (0.25, 0.45, 0.65, 0.85, 1.0)

_BASE_CSS = """
svg { background-color: #000000; }
.landxx { fill: #1d1f24; stroke: #2e3035; stroke-width: 0.5; }
.oceanxx { fill: #000000; }
"""


def build_country_css(counts: dict[str, int]) -> str:
    if not counts:
        return _BASE_CSS
    hi = max(counts.values()) or 1
    rules = [_BASE_CSS]
    for code, value in counts.items():
        bucket = _BUCKETS[min(int(value / hi * (len(_BUCKETS) - 1)), len(_BUCKETS) - 1)]
        rules.append(f".{code.lower()} {{ fill:{BRAND_FILL}; fill-opacity:{bucket}; }}")
    return "\n".join(rules)


def render_heatmap_png(
    counts: dict[str, int], *, svg_path: str | Path, width: int = 1400
) -> bytes:
    svg = Path(svg_path).read_text(encoding="utf-8")
    css = build_country_css(counts)
    # Inject a <style> block right after the opening <svg ...> tag.
    head_end = svg.index(">", svg.index("<svg")) + 1
    styled = f"{svg[:head_end]}<style>{css}</style>{svg[head_end:]}"
    return bytes(resvg_py.svg_to_bytes(svg_string=styled, width=width))
