from __future__ import annotations

import discord

from spoobot.ui import theme


def user_footer(
    embed: discord.Embed, user: discord.abc.User, *, prefix: str = "Requested by"
) -> discord.Embed:
    """The one place the avatar-fallback dance lives (was copy-pasted 15× before)."""
    icon = user.avatar or user.default_avatar
    embed.set_footer(text=f"{prefix} {user.name}", icon_url=icon.url)
    return embed


def error_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=theme.ERROR)


def cooldown_embed(retry_after: float) -> discord.Embed:
    import time

    retry_at = int(time.time() + retry_after)
    return discord.Embed(
        title="Slow down ⏳",
        description=f"You're on cooldown. Try again <t:{retry_at}:R>.",
        color=theme.WARNING,
    )


def not_linked_embed() -> discord.Embed:
    return discord.Embed(
        title="Link your spoo.me account",
        description=(
            "This command works with **your** spoo.me links, so the bot needs your "
            "permission first. Run **/link** — it takes ten seconds.\n\n"
            "*Only ever enter your spoo.me credentials on `spoo.me`.*"
        ),
        color=theme.PRIMARY,
    )


def relink_embed() -> discord.Embed:
    return discord.Embed(
        title="Your spoo.me link was revoked",
        description="Access was revoked (or expired) on the spoo.me side. Run **/link** to reconnect.",
        color=theme.WARNING,
    )
