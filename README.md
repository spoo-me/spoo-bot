# SpooBot

The official Discord bot for [spoo.me](https://spoo.me) — shorten URLs, emojify them, browse and manage your links, and explore click statistics without leaving Discord.

## How it works: two tiers, one bot

Every public command works **without an account** — you get anonymous shortening with the default limits. Linking your spoo.me account (`/link`) upgrades the same commands transparently:

| | Unlinked | Linked |
|---|---|---|
| `/shorten`, `/emojify` | anonymous link, default limits | saved to your account, your plan's limits |
| `/stats` | public stats by short code | your links autocomplete, private stats |
| `/links …` | — | full management: list, edit, toggle, delete |

Linking uses the spoo.me device-auth flow: the bot sends you a button, you approve in the browser, and the original Discord message edits itself once the callback lands. `/unlink` removes the stored tokens; revoke the grant itself at [spoo.me/dashboard/apps](https://spoo.me/dashboard/apps).

## Commands

| Command | Description |
|---|---|
| `/shorten` | Shorten a long URL (alias, password, max-clicks options) |
| `/emojify` | Convert a long URL to an emoji URL |
| `/stats` | Stats overview with charts: timeline, browsers, platforms, countries |
| `/links list` | Browse and manage your links |
| `/links edit` | Edit a link (autocomplete on your aliases) |
| `/links toggle` | Activate / deactivate a link |
| `/links delete` | Delete a link permanently |
| `/link` / `/unlink` / `/whoami` | Account linking |
| `/qr` | QR codes (classic or gradient) via qr.spoo.me |
| `/get-code` | API code snippet in 19 languages |
| `/help`, `/about`, `/invite`, `/support`, `/bot-stats` | Meta |

## Self-hosting

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/spoo-me/spoo-bot && cd spoo-bot
uv sync --group dev
cp config.template.toml config.toml   # then fill in the values
```

Secrets are read from the environment (a local `.env` file is loaded automatically):

| Variable | Purpose |
|---|---|
| `BOT_TOKEN` | Discord bot token |
| `STATE_SECRET` | HMAC secret for link-state signing (≥32 chars): `openssl rand -hex 32` |
| `VAULT_KEY` | Fernet key encrypting stored tokens: `uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

Run the bot:

```bash
uv run python -m spoobot
```

### Callback server

Account linking needs an inbound HTTPS callback. The bot runs a small aiohttp server (default `0.0.0.0:9274`, configurable under `[web]`) exposing `GET /callback` and `GET /health`. Point a reverse proxy at it, e.g. `discord-bot.spoo.me → :9274`, and set `web.public_callback_url` accordingly. Set `web.enabled = false` to run without linking support.

### Chart renderer

Two interchangeable renderers live behind one protocol; pick one in `config.toml`:

- `charts.renderer = "quickchart"` (default) — chart.js PNGs via QuickChart, no extra deps.
- `charts.renderer = "htmlcards"` — HTML/CSS cards screenshotted by headless Chromium. Requires `uv sync --group cards` and `uv run playwright install chromium`.

Country heatmaps render locally (SVG + resvg) in both modes. Compare them yourself with `uv run python scripts/chart_bakeoff.py`.

## Development

```bash
uv run pytest            # tests
uv run ruff check .      # lint
uv run ruff format .     # format
uv run pyright           # types
```

CI runs all four on every push.

## License

[Apache 2.0](LICENSE)
