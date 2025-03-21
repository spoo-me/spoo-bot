import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from py_spoo_url import Statistics
from utils import (
    generate_chart,
    generate_error_message,
    generate_command_error_embed,
    generate_countries_heatmap,
)
from schemas import ChartColors
from config import config


class StatsSelectView(discord.ui.View):
    def __init__(self, stats: Statistics) -> None:
        super().__init__(timeout=None)
        self.stats: Statistics = stats
        self.used_export_options = []
        self.used_charts_options = []
        self.chart_colors: ChartColors = config.ui.charts.colors
        self.base_url: str = config.urls.api_base

    @discord.ui.select(
        placeholder="➕ Additional Statistics Chart",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Platforms Analysis",
                description="Generate a chart for platforms analysis trend",
                emoji="📱",
                value="Platform Analysis 📱",
            ),
            discord.SelectOption(
                label="Browsers Analysis",
                description="Generate a chart for browsers analysis trend",
                emoji="🌐",
                value="Browser Analysis 🌐",
            ),
            discord.SelectOption(
                label="Referrers Analysis",
                description="Generate a chart for referrers analysis trend",
                emoji="🔗",
                value="Referrers Analysis 🔗",
            ),
            discord.SelectOption(
                label="Countries Heatmap",
                description="Generate a heatmap for countries analysis trend",
                emoji="🔥",
                value="Countries Heatmap 🔥",
            ),
            discord.SelectOption(
                label="Unique Countries Heatmap",
                description="Generate a heatmap for unique countries analysis trend",
                emoji="🌍",
                value="Unique Countries Heatmap 🌍",
            ),
            discord.SelectOption(
                label="Clicks Over Time",
                description="Generate a chart for clicks over time for the last 30 days",
                emoji="📈",
                value="Clicks Over Time 📈",
            ),
        ],
    )
    async def analysis_chart_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        if select.values[0] in self.used_charts_options:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="An Error Occured",
                    description=f"```{select.values[0]} option has already been used before.```",
                    color=int(config.ui.colors.error, 16),
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        # Create a common embed for all charts
        embed = discord.Embed(
            title="",
            description="",
            timestamp=interaction.created_at,
            url=f"{self.base_url}/stats/{self.stats.short_code}",
            color=int(config.ui.colors.primary, 16),
        )
        file: discord.File = None

        try:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except Exception:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        if select.values[0] == "Platform Analysis 📱":
            resp = generate_chart(
                data=[
                    self.stats.platforms_analysis,
                    self.stats.unique_platforms_analysis,
                ],
                backgrounds=self.chart_colors.platform,
                labels=["Clicks", "Unique Clicks"],
                title="Platforms Analysis Chart",
                type="bar",
            )

            embed.title = "Platforms Analysis Chart 📱"
            embed.description = (
                "This chart shows the trend of platforms used to access the URL"
            )

            embed.set_image(url=resp["url"])
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            platform_data = json.dumps(self.stats.platforms_analysis)
            unique_platform_data = json.dumps(self.stats.unique_platforms_analysis)

            embed.add_field(
                name="Raw Non-Unique Data",
                value=f"```json\n{platform_data}```",
                inline=False,
            )
            embed.add_field(
                name="Raw Unique Data",
                value=f"```json\n{unique_platform_data}```",
                inline=False,
            )

        elif select.values[0] == "Browser Analysis 🌐":
            resp = generate_chart(
                data=[
                    self.stats.browsers_analysis,
                    self.stats.unique_browsers_analysis,
                ],
                backgrounds=self.chart_colors.browser,
                labels=["Clicks", "Unique Clicks"],
                title="Browsers Analysis Chart",
                type="bar",
            )

            embed.title = "Browsers Analysis Chart 🌐"
            embed.description = (
                "This chart shows the trend of browsers used to access the URL"
            )

            embed.set_image(url=resp["url"])
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            browser_data: str = json.dumps(self.stats.browsers_analysis)
            unique_browser_data: str = json.dumps(self.stats.unique_browsers_analysis)

            embed.add_field(
                name="Raw Non-Unique Data",
                value=f"```json\n{browser_data}```",
                inline=False,
            )
            embed.add_field(
                name="Raw Unique Data",
                value=f"```json\n{unique_browser_data}```",
                inline=False,
            )

        elif select.values[0] == "Referrers Analysis 🔗":
            resp = generate_chart(
                data=[
                    self.stats.referrers_analysis,
                    self.stats.unique_referrers_analysis,
                ],
                backgrounds=self.chart_colors.referrer,
                labels=["Clicks", "Unique Clicks"],
                title="Referrers Analysis Chart",
                type="bar",
            )

            embed.title = "Referrers Analysis Chart 🔗"
            embed.description = (
                "This chart shows the trend of referrers used to access the URL"
            )

            embed.set_image(url=resp["url"])
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            refferer_data = json.dumps(self.stats.referrers_analysis)
            unique_refferer_data = json.dumps(self.stats.unique_referrers_analysis)

            embed.add_field(
                name="Raw Non-Unique Data",
                value=f"```json\n{refferer_data}```",
                inline=False,
            )
            embed.add_field(
                name="Raw Unique Data",
                value=f"```json\n{unique_refferer_data}```",
                inline=False,
            )

        elif select.values[0] == "Clicks Over Time 📈":
            click_data = self.stats.last_n_days_analysis(30)
            unique_click_data = self.stats.last_n_days_unique_analysis(30)

            resp = generate_chart(
                data=[click_data, unique_click_data],
                backgrounds=self.chart_colors.timeline,
                labels=["Clicks", "Unique Clicks"],
                title="Clicks Over Time Chart",
                type="line",
            )

            embed.title = "Clicks Over Time Chart 📈"
            embed.description = (
                "This chart shows the trend of clicks over the last 30 days"
            )

            embed.set_image(url=resp["url"])
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            click_data = json.dumps(click_data)
            unique_click_data = json.dumps(unique_click_data)

            embed.add_field(
                name="Raw Non-Unique Data",
                value=f"```json\n{click_data}```",
                inline=False,
            )
            embed.add_field(
                name="Raw Unique Data",
                value=f"```json\n{unique_click_data}```",
                inline=False,
            )

        elif select.values[0] == "Countries Heatmap 🔥":
            heatmap_config = config.ui.charts.heatmap
            map = generate_countries_heatmap(
                data=self.stats.country_analysis, alpha=heatmap_config.alpha
            )
            map.savefig(
                "heatmap.png",
                format="png",
                bbox_inches=heatmap_config.bbox_inches,
                pad_inches=heatmap_config.pad_inches,
                dpi=heatmap_config.dpi,
            )

            embed.title = "Countries Heatmap 🔥"
            embed.description = (
                "This heatmap shows the countries from where the URL was accessed"
            )

            embed.set_image(url="attachment://heatmap.png")
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            country_data = json.dumps(self.stats.country_analysis)

            embed.add_field(
                name="Raw Countries Data",
                value=f"```json\n{country_data}```",
                inline=False,
            )

            file = discord.File("heatmap.png", filename="heatmap.png")

        elif select.values[0] == "Unique Countries Heatmap 🌍":
            heatmap_config = config.ui.charts.heatmap
            map = generate_countries_heatmap(
                data=self.stats.unique_country_analysis,
                alpha=heatmap_config.alpha,
                title="Unique Countries Heatmap",
            )
            map.savefig(
                "unique_heatmap.png",
                format="png",
                bbox_inches=heatmap_config.bbox_inches,
                pad_inches=heatmap_config.pad_inches,
                dpi=heatmap_config.dpi,
            )

            embed.title = "Unique Countries Heatmap 🌍"
            embed.description = "This heatmap shows the unique clicks countries where the URL was accessed"

            embed.set_image(url="attachment://unique_heatmap.png")
            embed.add_field(
                name="Short Code", value=f"```{self.stats.short_code}```", inline=False
            )

            country_data = json.dumps(self.stats.unique_country_analysis)

            embed.add_field(
                name="Raw Unique Countries Data",
                value=f"```json\n{country_data}```",
                inline=False,
            )

            file = discord.File("unique_heatmap.png", filename="unique_heatmap.png")

        if file is not None:
            await interaction.followup.send(embed=embed, file=file)
        else:
            await interaction.followup.send(embed=embed)

        self.used_charts_options.append(select.values[0])
        if len(self.used_charts_options) == 6:
            select.disabled = True
            await interaction.message.edit(view=self)
            self.used_charts_options = []
        return

    @discord.ui.select(
        placeholder="📥 Export Statistics Data",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Export as JSON",
                description="Export the statistics data as JSON",
                emoji="🔑",
                value="Export as JSON 🔑",
            ),
            discord.SelectOption(
                label="Export as CSV",
                description="Export the statistics data as CSV",
                emoji="📝",
                value="Export as CSV 📝",
            ),
            discord.SelectOption(
                label="Export as Excel",
                description="Export the statistics data as Excel",
                emoji="📊",
                value="Export as Excel 📊",
            ),
        ],
    )
    async def export_data_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        if select.values[0] in self.used_export_options:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="An Error Occured",
                    description=f"```{select.values[0]} option has already been used before.```",
                    color=int(config.ui.colors.error, 16),
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            embed = discord.Embed(
                title="Data Export 📥",
                description=f"Statistics export for `{self.base_url}/{self.stats.short_code}`",
                color=int(config.ui.colors.success, 16),
                timestamp=interaction.created_at,
                url=f"{self.base_url}/stats/{self.stats.short_code}",
            )

            if select.values[0] == "Export as JSON 🔑":
                self.stats.export_data(filename="json_export.json", filetype="json")
                file_size: float = round(os.path.getsize("json_export.json") / 1024, 2)
                embed.add_field(
                    name="File Information",
                    value=f"```Size: {file_size} KB\nType: JSON```",
                    inline=False,
                )
                file = discord.File(
                    "json_export.json",
                    filename=f"{self.stats.short_code}_json_export.json",
                )

            elif select.values[0] == "Export as CSV 📝":
                self.stats.export_data(filename="csv_export", filetype="csv")
                file_size: float = round(os.path.getsize("csv_export.zip") / 1024, 2)
                embed.add_field(
                    name="File Information",
                    value=f"```Size: {file_size} KB\nType: CSV```",
                    inline=False,
                )
                file = discord.File(
                    "csv_export.zip", filename=f"{self.stats.short_code}_csv_export.zip"
                )

            elif select.values[0] == "Export as Excel 📊":
                self.stats.export_data(filename="excel_export.xlsx", filetype="xlsx")
                file_size = round(os.path.getsize("excel_export.xlsx") / 1024, 2)
                embed.add_field(
                    name="File Information",
                    value=f"```Size: {file_size} KB\nType: Excel```",
                    inline=False,
                )
                file = discord.File(
                    "excel_export.xlsx",
                    filename=f"{self.stats.short_code}_excel_export.xlsx",
                )

            try:
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}",
                    icon_url=interaction.user.avatar,
                )
            except Exception:
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}",
                    icon_url=interaction.user.default_avatar,
                )

            await interaction.followup.send(embed=embed, file=file)

            # Cleanup exported files
            if select.values[0] == "Export as JSON 🔑":
                os.remove("json_export.json")
            elif select.values[0] == "Export as CSV 📝":
                os.remove("csv_export.zip")
            elif select.values[0] == "Export as Excel 📊":
                os.remove("excel_export.xlsx")

            self.used_export_options.append(select.values[0])
            if len(self.used_export_options) == 3:
                select.disabled = True
                await interaction.message.edit(view=self)
                self.used_export_options = []

            return

        except Exception as e:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="An Error Occured",
                    description=f"```{e}```",
                    color=int(config.ui.colors.error, 16),
                )
            )


