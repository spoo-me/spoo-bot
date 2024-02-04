from utils import *
from discord import app_commands, ui
from discord.ext import commands
from utils_code import *

class genCode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="get-code",
        description="Get the code to use the https://spoo.me API in your preferred language to shorten a URL 🔗",
        )
    @app_commands.guild_only()
    @app_commands.choices(
        language=[
            app_commands.Choice(name="Python-Requests", value="Python-Requests"),
            app_commands.Choice(name="Python-Aiohttp", value="Python-Aiohttp"),
            app_commands.Choice(name="C", value="C"),
            app_commands.Choice(name="C#", value="C#"),
            app_commands.Choice(name="Clojure", value="Clojure"),
            app_commands.Choice(name="Go", value="Go"),
            app_commands.Choice(name="HTTP", value="HTTP"),
            app_commands.Choice(name="Java", value="Java"),
            app_commands.Choice(name="JavaScript-Fetch", value="JavaScript-Fetch"),
            app_commands.Choice(name="JavaScript-XMLHttpRequest", value="JavaScript-XMLHttpRequest"),
            app_commands.Choice(name="Kotlin", value="Kotlin"),
            app_commands.Choice(name="Node.js-Requests", value="Node.js-Requests"),
            app_commands.Choice(name="Node.js-Axios", value="Node.js-Axios"),
            app_commands.Choice(name="Node.js-Unirest", value="Node.js-Unirest"),
            app_commands.Choice(name="PHP", value="PHP"),
            app_commands.Choice(name="R", value="R"),
            app_commands.Choice(name="Ruby", value="Ruby"),
            app_commands.Choice(name="Shell", value="Shell"),
            app_commands.Choice(name="Rust", value="Rust"),
        ],
    )
    @app_commands.describe(
        language="The language of the code",
        url="The URL to shorten",
        alias="The custom alias for the URL",
        max_clicks="The maximum number of clicks for the URL",
        password="The password for the URL",
    )
    async def get_code(self, interaction: discord.Interaction, language:app_commands.Choice[str] , url: str, alias:str = None, max_clicks: int=None, password: str=None):

        await interaction.response.defer()

        code, lang = generate_code_snippet(language.value, url, alias, max_clicks, password)

        soft_errors = []

        if not validate_url(url):
            url = url[:150] + "..." if len(url) > 150 else url
            soft_errors.append(f"- ```'{url}' is not a valid URL, the API might return an error```")
        if alias is not None and not validate_string(alias):
            alias = alias[:150] + "..." if len(alias) > 150 else alias
            soft_errors.append(f"- ```'{alias}' is not a valid alias, the API might return an error```")
        if alias is not None and len(alias) > 15:
            alias = alias[:150] + "..." if len(alias) > 150 else alias
            soft_errors.append(f"- ```'{alias}' is too long, the API will strip it to 15 characters```")
        if password is not None and not validate_password(password):
            password = password[:150] + "..." if len(password) > 150 else password
            soft_errors.append(f"- ```'{password}' is not a valid password, the API might return an error. Password must be atleast 8 characters long, must contain a letter and a number and a special character either '@' or '.' and cannot be consecutive```")

        if len(code) <= 4096:

            embed = discord.Embed(
                title=f"{language.value} code to Use spoo.me's API",
                color=discord.Color.blurple(),
                description=f"```{lang}\n\n{code}\n\n```",
                timestamp=interaction.created_at,
            )

            if len(soft_errors) > 0:
                embed.add_field(name="Soft Warnings", value="\n".join(soft_errors), inline=False)

            try:
                embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
            except:
                embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.default_avatar.url)

            await interaction.followup.send(embed=embed)

        else:
            message = f"## {language.value} Code to use spoo.me's API \n```{lang}\n{code}```"

            if len(soft_errors) > 0:
                message += "\n\nSoft Warnings\n" + "\n".join(soft_errors)

            await interaction.followup.send(message)


    @get_code.error
    async def get_code_error(self, interaction, error):
        if isinstance(error, app_commands.errors.CommandError):
            embed = discord.Embed(
                title="An error occurred",
                description=f"```{error}```",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(genCode(bot))
    print("genCode is loaded")