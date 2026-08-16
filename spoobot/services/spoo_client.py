"""Async client for the modern spoo.me API (/api/v1) and device-auth endpoints.

LEGACY EXCEPTIONS (the only two, by decision):
  - POST /emoji      — emojify has no /api/v1 equivalent yet
  - GET  /metric     — public site totals used by the community stats channels
Both are marked # LEGACY below; remove when v1 grows equivalents.
"""

from __future__ import annotations

from typing import Any

import httpx

from spoobot.errors import AuthRequiredError
from spoobot.infrastructure.http import raise_for_status_mapped
from spoobot.services.models import (
    AliasCheck,
    DeviceTokenGrant,
    PublicStats,
    ShortUrl,
    SiteMetrics,
    SpooProfile,
    TokenPair,
    UrlListItem,
    UrlPage,
)


class SpooClient:
    """The httpx.AsyncClient is injected with base_url already set
    (create_client(base_url=cfg.spoo.api_base)) — paths below are relative."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    # ── plumbing ─────────────────────────────────────────────────────────

    def _headers(self, token: str | None) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"} if token else {}

    async def _json(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        resp = await self._http.request(
            method, path, params=params, json=json, headers=self._headers(token)
        )
        raise_for_status_mapped(resp)
        return resp.json()

    @staticmethod
    def _require(token: str | None) -> str:
        if not token:
            raise AuthRequiredError(
                "this action requires a linked spoo.me account", status=401
            )
        return token

    # ── shortening ───────────────────────────────────────────────────────

    async def shorten(
        self,
        long_url: str,
        *,
        alias: str | None = None,
        password: str | None = None,
        max_clicks: int | None = None,
        expire_after: str | None = None,
        block_bots: bool | None = None,
        private_stats: bool | None = None,
        domain: str | None = None,
        token: str | None = None,
    ) -> ShortUrl:
        body: dict[str, Any] = {"long_url": long_url}
        for key, val in {
            "alias": alias,
            "password": password,
            "max_clicks": max_clicks,
            "expire_after": expire_after,
            "block_bots": block_bots,
            "private_stats": private_stats,
            "domain": domain,
        }.items():
            if val is not None:
                body[key] = val
        data = await self._json("POST", "/api/v1/shorten", token=token, json=body)
        return ShortUrl.model_validate(data)

    async def check_alias(self, alias: str, *, token: str | None = None) -> AliasCheck:
        data = await self._json(
            "GET", "/api/v1/shorten/check-alias", token=token, params={"alias": alias}
        )
        return AliasCheck.model_validate(data)

    async def emojify(
        self,
        long_url: str,
        *,
        emojies: str | None = None,
        password: str | None = None,
        max_clicks: int | None = None,
    ) -> ShortUrl:
        # LEGACY: no /api/v1 emoji endpoint exists (research §6).
        body: dict[str, Any] = {"url": long_url}
        if emojies:
            body["emojies"] = emojies
        if password:
            body["password"] = password
        if max_clicks:
            body["max-clicks"] = max_clicks
        data = await self._json("POST", "/emoji", json=body)
        short_url = data.get("short_url", "")
        return ShortUrl(
            alias=short_url.rstrip("/").split("/")[-1],
            short_url=short_url,
            long_url=long_url,
        )

    # ── link management (auth required) ──────────────────────────────────

    async def list_urls(
        self,
        token: str,
        *,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> UrlPage:
        self._require(token)
        params: dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        if search:
            params["filter"] = f'{{"search": "{search}"}}'
        data = await self._json("GET", "/api/v1/urls", token=token, params=params)
        return UrlPage.model_validate(data)

    async def update_url(self, token: str, url_id: str, **fields: Any) -> UrlListItem:
        self._require(token)
        data = await self._json(
            "PATCH", f"/api/v1/urls/{url_id}", token=token, json=fields
        )
        return UrlListItem.model_validate(data)

    async def set_url_status(self, token: str, url_id: str, status: str) -> UrlListItem:
        self._require(token)
        data = await self._json(
            "PATCH",
            f"/api/v1/urls/{url_id}/status",
            token=token,
            json={"status": status},
        )
        return UrlListItem.model_validate(data)

    async def delete_url(self, token: str, url_id: str) -> None:
        self._require(token)
        await self._json("DELETE", f"/api/v1/urls/{url_id}", token=token)

    # ── stats ────────────────────────────────────────────────────────────

    async def public_stats(
        self,
        short_code: str,
        *,
        password: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        timezone: str = "UTC",
        token: str | None = None,
    ) -> PublicStats:
        """Per-link public statistics, no auth required.

        The endpoint returns every dimension in one response (no group_by
        param). A password only travels in a POST body — the server ignores
        query-string passwords — so a password flips the method to POST.
        An owner token bypasses the privacy and password gates.
        """
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if timezone != "UTC":
            params["timezone"] = timezone
        path = f"/api/v1/public/stats/{short_code}"
        if password:
            data = await self._json(
                "POST", path, token=token, params=params, json={"password": password}
            )
        else:
            data = await self._json("GET", path, token=token, params=params)
        return PublicStats.model_validate(data)

    # ── account / auth ───────────────────────────────────────────────────

    async def me(self, token: str) -> SpooProfile:
        self._require(token)
        data = await self._json("GET", "/auth/me", token=token)
        return SpooProfile.model_validate(data)

    async def exchange_device_code(self, code: str) -> DeviceTokenGrant:
        data = await self._json("POST", "/auth/device/token", json={"code": code})
        return DeviceTokenGrant.model_validate(data)

    async def refresh_device_tokens(self, refresh_token: str) -> TokenPair:
        data = await self._json(
            "POST", "/auth/device/refresh", json={"refresh_token": refresh_token}
        )
        return TokenPair.model_validate(data)

    # ── site metrics ─────────────────────────────────────────────────────

    async def site_metrics(self) -> SiteMetrics:
        # LEGACY: public totals endpoint predates /api/v1.
        data = await self._json("GET", "/metric")
        return SiteMetrics.model_validate(data)
