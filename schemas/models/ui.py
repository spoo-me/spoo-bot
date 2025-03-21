"""UI-related configuration schemas."""

from typing import Annotated

from schemas.base import BaseConfigModel
from schemas.validators import HexColorField
from schemas.models.charts import Charts


class UIColors(BaseConfigModel):
    """UI color configuration."""

    primary: Annotated[str, HexColorField("Primary UI color")]
    success: Annotated[str, HexColorField("Success UI color")]
    error: Annotated[str, HexColorField("Error UI color")]
    warning: Annotated[str, HexColorField("Warning UI color")]
    info: Annotated[str, HexColorField("Info UI color")]


class UIMessages(BaseConfigModel):
    """UI message configuration."""

    welcome: str
    bot_mention: str


class UI(BaseConfigModel):
    """Main UI configuration."""

    colors: UIColors
    charts: Charts
    messages: UIMessages
