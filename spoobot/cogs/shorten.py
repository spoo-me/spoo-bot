from __future__ import annotations

import urllib.parse
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.errors import NotLinkedError
from spoobot.services.models import ShortUrl
from spoobot.ui import theme
from spoobot.ui.views import ShortenResultView

if TYPE_CHECKING:
    from spoobot.bot import SpooBot


class Shorten(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    def _qr_url(self, short_url: str) -> str:
        g1, g2 = theme.BRAND_QR_GRADIENT
        return (
            f"{self.bot.config.spoo.qr_api_base}/gradient"
            f"?text={urllib.parse.quote(short_url, safe='')}&gradient1={g1}&gradient2={g2}"
        )

    def _result_view(
        self, interaction: discord.Interaction, result: ShortUrl, *, owned: bool
    ) -> ShortenResultView:
        cfg = self.bot.config
        return ShortenResultView(
            result,
            owned=owned,
            base_url=cfg.spoo.api_base,
            qr_url=self._qr_url(result.short_url),
            emojis=cfg.emojis.model_dump(),
            requested_by=interaction.user,
        )

    async def _shorten_two_tier(
        self,
        user_id: int,
        *,
        long_url: str,
        alias: str | None,
        max_clicks: int | None,
        password: str | None,
    ) -> tuple[ShortUrl, bool]:
        """Linked → owned link; unlinked → anon link. Returns (result, owned)."""
        try:
            result = await self.bot.auth.authed_call(
                user_id,
                lambda token: self.bot.spoo.shorten(
                    long_url,
                    alias=alias,
                    max_clicks=max_clicks,
                    password=password,
                    token=token,
                ),
            )
            return result, True
        except NotLinkedError:
            result = await self.bot.spoo.shorten(
                long_url, alias=alias, max_clicks=max_clicks, password=password
            )
            return result, False

    @app_commands.command(name="shorten", description="Shorten a long URL 🤏🏻")
    @app_commands.describe(
        url="The url you want to shorten",
        alias="Custom alias for the short url",
        max_clicks="Maximum clicks before the url expires",
        password="Password-protect the short url",
    )
    @app_commands.checks.cooldown(1, 10)
    @app_commands.checks.cooldown(5, 60)
    @app_commands.checks.cooldown(200, 86400)
    async def shorten(
        self,
        interaction: discord.Interaction,
        url: str,
        alias: str | None = None,
        max_clicks: app_commands.Range[int, 1] | None = None,
        password: str | None = None,
    ) -> None:
        await interaction.response.defer()
        result, owned = await self._shorten_two_tier(
            interaction.user.id,
            long_url=url,
            alias=alias,
            max_clicks=max_clicks,
            password=password,
        )
        await interaction.followup.send(
            view=self._result_view(interaction, result, owned=owned)
        )

    @app_commands.command(name="emojify", description="Convert long URLs to emojis 😉")
    @app_commands.describe(
        url="The url you want to emojify",
        emojies="Custom emoji sequence for the short url",
        max_clicks="Maximum clicks before the url expires",
        password="Password-protect the short url",
    )
    @app_commands.checks.cooldown(1, 10)
    @app_commands.checks.cooldown(5, 60)
    @app_commands.checks.cooldown(200, 86400)
    async def emojify(
        self,
        interaction: discord.Interaction,
        url: str,
        emojies: str | None = None,
        max_clicks: app_commands.Range[int, 1] | None = None,
        password: str | None = None,
    ) -> None:
        await interaction.response.defer()
        # LEGACY route — always anonymous (see SpooClient.emojify docstring).
        result = await self.bot.spoo.emojify(
            url, emojies=emojies, max_clicks=max_clicks, password=password
        )
        await interaction.followup.send(
            view=self._result_view(interaction, result, owned=False)
        )


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(Shorten(bot))
