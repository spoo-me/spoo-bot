from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.ui import embeds, theme
from spoobot.ui.views import LinkButtonView

if TYPE_CHECKING:
    from spoobot.bot import SpooBot


class Meta(commands.Cog):
    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot
        self.started_at = datetime.datetime.now(datetime.UTC)

    def _uptime(self) -> str:
        delta = datetime.datetime.now(datetime.UTC) - self.started_at
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours}h {minutes}m {seconds}s"

    @commands.hybrid_command(name="help", description="See the list of commands ❔")
    async def help(self, ctx: commands.Context[SpooBot]) -> None:
        lines: list[str] = []
        for c in sorted(self.bot.tree.get_commands(), key=lambda c: c.name):
            desc = (
                c.description
                if isinstance(c, (app_commands.Command, app_commands.Group))
                else ""
            )
            lines.append(f"**/{c.qualified_name}** — {desc}")
        embed = discord.Embed(
            title="SpooBot Commands",
            description="\n".join(lines),
            color=theme.PRIMARY,
        )
        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embeds.user_footer(embed, ctx.author))

    @commands.hybrid_command(
        name="invite", description="Invite SpooBot to your server 💌"
    )
    async def invite(self, ctx: commands.Context[SpooBot]) -> None:
        cfg = self.bot.config
        embed = discord.Embed(
            title="Invite SpooBot!",
            description=f"[Click here]({cfg.urls.bot_invite}) to add SpooBot to your server.",
            color=theme.WARNING,
        )
        await ctx.send(embed=embeds.user_footer(embed, ctx.author))

    @commands.hybrid_command(name="support", description="Join the support server 📞")
    async def support(self, ctx: commands.Context[SpooBot]) -> None:
        cfg = self.bot.config
        embed = discord.Embed(
            title="Join the SpooBot Support Server!",
            description=f"Click {cfg.urls.discord_invite} to join.",
            color=theme.WARNING,
        )
        await ctx.send(embed=embeds.user_footer(embed, ctx.author))

    @commands.hybrid_command(name="about", description="About SpooBot ℹ️")
    async def about(self, ctx: commands.Context[SpooBot]) -> None:
        cfg = self.bot.config
        embed = discord.Embed(
            title="About SpooBot 🙌",
            description="The official Discord bot for spoo.me — shorten, manage, and track links without leaving Discord.",
            color=theme.PRIMARY,
            url=cfg.spoo.api_base,
        )
        metrics = await self.bot.spoo.site_metrics()
        embed.add_field(
            name="Total Shortlinks 🔗",
            value=f"```{metrics.total_shortlinks:,}```",
            inline=True,
        )
        embed.add_field(
            name="Total Clicks 📈", value=f"```{metrics.total_clicks:,}```", inline=True
        )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Source Code", url=cfg.urls.github))
        view.add_item(discord.ui.Button(label="Website", url=cfg.spoo.api_base))
        await ctx.send(embed=embeds.user_footer(embed, ctx.author), view=view)

    @commands.hybrid_command(name="bot-stats", description="Bot statistics 🤖")
    async def botstats(self, ctx: commands.Context[SpooBot]) -> None:
        embed = discord.Embed(title="SpooBot Stats", color=theme.PRIMARY)
        embed.add_field(
            name="Servers", value=f"```{len(self.bot.guilds)}```", inline=True
        )
        embed.add_field(
            name="Users",
            value=f"```{sum(g.member_count or 0 for g in self.bot.guilds):,}```",
            inline=True,
        )
        embed.add_field(name="Uptime", value=f"```{self._uptime()}```", inline=False)
        embed.add_field(
            name="Gateway Latency",
            value=f"```{self.bot.latency * 1000:.0f} ms```",
            inline=True,
        )
        await ctx.send(embed=embeds.user_footer(embed, ctx.author))

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context[SpooBot]) -> None:
        embed = discord.Embed(title="Pong!", color=theme.SUCCESS)
        embed.add_field(
            name="Gateway Latency",
            value=f"{self.bot.latency * 1000:.2f} ms",
            inline=False,
        )
        embed.add_field(name="Uptime", value=self._uptime(), inline=False)
        await ctx.send(embed=embeds.user_footer(embed, ctx.author))

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context[SpooBot]) -> None:
        synced = await self.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands ✔️")

    @commands.command(name="link-required-preview")
    @commands.is_owner()
    async def link_required_preview(self, ctx: commands.Context[SpooBot]) -> None:
        """Owner utility: preview the not-linked embed without unlinking."""
        await ctx.send(
            embed=embeds.not_linked_embed(),
            view=LinkButtonView(self.bot.config.spoo.api_base, label="spoo.me"),
        )


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(Meta(bot))
