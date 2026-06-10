from __future__ import annotations

import urllib.parse

import discord

from spoobot.services.models import ShortUrl
from spoobot.ui import theme

SOCIALS = {
    "twitter": "https://twitter.com/intent/tweet?url=",
    "facebook": "https://www.facebook.com/sharer/sharer.php?u=",
    "telegram": "https://t.me/share/url?url=",
    "whatsapp": "https://wa.me/?text=",
    "reddit": "https://www.reddit.com/submit?url=",
}


class ShortenResultView(discord.ui.LayoutView):
    """CV2 card for a freshly shortened URL."""

    def __init__(
        self,
        result: ShortUrl,
        *,
        owned: bool,
        base_url: str,
        qr_url: str,
        emojis: dict[str, str],
        requested_by: discord.abc.User,
    ) -> None:
        super().__init__(timeout=None)
        header = "### 🔗 URL shortened" + ("  ·  saved to your account" if owned else "")
        body = (
            f"**Short URL**\n{result.short_url}\n\n"
            f"**Destination**\n{result.long_url[:200]}"
        )
        container = discord.ui.Container(accent_colour=discord.Colour(theme.PRIMARY))
        container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(header),
                discord.ui.TextDisplay(body),
                accessory=discord.ui.Thumbnail(media=qr_url),
            )
        )
        container.add_item(discord.ui.Separator())
        stats_row = discord.ui.ActionRow()
        stats_row.add_item(
            discord.ui.Button(label="View Statistics", url=f"{base_url}/stats/{result.alias}")
        )
        container.add_item(stats_row)
        share_row = discord.ui.ActionRow()
        quoted = urllib.parse.quote(result.short_url, safe="")
        for name, prefix in SOCIALS.items():
            emoji_id = emojis.get(name, "")
            share_row.add_item(
                discord.ui.Button(
                    url=f"{prefix}{quoted}",
                    emoji=f"<:{name}:{emoji_id}>" if emoji_id else None,
                    label=None if emoji_id else name.title(),
                )
            )
        container.add_item(share_row)
        container.add_item(
            discord.ui.TextDisplay(f"-# Shortened by {requested_by.name} · spoo.me")
        )
        self.add_item(container)


class LinkButtonView(discord.ui.View):
    """Single link button (used by /link, /unlink and not-linked errors)."""

    def __init__(self, url: str, *, label: str) -> None:
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label=label, url=url))
