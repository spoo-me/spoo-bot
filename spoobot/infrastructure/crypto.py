from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken


class StateError(Exception):
    """Invalid, tampered, or expired link state."""


class TokenCipher:
    """Encrypts/decrypts stored JWTs at rest (Fernet)."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode())

    def decrypt(self, ciphertext: bytes) -> str:
        try:
            return self._fernet.decrypt(ciphertext).decode()
        except InvalidToken as exc:
            raise StateError("vault decryption failed — wrong VAULT_KEY?") from exc


@dataclass(frozen=True)
class LinkState:
    nonce: str
    discord_user_id: int
    expires_at: int


def _sign(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_state(secret: str, *, discord_user_id: int, ttl_seconds: int) -> str:
    nonce = secrets.token_urlsafe(16)
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{nonce}.{discord_user_id}.{expires_at}"
    return f"{payload}.{_sign(secret, payload)}"


def parse_state(secret: str, state: str) -> LinkState:
    parts = state.split(".")
    if len(parts) != 4:
        raise StateError("malformed state")
    nonce, uid_raw, exp_raw, sig = parts
    payload = f"{nonce}.{uid_raw}.{exp_raw}"
    if not hmac.compare_digest(_sign(secret, payload), sig):
        raise StateError("bad signature")
    try:
        uid, exp = int(uid_raw), int(exp_raw)
    except ValueError as exc:
        raise StateError("malformed state fields") from exc
    if exp < time.time():
        raise StateError("state expired")
    return LinkState(nonce=nonce, discord_user_id=uid, expires_at=exp)
