import requests
from py_spoo_url import Shortener
from typing import Literal
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import matplotlib
import discord
import random
import datetime
import aiohttp
from config import ChartHeatmap, config

shortener = Shortener()

# Use waiting_gifs and welcome_gifs from config
waiting_gifs = config.assets.waiting_gifs
welcome_gifs = config.assets.welcome_gifs


# Build commands_ dictionary from config
def build_commands_help():
    commands_ = {}
    for cmd_name, cmd in config.commands.items():
        # Build the command string (e.g., "</shorten:1234> 🤏🏻")
        key = (
            f"</{cmd_name.replace('_', '-')}:{cmd.id}> {cmd.emoji} - {cmd.description}"
        )

        # If command has parameters, build the parameter string
        if cmd.parameters:
            value: str = "**Parameters:**\n" + "\n".join(
                [
                    f"- **{param.name}** - {param.description} {param.emoji}"
                    for param in cmd.parameters
                ]
            )
        else:
            value = ""

        commands_[key] = value
    return commands_


# Initialize commands_ using the config
commands_ = build_commands_help()


async def fetch_spoo_stats():
    """Fetch statistics from spoo.me API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(config.urls.spoo_metrics) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        print(f"Error fetching stats: {e}")
    return None


def generate_chart(
    data: list,
    backgrounds: list,
    labels: list,
    title: str,
    type: str,
    fill: bool = True,
):
    chart_style = config.ui.charts.style
    chart_scales = config.ui.charts.scales
    chart_plugins = config.ui.charts.plugins

    data_dict = {
        "type": type,
        "data": {
            "labels": list(data[0].keys()),
            "datasets": [],
        },
        "options": {
            "layout": {"padding": chart_style.padding.dict()},
            "scales": {
                "y": {
                    "beginAtZero": "true",
                    "grid": {
                        "color": chart_scales.grid_color,
                    },
                    "ticks": {
                        "color": chart_scales.tick_color,
                    },
                },
                "x": {
                    "grid": {
                        "color": chart_scales.grid_color,
                    },
                    "ticks": {
                        "color": chart_scales.tick_color,
                    },
                },
            },
            "plugins": {
                "title": {
                    "display": "true",
                    "text": title,
                    "color": chart_plugins.title.color,
                    "fontStyle": chart_plugins.title.font_style,
                    "fontSize": chart_plugins.title.font_size,
                },
                "legend": {
                    "display": "true",
                    "labels": {
                        "color": chart_plugins.legend.labels_color,
                    },
                },
            },
        },
    }

    if type == "bar" or type == "horizontalBar":
        data_dict["options"]["scales"]["x"]["stacked"] = "true"

    for index, i in enumerate(data):
        data_dict["data"]["datasets"].append(
            {
                "label": labels[index],
                "data": list(i.values()),
                "fill": fill,
                "backgroundColor": backgrounds[index][0],
                "borderWidth": chart_style.border_width,
                "borderRadius": chart_style.border_radius,
                "borderColor": backgrounds[index][1],
                "lineTension": chart_style.line_tension,
            }
        )

    resp = requests.post(
        config.urls.charts_api_base,
        json={"chart": data_dict, "v": 4, "backgroundColor": chart_style.background},
    )

    return resp.json()


def generate_countries_heatmap(
    data,
    cmap: Literal[
        "YlOrRd", "viridis", "plasma", "inferno", "RdPu_r", "pink", "turbo"
    ] = "YlOrRd",
    alpha: float = None,
    title: str = "Countries Heatmap",
):
    heatmap_config: ChartHeatmap = config.ui.charts.heatmap
    alpha = alpha if alpha is not None else heatmap_config.alpha

    matplotlib.rcParams["font.size"] = config.ui.charts.style.font_size
    matplotlib.rcParams["axes.labelcolor"] = config.ui.charts.style.text_color

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    world = world.merge(
        gpd.GeoDataFrame(data.items(), columns=["Country", "Value"]),
        how="left",
        left_on="name",
        right_on="Country",
    )

    plt.figure(figsize=(15, 10), dpi=heatmap_config.dpi)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)

    # Create a figure and axis with background color from config
    background_color = tuple(
        int(config.ui.charts.style.background.strip("rgb()").split(",")[i]) / 255
        for i in range(3)
    )
    fig, ax = plt.subplots(1, 1, figsize=(15, 10), facecolor=(*background_color, alpha))

    grid_color = tuple(
        int(config.ui.charts.scales.grid_color.strip("rgb()").split(",")[i]) / 255
        for i in range(3)
    )
    for spine in ax.spines.values():
        spine.set_color(grid_color)
        spine.set_linewidth(config.ui.charts.style.border_width)

    ax.tick_params(labelcolor=config.ui.charts.style.text_color)

    world.boundary.plot(ax=ax, linewidth=1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    p = world.plot(
        column="Value",
        ax=ax,
        legend=True,
        cax=cax,
        cmap=cmap,
        edgecolor=None,
        legend_kwds={
            "label": "Clicks",
        },
        alpha=alpha,
    )
    p.set_facecolor((*background_color, alpha))
    cbax = cax
    cbax.tick_params(labelcolor=config.ui.charts.style.text_color)

    plt.suptitle(
        title,
        x=0.5,
        y=0.82,
        fontsize=config.ui.charts.plugins.title.font_size,
        fontweight=config.ui.charts.plugins.title.font_style,
        color=config.ui.charts.plugins.title.color,
    )

    return plt


async def generate_error_message(
    interaction: discord.Interaction,
    error,
    cooldown_configuration=[
        "- ```1 time every 10 seconds```",
        "- ```5 times every 60 seconds```",
        "- ```200 times every 24 hours```",
    ],
) -> discord.Embed:
    end_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
        seconds=error.retry_after
    )
    end_time_ts = int(end_time.timestamp())

    embed = discord.Embed(
        title="⏳ Cooldown",
        description=f"### You can use this command again <t:{end_time_ts}:R>",
        color=int(config.ui.colors.error, 16),
        timestamp=interaction.created_at,
    )
    embed.set_image(url=random.choice(config.assets.waiting_gifs))

    embed.add_field(
        name="How many times can I use this command?",
        value="\n".join(cooldown_configuration),
        inline=False,
    )

    try:
        embed.set_footer(
            text=f"{interaction.user} used /{interaction.command.name}",
            icon_url=interaction.user.avatar,
        )
    except Exception:
        embed.set_footer(
            text=f"{interaction.user} used /{interaction.command.name}",
            icon_url=interaction.user.default_avatar,
        )

    return embed


async def generate_command_error_embed(
    interaction: discord.Interaction, error, command_name
):
    embed = discord.Embed(
        title="An error occured",
        description=f"```{error}```",
        color=int(config.ui.colors.error, 16),
        timestamp=interaction.created_at,
    )

    try:
        embed.set_footer(
            text=f"{interaction.user.name} used /{command_name}",
            icon_url=interaction.user.avatar,
        )
    except Exception:
        embed.set_footer(
            text=f"{interaction.user.name} used /{command_name}",
            icon_url=interaction.user.default_avatar,
        )

    return embed
