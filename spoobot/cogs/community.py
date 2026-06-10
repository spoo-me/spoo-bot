from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

from spoobot.infrastructure.logging import get_logger
from spoobot.ui import theme

if TYPE_CHECKING:
    from spoobot.bot import SpooBot

log = get_logger(__name__)


class Community(commands.Cog):
    """Parent-server niceties: welcome messages, mention reply, stats channels."""

    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot
        self.update_stats.start()

    async def cog_unload(self) -> None:
        self.update_stats.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        cfg = self.bot.config
        if not cfg.channels.welcome:
            return
        channel = self.bot.get_channel(int(cfg.channels.welcome))
        if not isinstance(channel, discord.TextChannel):
            return
        if member.guild.id != int(cfg.bot.parent_server_id or 0):
            return
        embed = discord.Embed(
            title="Welcome to the spoo.me Support Server!",
            description=f"Hey {member.mention}! Welcome to the support server for spoo.me 🎉",
            color=theme.PRIMARY,
        )
        embed.set_thumbnail(url=(member.avatar or member.default_avatar).url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if (
            self.bot.user in message.mentions
            and message.type is not discord.MessageType.reply
        ):
            embed = discord.Embed(
                description="Hello! I'm SpooBot — I make your URLs spoo-tacular 😎\nUse **/help** to see what I can do.",
                color=theme.PRIMARY,
            )
            await message.reply(embed=embed)

    @tasks.loop(minutes=10)
    async def update_stats(self) -> None:
        cfg = self.bot.config
        if not (cfg.channels.stats_clicks and cfg.channels.stats_shortlinks):
            return
        try:
            metrics = await self.bot.spoo.site_metrics()
        except Exception:
            log.warning("site metrics fetch failed", exc_info=True)
            return
        for channel_id, name in (
            (cfg.channels.stats_clicks, f"📈︱Clicks— {metrics.total_clicks:,}"),
            (cfg.channels.stats_shortlinks, f"🔗︱Links— {metrics.total_shortlinks:,}"),
        ):
            channel = self.bot.get_channel(int(channel_id))
            if isinstance(
                channel,
                (discord.TextChannel, discord.VoiceChannel, discord.StageChannel),
            ):
                try:
                    await channel.edit(name=name)
                except discord.HTTPException:
                    log.warning("stats channel rename failed channel=%s", channel_id)

    @update_stats.before_loop
    async def before_update_stats(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(Community(bot))
