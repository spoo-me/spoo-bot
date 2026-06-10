from __future__ import annotations

from spoobot.services.charts.quickchart import build_chart_config


def test_timeseries_config_is_dark_line_chart():
    cfg = build_chart_config(
        kind="line", title="Clicks", labels=["Mon", "Tue"], datasets=[("Clicks", [3, 5])]
    )
    assert cfg["type"] == "line"
    assert cfg["data"]["labels"] == ["Mon", "Tue"]
    assert cfg["data"]["datasets"][0]["data"] == [3, 5]
    assert cfg["options"]["plugins"]["title"]["text"] == "Clicks"


def test_breakdown_config_is_bar_chart():
    cfg = build_chart_config(
        kind="bar", title="Browsers", labels=["Chrome"], datasets=[("Clicks", [9])]
    )
    assert cfg["type"] == "bar"
