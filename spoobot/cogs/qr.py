from __future__ import annotations

import io
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.ui import embeds, theme

if TYPE_CHECKING:
    from spoobot.bot import SpooBot


class QrCog(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    @app_commands.command(name="qr", description="Generate a QR code 🔳")
    @app_commands.describe(
        content="URL or text to encode",
        style="QR style",
        color="Foreground color (hex or name, classic style only)",
    )
    @app_commands.choices(style=[
        app_commands.Choice(name="Gradient (brand)", value="gradient"),
        app_commands.Choice(name="Classic", value="classic"),
    ])
    async def qr(
        self,
        interaction: discord.Interaction,
        content: str,
        style: app_commands.Choice[str] | None = None,
        color: str = "black",
    ) -> None:
        await interaction.response.defer()
        chosen = style.value if style else "gradient"
        if chosen == "gradient":
            png = await self.bot.qr.gradient(content, start="#497dff", end="#7289da")
        else:
            png = await self.bot.qr.classic(content, color=color)
        embed = discord.Embed(title="Your QR code", color=theme.PRIMARY)
        embed.set_image(url="attachment://qr.png")
        await interaction.followup.send(
            embed=embeds.user_footer(embed, interaction.user),
            file=discord.File(io.BytesIO(png), filename="qr.png"),
        )


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(QrCog(bot))
