from __future__ import annotations

import io
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.services.models import StatsResult
from spoobot.ui import theme

if TYPE_CHECKING:
    from spoobot.bot import SpooBot

DIMENSIONS = ["browser", "os", "country", "referrer"]


class StatsCog(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    async def fetch(
        self, short_code: str, password: str | None, group_by: list[str]
    ) -> StatsResult:
        return await self.bot.spoo.stats(
            scope="anon",
            short_code=short_code,
            password=password,
            group_by=group_by,
            metrics=["clicks", "unique_clicks"],
        )

    @app_commands.command(name="stats", description="View short URL statistics 📊")
    @app_commands.describe(
        short_code="The short code (the part after spoo.me/)",
        password="Password, if the URL is protected",
    )
    @app_commands.checks.cooldown(5, 60)
    async def stats(
        self,
        interaction: discord.Interaction,
        short_code: str,
        password: str | None = None,
    ) -> None:
        await interaction.response.defer()
        result = await self.fetch(short_code, password, ["time"])

        clicks_by_time = result.series("clicks", "time")
        files: list[discord.File] = []
        if clicks_by_time:
            png = await self.bot.charts.timeseries(
                f"Clicks over time — {short_code}",
                clicks_by_time,
                result.series("unique_clicks", "time") or None,
            )
            files.append(discord.File(io.BytesIO(png), filename="timeline.png"))

        view = StatsOverviewView(
            self,
            short_code=short_code,
            password=password,
            result=result,
            has_chart=bool(files),
            base_url=self.bot.config.spoo.api_base,
            requested_by=interaction.user,
        )
        await interaction.followup.send(view=view, files=files)

    @stats.autocomplete("short_code")
    async def short_code_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Linked users get their own aliases suggested; unlinked get nothing."""
        if await self.bot.vault.get(interaction.user.id) is None:
            return []
        try:
            page = await self.bot.auth.authed_call(
                interaction.user.id,
                lambda t: self.bot.spoo.list_urls(
                    t, page=1, page_size=25, search=current or None
                ),
            )
        except Exception:
            return []
        return [
            app_commands.Choice(name=f"{u.alias} → {u.long_url[:60]}", value=u.alias)
            for u in page.items
        ][:25]


class DimensionRow(discord.ui.ActionRow["StatsOverviewView"]):
    """Dimension picker: replies with a breakdown chart (heatmap for country)."""

    def __init__(self, cog: StatsCog, short_code: str, password: str | None) -> None:
        super().__init__()
        self.cog, self.short_code, self.password = cog, short_code, password

    @discord.ui.select(
        placeholder="Explore a dimension…",
        options=[discord.SelectOption(label=d.title(), value=d) for d in DIMENSIONS],
    )
    async def pick(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        await interaction.response.defer()
        dim = select.values[0]
        result = await self.cog.fetch(self.short_code, self.password, [dim])
        rows = result.series("clicks", dim)
        if dim == "country":
            png = await self.cog.bot.charts.country_heatmap(dict(rows))
        else:
            png = await self.cog.bot.charts.breakdown(
                f"{dim.title()} — {self.short_code}", rows
            )
        gallery_view = ChartGalleryView(
            title=f"{dim.title()} — spoo.me/{self.short_code}", filename=f"{dim}.png"
        )
        await interaction.followup.send(
            view=gallery_view,
            files=[discord.File(io.BytesIO(png), filename=f"{dim}.png")],
        )


class ChartGalleryView(discord.ui.LayoutView):
    """Minimal CV2 wrapper: heading + chart image."""

    def __init__(self, *, title: str, filename: str) -> None:
        super().__init__(timeout=None)
        container = discord.ui.Container(accent_colour=discord.Colour(theme.PRIMARY))
        container.add_item(discord.ui.TextDisplay(f"### {title}"))
        container.add_item(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=f"attachment://{filename}")
            )
        )
        self.add_item(container)


class StatsOverviewView(discord.ui.LayoutView):
    """CV2 stats card: headline numbers + sparkline + timeline chart + explorer."""

    def __init__(
        self,
        cog: StatsCog,
        *,
        short_code: str,
        password: str | None,
        result: StatsResult,
        has_chart: bool,
        base_url: str,
        requested_by: discord.abc.User,
    ) -> None:
        super().__init__(timeout=900)
        s = result.summary
        spark = theme.sparkline([v for _, v in result.series("clicks", "time")][-24:])

        container = discord.ui.Container(accent_colour=discord.Colour(theme.PRIMARY))
        container.add_item(discord.ui.TextDisplay(f"### 📊 spoo.me/{short_code}"))
        headline = f"**{s.total_clicks:,}** clicks  ·  **{s.unique_clicks:,}** unique"
        if spark:
            headline += f"\n`{spark}`  -# last 24 buckets"
        if s.last_click:
            headline += f"\n-# last click: {s.last_click}"
        container.add_item(discord.ui.TextDisplay(headline))
        if has_chart:
            container.add_item(
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(media="attachment://timeline.png")
                )
            )
        container.add_item(discord.ui.Separator())
        container.add_item(DimensionRow(cog, short_code, password))
        link_row = discord.ui.ActionRow()
        link_row.add_item(
            discord.ui.Button(
                label="Full analytics on spoo.me", url=f"{base_url}/stats/{short_code}"
            )
        )
        container.add_item(link_row)
        container.add_item(
            discord.ui.TextDisplay(f"-# Requested by {requested_by.name}")
        )
        self.add_item(container)


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(StatsCog(bot))
