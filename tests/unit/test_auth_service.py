from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from spoobot.errors import AuthRequiredError, GrantRevokedError, NotLinkedError
from spoobot.infrastructure.crypto import TokenCipher
from spoobot.services.auth import AuthService
from spoobot.services.models import DeviceTokenGrant, SpooProfile, TokenPair
from spoobot.services.vault import TokenVault

SECRET = "s" * 32


class FakeClient:
    def __init__(self):
        self.exchanged: list[str] = []
        self.refresh_calls = 0
        self.refresh_raises: Exception | None = None

    async def exchange_device_code(self, code: str) -> DeviceTokenGrant:
        self.exchanged.append(code)
        return DeviceTokenGrant(
            access_token="acc-new",
            refresh_token="ref-new",
            user=SpooProfile(email="z@example.com"),
        )

    async def refresh_device_tokens(self, refresh_token: str) -> TokenPair:
        self.refresh_calls += 1
        if self.refresh_raises:
            raise self.refresh_raises
        return TokenPair(access_token="acc-refreshed", refresh_token="ref-rotated")


@pytest.fixture
async def svc(tmp_path):
    vault = TokenVault(tmp_path / "v.sqlite3", TokenCipher(Fernet.generate_key().decode()))
    await vault.init()
    client = FakeClient()
    yield AuthService(client, vault, state_secret=SECRET, app_id="spoo-discord",
                      spoo_base="https://spoo.test", callback_url="https://cb.test/callback",
                      link_ttl_seconds=600), client, vault
    await vault.close()


async def test_begin_link_returns_consent_url_and_stores_session(svc):
    service, _, vault = svc
    url = await service.begin_link(discord_user_id=42, interaction_token="itok")
    assert url.startswith("https://spoo.test/auth/device/login?")
    assert "app_id=spoo-discord" in url
    assert "redirect_uri=https%3A%2F%2Fcb.test%2Fcallback" in url
    nonce = url.split("state=")[1].split("&")[0].split(".")[0]
    sess = await vault.consume_link_session(nonce)
    assert sess and sess.discord_user_id == 42


async def test_complete_link_exchanges_and_stores(svc):
    service, client, vault = svc
    url = await service.begin_link(discord_user_id=7, interaction_token="itok")
    state = url.split("state=")[1].split("&")[0]
    result = await service.complete_link(code="onetime", state=state)
    assert result.discord_user_id == 7
    assert result.spoo_email == "z@example.com"
    assert client.exchanged == ["onetime"]
    acct = await vault.get(7)
    assert acct and acct.tokens.access_token == "acc-new"


async def test_complete_link_replayed_state_rejected(svc):
    service, _, _ = svc
    url = await service.begin_link(discord_user_id=7, interaction_token="t")
    state = url.split("state=")[1].split("&")[0]
    await service.complete_link(code="c1", state=state)
    with pytest.raises(Exception):  # StateError or LinkError — single use
        await service.complete_link(code="c2", state=state)


async def test_authed_call_refreshes_once_on_401(svc):
    service, client, vault = svc
    await vault.put(1, TokenPair(access_token="stale", refresh_token="ref"), spoo_email="e")
    calls = []

    async def api_call(token: str) -> str:
        calls.append(token)
        if token == "stale":
            raise AuthRequiredError("expired", status=401)
        return f"ok:{token}"

    result = await service.authed_call(1, api_call)
    assert result == "ok:acc-refreshed"
    assert client.refresh_calls == 1
    stored = await vault.get(1)
    assert stored.tokens.refresh_token == "ref-rotated"


async def test_authed_call_revoked_grant_clears_vault(svc):
    service, client, vault = svc
    await vault.put(1, TokenPair(access_token="stale", refresh_token="ref"), spoo_email="e")
    client.refresh_raises = AuthRequiredError("app access has been revoked", status=401)

    async def api_call(token: str) -> str:
        raise AuthRequiredError("expired", status=401)

    with pytest.raises(GrantRevokedError):
        await service.authed_call(1, api_call)
    assert await vault.get(1) is None


async def test_authed_call_unlinked_raises(svc):
    service, _, _ = svc

    async def api_call(token: str) -> str:
        return "never"

    with pytest.raises(NotLinkedError):
        await service.authed_call(999, api_call)
