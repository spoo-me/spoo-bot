from __future__ import annotations

from typing import Callable, Protocol, TypeVar, cast

import discord
from discord import app_commands

from spoobot.errors import NotLinkedError
from spoobot.services.vault import TokenVault

T = TypeVar("T")


class _LinkAware(Protocol):
    """Structural view of SpooBot: anything exposing the token vault."""

    @property
    def vault(self) -> TokenVault: ...


def require_link() -> Callable[[T], T]:
    """App-command check: the invoker must have a vault entry.

    Cogs read services off `interaction.client` (SpooBot exposes `.vault`).
    Raises NotLinkedError → handled centrally by the tree error handler.
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        client = cast("_LinkAware", interaction.client)
        if await client.vault.get(interaction.user.id) is None:
            raise NotLinkedError()
        return True

    return app_commands.check(predicate)
