"""Encrypted per-Discord-user token store. SQLite is a temporary choice
(research §6) — keep all SQL in this module so a swap stays cheap.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiosqlite

from spoobot.infrastructure.crypto import TokenCipher
from spoobot.services.models import TokenPair

_SCHEMA = """
CREATE TABLE IF NOT EXISTS linked_accounts (
    discord_user_id INTEGER PRIMARY KEY,
    access_token    BLOB NOT NULL,
    refresh_token   BLOB NOT NULL,
    spoo_email      TEXT NOT NULL,
    linked_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS link_sessions (
    nonce             TEXT PRIMARY KEY,
    discord_user_id   INTEGER NOT NULL,
    interaction_token TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@dataclass(frozen=True)
class LinkedAccount:
    discord_user_id: int
    tokens: TokenPair
    spoo_email: str


@dataclass(frozen=True)
class LinkSession:
    nonce: str
    discord_user_id: int
    interaction_token: str


class TokenVault:
    def __init__(self, path: str | Path, cipher: TokenCipher) -> None:
        self._path = Path(path)
        self._cipher = cipher
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self._path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None, "TokenVault.init() not called"
        return self._db

    # ── linked accounts ──────────────────────────────────────────────────

    async def put(self, discord_user_id: int, pair: TokenPair, *, spoo_email: str) -> None:
        await self.db.execute(
            """INSERT INTO linked_accounts (discord_user_id, access_token, refresh_token, spoo_email)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(discord_user_id) DO UPDATE SET
                 access_token=excluded.access_token,
                 refresh_token=excluded.refresh_token,
                 spoo_email=excluded.spoo_email,
                 updated_at=datetime('now')""",
            (
                discord_user_id,
                self._cipher.encrypt(pair.access_token),
                self._cipher.encrypt(pair.refresh_token),
                spoo_email,
            ),
        )
        await self.db.commit()

    async def get(self, discord_user_id: int) -> LinkedAccount | None:
        cur = await self.db.execute(
            "SELECT access_token, refresh_token, spoo_email FROM linked_accounts WHERE discord_user_id = ?",
            (discord_user_id,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        return LinkedAccount(
            discord_user_id=discord_user_id,
            tokens=TokenPair(
                access_token=self._cipher.decrypt(row[0]),
                refresh_token=self._cipher.decrypt(row[1]),
            ),
            spoo_email=row[2],
        )

    async def delete(self, discord_user_id: int) -> bool:
        cur = await self.db.execute(
            "DELETE FROM linked_accounts WHERE discord_user_id = ?", (discord_user_id,)
        )
        await self.db.commit()
        return cur.rowcount > 0

    # ── link sessions (single-use, nonce-keyed) ──────────────────────────

    async def create_link_session(
        self, nonce: str, *, discord_user_id: int, interaction_token: str
    ) -> None:
        await self.db.execute(
            "INSERT OR REPLACE INTO link_sessions (nonce, discord_user_id, interaction_token) VALUES (?, ?, ?)",
            (nonce, discord_user_id, interaction_token),
        )
        await self.db.commit()

    async def consume_link_session(self, nonce: str) -> LinkSession | None:
        cur = await self.db.execute(
            "SELECT discord_user_id, interaction_token FROM link_sessions WHERE nonce = ?",
            (nonce,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        await self.db.execute("DELETE FROM link_sessions WHERE nonce = ?", (nonce,))
        await self.db.commit()
        return LinkSession(nonce=nonce, discord_user_id=row[0], interaction_token=row[1])
