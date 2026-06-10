from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
from discord import app_commands
from discord.ext import commands

from spoobot.errors import NotFoundError
from spoobot.services.models import UrlListItem, UrlPage
from spoobot.ui import theme
from spoobot.ui.checks import require_link

if TYPE_CHECKING:
    from spoobot.bot import SpooBot

PAGE_SIZE = 8


class EditLinkModal(discord.ui.Modal, title="Edit link"):
    long_url = discord.ui.TextInput(label="Destination URL", required=False,
                                    placeholder="leave empty to keep")
    password = discord.ui.TextInput(label="Password (empty = keep, 'off' = remove)",
                                    required=False)
    max_clicks = discord.ui.TextInput(label="Max clicks (empty = keep, 0 = remove)",
                                      required=False)

    def __init__(self, cog: LinksCog, url_id: str, alias: str) -> None:
        super().__init__()
        self.cog, self.url_id, self.alias = cog, url_id, alias

    async def on_submit(self, interaction: discord.Interaction) -> None:
        fields: dict[str, Any] = {}
        if self.long_url.value:
            fields["long_url"] = self.long_url.value
        if self.password.value:
            fields["password"] = None if self.password.value == "off" else self.password.value
        if self.max_clicks.value:
            fields["max_clicks"] = int(self.max_clicks.value)
        if not fields:
            await interaction.response.send_message("Nothing to change.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await self.cog.bot.auth.authed_call(
            interaction.user.id,
            lambda t: self.cog.bot.spoo.update_url(t, self.url_id, **fields),
        )
        await interaction.followup.send(
            embed=discord.Embed(title=f"Updated `{self.alias}` ✓", color=theme.SUCCESS),
            ephemeral=True,
        )


class LinksCog(commands.Cog):
    group = app_commands.Group(name="links", description="Manage your spoo.me links")

    def __init__(self, bot: SpooBot) -> None:
        self.bot = bot

    async def _page(self, user_id: int, page: int, search: str | None = None) -> UrlPage:
        return await self.bot.auth.authed_call(
            user_id,
            lambda t: self.bot.spoo.list_urls(t, page=page, page_size=PAGE_SIZE, search=search),
        )

    async def _resolve_id(self, user_id: int, alias: str) -> tuple[str, str]:
        """alias → (url_id, alias). Raises NotFoundError-ish message via search miss."""
        page = await self._page(user_id, 1, search=alias)
        for item in page.items:
            if item.alias == alias:
                return item.id, item.alias
        raise NotFoundError(f"no link with alias '{alias}' on your account", status=404)

    def _browser_view(self, page: UrlPage) -> LinksBrowserView:
        return LinksBrowserView(self, page)

    async def _alias_choices(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        try:
            page = await self._page(interaction.user.id, 1, search=current or None)
        except Exception:
            return []
        return [app_commands.Choice(name=f"{u.alias} → {u.long_url[:60]}", value=u.alias)
                for u in page.items][:25]

    # ── commands ─────────────────────────────────────────────────────────

    @group.command(name="list", description="Browse and manage your links 📋")
    @require_link()
    async def list_links(self, interaction: discord.Interaction, page: int = 1) -> None:
        await interaction.response.defer(ephemeral=True)
        result = await self._page(interaction.user.id, page)
        await interaction.followup.send(view=self._browser_view(result), ephemeral=True)

    @group.command(name="edit", description="Edit one of your links ✏️")
    @require_link()
    async def edit_link(self, interaction: discord.Interaction, alias: str) -> None:
        url_id, alias = await self._resolve_id(interaction.user.id, alias)
        await interaction.response.send_modal(EditLinkModal(self, url_id, alias))

    @group.command(name="toggle", description="Activate/deactivate a link ⏯️")
    @require_link()
    async def toggle_link(self, interaction: discord.Interaction, alias: str) -> None:
        await interaction.response.defer(ephemeral=True)
        url_id, alias = await self._resolve_id(interaction.user.id, alias)
        page = await self._page(interaction.user.id, 1, search=alias)
        current = next(u.status for u in page.items if u.alias == alias)
        new_status = "INACTIVE" if current == "ACTIVE" else "ACTIVE"
        await self.bot.auth.authed_call(
            interaction.user.id, lambda t: self.bot.spoo.set_url_status(t, url_id, new_status)
        )
        await interaction.followup.send(
            embed=discord.Embed(title=f"`{alias}` is now {new_status} ✓", color=theme.SUCCESS),
            ephemeral=True,
        )

    @group.command(name="delete", description="Delete a link permanently 🗑️")
    @require_link()
    async def delete_link(self, interaction: discord.Interaction, alias: str) -> None:
        url_id, alias = await self._resolve_id(interaction.user.id, alias)
        view = ConfirmDelete(self, url_id, alias)
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"Delete `{alias}`?",
                description="This is **irreversible** — analytics are deleted too.",
                color=theme.WARNING,
            ),
            view=view,
            ephemeral=True,
        )

    @edit_link.autocomplete("alias")
    @toggle_link.autocomplete("alias")
    @delete_link.autocomplete("alias")
    async def alias_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        if await self.bot.vault.get(interaction.user.id) is None:
            return []
        return await self._alias_choices(interaction, current)


