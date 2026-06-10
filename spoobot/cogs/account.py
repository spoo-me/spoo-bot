from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.ui import embeds, theme
from spoobot.ui.checks import require_link
from spoobot.ui.views import LinkButtonView

if TYPE_CHECKING:
    from spoobot.bot import SpooBot


class Account(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    @app_commands.command(name="link", description="Connect your spoo.me account 🔗")
    async def link(self, interaction: discord.Interaction) -> None:
        auth = self.bot.auth
        existing = await auth.linked_email(interaction.user.id)
        url = await auth.begin_link(
            discord_user_id=interaction.user.id,
            interaction_token=interaction.token,
        )
        if existing:
            title = "Reconnect your spoo.me account"
            desc = (
                f"You're currently linked as **{existing}**. Connecting again replaces "
                "that link (use this if the bot says you have to re-link)."
            )
        else:
            title = "Connect your spoo.me account"
            desc = (
                "Click the button to authorize SpooBot on spoo.me. "
                "This link **expires in 10 minutes** and only works for you.\n\n"
                "*Only ever enter your spoo.me credentials on `spoo.me`.*"
            )
        embed = discord.Embed(title=title, description=desc, color=theme.PRIMARY)
        await interaction.response.send_message(
            embed=embed,
            view=LinkButtonView(url, label="Connect spoo.me account"),
            ephemeral=True,
        )
        # The callback server edits this message in place on success
        # (web/server.py make_interaction_notifier).

    @app_commands.command(name="unlink", description="Disconnect your spoo.me account 🔓")
    @require_link()
    async def unlink(self, interaction: discord.Interaction) -> None:
        await self.bot.auth.unlink(interaction.user.id)
        embed = discord.Embed(
            title="Account disconnected",
            description=(
                "SpooBot forgot your tokens. To fully revoke the bot's grant, "
                "remove **Discord Bot** in your spoo.me dashboard too."
            ),
            color=theme.SUCCESS,
        )
        await interaction.response.send_message(
            embed=embed,
            view=LinkButtonView(self.bot.config.urls.dashboard_apps, label="Open spoo.me dashboard"),
            ephemeral=True,
        )

    @app_commands.command(name="whoami", description="Show the linked spoo.me account 👤")
    @require_link()
    async def whoami(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        profile = await self.bot.auth.authed_call(interaction.user.id, self.bot.spoo.me)
        embed = discord.Embed(title="Linked spoo.me account", color=theme.PRIMARY)
        embed.add_field(name="Email", value=f"```{profile.email}```", inline=False)
        embed.add_field(name="Plan", value=f"```{profile.plan}```", inline=True)
        embed.add_field(name="Verified", value=f"```{profile.email_verified}```", inline=True)
        await interaction.followup.send(embed=embeds.user_footer(embed, interaction.user), ephemeral=True)


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(Account(bot))
