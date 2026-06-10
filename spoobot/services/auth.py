from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Protocol, TypeVar
from urllib.parse import urlencode

from spoobot.errors import AuthRequiredError, GrantRevokedError, NotLinkedError
from spoobot.infrastructure.crypto import StateError, make_state, parse_state
from spoobot.infrastructure.logging import get_logger
from spoobot.services.models import DeviceTokenGrant, TokenPair
from spoobot.services.vault import LinkSession, TokenVault

log = get_logger(__name__)

T = TypeVar("T")


class DeviceAuthClient(Protocol):
    async def exchange_device_code(self, code: str) -> DeviceTokenGrant: ...
    async def refresh_device_tokens(self, refresh_token: str) -> TokenPair: ...


class LinkError(Exception):
    """User-facing linking failure (bad/expired state, unknown session)."""


@dataclass(frozen=True)
class LinkResult:
    discord_user_id: int
    spoo_email: str
    interaction_token: str


class AuthService:
    def __init__(
        self,
        client: DeviceAuthClient,
        vault: TokenVault,
        *,
        state_secret: str,
        app_id: str,
        spoo_base: str,
        callback_url: str,
        link_ttl_seconds: int = 600,
    ) -> None:
        self._client = client
        self._vault = vault
        self._secret = state_secret
        self._app_id = app_id
        self._spoo_base = spoo_base.rstrip("/")
        self._callback_url = callback_url
        self._ttl = link_ttl_seconds

    # ── linking ──────────────────────────────────────────────────────────

    async def begin_link(self, *, discord_user_id: int, interaction_token: str) -> str:
        """Mint state, persist the pending session, return the consent URL."""
        state = make_state(self._secret, discord_user_id=discord_user_id, ttl_seconds=self._ttl)
        nonce = state.split(".")[0]
        await self._vault.create_link_session(
            nonce, discord_user_id=discord_user_id, interaction_token=interaction_token
        )
        query = urlencode(
            {"app_id": self._app_id, "redirect_uri": self._callback_url, "state": state}
        )
        return f"{self._spoo_base}/auth/device/login?{query}"

    async def complete_link(self, *, code: str, state: str) -> LinkResult:
        """Callback path: verify state, single-use the session, exchange the code."""
        try:
            parsed = parse_state(self._secret, state)
        except StateError as exc:
            raise LinkError(f"invalid link state: {exc}") from exc

        session: LinkSession | None = await self._vault.consume_link_session(parsed.nonce)
        if session is None or session.discord_user_id != parsed.discord_user_id:
            raise LinkError("unknown or already-used link session")

        grant = await self._client.exchange_device_code(code)
        email = grant.user.email if grant.user else ""
        await self._vault.put(
            parsed.discord_user_id,
            TokenPair(access_token=grant.access_token, refresh_token=grant.refresh_token),
            spoo_email=email,
        )
        log.info("account linked discord_user_id=%s", parsed.discord_user_id)
        return LinkResult(
            discord_user_id=parsed.discord_user_id,
            spoo_email=email,
            interaction_token=session.interaction_token,
        )

    async def unlink(self, discord_user_id: int) -> bool:
        """Forget the user locally. Grant revocation happens on the dashboard."""
        return await self._vault.delete(discord_user_id)

    async def linked_email(self, discord_user_id: int) -> str | None:
        acct = await self._vault.get(discord_user_id)
        return acct.spoo_email if acct else None

    # ── authed API calls with refresh-once semantics ─────────────────────

    async def authed_call(
        self, discord_user_id: int, call: Callable[[str], Awaitable[T]]
    ) -> T:
        acct = await self._vault.get(discord_user_id)
        if acct is None:
            raise NotLinkedError("no linked spoo.me account")
        try:
            return await call(acct.tokens.access_token)
        except AuthRequiredError:
            pass  # fall through to refresh
        try:
            fresh = await self._client.refresh_device_tokens(acct.tokens.refresh_token)
        except AuthRequiredError as exc:
            # Refresh rejected — grant revoked (or refresh token expired).
            await self._vault.delete(discord_user_id)
            raise GrantRevokedError(
                "spoo.me access was revoked — relink with /link", status=401
            ) from exc
        await self._vault.put(discord_user_id, fresh, spoo_email=acct.spoo_email)
        return await call(fresh.access_token)
