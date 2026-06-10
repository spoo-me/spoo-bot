from __future__ import annotations

import discord
import httpx
from aiohttp import web
from discord import app_commands
from discord.ext import commands

from spoobot.config import Config
from spoobot.errors import (
    GrantRevokedError,
    NotLinkedError,
    RateLimitedError,
    SpooApiError,
)
from spoobot.infrastructure.crypto import TokenCipher
from spoobot.infrastructure.http import create_client
from spoobot.infrastructure.logging import get_logger
from spoobot.services.auth import AuthService
from spoobot.services.charts import ChartRenderer, build_renderer
from spoobot.services.qr_client import QrClient
from spoobot.services.spoo_client import SpooClient
from spoobot.services.vault import TokenVault
from spoobot.ui import embeds
from spoobot.web.server import make_app, make_interaction_notifier

log = get_logger(__name__)

COGS = (
    "spoobot.cogs.meta",
    "spoobot.cogs.community",
    "spoobot.cogs.shorten",
    "spoobot.cogs.account",
    "spoobot.cogs.links",
    "spoobot.cogs.stats",
    "spoobot.cogs.qr",
    "spoobot.cogs.getcode",
)


def make_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.members = True  # welcome messages
    intents.message_content = True  # prefix commands ($sync, $ping)
    return intents


class SpooBot(commands.Bot):
    def __init__(self, config: Config) -> None:
        super().__init__(
            command_prefix=config.bot.command_prefix,
            intents=make_intents(),
            help_command=None,
        )
        self.config = config
        # Composition-root state — built in setup_hook (needs the running loop).
        self._http_spoo: httpx.AsyncClient | None = None
        self._http_qr: httpx.AsyncClient | None = None
        self._http_misc: httpx.AsyncClient | None = None
        self._spoo: SpooClient | None = None
        self._qr: QrClient | None = None
        self._vault: TokenVault | None = None
        self._auth: AuthService | None = None
        self._charts: ChartRenderer | None = None
        self._web_runner: web.AppRunner | None = None

    # ── typed service access (cogs read these off `self.bot`) ───────────

    @property
    def spoo(self) -> SpooClient:
        assert self._spoo is not None, "SpooBot.setup_hook has not run"
        return self._spoo

    @property
    def qr(self) -> QrClient:
        assert self._qr is not None, "SpooBot.setup_hook has not run"
        return self._qr

    @property
    def vault(self) -> TokenVault:
        assert self._vault is not None, "SpooBot.setup_hook has not run"
        return self._vault

    @property
    def auth(self) -> AuthService:
        assert self._auth is not None, "SpooBot.setup_hook has not run"
        return self._auth

    @property
    def charts(self) -> ChartRenderer:
        assert self._charts is not None, "SpooBot.setup_hook has not run"
        return self._charts

    @property
    def http_misc(self) -> httpx.AsyncClient:
        assert self._http_misc is not None, "SpooBot.setup_hook has not run"
        return self._http_misc

    # ── lifecycle ────────────────────────────────────────────────────────

    async def setup_hook(self) -> None:
        cfg = self.config
        self._http_spoo = create_client(base_url=cfg.spoo.api_base)
        self._http_qr = create_client(base_url=cfg.spoo.qr_api_base)
        self._http_misc = create_client()
        self._spoo = SpooClient(self._http_spoo)
        self._qr = QrClient(self._http_qr)
        self._vault = TokenVault(cfg.auth.vault_path, TokenCipher(cfg.auth.vault_key))
        await self._vault.init()
        self._auth = AuthService(
            self._spoo,
            self._vault,
            state_secret=cfg.auth.state_secret,
            app_id=cfg.auth.app_id,
            spoo_base=cfg.spoo.api_base,
            callback_url=cfg.web.public_callback_url,
            link_ttl_seconds=cfg.auth.link_ttl_seconds,
        )
        self._charts = build_renderer(cfg.charts.renderer, self._http_misc, cfg)

        for cog in COGS:
            await self.load_extension(cog)
        self.tree.error(self.on_app_command_error)

        if cfg.web.enabled:
            assert self.application_id is not None, "application_id missing after login"
            app = make_app(
                self._auth,
                on_linked=make_interaction_notifier(
                    self.application_id, self._http_misc
                ),
            )
            self._web_runner = web.AppRunner(app)
            await self._web_runner.setup()
            site = web.TCPSite(self._web_runner, cfg.web.host, cfg.web.port)
            await site.start()
            log.info("callback server on %s:%s", cfg.web.host, cfg.web.port)

    async def on_ready(self) -> None:
        log.info("logged in as %s (%s guilds)", self.user, len(self.guilds))
        if self.config.bot.custom_status:
            await self.change_presence(
                activity=discord.CustomActivity(name=self.config.bot.custom_status)
            )

    async def close(self) -> None:
        if self._web_runner:
            await self._web_runner.cleanup()
        if self._charts:
            await self._charts.close()
        if self._vault:
            await self._vault.close()
        for client in (self._http_spoo, self._http_qr, self._http_misc):
            if client:
                await client.aclose()
        await super().close()

    # ── central app-command error handler ────────────────────────────────

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        original = getattr(error, "original", error)

        if isinstance(error, app_commands.CommandOnCooldown):
            embed = embeds.cooldown_embed(error.retry_after)
        elif isinstance(original, NotLinkedError):
            embed = embeds.not_linked_embed()
        elif isinstance(original, GrantRevokedError):
            embed = embeds.relink_embed()
        elif isinstance(original, RateLimitedError):
            after = (
                f" Try again in ~{int(original.retry_after)}s."
                if original.retry_after
                else ""
            )
            embed = embeds.error_embed(
                "Rate limited", f"spoo.me told us to slow down.{after}"
            )
        elif isinstance(original, SpooApiError):
            embed = embeds.error_embed("spoo.me error", str(original))
        else:
            log.exception("unhandled command error", exc_info=original)
            embed = embeds.error_embed(
                "Something broke", "Unexpected error — the team has the logs."
            )

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
