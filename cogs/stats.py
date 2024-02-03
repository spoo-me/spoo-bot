from utils import *
from discord import app_commands, ui
from discord.ext import commands
import json

class StatsSelectView(discord.ui.View):
    def __init__(self, stats:Statistics):
        super().__init__(timeout=None)
        self.stats = stats

    @discord.ui.select(
        placeholder="➕ Additional Statistics Chart",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Platforms Analysis", description="Generate a chart for platforms analysis trend", emoji="📱", value="Platform Analysis 📱"),
            discord.SelectOption(label="Browsers Analysis", description="Generate a chart for browsers analysis trend", emoji="🌐", value="Browser Analysis 🌐"),
            discord.SelectOption(label="Referrers Analysis", description="Generate a chart for referrers analysis trend", emoji="🔗", value="Referrers Analysis 🔗"),
            discord.SelectOption(label="Countries Heatmap", description="Generate a heatmap for countries analysis trend", emoji="🔥", value="Countries Heatmap 🔥"),
            discord.SelectOption(label="Unique Countries Heatmap", description="Generate a heatmap for unique countries analysis trend", emoji="🌍", value="Unique Countries Heatmap 🌍"),
            discord.SelectOption(label="Clicks Over Time", description="Generate a chart for clicks over time for the last 30 days", emoji="📈", value="Clicks Over Time 📈"),
        ]
    )
    async def analysis_chart_callback(self, interaction:discord.Interaction, select:discord.ui.Select):

        await interaction.response.defer()

        if select.values[0] == "Platform Analysis 📱":
            resp = generate_chart(data=[self.stats.platforms_analysis, self.stats.unique_platforms_analysis], backgrounds=[["rgba(0, 0, 255, 0.15)", "rgb(0, 0, 255)"], ["rgba(255, 69, 0, 0.15)", "rgb(255, 69, 0)"]], labels=["Clicks", "Unique Clicks"], title="Platforms Analysis Chart", type="bar")

            embed = discord.Embed(
                title="Platforms Analysis Chart 📱",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This chart shows the trend of platforms used to access the URL",
            )

            embed.set_image(url=resp["url"])

            platform_data = json.dumps(self.stats.platforms_analysis)
            unique_platform_data = json.dumps(self.stats.unique_platforms_analysis)

            embed.add_field(name="Raw Non-Unique Data", value=f"```json\n{platform_data}```", inline=False)
            embed.add_field(name="Raw Unique Data", value=f"```json\n{unique_platform_data}```", inline=False)

        elif select.values[0] == "Browser Analysis 🌐":
            resp = generate_chart(data=[self.stats.browsers_analysis, self.stats.unique_browsers_analysis], backgrounds=[["rgba(153, 102, 255, 0.15)", "rgb(153, 102, 255)"], ["rgba(255, 159, 64, 0.15)", "rgb(255, 159, 64)"]], labels=["Clicks", "Unique Clicks"], title="Browsers Analysis Chart", type="bar")
            embed = discord.Embed(
                title="Browsers Analysis Chart 🌐",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This chart shows the trend of browsers used to access the URL",
            )
            embed.set_image(url=resp["url"])

            browser_data = json.dumps(self.stats.browsers_analysis)
            unique_browser_data = json.dumps(self.stats.unique_browsers_analysis)

            embed.add_field(name="Raw Non-Unique Data", value=f"```json\n{browser_data}```", inline=False)
            embed.add_field(name="Raw Unique Data", value=f"```json\n{unique_browser_data}```", inline=False)

        elif select.values[0] == "Referrers Analysis 🔗":
            resp = generate_chart(data=[self.stats.referrers_analysis, self.stats.unique_referrers_analysis], backgrounds=[["rgba(255, 105, 180, 0.15)", "rgb(255, 105, 180)"], ["rgba(60, 179, 113, 0.15)", "rgb(60, 179, 113)"]], labels=["Clicks", "Unique Clicks"], title="Referrers Analysis Chart", type="bar")
            embed = discord.Embed(
                title="Referrers Analysis Chart 🔗",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This chart shows the trend of referrers used to access the URL",
            )
            embed.set_image(url=resp["url"])

            refferer_data = json.dumps(self.stats.referrers_analysis)
            unique_refferer_data = json.dumps(self.stats.unique_referrers_analysis)

            embed.add_field(name="Raw Non-Unique Data", value=f"```json\n{refferer_data}```", inline=False)
            embed.add_field(name="Raw Unique Data", value=f"```json\n{unique_refferer_data}```", inline=False)

        elif select.values[0] == "Clicks Over Time 📈":

            click_data = self.stats.last_n_days_analysis(30)
            unique_click_data = self.stats.last_n_days_unique_analysis(30)

            resp = generate_chart(data=[click_data, unique_click_data], backgrounds=[["rgba(255, 159, 64, 0.15)", "rgb(255, 159, 64)"], ["rgba(201, 203, 207, 0.25)", "rgb(201, 203, 207)"]], labels=["Clicks", "Unique Clicks"], title="Clicks Over Time Chart", type="line")
            embed = discord.Embed(
                title="Clicks Over Time Chart 📈",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This chart shows the trend of clicks over the last 30 days",
            )
            embed.set_image(url=resp["url"])

            click_data = json.dumps(click_data)
            unique_click_data = json.dumps(unique_click_data)

            embed.add_field(name="Raw Non-Unique Data", value=f"```json\n{click_data}```", inline=False)
            embed.add_field(name="Raw Unique Data", value=f"```json\n{unique_click_data}```", inline=False)

        elif select.values[0] == "Countries Heatmap 🔥":

            map = make_countries_heatmap(data=self.stats.country_analysis, alpha=1)
            map.savefig("heatmap.png", format="png", bbox_inches="tight", pad_inches=0.5, dpi=300)

            embed = discord.Embed(
                title="Countries Heatmap 🔥",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This heatmap shows the countries from where the URL was accessed",
            )
            embed.set_image(url="attachment://heatmap.png")

            country_data = json.dumps(self.stats.country_analysis)

            embed.add_field(name="Raw Countries Data", value=f"```json\n{country_data}```", inline=False)

            try:
                embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.avatar)
            except:
                embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.default_avatar)

            await interaction.followup.send(embed=embed, file=discord.File("heatmap.png"))

            if len(select.options) == 1:
                select.disabled = True
            else:
                for i in select.options:
                    if i.value == select.values[0]:
                        select.options.remove(i)

            await interaction.message.edit(view=self)
            return

        elif select.values[0] == "Unique Countries Heatmap 🌍":

            map = make_countries_heatmap(data=self.stats.unique_country_analysis, alpha=1, title="Unique Countries Heatmap")
            map.savefig("unique_heatmap.png", format="png", bbox_inches="tight", pad_inches=0.5, dpi=300)

            embed = discord.Embed(
                title="Unique Countries Heatmap 🌍",
                color=discord.Color.blurple(),
                timestamp=interaction.created_at,
                url=f'https://spoo.me/stats/{self.stats.short_code}',
                description="This heatmap shows the unique clicks countries where the URL was accessed",
            )
            embed.set_image(url="attachment://unique_heatmap.png")

            country_data = json.dumps(self.stats.unique_country_analysis)

            embed.add_field(name="Raw Unique Countries Data", value=f"```json\n{country_data}```", inline=False)

            try:
                embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.avatar)
            except:
                embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.default_avatar)

            await interaction.followup.send(embed=embed, file=discord.File("unique_heatmap.png"))

            if len(select.options) == 1:
                select.disabled = True
            else:
                for i in select.options:
                    if i.value == select.values[0]:
                        select.options.remove(i)

            await interaction.message.edit(view=self)
            return

        try:
            embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.avatar)
        except:
            embed.set_footer(text="Requested by {}".format(interaction.user.name), icon_url=interaction.user.default_avatar)

        await interaction.followup.send(embed=embed)

        if len(select.options) == 1:
                select.disabled = True
        else:
            for i in select.options:
                if i.value == select.values[0]:
                    select.options.remove(i)

        await interaction.message.edit(view=self)
        return

    @discord.ui.select(
        placeholder="📥 Export Statistics Data",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Export as JSON", description="Export the statistics data as JSON", emoji="🔑", value="Export as JSON 🔑"),
            discord.SelectOption(label="Export as CSV", description="Export the statistics data as CSV", emoji="📝", value="Export as CSV 📝"),
            discord.SelectOption(label="Export as Excel", description="Export the statistics data as Excel", emoji="📊", value="Export as Excel 📊"),
        ]
    )
    async def export_data_callback(self, interaction:discord.Interaction, select:discord.ui.Select):
        await interaction.response.defer()

        try:
            if select.values[0] == "Export as JSON 🔑":
                self.stats.export_data(filename=f"json_export.json", filetype="json")
                await interaction.followup.send(file=discord.File(r"json_export.json", filename=f"{self.stats.short_code}_json_export.json"))

            elif select.values[0] == "Export as CSV 📝":
                self.stats.export_data(filename="csv_export", filetype="csv")
                await interaction.followup.send(file=discord.File(r"csv_export.zip", filename=f"{self.stats.short_code}_csv_export.zip"))

            elif select.values[0] == "Export as Excel 📊":
                self.stats.export_data(filename="excel_export.xlsx", filetype="xlsx")
                await interaction.followup.send(file=discord.File(r"excel_export.xlsx", filename=f"{self.stats.short_code}_excel_export.xlsx"))

            if len(select.options) == 1:
                select.disabled = True
            else:
                for i in select.options:
                    if i.value == select.values[0]:
                        select.options.remove(i)

            await interaction.message.edit(view=self)
            return

        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(title="An Error Occured", description=f"```{e}```", color=discord.Color.red()))


class urlStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="stats",
        description="View URL Statistics 📊",
    )
    @app_commands.describe(
        short_code="The short code of the url to view statistics for",
        password="The password for the URL",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30.0)
    async def stats(self, interaction:discord.Interaction, short_code: str, password: str=None):

        await interaction.response.send_message(embed=discord.Embed(description="Fetching statistics...", color=discord.Color.blurple()), ephemeral=True)

        result = Statistics(short_code, password=password)

        embed = discord.Embed(
            title="URL Statistics 📊",
            description=f"Statistics for short url - `https://spoo.me/{result.short_code}`",
            color=discord.Color.blurple(),
            timestamp=interaction.created_at,
            url=f'https://spoo.me/stats/{result.short_code}',
        )

        embed.add_field(name="Original URL", value=f'```{result.long_url}```', inline=False)
        embed.add_field(name="Total Clicks", value=f"```{result.total_clicks}```", inline=True)
        embed.add_field(name="Total Unique Clicks", value=f'```{result.total_unique_clicks}```', inline=True)
        embed.add_field(name="Created At", value=f'```{result.created_at}```', inline=False)
        embed.add_field(name="Last Click", value=f'```Time - {result.last_click}```\n```Browsers - {result.last_click_browser}```\n```Platform - {result.last_click_platform}```', inline=True)
        embed.add_field(name="Average Clicks", value=f"```Daily - {result.average_daily_clicks}```\n```Weekly - {result.average_weekly_clicks}```\n```Monthly - {result.average_monthly_clicks}```", inline=True)

        try:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        resp = generate_chart(data=[result.last_n_days_analysis(7), result.last_n_days_unique_analysis(7)], backgrounds=[["rgba(75, 192, 192, 0.15)", "rgb(75, 192, 192)"], ["rgba(85, 52, 235, .25)", "rgb(85, 52, 235)"]], labels=["Clicks", "Unique Clicks"], title="Clicks Over Time Chart", type="line")
        embed.set_image(url=resp["url"])

        if result.password:
            embed.add_field(name="Password", value=f"```{password}```", inline=False)
            await interaction.user.send(embed=embed, view=StatsSelectView(result))
        else:
            await interaction.channel.send(embed=embed, view=StatsSelectView(result))

        return

    @stats.error
    async def stats_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(interaction, error)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "stats")
            await interaction.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(urlStats(bot))
    print("Loaded stats cog")