class ManageButton(discord.ui.Button["LinksBrowserView"]):
    """Per-row accessory: opens an ephemeral action palette for one link."""

    def __init__(self, cog: LinksCog, item: UrlListItem) -> None:
        super().__init__(label="Manage", style=discord.ButtonStyle.secondary)
        self.cog, self.item = cog, item

    async def callback(self, interaction: discord.Interaction) -> None:
        view = discord.ui.View(timeout=300)

        edit_btn: discord.ui.Button[discord.ui.View] = discord.ui.Button(
            label="Edit ✏️", style=discord.ButtonStyle.primary
        )
        toggle_label = "Deactivate ⏸️" if self.item.status == "ACTIVE" else "Activate ▶️"
        toggle_btn: discord.ui.Button[discord.ui.View] = discord.ui.Button(
            label=toggle_label, style=discord.ButtonStyle.secondary
        )
        delete_btn: discord.ui.Button[discord.ui.View] = discord.ui.Button(
            label="Delete 🗑️", style=discord.ButtonStyle.danger
        )

        async def on_edit(interaction: discord.Interaction) -> None:
            await interaction.response.send_modal(
                EditLinkModal(self.cog, self.item.id, self.item.alias)
            )

        async def on_toggle(interaction: discord.Interaction) -> None:
            await interaction.response.defer(ephemeral=True)
            new_status = "INACTIVE" if self.item.status == "ACTIVE" else "ACTIVE"
            await self.cog.bot.auth.authed_call(
                interaction.user.id,
                lambda t: self.cog.bot.spoo.set_url_status(t, self.item.id, new_status),
            )
            await interaction.followup.send(
                embed=discord.Embed(title=f"`{self.item.alias}` is now {new_status} ✓",
                                    color=theme.SUCCESS),
                ephemeral=True,
            )

        async def on_delete(interaction: discord.Interaction) -> None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Delete `{self.item.alias}`?",
                    description="This is **irreversible** — analytics are deleted too.",
                    color=theme.WARNING,
                ),
                view=ConfirmDelete(self.cog, self.item.id, self.item.alias),
                ephemeral=True,
            )

        edit_btn.callback, toggle_btn.callback, delete_btn.callback = on_edit, on_toggle, on_delete
        for b in (edit_btn, toggle_btn, delete_btn):
            view.add_item(b)
        await interaction.response.send_message(
            f"Managing **`{self.item.alias}`** → {self.item.long_url[:80]}",
            view=view, ephemeral=True,
        )


class PagerRow(discord.ui.ActionRow["LinksBrowserView"]):
    def __init__(self, cog: LinksCog, *, page: int, has_next: bool) -> None:
        super().__init__()
        self.cog, self.page = cog, page
        self.prev.disabled = page <= 1
        self.next.disabled = not has_next

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._flip(interaction, self.page - 1)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._flip(interaction, self.page + 1)

    async def _flip(self, interaction: discord.Interaction, new_page: int) -> None:
        await interaction.response.defer()
        result = await self.cog._page(interaction.user.id, new_page)
        await interaction.edit_original_response(view=self.cog._browser_view(result))


class LinksBrowserView(discord.ui.LayoutView):
    """CV2 links browser: one Section per link with a Manage accessory button."""

    def __init__(self, cog: LinksCog, page: UrlPage) -> None:
        super().__init__(timeout=900)
        container = discord.ui.Container(accent_colour=discord.Colour(theme.PRIMARY))
        container.add_item(
            discord.ui.TextDisplay(f"### 🗂️ Your links — page {page.page} · {page.total} total")
        )
        if not page.items:
            container.add_item(discord.ui.TextDisplay("No links yet. Try **/shorten**!"))
        for u in page.items:
            flag = "🟢" if u.status == "ACTIVE" else "⚪"
            extras: list[str] = []
            if u.password_set:
                extras.append("🔑")
            if u.max_clicks:
                extras.append(f"⏱ {u.max_clicks}")
            meta = f" {' '.join(extras)}" if extras else ""
            container.add_item(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        f"{flag} **`{u.alias}`** · {u.total_clicks:,} clicks{meta}\n"
                        f"-# → {u.long_url[:70]}"
                    ),
                    accessory=ManageButton(cog, u),
                )
            )
        container.add_item(discord.ui.Separator())
        container.add_item(PagerRow(cog, page=page.page, has_next=page.has_next))
        self.add_item(container)


class ConfirmDelete(discord.ui.View):
    def __init__(self, cog: LinksCog, url_id: str, alias: str) -> None:
        super().__init__(timeout=120)
        self.cog, self.url_id, self.alias = cog, url_id, alias

    @discord.ui.button(label="Delete forever", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.cog.bot.auth.authed_call(
            interaction.user.id, lambda t: self.cog.bot.spoo.delete_url(t, self.url_id)
        )
        await interaction.edit_original_response(
            embed=discord.Embed(title=f"Deleted `{self.alias}` ✓", color=theme.SUCCESS), view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await interaction.edit_original_response(
            embed=discord.Embed(title="Cancelled", color=theme.PRIMARY), view=None
        )


async def setup(bot: SpooBot) -> None:
    await bot.add_cog(LinksCog(bot))
