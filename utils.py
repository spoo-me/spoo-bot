from constants import *


shortener = Shortener()

waiting_gifs = [
    "https://media3.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif?cid=ecf05e475p246q1gdcu96b5mkqlqvuapb7xay2hywmki7f5q&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media2.giphy.com/media/QBd2kLB5qDmysEXre9/giphy.gif?cid=ecf05e47ha6xwa7rq38dcst49nefabwwrods631hvz67ptfg&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media2.giphy.com/media/ZgqJGwh2tLj5C/giphy.gif?cid=ecf05e47gflyso481izbdcrw7y8okfkgdxgc7zoh34q9rxim&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media0.giphy.com/media/EWhLjxjiqdZjW/giphy.gif?cid=ecf05e473fifxe2bg4act0zq73nkyjw0h69fxi52t8jt37lf&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media2.giphy.com/media/26BRuo6sLetdllPAQ/200w.webp",
    "https://media4.giphy.com/media/tXL4FHPSnVJ0A/200w.webp",
]

welcome_gifs = [
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-0j.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-3k.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-6u.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-8W.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-DC.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-Gv.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-J2.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-ZY.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-f5.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-hy.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-kU.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-nh.gif?raw=true",
    "https://github.com/spoo-me/spoo-bot/blob/main/blinkies/blinkiesCafe-xO.gif?raw=true",
]

commands_ = {
    "</shorten:1202754338272051252> 🤏🏻 - With this command you can shorten your long urls.": """**Parameters:**
- **url** - The url you want to shorten 🌐
- **alias** - The custom alias you want to use for the url (optional) 🆔
- **password** - The password you want to use for the url (optional) 🔑
- **max_clicks** - The maximum number of clicks you want to allow for the url (optional) 🖱️""",
    "</emojify:1202760315247403109> 😉 - With this command you can generate a short emoji link for your long boring urls.": """**Parameters:**
- **url** - The url you want to shorten 🌐
- **emojies** - The custom emojies you want to use for the url (optional) 😎
- **password** - The password you want to use for the url (optional) 🔑
- **max_clicks** - The maximum number of clicks you want to allow for the url (optional) 🖱️""",
    "</stats:1202895069628203048> 📊 - With this command you can generate detailed statistical insights and charts of your shortened urls": """**Parameters:**
- **short_code** - The short code of the url you want to get the stats for 🔢
- **password** - The password of the url, if the url was password-protected (optional) 🔑""",
    "</bot-stats:1203422993275949056> 🤖": "With this command you can get detailed information about the bot and the developer",
    "</about:1203426619721785384> ℹ️": "With this command you can get detailed information about the bot and the developer",
    "</support:1203424044418994268> 📞": "With this command you can get the support server invite link",
    "</invite:1203421046850584706> 💌": "With this command you can get the bot’s invite link to add it to your own server",
    "</help:1202746904203759646> ❔": "👀 See this message again",
}


def get_server_name_and_icon(server_id):
    response = requests.get(
        f"https://discord.com/api/v9/guilds/{server_id}",
        headers={"Authorization": f"Bot {TOKEN}"},
    )
    if response.status_code == 200:
        data = response.json()
        name = data["name"]
        icon = data["icon"]
        if icon.startswith("a_"):
            # Animated icon
            icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon}.gif"
        else:
            # Static icon
            icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon}.png"

        return (name, icon_url)
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        return None


def generate_chart(
    data: list,
    backgrounds: list,
    labels: list,
    title: str,
    type: str,
    fill: bool = True,
):

    data_dict = {
        "type": type,
        "data": {
            "labels": list(data[0].keys()),
            "datasets": [],
        },
        "options": {
            "layout": {
                "padding": {
                    "left": 20,
                    "right": 20,
                    "top": 5,
                    "bottom": 20,
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": "true",
                    "grid": {
                        "color": "rgb(46, 48, 53)",
                    },
                    "ticks": {
                        "color": "#fff",
                    },
                },
                "x": {
                    "grid": {
                        "color": "rgb(46, 48, 53)",
                    },
                    "ticks": {
                        "color": "#fff",
                    },
                },
            },
            "plugins": {
                "title": {
                    "display": "true",
                    "text": title,
                    "color": "#fff",
                    "fontStyle": "bold",
                    "fontSize": 20,
                },
                "legend": {
                    "display": "true",
                    "labels": {
                        "color": "#fff",
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
                "borderWidth": 2,
                "borderRadius": 10,
                "borderColor": backgrounds[index][1],
                "lineTension": 0.5,
                "fill": "origin",
            }
        )

    resp = requests.post(
        f"https://quickchart.io/chart/create",
        json={"chart": data_dict, "v": 4, "backgroundColor": "rgb(32, 34, 37)"},
    )

    return resp.json()


def make_countries_heatmap(
    data,
    cmap: Literal[
        "YlOrRd", "viridis", "plasma", "inferno", "RdPu_r", "pink", "turbo"
    ] = "YlOrRd",
    alpha: float = 1,
    title: str = "Countries Heatmap",
):

    matplotlib.rcParams["font.size"] = 18
    matplotlib.rcParams["axes.labelcolor"] = "White"

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    world = world.merge(
        gpd.GeoDataFrame(data.items(), columns=["Country", "Value"]),
        how="left",
        left_on="name",
        right_on="Country",
    )

    plt.figure(figsize=(15, 10), dpi=100)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)

    # Create a figure and axis
    fig, ax = plt.subplots(
        1, 1, figsize=(15, 10), facecolor=(32 / 255, 34 / 255, 37 / 255, alpha)
    )

    for spine in ax.spines.values():
        spine.set_color((46 / 255, 48 / 255, 53 / 255))
        spine.set_linewidth(2)

    ax.tick_params(labelcolor="white")

    # Plot the world map
    world.boundary.plot(ax=ax, linewidth=1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    # Plot the heatmap
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
        alpha=0.9,
    )
    p.set_facecolor((32 / 255, 34 / 255, 37 / 255, alpha))
    cbax = cax
    cbax.tick_params(labelcolor="white")

    # Set plot title
    plt.suptitle(
        "Countries Heatmap",
        x=0.5,
        y=0.82,
        fontsize=22,
        fontweight="semibold",
        color="white",
    )

    # Show the plot
    return plt


async def generate_error_message(interaction: discord.Interaction, error):
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after)
    end_time_ts = f"<t:{int(end_time.timestamp())}>"

    hours, remainder = divmod(error.retry_after, 3600)
    minutes, seconds = divmod(remainder, 60)
    seconds = round(seconds)
    time_left = f"{seconds} second{'s' if seconds != 1 else ''}"

    embed = discord.Embed(
        title="⏳ Cooldown",
        description=f"You have to wait until **{end_time_ts}** ({time_left}) to use this command again.",
        color=discord.Color.red(),
    )
    embed.set_image(url=random.choice(waiting_gifs))

    try:
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar,
        )
    except:
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.default_avatar,
        )

    return embed


async def generate_command_error_embed(
    interaction: discord.Interaction, error, command_name
):
    embed = discord.Embed(
        title="An error occured",
        description=f"```{error}```",
        color=discord.Color.red(),
        timestamp=interaction.created_at,
    )

    try:
        embed.set_footer(
            text=f"{interaction.user.name} used /{command_name}",
            icon_url=interaction.user.avatar,
        )
    except:
        embed.set_footer(
            text=f"{interaction.user.name} used /{command_name}",
            icon_url=interaction.user.default_avatar,
        )

    return embed
