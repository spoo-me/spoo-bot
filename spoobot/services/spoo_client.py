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
    ExportFile,
    ShortUrl,
    SiteMetrics,
    SpooProfile,
    StatsResult,
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

    # ── stats & export ───────────────────────────────────────────────────

    async def stats(
        self,
        *,
        scope: str,
        short_code: str | None = None,
        group_by: list[str] | None = None,
        metrics: list[str] | None = None,
        timezone: str = "UTC",
        password: str | None = None,
        token: str | None = None,
    ) -> StatsResult:
        params: dict[str, Any] = {"scope": scope}
        if short_code:
            params["short_code"] = short_code
        if group_by:
            params["group_by"] = ",".join(group_by)
        if metrics:
            params["metrics"] = ",".join(metrics)
        if timezone != "UTC":
            params["timezone"] = timezone
        if password:
            params["password"] = password
        data = await self._json("GET", "/api/v1/stats", token=token, params=params)
        return StatsResult.model_validate(data)

    async def export(
        self,
        *,
        scope: str,
        fmt: str,
        short_code: str | None = None,
        token: str | None = None,
    ) -> ExportFile:
        params: dict[str, Any] = {"scope": scope, "format": fmt}
        if short_code:
            params["short_code"] = short_code
        resp = await self._http.get(
            "/api/v1/export", params=params, headers=self._headers(token)
        )
        raise_for_status_mapped(resp)
        dispo = resp.headers.get("Content-Disposition", "")
        filename = "export"
        if "filename=" in dispo:
            filename = dispo.split("filename=")[-1].strip('" ')
        return ExportFile(filename=filename, content=resp.content)

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
