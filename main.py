import datetime
import os
import random
import statistics
import sys
import time
from discord.app_commands.models import AppCommand
from discord.ext import commands, tasks
import discord
from config import config
from api import keep_alive
from utils import welcome_gifs, commands_, fetch_spoo_stats

start_time = None
latencies = []


class spooBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.bot.command_prefix,
            intents=discord.Intents.all(),
            help_command=None,
        )
        self.synced = False
        self.stats_channel_1 = None  # Will store channel object for total clicks
        self.stats_channel_2 = None  # Will store channel object for total shortlinks

    async def on_ready(self):
        await load()

        global start_time
        start_time = datetime.datetime.now(datetime.UTC)

        await self.wait_until_ready()
        if not self.synced:
            await self.tree.sync()
            try:
                await bot.change_presence(
                    activity=discord.CustomActivity(
                        name="Custom Status",
                        state=config.bot.custom_status,
                    )
                )
                print("Status set to custom status")
            except Exception as e:
                print(f"Error setting custom status: {e}", file=sys.stdout)
            self.synced = True

            # Start the stats update task
            self.update_stats.start()

        print(f"Logged in as {self.user.name} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guilds")

    @tasks.loop(minutes=10)
    async def update_stats(self):
        """Update channel names with current statistics"""
        if not (self.stats_channel_1 and self.stats_channel_2):
            guild = self.get_guild(int(config.discord.ids.parent_server))
            if guild:
                # Get the channels for displaying stats
                self.stats_channel_1: discord.TextChannel | None = guild.get_channel(
                    int(config.discord.ids.channels.stats_clicks)
                )
                self.stats_channel_2: discord.TextChannel | None = guild.get_channel(
                    int(config.discord.ids.channels.stats_shortlinks)
                )

        if self.stats_channel_1 and self.stats_channel_2:
            stats = await fetch_spoo_stats()
            if stats:
                try:
                    await self.stats_channel_1.edit(
                        name=f"📈︱Clicks— {stats['total-clicks']}"
                    )
                    await self.stats_channel_2.edit(
                        name=f"🔗︱Links— {stats['total-shortlinks']}"
                    )
                except Exception as e:
                    print(f"Error updating channel names: {e}", file=sys.stdout)


bot = spooBot()


async def load() -> None:
    for f in os.listdir("cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")


@bot.event
async def on_message(message) -> None:
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if message.type is not discord.MessageType.reply:
            embed = discord.Embed(
                description=config.ui.messages.bot_mention.format(
                    help_cmd_id=config.commands["help"].id
                ),
                color=int(config.ui.colors.primary, 16),
            )
            await message.reply(embed=embed)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(config.discord.ids.channels.welcome))

    embed = discord.Embed(
        title="Welcome to the spoo.me Support Server!",
        description=config.ui.messages.welcome.format(mention=member.mention),
        color=int(config.ui.colors.primary, 16),
        url=config.urls.api_base,
    )

    embed.set_image(url=random.choice(welcome_gifs))

    try:
        embed.set_thumbnail(url=member.avatar.url)
    except Exception:
        embed.set_thumbnail(url=member.default_avatar.url)

    await channel.send(embed=embed)


@bot.command()
@commands.is_owner()
async def sync(ctx) -> None:
    await bot.tree.sync()
    synced: tasks.List[AppCommand] = await bot.tree.sync()
    if len(synced) > 0:
        await ctx.send(f"Successfully Synced {len(synced)} Commands ✔️")
    else:
        await ctx.send("No Slash Commands to Sync :/")


@bot.event
async def on_command_completion(ctx) -> None:
    end: float = time.perf_counter()
    start = ctx.start
    latency = (end - start) * 1000
    latencies.append(latency)
    if len(latencies) > 10:
        latencies.pop(0)


@bot.before_invoke
async def before_invoke(ctx) -> None:
    start = time.perf_counter()
    ctx.start = start


@bot.command()
async def ping(ctx) -> None:
    try:
        embed = discord.Embed(title="Pong!", color=int(config.ui.colors.success, 16))
        message = await ctx.send(embed=embed)

        end: float = time.perf_counter()
        latency = (end - ctx.start) * 1000

        embed.add_field(
            name="Latency", value=f"{bot.latency * 1000:.2f} ms", inline=False
        )
        embed.add_field(name="Message Latency", value=f"{latency:.2f} ms", inline=False)

        if latencies:
            average_ping = statistics.mean(latencies)
            embed.add_field(
                name="Average Ping", value=f"{average_ping:.2f} ms", inline=False
            )

        global start_time
        current_time: datetime.datetime = datetime.datetime.now(datetime.UTC)
        delta: datetime.timedelta = current_time - start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        embed.add_field(
            name="Uptime",
            value=f"{hours} hours {minutes} minutes {seconds} seconds",
            inline=False,
        )
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
        embed.set_thumbnail(url=config.assets.ping_uri)

        await message.edit(embed=embed)

    except Exception as e:
        print(e, file=sys.stdout)


