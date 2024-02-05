from utils import *
from discord import app_commands, ui
from discord.ext import commands


class shortenUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class buttonView(discord.ui.View):
        def __init__(self, short_code):
            super().__init__(timeout=None)

            stats_button = discord.ui.Button(label="View Statistics", url=f"https://spoo.me/stats/{short_code}")
            tweet_button = discord.ui.Button(url=f"https://twitter.com/intent/tweet?url=https://spoo.me/{short_code}", emoji="<:twitter:1203389152712724581>")
            facebook_button = discord.ui.Button(url=f"https://www.facebook.com/sharer/sharer.php?u=https://spoo.me/{short_code}", emoji="<:facebook:1203389150028369970>")
            telegram_button = discord.ui.Button(url=f"https://t.me/share/url?url=https://spoo.me/{short_code}", emoji="<:telegram:1203389144756391966>")
            whatsapp_button = discord.ui.Button(url=f"https://wa.me/?text=https://spoo.me/{short_code}", emoji="<:whatsapp:1203389130428518460>")
            reddit_button = discord.ui.Button(url=f"https://www.reddit.com/submit?url=https://spoo.me/{short_code}", emoji="<:reddit:1203389126100131910>")
            snapchat_button = discord.ui.Button(url=f"https://www.snapchat.com/scan?attachmentUrl=https://spoo.me/{short_code}", emoji="<:snapchat:1203389123784609812>")

            self.add_item(stats_button)
            self.add_item(tweet_button)
            self.add_item(facebook_button)
            self.add_item(telegram_button)
            self.add_item(whatsapp_button)
            self.add_item(reddit_button)
            self.add_item(snapchat_button)

    @app_commands.command(
        name="shorten",
        description="Shorten a Long URL 🤏🏻",
    )
    @app_commands.describe(
            url="The URL to shorten",
            alias="The custom alias for the URL",
            max_clicks="The maximum number of clicks for the URL",
            password="The password for the URL",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10.0)
    @app_commands.checks.cooldown(5, 60.0)
    @app_commands.checks.cooldown(200, 24*60*60.0)
    async def shorten(self, interaction: discord.Interaction, url: str, alias:str = None, max_clicks: int=None, password: str=None ):

        await interaction.response.defer()

        result = shortener.shorten(url, alias=alias, max_clicks=max_clicks, password=password)

        embed = discord.Embed(
            title="URL Shortened Successfully!",
            description="You can also view the statistics page of the shortened url by clicking the button below or you can also use the command </stats:1202895069628203048> to view the statistics.",
            color=discord.Color.blurple(),
            timestamp=interaction.created_at,
        )

        embed.set_thumbnail(url=f"https://qr.spoo.me/gradient?text={result}&gradient1=(117,129,86)&gradient2=(103,175,38)")

        embed.add_field(name="Shortened URL", value=f"```{result}```", inline=False)
        embed.add_field(name="Original URL", value=f"```{url}```", inline=False)

        try:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        short_code = result.split("/")[-1]

        await interaction.followup.send(embed=embed, view=self.buttonView(short_code))


    @app_commands.command(
        name="emojify",
        description="Convert Long Urls to Emojis 😉"
    )
    @app_commands.describe(
        url="The URL to emojify",
        emojies="Custom Emoji Sequence you want your short url to be",
        max_clicks="The maximum number of clicks for the URL",
        password="The password for the URL",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10.0)
    @app_commands.checks.cooldown(5, 60.0)
    @app_commands.checks.cooldown(200, 24*60*60.0)
    async def emojify(self, interaction, url: str, emojies: str = None, max_clicks: int = None, password: str = None):

        await interaction.response.defer()

        result = shortener.emojify(url, emoji_alias=emojies, max_clicks=max_clicks, password=password)

        embed = discord.Embed(
            title="URL Shortened Successfully!",
            description="You can also view the statistics page of the shortened url by clicking the button below or you can also use the command </stats:1202895069628203048> to view the statistics.",
            color=discord.Color.blurple(),
            timestamp=interaction.created_at,
        )

        embed.set_thumbnail(url=f"https://qr.spoo.me/gradient?text={result}&gradient1=(117,129,86)&gradient2=(103,175,38)")

        embed.add_field(name="Shortened URL", value=f"```{result}```", inline=False)
        embed.add_field(name="Original URL", value=f"```{url}```", inline=False)

        try:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        short_code = result.split("/")[-1]

        await interaction.followup.send(embed=embed, view=self.buttonView(short_code))


    @shorten.error
    async def shorten_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(interaction, error)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "shorten")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @emojify.error
    async def emoji_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(interaction, error)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "emojify")
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(shortenUrl(bot))
    print("Loaded shortenUrl")