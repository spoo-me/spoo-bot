from __future__ import annotations

from spoobot.ui.theme import sparkline


def test_sparkline_scales_to_blocks():
    assert sparkline([0, 4, 8]) == "▁▅█"


def test_sparkline_empty():
    assert sparkline([]) == ""


def test_sparkline_flat_nonzero():
    assert sparkline([3, 3, 3]) == "███"
