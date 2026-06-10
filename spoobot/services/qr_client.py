from __future__ import annotations

from typing import Any

import httpx

from spoobot.infrastructure.http import raise_for_status_mapped


class QrClient:
    """Client for qr.spoo.me (public, no auth). httpx client injected with base_url set."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def _png(self, path: str, params: dict[str, Any]) -> bytes:
        resp = await self._http.get(path, params=params)
        raise_for_status_mapped(resp)
        return resp.content

    async def classic(
        self,
        content: str,
        *,
        color: str = "black",
        background: str = "white",
        size: int | None = None,
        style: str = "rounded",
    ) -> bytes:
        params: dict[str, Any] = {"content": content, "color": color, "style": style}
        if background != "white":
            params["background"] = background
        if size:
            params["size"] = size
        return await self._png("/api/v1/classic", params)

    async def gradient(
        self,
        content: str,
        *,
        start: str,
        end: str,
        direction: str = "vertical",
        size: int | None = None,
    ) -> bytes:
        params: dict[str, Any] = {"content": content, "start": start, "end": end}
        if direction != "vertical":
            params["direction"] = direction
        if size:
            params["size"] = size
        return await self._png("/api/v1/gradient", params)
