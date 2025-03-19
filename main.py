import datetime
import os
import random
import statistics
import sys
import time
import aiohttp
from discord.ext import commands, tasks
import discord
from constants import TOKEN
from api import keep_alive
from utils import welcome_gifs, commands_

start_time = None
latencies = []


class spooBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$", intents=discord.Intents.all(), help_command=None
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
            await bot.change_presence(
                activity=discord.CustomActivity(
                    name="Custom Status",
                    state="Shorten your URLs, not your possibilities.",
                )
            )
            self.synced = True

            # Start the stats update task
            self.update_stats.start()

        try:
            file = r"assets\\pfp-animated.gif"
            with open(file, "rb") as avatar:
                await self.user.edit(avatar=avatar.read())
                print("Applied Animated Avatar")
        except Exception as e:
            print(e, file=sys.stdout)
            pass

        print(f"Logged in as {self.user.name} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guilds")

    async def fetch_spoo_stats(self):
        """Fetch statistics from spoo.me API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://spoo.me/metric") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Error fetching stats: {e}", file=sys.stdout)
        return None

    @tasks.loop(minutes=10)
    async def update_stats(self):
        """Update channel names with current statistics"""
        if not (self.stats_channel_1 and self.stats_channel_2):
            guild = self.get_guild(1192388005206433892)  # Parent server ID
            if guild:
                # Get the channels for displaying stats
                self.stats_channel_1 = guild.get_channel(
                    1351907108190162944
                )  # Total clicks channel
                self.stats_channel_2 = guild.get_channel(
                    1351907592380612608
                )  # Total shortlinks channel

        if self.stats_channel_1 and self.stats_channel_2:
            stats = await self.fetch_spoo_stats()
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


async def load():
    for f in os.listdir("cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if message.type is not discord.MessageType.reply:
            embed = discord.Embed(
                description="Hello, I am the SpooBot. I am a URL shortener bot that makes your URLs spoo-tacular! 😎\nType </help:1202746904203759646> to see the list of commands I can do for you!",
                color=discord.Color.og_blurple(),
            )

            await message.reply(embed=embed)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1192388005206433894)

    embed = discord.Embed(
        title="Welcome to the spoo.me Support Server!",
        description=f"Hey {member.mention}! Welcome to the support server for spoo.me, the best URL shortener out there! We hope you enjoy your stay here!",
        color=discord.Color.blurple(),
        url="https://spoo.me",
    )

    embed.set_image(url=random.choice(welcome_gifs))

    try:
        embed.set_thumbnail(url=member.avatar.url)
    except Exception:
        embed.set_thumbnail(url=member.default_avatar.url)

    await channel.send(embed=embed)


@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    synced = await bot.tree.sync()
    if len(synced) > 0:
        await ctx.send(f"Successfully Synced {len(synced)} Commands ✔️")
    else:
        await ctx.send("No Slash Commands to Sync :/")


@bot.event
async def on_command_completion(ctx):
    end = time.perf_counter()
    start = ctx.start
    latency = (end - start) * 1000
    latencies.append(latency)
    if len(latencies) > 10:
        latencies.pop(0)


@bot.before_invoke
async def before_invoke(ctx):
    start = time.perf_counter()
    ctx.start = start


@bot.command()
async def ping(ctx):
    try:
        embed = discord.Embed(title="Pong!", color=discord.Color.green())
        message = await ctx.send(embed=embed)

        end = time.perf_counter()

        latency = (end - ctx.start) * 1000

        embed.add_field(
            name="Latency", value=f"{bot.latency * 1000:.2f} ms", inline=False
        )

        embed.add_field(name="Message Latency", value=f"{latency:.2f} ms", inline=False)

        # Calculate the average ping of the bot in the last 10 minutes
        if latencies:
            average_ping = statistics.mean(latencies)
            embed.add_field(
                name="Average Ping", value=f"{average_ping:.2f} ms", inline=False
            )

        global start_time

        current_time = datetime.datetime.now(datetime.UTC)
        delta = current_time - start_time

        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        embed.add_field(
            name="Uptime",
            value=f"{hours} hours {minutes} minutes {seconds} seconds",
            inline=False,
        )
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
        embed.set_thumbnail(
            url="https://uploads.poxipage.com/7q5iw7dwl5jc3zdjaergjhpat27tws8bkr9fgy45_938843265627717703-webp"
        )

        await message.edit(embed=embed)

    except Exception as e:
        print(e, file=sys.stdout)


@bot.hybrid_command(name="help", description="View the various commands of this bot 📃")
async def help(ctx):
    user = bot.get_user(1202738385194717205)
    profilePicture = user.avatar.url

    embed = discord.Embed(
        title="SpooBot Commands",
        description="Here is the list of the available commands:",
        color=discord.Color.blurple(),
        timestamp=ctx.message.created_at,
    )

    embed.set_thumbnail(url=profilePicture)
    for i in commands_.keys():
        embed.add_field(name=i, value=commands_[i], inline=False)

    try:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="invite",
    description="Get the invite link for the bot 💌",
)
async def invite(ctx):
    embed = discord.Embed(
        title="Invite SpooBot to your server!",
        description="Click [here](https://discord.com/api/oauth2/authorize?client_id=1202738385194717205&permissions=9242837113920&scope=bot) to invite SpooBot to your server!",
        color=discord.Color.orange(),
        timestamp=ctx.message.created_at,
    )

    try:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="bot-stats",
    description="View the stats of the bot 👀",
)
async def stats(ctx):
    global start_time

    current_time = datetime.datetime.now(datetime.UTC)
    delta = current_time - start_time

    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="SpooBot Stats",
        description="Here are the stats of the bot:",
        color=discord.Color.og_blurple(),
        timestamp=ctx.message.created_at,
    )

    embed.add_field(name="Servers", value=f"```{len(bot.guilds)}```", inline=True)
    embed.add_field(name="Users", value=f"```{len(bot.users)}```", inline=True)

    embed.add_field(
        name="Uptime",
        value=f"```{hours} hours {minutes} minutes {seconds} seconds```",
        inline=False,
    )

    embed.add_field(name="Command Prefix", value="``` $ ```", inline=True)
    embed.add_field(name="Total Commands", value=f"```{len(commands_)}```", inline=True)

    try:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="support",
    description="Join the Support Server of the bot 🛠️",
)
async def support(ctx):
    embed = discord.Embed(
        title="Join the SpooBot Support Server!",
        description="Click https://spoo.me/discord to join the support server for SpooBot!",
        color=discord.Color.gold(),
        timestamp=ctx.message.created_at,
    )

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/1192388005206433892/461edd6dd7b92f24a94505fe3a660f91.webp?size=1024&format=webp&width=0&height=320"
    )

    try:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.default_avatar.url,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="about",
    description="View information about the bot 🤖",
)
async def about(ctx):
    embed = discord.Embed(
        title="About SpooBot 🙌",
        description="```SpooBot is a URL shortener bot that makes your URLs spoo-tacular! 🎉 It is a bot that saves you time and hassle by shortening URLs for you, so you can focus on more important things! 😎\nBut wait, there's more! SpooBot also lets you view all your URL statistics from this bot, so you can track how many clicks, views, and visits your URLs get! 📈\nSpooBot is the ultimate URL shortener bot that you need in your life! 😍```",
        color=discord.Color.greyple(),
        url="https://spoo.me",
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

    user = bot.get_user(1202738385194717205)
    embed.set_thumbnail(url=user.avatar.url)

    try:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.avatar.url,
        )
    except Exception:
        embed.set_footer(
            text="Information requested by: {}".format(ctx.author.name),
            icon_url=ctx.author.default_avatar.url,
        )

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="View Source Code",
            url="https://github.com/spoo-me/spoo-bot",
            style=discord.ButtonStyle.link,
            emoji="<:git:1203429172903542835>",
        )
    )
    view.add_item(
        discord.ui.Button(
            label="View Website",
            url="https://spoo.me",
            style=discord.ButtonStyle.link,
            emoji="<:spoo:1203429402071797760>",
        )
    )

    await ctx.send(embed=embed, view=view)


if __name__ == "__main__":
    keep_alive()
    bot.run(token=TOKEN)