class urlStats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="stats",
        description=f"{config.commands['stats'].description} {config.commands['stats'].emoji}",
    )
    @app_commands.describe(**{
        param.name: f"{param.description}"
        for param in config.commands["stats"].parameters
    })
    @app_commands.guild_only()
    @app_commands.checks.cooldown(
        config.cooldowns.short_term.count, config.cooldowns.short_term.seconds
    )
    async def stats(
        self, interaction: discord.Interaction, short_code: str, password: str = None
    ) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="Fetching statistics...",
                color=int(config.ui.colors.primary, 16),
            ),
            ephemeral=True,
        )

        result = Statistics(short_code, password=password)

        embed = discord.Embed(
            title="URL Statistics 📊",
            description=f"Statistics for short url - `{config.urls.api_base}/{result.short_code}`",
            color=int(config.ui.colors.primary, 16),
            timestamp=interaction.created_at,
            url=f"{config.urls.api_base}/stats/{result.short_code}",
        )

        embed.add_field(
            name="Original URL", value=f"```{result.long_url}```", inline=False
        )
        embed.add_field(
            name="Total Clicks", value=f"```{result.total_clicks}```", inline=True
        )
        embed.add_field(
            name="Total Unique Clicks",
            value=f"```{result.total_unique_clicks}```",
            inline=True,
        )
        embed.add_field(
            name="Created At", value=f"```{result.created_at}```", inline=False
        )
        embed.add_field(
            name="Last Click",
            value=f"```Time - {result.last_click}```\n```Browsers - {result.last_click_browser}```\n```Platform - {result.last_click_platform}```",
            inline=True,
        )
        embed.add_field(
            name="Average Clicks",
            value=f"```Daily - {result.average_daily_clicks}```\n```Weekly - {result.average_weekly_clicks}```\n```Monthly - {result.average_monthly_clicks}```",
            inline=True,
        )

        try:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.avatar,
            )
        except Exception:
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.default_avatar,
            )

        resp = generate_chart(
            data=[
                result.last_n_days_analysis(7),
                result.last_n_days_unique_analysis(7),
            ],
            backgrounds=config.ui.charts.colors.timeline,
            labels=["Clicks", "Unique Clicks"],
            title="Clicks Over Time Chart",
            type="line",
        )
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
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await generate_error_message(
                interaction,
                error,
                cooldown_configuration=[
                    f"- ```{config.cooldowns.short_term.count} time every {config.cooldowns.short_term.seconds} seconds```",
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await generate_command_error_embed(interaction, error, "stats")
            await interaction.channel.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(urlStats(bot))
    print(f"Loaded {urlStats.__name__}")