@bot.hybrid_command(
    name="help",
    description=f"{config.commands['help'].description} {config.commands['help'].emoji}",
)
async def help(ctx) -> None:
    user: discord.User | None = bot.get_user(int(config.bot.bot_id))
    profilePicture: str = user.avatar.url

    embed = discord.Embed(
        title="SpooBot Commands",
        description="Here is the list of the available commands:",
        color=int(config.ui.colors.primary, 16),
        timestamp=ctx.message.created_at,
    )

    embed.set_thumbnail(url=profilePicture)
    for cmd_name, cmd_help in commands_.items():
        embed.add_field(name=cmd_name, value=cmd_help, inline=False)

    try:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="invite",
    description="Get the invite link for the bot 💌",
)
async def invite(ctx) -> None:
    embed = discord.Embed(
        title="Invite SpooBot to your server!",
        description=f"Click [here]({config.urls.bot_invite}) to invite SpooBot to your server!",
        color=int(config.ui.colors.warning, 16),
        timestamp=ctx.message.created_at,
    )

    try:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="bot-stats",
    description=f"{config.commands['bot_stats'].description} {config.commands['bot_stats'].emoji}",
)
async def stats(ctx) -> None:
    global start_time

    current_time: datetime.datetime = datetime.datetime.now(datetime.UTC)
    delta: datetime.timedelta = current_time - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="SpooBot Stats",
        description="Here are the stats of the bot:",
        color=int(config.ui.colors.primary, 16),
        timestamp=ctx.message.created_at,
    )

    embed.add_field(name="Servers", value=f"```{len(bot.guilds)}```", inline=True)
    embed.add_field(name="Users", value=f"```{len(bot.users)}```", inline=True)
    embed.add_field(
        name="Uptime",
        value=f"```{hours} hours {minutes} minutes {seconds} seconds```",
        inline=False,
    )
    embed.add_field(
        name="Command Prefix", value=f"```{config.bot.command_prefix}```", inline=True
    )
    embed.add_field(name="Total Commands", value=f"```{len(commands_)}```", inline=True)

    try:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="support",
    description="Join the Support Server of the bot 🛠️",
)
async def support(ctx) -> None:
    embed = discord.Embed(
        title="Join the SpooBot Support Server!",
        description=f"Click {config.urls.discord_invite} to join the support server for SpooBot!",
        color=int(config.ui.colors.warning, 16),
        timestamp=ctx.message.created_at,
    )

    try:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="about",
    description="View information about the bot 🤖",
)
async def about(ctx) -> None:
    embed = discord.Embed(
        title="About SpooBot 🙌",
        description=f"```{config.bot.description}```",
        color=int(config.ui.colors.info, 16),
        url=config.urls.api_base,
        timestamp=ctx.message.created_at,
    )

    embed.add_field(
        name="What service does SpooBot use? 🌐",
        value="```SpooBot uses the spoo.me URL shortening service to shorten URLs. spoo.me is a fast, reliable, and secure URL shortening service that allows you to shorten URLs with ease. 🚀```",
        inline=False,
    )
    embed.add_field(
        name="Where can I find the source code? 💻",
        value="```You can find the source code for SpooBot on GitHub. 🌟```",
        inline=False,
    )
    embed.add_field(
        name="Who made SpooBot? 👥",
        value="```SpooBot was made by the devs of spoo.me. 🙏```",
        inline=False,
    )

    stats = await fetch_spoo_stats()
    if stats:
        embed.add_field(
            name="Total Shortlinks 🔗",
            value=f"```{stats['total-shortlinks']}```",
            inline=True,
        )
        embed.add_field(
            name="Total Clicks 📈",
            value=f"```{stats['total-clicks']}```",
            inline=True,
        )

    user: discord.User | None = bot.get_user(int(config.bot.bot_id))
    embed.set_thumbnail(url=user.avatar.url)

    try:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Information requested by: {ctx.author.name}",
            icon_url=ctx.author.default_avatar.url,
        )

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="View Source Code",
            url=config.urls.github,
            style=discord.ButtonStyle.link,
            emoji=f"<:git:{config.bot.emojis.git}>",
        )
    )
    view.add_item(
        discord.ui.Button(
            label="View Website",
            url=config.urls.api_base,
            style=discord.ButtonStyle.link,
            emoji=f"<:spoo:{config.bot.emojis.spoo}>",
        )
    )

    await ctx.send(embed=embed, view=view)


if __name__ == "__main__":
    if (
        config.server.environment != "development"
        and config.server.is_cloud_hosted
        and config.server.keep_alive.enabled
    ):
        keep_alive()
    bot.run(token=config.bot.bot_token)
