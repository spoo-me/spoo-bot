from __future__ import annotations

from typing import Awaitable, Callable, Protocol

import httpx
from aiohttp import web

from spoobot.infrastructure.logging import get_logger
from spoobot.services.auth import LinkError, LinkResult

log = get_logger(__name__)

_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>spoo.me × Discord</title>
<style>
  body {{ background:#000; color:#dcddde; font:16px/1.6 system-ui, sans-serif;
         display:grid; place-items:center; min-height:100vh; margin:0 }}
  .card {{ text-align:center; padding:2.5rem 3rem; border:1px solid #2e3035; border-radius:12px }}
  h1 {{ font-size:1.25rem; margin:0 0 .5rem }}
  .ok {{ color:#2ecc71 }} .err {{ color:#e74c3c }}
</style></head>
<body><div class="card"><h1 class="{cls}">{title}</h1><p>{body}</p></div></body></html>"""


class CompletesLink(Protocol):
    async def complete_link(self, *, code: str, state: str) -> LinkResult: ...


def make_app(
    auth: CompletesLink,
    *,
    on_linked: Callable[[LinkResult], Awaitable[None]] | None = None,
) -> web.Application:
    async def callback(request: web.Request) -> web.Response:
        code = request.query.get("code", "")
        state = request.query.get("state", "")
        if not code or not state:
            return web.Response(
                text=_PAGE.format(cls="err", title="Missing parameters",
                                  body="This page is reached from the /link command in Discord."),
                content_type="text/html", status=400,
            )
        try:
            result = await auth.complete_link(code=code, state=state)
        except LinkError as exc:
            return web.Response(
                text=_PAGE.format(cls="err", title="Linking failed", body=str(exc)),
                content_type="text/html", status=400,
            )
        except Exception:
            log.exception("link completion failed")
            return web.Response(
                text=_PAGE.format(cls="err", title="Linking failed",
                                  body="Something went wrong. Run /link again in Discord."),
                content_type="text/html", status=500,
            )
        if on_linked is not None:
            try:
                await on_linked(result)
            except Exception:
                log.exception("on_linked notifier failed")
        return web.Response(
            text=_PAGE.format(cls="ok", title="Account linked ✓",
                              body=f"Linked as {result.spoo_email}. You can close this tab "
                                   "and head back to Discord."),
            content_type="text/html",
        )

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    app = web.Application()
    app.router.add_get("/callback", callback)
    app.router.add_get("/health", health)
    return app


def make_interaction_notifier(
    application_id: int, http: httpx.AsyncClient
) -> Callable[[LinkResult], Awaitable[None]]:
    """Edits the original ephemeral /link message via the interaction webhook.

    `http` is an httpx.AsyncClient (the bot's misc client).
    """

    async def notify(result: LinkResult) -> None:
        url = (
            f"https://discord.com/api/v10/webhooks/{application_id}"
            f"/{result.interaction_token}/messages/@original"
        )
        payload = {
            "content": "",
            "embeds": [{
                "title": "Account linked ✓",
                "description": f"Linked as **{result.spoo_email}**. Account commands are live — try `/links`.",
                "color": 0x2ECC71,
            }],
            "components": [],
        }
        resp = await http.patch(url, json=payload)
        if resp.status_code >= 400:
            log.warning("interaction edit failed status=%s", resp.status_code)

    return notify
