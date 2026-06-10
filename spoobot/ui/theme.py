from __future__ import annotations

PRIMARY = 0x7289DA
SUCCESS = 0x2ECC71
ERROR = 0xE74C3C
WARNING = 0xF1C40F
BRAND_QR_GRADIENT = (
    "(117,129,86)",
    "(103,175,38)",
)  # legacy gradient args kept for parity
SPARK_BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values: list[int]) -> str:
    """Unicode sparkline; empty string for no data."""
    if not values:
        return ""
    hi = max(values) or 1
    return "".join(SPARK_BLOCKS[min(round(v / hi * 7), 7)] for v in values)
