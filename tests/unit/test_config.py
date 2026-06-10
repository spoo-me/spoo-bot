from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from spoobot.config import Config, ConfigError, load_config

MINIMAL = """
[bot]
command_prefix = "$"
bot_token = "${TEST_BOT_TOKEN}"
super_user_id = "1"

[spoo]
api_base = "https://spoo.me"
qr_api_base = "https://qr.spoo.me"

[auth]
app_id = "spoo-discord"
state_secret = "${TEST_STATE_SECRET}"
vault_key = "${TEST_VAULT_KEY}"
vault_path = "data/vault.sqlite3"

[web]
enabled = true
host = "127.0.0.1"
port = 9274
public_callback_url = "https://discord-bot.spoo.me/callback"

[charts]
renderer = "quickchart"
quickchart_url = "https://quickchart.io"
"""


def write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(textwrap.dedent(body))
    return p


def test_env_interpolation(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TEST_STATE_SECRET", "s" * 32)
    monkeypatch.setenv("TEST_VAULT_KEY", "k" * 44)
    cfg = load_config(write(tmp_path, MINIMAL))
    assert isinstance(cfg, Config)
    assert cfg.bot.bot_token == "tok123"
    assert cfg.web.port == 9274


def test_missing_env_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("TEST_BOT_TOKEN", raising=False)
    monkeypatch.setenv("TEST_STATE_SECRET", "s" * 32)
    monkeypatch.setenv("TEST_VAULT_KEY", "k" * 44)
    with pytest.raises(ConfigError, match="TEST_BOT_TOKEN"):
        load_config(write(tmp_path, MINIMAL))


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")


def test_invalid_renderer_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_BOT_TOKEN", "t")
    monkeypatch.setenv("TEST_STATE_SECRET", "s" * 32)
    monkeypatch.setenv("TEST_VAULT_KEY", "k" * 44)
    bad = MINIMAL.replace('renderer = "quickchart"', 'renderer = "crayon"')
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, bad))
