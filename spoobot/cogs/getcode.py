from __future__ import annotations

from pathlib import Path
from string import Template
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.ui import embeds, theme

if TYPE_CHECKING:
    from spoobot.bot import SpooBot

TEMPLATE_DIR = Path("spoobot/templates/code")

# display name → (filename stem, markdown language tag)
LANGUAGES: dict[str, tuple[str, str]] = {
    "Python": ("python", "py"),
    "JavaScript": ("javascript", "js"),
    "TypeScript": ("typescript", "ts"),
    "Node.js": ("nodejs", "js"),
    "Curl": ("curl", "bash"),
    "Go": ("go", "go"),
    "Rust": ("rust", "rust"),
    "Java": ("java", "java"),
    "Kotlin": ("kotlin", "kotlin"),
    "Swift": ("swift", "swift"),
    "C#": ("csharp", "cs"),
    "C++": ("cpp", "cpp"),
    "C": ("c", "c"),
    "PHP": ("php", "php"),
    "Ruby": ("ruby", "rb"),
    "Dart": ("dart", "dart"),
    "R": ("r", "r"),
    "Perl": ("perl", "perl"),
    "Clojure": ("clojure", "clojure"),
}


def render_snippet(
    language: str,
    *,
    url: str,
    alias: str | None,
    password: str | None,
    max_clicks: int | None,
) -> tuple[str, str]:
    """Returns (code, md_tag). Raises KeyError for unknown language."""
    stem, tag = LANGUAGES[language]
    raw = (TEMPLATE_DIR / f"{stem}.tmpl").read_text(encoding="utf-8")
    code = Template(raw).safe_substitute(
        url=url,
        alias=alias or "",
        password=password or "",
        max_clicks=str(max_clicks or ""),
    )
    return code, tag


class GetCode(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="get-code", description="API code snippet for your language 🧑🏻‍💻"
    )
    @app_commands.describe(
        language="Programming language", url="URL to shorten in the snippet"
    )
    @app_commands.choices(
        language=[
            app_commands.Choice(name=name, value=name) for name in sorted(LANGUAGES)
        ]
    )
    async def get_code(
        self,
        interaction: discord.Interaction,
        language: app_commands.Choice[str],
        url: str,
        alias: str | None = None,
        password: str | None = None,
        max_clicks: int | None = None,
    ) -> None:
        code, tag = render_snippet(
            language.value,
            url=url,
            alias=alias,
            password=password,
            max_clicks=max_clicks,
        )
        body = f"```{tag}\n{code}\n```"
        embed = discord.Embed(
            title=f"spoo.me API — {language.value}",
            description=body if len(body) <= 4096 else None,
            color=theme.PRIMARY,
        )
        if len(body) > 4096:
            await interaction.response.send_message(body[:2000])
            return
        await interaction.response.send_message(
            embed=embeds.user_footer(embed, interaction.user)
        )


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(GetCode(bot))
