import discord
from discord import app_commands
from discord.ext import commands
from utils import shortener, generate_error_message, generate_command_error_embed
from config import BotEmojis, SocialShareUrls, config


class shortenUrl(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    class buttonView(discord.ui.View):
        def __init__(self, short_code) -> None:
            super().__init__(timeout=None)
            base_url: str = config.urls.api_base
            social: SocialShareUrls = config.urls.social_share
            emojis: BotEmojis = config.bot.emojis

            stats_button = discord.ui.Button(
                label="View Statistics", url=f"{base_url}/stats/{short_code}"
            )
            tweet_button = discord.ui.Button(
                url=f"{social.twitter}{base_url}/{short_code}",
                emoji=f"<:twitter:{emojis.twitter}>",
            )
            facebook_button = discord.ui.Button(
                url=f"{social.facebook}{base_url}/{short_code}",
                emoji=f"<:facebook:{emojis.facebook}>",
            )
            telegram_button = discord.ui.Button(
                url=f"{social.telegram}{base_url}/{short_code}",
                emoji=f"<:telegram:{emojis.telegram}>",
            )
            whatsapp_button = discord.ui.Button(
                url=f"{social.whatsapp}{base_url}/{short_code}",
                emoji=f"<:whatsapp:{emojis.whatsapp}>",
            )
            reddit_button = discord.ui.Button(
                url=f"{social.reddit}{base_url}/{short_code}",
                emoji=f"<:reddit:{emojis.reddit}>",
            )
            snapchat_button = discord.ui.Button(
                url=f"{social.snapchat}{base_url}/{short_code}",
                emoji=f"<:snapchat:{emojis.snapchat}>",
            )

            self.add_item(stats_button)
            self.add_item(tweet_button)
            self.add_item(facebook_button)
            self.add_item(telegram_button)
            self.add_item(whatsapp_button)
            self.add_item(reddit_button)
            self.add_item(snapchat_button)

    @app_commands.command(
        name="shorten",
        description=f"{config.commands['shorten'].description} {config.commands['shorten'].emoji}",
    )
    @app_commands.describe(
        **{
            param.name: f"{param.description}"
            for param in config.commands["shorten"].parameters
        }
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(
        config.cooldowns.short_term.count, config.cooldowns.short_term.seconds
    )
    @app_commands.checks.cooldown(
        config.cooldowns.medium_term.count, config.cooldowns.medium_term.seconds
    )
    @app_commands.checks.cooldown(
        config.cooldowns.long_term.count, config.cooldowns.long_term.seconds
    )
    async def shorten(
        self,
        interaction: discord.Interaction,
        url: str,
        alias: str = None,
        max_clicks: int = None,
        password: str = None,
    ) -> None:
        await interaction.response.defer()

        result = shortener.shorten(
            url, alias=alias, max_clicks=max_clicks, password=password
        )

        embed = discord.Embed(
            title="URL Shortened Successfully!",
            description=f"You can also view the statistics page of the shortened url by clicking the button below or you can also use the command </stats:{config.commands['stats'].id}> to view the statistics.",
            color=int(config.ui.colors.primary, 16),
            timestamp=interaction.created_at,
        )

        embed.set_thumbnail(
            url=f"https://qr.spoo.me/gradient?text={result}&gradient1=(117,129,86)&gradient2=(103,175,38)"
        )

        embed.add_field(name="Shortened URL", value=f"```{result}```", inline=False)
        embed.add_field(name="Original URL", value=f"```{url}```", inline=False)

        try:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except Exception:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        short_code = result.split("/")[-1]
        await interaction.followup.send(embed=embed, view=self.buttonView(short_code))

    @app_commands.command(
        name="emojify",
        description=f"{config.commands['emojify'].description} {config.commands['emojify'].emoji}",
    )
    @app_commands.describe(
        **{
            param.name: f"{param.description}"
            for param in config.commands["emojify"].parameters
        }
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(
        config.cooldowns.short_term.count, config.cooldowns.short_term.seconds
    )
    @app_commands.checks.cooldown(
        config.cooldowns.medium_term.count, config.cooldowns.medium_term.seconds
    )
    @app_commands.checks.cooldown(
        config.cooldowns.long_term.count, config.cooldowns.long_term.seconds
    )
    async def emojify(
        self,
        interaction,
        url: str,
        emojies: str = None,
        max_clicks: int = None,
        password: str = None,
    ) -> None:
        await interaction.response.defer()

        result = shortener.emojify(
            url, emoji_alias=emojies, max_clicks=max_clicks, password=password
        )

        embed = discord.Embed(
            title="URL Shortened Successfully!",
            description=f"You can also view the statistics page of the shortened url by clicking the button below or you can also use the command </stats:{config.commands['stats'].id}> to view the statistics.",
            color=int(config.ui.colors.primary, 16),
            timestamp=interaction.created_at,
        )

        embed.set_thumbnail(
            url=f"https://qr.spoo.me/gradient?text={result}&gradient1=(117,129,86)&gradient2=(103,175,38)"
        )

        embed.add_field(name="Shortened URL", value=f"```{result}```", inline=False)
        embed.add_field(name="Original URL", value=f"```{url}```", inline=False)

        try:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except Exception:
            embed.set_footer(
                text=f"Shortened by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        short_code: str = result.split("/")[-1]
        await interaction.followup.send(embed=embed, view=self.buttonView(short_code))

    @shorten.error
    async def shorten_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(
                interaction,
                error,
                cooldown_configuration=[
                    f"- ```{config.cooldowns.short_term.count} time every {config.cooldowns.short_term.seconds} seconds```",
                    f"- ```{config.cooldowns.medium_term.count} time every {config.cooldowns.medium_term.seconds} seconds```",
                    f"- ```{config.cooldowns.long_term.count} time every {config.cooldowns.long_term.seconds} seconds```",
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "shorten")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @emojify.error
    async def emoji_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(
                interaction,
                error,
                cooldown_configuration=[
                    f"- ```{config.cooldowns.short_term.count} time every {config.cooldowns.short_term.seconds} seconds```",
                    f"- ```{config.cooldowns.medium_term.count} time every {config.cooldowns.medium_term.seconds} seconds```",
                    f"- ```{config.cooldowns.long_term.count} time every {config.cooldowns.long_term.seconds} seconds```",
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "emojify")
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(shortenUrl(bot))
    print(f"Loaded {shortenUrl.__name__}")
