from __future__ import annotations

import httpx
import pytest

from spoobot.errors import (
    ApiValidationError,
    AuthRequiredError,
    NotFoundError,
    RateLimitedError,
    ServerError,
)
from spoobot.infrastructure.http import create_client, raise_for_status_mapped


def _client(
    status: int, body: dict | None = None, headers: dict | None = None
) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body or {}, headers=headers or {})

    return create_client(
        base_url="https://t.test", transport=httpx.MockTransport(handler)
    )


@pytest.mark.parametrize(
    "status,exc",
    [
        (400, ApiValidationError),
        (401, AuthRequiredError),
        (404, NotFoundError),
        (500, ServerError),
    ],
)
async def test_status_mapping(status, exc):
    async with _client(status, {"message": "boom"}) as client:
        resp = await client.get("/")
        with pytest.raises(exc, match="boom"):
            raise_for_status_mapped(resp)


async def test_rate_limit_includes_retry_after():
    async with _client(429, {"error": "slow down"}, {"Retry-After": "13"}) as client:
        resp = await client.get("/")
        with pytest.raises(RateLimitedError) as ei:
            raise_for_status_mapped(resp)
        assert ei.value.retry_after == 13.0


async def test_2xx_passes():
    async with _client(200, {"ok": True}) as client:
        resp = await client.get("/")
        raise_for_status_mapped(resp)  # no raise


async def test_user_agent_header():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["ua"] = request.headers.get("User-Agent", "")
        return httpx.Response(200, json={})

    async with create_client(
        base_url="https://t.test", transport=httpx.MockTransport(handler)
    ) as client:
        await client.get("/")
    assert captured["ua"].startswith("spoo-bot/2.0")
