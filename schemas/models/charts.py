"""Chart configuration schemas."""

from typing import List, Annotated
from pydantic import Field

from schemas.base import BaseConfigModel
from schemas.validators import RgbColorField, FontStyleField, RangeField


class ChartColors(BaseConfigModel):
    """Chart color configuration for different chart types."""

    platform: List[List[Annotated[str, RgbColorField("Platform chart colors")]]]
    browser: List[List[Annotated[str, RgbColorField("Browser chart colors")]]]
    referrer: List[List[Annotated[str, RgbColorField("Referrer chart colors")]]]
    timeline: List[List[Annotated[str, RgbColorField("Timeline chart colors")]]]


class ChartPadding(BaseConfigModel):
    """Chart padding configuration."""

    left: Annotated[int, RangeField(ge=0, le=100, description="Left padding in pixels")]
    right: Annotated[
        int, RangeField(ge=0, le=100, description="Right padding in pixels")
    ]
    top: Annotated[int, RangeField(ge=0, le=100, description="Top padding in pixels")]
    bottom: Annotated[
        int, RangeField(ge=0, le=100, description="Bottom padding in pixels")
    ]


class ChartStyle(BaseConfigModel):
    """Chart styling configuration."""

    background: Annotated[str, RgbColorField("Chart background color")]
    grid_color: Annotated[str, RgbColorField("Chart grid color")]
    text_color: Annotated[str, RgbColorField("Chart text color")]
    font_style: Annotated[str, FontStyleField("Chart font style")]
    font_size: Annotated[
        int, RangeField(ge=8, le=72, description="Chart font size in points")
    ]
    border_width: Annotated[
        int, RangeField(ge=0, le=10, description="Chart border width in pixels")
    ]
    border_radius: Annotated[
        int, RangeField(ge=0, le=50, description="Chart border radius in pixels")
    ]
    line_tension: Annotated[
        float, RangeField(ge=0, le=1, description="Chart line tension (0.0 - 1.0)")
    ]
    padding: ChartPadding


class ChartScales(BaseConfigModel):
    """Chart scales configuration."""

    grid_color: Annotated[str, RgbColorField("Chart grid color")]
    tick_color: Annotated[str, RgbColorField("Chart tick color")]


class ChartPluginTitle(BaseConfigModel):
    """Chart title plugin configuration."""

    color: Annotated[str, RgbColorField("Chart title color")]
    font_style: Annotated[str, FontStyleField("Chart title font style")]
    font_size: Annotated[
        int, RangeField(ge=8, le=72, description="Chart title font size in points")
    ]


class ChartPluginLegend(BaseConfigModel):
    """Chart legend plugin configuration."""

    labels_color: Annotated[str, RgbColorField("Chart legend labels color")]


class ChartPlugins(BaseConfigModel):
    """Chart plugins configuration."""

    title: ChartPluginTitle
    legend: ChartPluginLegend


class ChartHeatmap(BaseConfigModel):
    """Chart heatmap configuration."""

    dpi: Annotated[
        int, RangeField(ge=72, le=600, description="Heatmap DPI (dots per inch)")
    ]
    alpha: Annotated[
        float, RangeField(ge=0, le=1, description="Heatmap transparency (0.0 - 1.0)")
    ]
    pad_inches: Annotated[
        float, RangeField(ge=0, le=2, description="Heatmap padding in inches")
    ]
    bbox_inches: Annotated[
        str,
        Field(pattern=r"^(tight|standard)$", description="Heatmap bounding box mode"),
    ]


# Subclass for UI configuration
class Charts(BaseConfigModel):
    """Complete charts configuration."""

    colors: ChartColors
    style: ChartStyle
    scales: ChartScales
    plugins: ChartPlugins
    heatmap: ChartHeatmap
