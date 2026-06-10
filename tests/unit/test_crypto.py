from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from spoobot.infrastructure.crypto import (
    StateError,
    TokenCipher,
    make_state,
    parse_state,
)

SECRET = "x" * 32


def test_cipher_roundtrip():
    cipher = TokenCipher(Fernet.generate_key().decode())
    assert cipher.decrypt(cipher.encrypt("jwt-token")) == "jwt-token"


def test_state_roundtrip():
    state = make_state(SECRET, discord_user_id=123, ttl_seconds=600)
    parsed = parse_state(SECRET, state)
    assert parsed.discord_user_id == 123
    assert len(parsed.nonce) >= 16


def test_state_tampered_uid_rejected():
    state = make_state(SECRET, discord_user_id=123, ttl_seconds=600)
    nonce, uid, exp, sig = state.split(".")
    forged = ".".join([nonce, "999", exp, sig])
    with pytest.raises(StateError, match="signature"):
        parse_state(SECRET, forged)


def test_state_expired_rejected():
    state = make_state(SECRET, discord_user_id=1, ttl_seconds=-1)
    with pytest.raises(StateError, match="expired"):
        parse_state(SECRET, state)


def test_state_garbage_rejected():
    with pytest.raises(StateError):
        parse_state(SECRET, "not-a-state")
