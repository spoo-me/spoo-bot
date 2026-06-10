from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from spoobot.infrastructure.crypto import TokenCipher
from spoobot.services.models import TokenPair
from spoobot.services.vault import LinkSession, TokenVault


@pytest.fixture
async def vault(tmp_path):
    v = TokenVault(
        tmp_path / "vault.sqlite3", TokenCipher(Fernet.generate_key().decode())
    )
    await v.init()
    yield v
    await v.close()


async def test_put_get_roundtrip(vault):
    pair = TokenPair(access_token="acc", refresh_token="ref")
    await vault.put(123, pair, spoo_email="z@example.com")
    stored = await vault.get(123)
    assert stored is not None
    assert stored.tokens.access_token == "acc"
    assert stored.spoo_email == "z@example.com"


async def test_get_missing_returns_none(vault):
    assert await vault.get(999) is None


async def test_delete(vault):
    await vault.put(1, TokenPair(access_token="a", refresh_token="r"), spoo_email="e")
    assert await vault.delete(1) is True
    assert await vault.get(1) is None
    assert await vault.delete(1) is False


async def test_put_overwrites(vault):
    await vault.put(1, TokenPair(access_token="a1", refresh_token="r1"), spoo_email="e")
    await vault.put(1, TokenPair(access_token="a2", refresh_token="r2"), spoo_email="e")
    stored = await vault.get(1)
    assert stored.tokens.access_token == "a2"


async def test_link_session_single_use(vault):
    await vault.create_link_session(
        "nonce1", discord_user_id=5, interaction_token="itok"
    )
    sess = await vault.consume_link_session("nonce1")
    assert sess == LinkSession(
        nonce="nonce1", discord_user_id=5, interaction_token="itok"
    )
    assert await vault.consume_link_session("nonce1") is None
